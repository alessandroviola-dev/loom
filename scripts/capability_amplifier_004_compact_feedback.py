#!/usr/bin/env python3
"""LOOM Capability Amplifier 004 — compact deterministic repair feedback.

Frozen transform of Capability Amplifier 001 preserving the validated
Amplifier 002 call-isolation policy and Amplifier 003 repair context 3072.
The only behavioral change vs Amplifier 003 is a deterministic 768-byte
UTF-8 budget for the variable repair-feedback detail body.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_BLOB = "9f472c60b523762276291232f6e8c6ffc1c5fcae"
AMPLIFIER_002_WRAPPER_BLOB = "df332568820e28c90baa5247df27e92cba43c0d6"
AMPLIFIER_003_WRAPPER_BLOB = "c2bcc8f126eb5b599645ba12d1fd08a348e2b443"
REPAIR_CONTEXT = 3072
FEEDBACK_DETAIL_BUDGET_BYTES = 768

OLD_RUN_MODEL_CALL = '''def run_model_call(adapter, prompt: str, task_id: str, phase: str, telemetry: list[dict]):
    monitor = SafetyMonitor(MODEL, task_id, phase, telemetry)
    monitor.start()
    response = None
    error = None
    try:
        response = adapter.ollama_generate(BASE_URL, MODEL, prompt, CONTEXT)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        monitor.stop()
    return response, error, monitor
'''

NEW_RUN_MODEL_CALL = '''def isolation_unload(model: str, task_id: str, phase: str, sink: list[dict], call_context: int) -> str | None:
    started = time.perf_counter()
    stop_result = run(["ollama", "stop", model], timeout=20)
    deadline = time.perf_counter() + 30.0
    last_ps = None

    while time.perf_counter() < deadline:
        last_ps = run(["ollama", "ps"], timeout=10)
        if last_ps.get("exit_code") != 0:
            return f"ollama ps failed during isolation: {last_ps!r}"
        if model not in last_ps.get("stdout", ""):
            sample = system_sample(task_id, f"{phase}_isolation")
            sample["isolation_event"] = "model_unloaded"
            sample["isolation_wait_seconds"] = round(time.perf_counter() - started, 3)
            sample["ollama_stop_exit_code"] = stop_result.get("exit_code")
            sample["call_context"] = call_context
            sink.append(sample)
            if sample.get("memory_free_percent") is None or sample.get("swap_used_mb") is None:
                return "required isolation telemetry unavailable"
            return None
        time.sleep(0.25)

    return f"model still resident after isolation timeout; last ollama ps={last_ps!r}"


def run_model_call(adapter, prompt: str, task_id: str, phase: str, telemetry: list[dict]):
    call_context = REPAIR_CONTEXT if phase == "repair" else CONTEXT
    monitor = SafetyMonitor(MODEL, task_id, phase, telemetry)
    monitor.isolation_reason = None
    monitor.call_context = call_context

    pre_error = isolation_unload(MODEL, task_id, f"{phase}_pre", telemetry, call_context)
    if pre_error:
        monitor.isolation_reason = pre_error
        return None, None, monitor

    monitor.start()
    response = None
    error = None
    try:
        response = adapter.ollama_generate(BASE_URL, MODEL, prompt, call_context)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        monitor.stop()

    post_error = isolation_unload(MODEL, task_id, f"{phase}_post", telemetry, call_context)
    if post_error:
        monitor.isolation_reason = post_error
    return response, error, monitor
'''

COMPACT_HELPER = '''def utf8_tail(text: str, budget_bytes: int) -> str:
    raw = text.encode("utf-8")
    if len(raw) <= budget_bytes:
        return text
    tail = raw[-budget_bytes:]
    while tail:
        try:
            return tail.decode("utf-8")
        except UnicodeDecodeError as exc:
            tail = tail[exc.start + 1 :]
    return ""


def compact_feedback(feedback: str) -> str:
    lines = feedback.splitlines()
    if not lines:
        return ""
    first = lines[0]
    detail = "\n".join(lines[1:])
    detail_tail = utf8_tail(detail, FEEDBACK_DETAIL_BUDGET_BYTES)
    if detail == detail_tail:
        return feedback
    return first + "\nCompact failure-detail tail (deterministic UTF-8 budget):\n" + detail_tail

'''

INITIAL_GUARDRAIL_BLOCK = '''        if monitor.guardrail_reason:
            summary["classification"] = "PARTIAL_RESOURCE_FAIL"
            summary["failure_reason"] = monitor.guardrail_reason
            summary["tasks"].append(record)
            return finish(5)
        if call_error or response is None:
'''

INITIAL_GUARDRAIL_REPLACEMENT = '''        if monitor.guardrail_reason:
            summary["classification"] = "PARTIAL_RESOURCE_FAIL"
            summary["failure_reason"] = monitor.guardrail_reason
            summary["tasks"].append(record)
            return finish(5)
        if getattr(monitor, "isolation_reason", None):
            summary["classification"] = "ISOLATION_FAIL"
            summary["failure_reason"] = monitor.isolation_reason
            summary["tasks"].append(record)
            return finish(8)
        if call_error or response is None:
'''

REPAIR_GUARDRAIL_BLOCK = '''        if repair_monitor.guardrail_reason:
            summary["classification"] = "PARTIAL_RESOURCE_FAIL"
            summary["failure_reason"] = repair_monitor.guardrail_reason
            summary["tasks"].append(record)
            return finish(5)
        if repair_call_error or repair_response is None:
'''

REPAIR_GUARDRAIL_REPLACEMENT = '''        if repair_monitor.guardrail_reason:
            summary["classification"] = "PARTIAL_RESOURCE_FAIL"
            summary["failure_reason"] = repair_monitor.guardrail_reason
            summary["tasks"].append(record)
            return finish(5)
        if getattr(repair_monitor, "isolation_reason", None):
            summary["classification"] = "ISOLATION_FAIL"
            summary["failure_reason"] = repair_monitor.isolation_reason
            summary["tasks"].append(record)
            return finish(8)
        if repair_call_error or repair_response is None:
'''

OLD_REPAIR_PROMPT_CALL = '''        repair_prompt = build_repair_prompt(frozen_task, working_task, task, feedback_kind, feedback)
        (prompt_dir / f"{task_id}-repair.txt").write_text(repair_prompt, encoding="utf-8")
'''

NEW_REPAIR_PROMPT_CALL = '''        compact_feedback_text = compact_feedback(feedback)
        record["repair"]["feedback_original_bytes"] = len(feedback.encode("utf-8"))
        record["repair"]["feedback_compact_bytes"] = len(compact_feedback_text.encode("utf-8"))
        record["repair"]["feedback_truncated"] = compact_feedback_text != feedback
        record["repair"]["feedback_detail_budget_bytes"] = FEEDBACK_DETAIL_BUDGET_BYTES
        repair_prompt = build_repair_prompt(frozen_task, working_task, task, feedback_kind, compact_feedback_text)
        record["repair"]["prompt_bytes"] = len(repair_prompt.encode("utf-8"))
        (prompt_dir / f"{task_id}-repair.txt").write_text(repair_prompt, encoding="utf-8")
'''


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_exact(text: str, old: str, new: str, label: str, expected_count: int = 1) -> str:
    count = text.count(old)
    if count != expected_count:
        raise RuntimeError(f"{label}: expected {expected_count} exact matches, found {count}")
    return text.replace(old, new)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source = repo / "scripts" / "capability_amplifier_001.py"
    wrapper_002 = repo / "scripts" / "capability_amplifier_002_call_isolated.py"
    wrapper_003 = repo / "scripts" / "capability_amplifier_003_repair_context_3072.py"

    observed_source = git_blob(source, repo)
    observed_002 = git_blob(wrapper_002, repo)
    observed_003 = git_blob(wrapper_003, repo)

    print("LOOM Capability Amplifier 004 — Compact Feedback frozen transform")
    print(f"Amplifier 001 source blob: {observed_source}")
    print(f"Amplifier 002 wrapper blob: {observed_002}")
    print(f"Amplifier 003 wrapper blob: {observed_003}")

    if observed_source != SOURCE_BLOB:
        print(f"Source blob preflight: FAIL expected {SOURCE_BLOB}", file=sys.stderr)
        return 2
    if observed_002 != AMPLIFIER_002_WRAPPER_BLOB:
        print(f"Amplifier 002 provenance preflight: FAIL expected {AMPLIFIER_002_WRAPPER_BLOB}", file=sys.stderr)
        return 2
    if observed_003 != AMPLIFIER_003_WRAPPER_BLOB:
        print(f"Amplifier 003 provenance preflight: FAIL expected {AMPLIFIER_003_WRAPPER_BLOB}", file=sys.stderr)
        return 2

    print("Source/provenance blob preflight: PASS")

    text = source.read_text(encoding="utf-8")
    text = replace_exact(
        text,
        'CONTEXT = 4096\nBASE_URL = "http://127.0.0.1:11434"',
        'CONTEXT = 4096\nREPAIR_CONTEXT = 3072\nFEEDBACK_DETAIL_BUDGET_BYTES = 768\nBASE_URL = "http://127.0.0.1:11434"',
        "repair context and feedback constants",
    )
    text = replace_exact(text, OLD_RUN_MODEL_CALL, NEW_RUN_MODEL_CALL, "run_model_call transform")
    text = replace_exact(text, "def build_repair_prompt(", COMPACT_HELPER + "def build_repair_prompt(", "compact feedback helper")
    text = replace_exact(text, INITIAL_GUARDRAIL_BLOCK, INITIAL_GUARDRAIL_REPLACEMENT, "initial isolation classification")
    text = replace_exact(text, REPAIR_GUARDRAIL_BLOCK, REPAIR_GUARDRAIL_REPLACEMENT, "repair isolation classification")
    text = replace_exact(text, OLD_REPAIR_PROMPT_CALL, NEW_REPAIR_PROMPT_CALL, "compact repair prompt call")

    text = replace_exact(
        text,
        'summary["model_calls"].append({"task": task_id, "phase": "initial", "metrics": initial_metrics})',
        'summary["model_calls"].append({"task": task_id, "phase": "initial", "context": CONTEXT, "metrics": initial_metrics})',
        "initial call context record",
    )
    text = replace_exact(
        text,
        'summary["model_calls"].append({"task": task_id, "phase": "repair", "metrics": repair_metrics})',
        'summary["model_calls"].append({"task": task_id, "phase": "repair", "context": REPAIR_CONTEXT, "metrics": repair_metrics})',
        "repair call context record",
    )
    text = replace_exact(
        text,
        'run_dir = repo / "results-local" / "amplify" / "capability-amplifier-001" / run_id',
        'run_dir = repo / "results-local" / "amplify" / "capability-amplifier-004-compact-feedback" / run_id',
        "run directory",
    )
    text = replace_exact(
        text,
        '"experiment": "Capability Amplifier 001",',
        '"experiment": "Capability Amplifier 004 — Compact Feedback",',
        "experiment label",
    )
    text = replace_exact(
        text,
        '"amplifier": "frozen_initial_plus_deterministic_validation_plus_max_one_repair",',
        '"amplifier": "initial_plus_validation_plus_one_repair_plus_isolation_plus_ctx3072_plus_compact_feedback",\n        "residency_policy": "ollama_stop_and_confirm_unloaded_between_every_model_call",\n        "context_policy": {"initial": 4096, "repair": 3072},\n        "feedback_policy": {"detail_budget_utf8_bytes": 768, "method": "preserve_first_line_plus_utf8_safe_tail"},',
        "amplifier metadata",
    )
    text = replace_exact(
        text,
        '"LOOM_MODE": "capability_amplifier_001",',
        '"LOOM_MODE": "capability_amplifier_004_compact_feedback",',
        "scorer mode",
    )
    text = replace_exact(
        text,
        'print("LOOM Capability Amplifier 001")',
        'print("LOOM Capability Amplifier 004 — Compact Feedback")',
        "console label",
    )

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=source.parent,
            prefix=".capability_amplifier_004_runtime_",
            suffix=".py",
            delete=False,
        ) as handle:
            handle.write(text)
            temp_path = Path(handle.name)

        print("Call-isolation transform: PASS")
        print("Context policy: initial=4096, repair=3072")
        print("Compact feedback policy: first line + <=768 UTF-8 bytes detail tail")
        print("Guardrails unchanged: free<5% OR swap>5600 MB")
        proc = subprocess.run([sys.executable, str(temp_path)], cwd=repo, check=False)
        return proc.returncode
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
