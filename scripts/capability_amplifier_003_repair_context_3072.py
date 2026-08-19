#!/usr/bin/env python3
"""LOOM Capability Amplifier 003 — repair context 3072.

Frozen transform of Capability Amplifier 001 preserving the validated
Amplifier 002 call-isolation policy. The only behavioral change vs 002 is:
- initial calls: num_ctx=4096
- repair calls: num_ctx=3072
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_BLOB = "9f472c60b523762276291232f6e8c6ffc1c5fcae"
AMPLIFIER_002_WRAPPER_BLOB = "df332568820e28c90baa5247df27e92cba43c0d6"
REPAIR_CONTEXT = 3072

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

    observed_source = git_blob(source, repo)
    observed_002 = git_blob(wrapper_002, repo)

    print("LOOM Capability Amplifier 003 — Repair Context 3072 frozen transform")
    print(f"Amplifier 001 source blob: {observed_source}")
    print(f"Amplifier 002 wrapper blob: {observed_002}")

    if observed_source != SOURCE_BLOB:
        print(f"Source blob preflight: FAIL expected {SOURCE_BLOB}", file=sys.stderr)
        return 2
    if observed_002 != AMPLIFIER_002_WRAPPER_BLOB:
        print(f"Amplifier 002 provenance preflight: FAIL expected {AMPLIFIER_002_WRAPPER_BLOB}", file=sys.stderr)
        return 2

    print("Source/provenance blob preflight: PASS")

    text = source.read_text(encoding="utf-8")
    text = replace_exact(
        text,
        'CONTEXT = 4096\nBASE_URL = "http://127.0.0.1:11434"',
        'CONTEXT = 4096\nREPAIR_CONTEXT = 3072\nBASE_URL = "http://127.0.0.1:11434"',
        "repair context constant",
    )
    text = replace_exact(text, OLD_RUN_MODEL_CALL, NEW_RUN_MODEL_CALL, "run_model_call transform")
    text = replace_exact(text, INITIAL_GUARDRAIL_BLOCK, INITIAL_GUARDRAIL_REPLACEMENT, "initial isolation classification")
    text = replace_exact(text, REPAIR_GUARDRAIL_BLOCK, REPAIR_GUARDRAIL_REPLACEMENT, "repair isolation classification")

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
        'run_dir = repo / "results-local" / "amplify" / "capability-amplifier-003-repair-context-3072" / run_id',
        "run directory",
    )
    text = replace_exact(
        text,
        '"experiment": "Capability Amplifier 001",',
        '"experiment": "Capability Amplifier 003 — Repair Context 3072",',
        "experiment label",
    )
    text = replace_exact(
        text,
        '"amplifier": "frozen_initial_plus_deterministic_validation_plus_max_one_repair",',
        '"amplifier": "frozen_initial_plus_validation_plus_max_one_repair_plus_call_isolation_plus_repair_context_3072",\n        "residency_policy": "ollama_stop_and_confirm_unloaded_between_every_model_call",\n        "context_policy": {"initial": 4096, "repair": 3072},',
        "amplifier metadata",
    )
    text = replace_exact(
        text,
        '"LOOM_MODE": "capability_amplifier_001",',
        '"LOOM_MODE": "capability_amplifier_003_repair_context_3072",',
        "scorer mode",
    )
    text = replace_exact(
        text,
        'print("LOOM Capability Amplifier 001")',
        'print("LOOM Capability Amplifier 003 — Repair Context 3072")',
        "console label",
    )

    # Repair prompt content is intentionally inherited byte-for-byte from Amplifier 001.
    # Only model residency and the repair-call context allocation differ operationally.

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=source.parent,
            prefix=".capability_amplifier_003_runtime_",
            suffix=".py",
            delete=False,
        ) as handle:
            handle.write(text)
            temp_path = Path(handle.name)

        print("Call-isolation transform: PASS")
        print("Context policy: initial=4096, repair=3072")
        print("Inter-call >=70% recovery gate: NONE")
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
