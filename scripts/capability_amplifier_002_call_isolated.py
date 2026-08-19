#!/usr/bin/env python3
"""LOOM Capability Amplifier 002 — call-isolated transform.

Transforms the frozen Capability Amplifier 001 runner only at the residency
boundary. The quality mechanism, prompts, validation, repair policy, candidate
selection, benchmark and scorer remain inherited from the locked source blob.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_BLOB = "9f472c60b523762276291232f6e8c6ffc1c5fcae"

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

NEW_RUN_MODEL_CALL = '''def isolation_unload(model: str, task_id: str, phase: str, sink: list[dict]) -> str | None:
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
            sink.append(sample)
            if sample.get("memory_free_percent") is None or sample.get("swap_used_mb") is None:
                return "required isolation telemetry unavailable"
            return None
        time.sleep(0.25)

    return f"model still resident after isolation timeout; last ollama ps={last_ps!r}"


def run_model_call(adapter, prompt: str, task_id: str, phase: str, telemetry: list[dict]):
    monitor = SafetyMonitor(MODEL, task_id, phase, telemetry)
    monitor.isolation_reason = None

    pre_error = isolation_unload(MODEL, task_id, f"{phase}_pre", telemetry)
    if pre_error:
        monitor.isolation_reason = pre_error
        return None, None, monitor

    monitor.start()
    response = None
    error = None
    try:
        response = adapter.ollama_generate(BASE_URL, MODEL, prompt, CONTEXT)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        monitor.stop()

    post_error = isolation_unload(MODEL, task_id, f"{phase}_post", telemetry)
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
    observed = git_blob(source, repo)
    print("LOOM Capability Amplifier 002 — Call-Isolated frozen transform")
    print(f"Amplifier 001 source blob: {observed}")
    if observed != SOURCE_BLOB:
        print(f"Source blob preflight: FAIL expected {SOURCE_BLOB}", file=sys.stderr)
        return 2
    print("Source blob preflight: PASS")

    text = source.read_text(encoding="utf-8")
    text = replace_exact(text, OLD_RUN_MODEL_CALL, NEW_RUN_MODEL_CALL, "run_model_call transform")
    text = replace_exact(text, INITIAL_GUARDRAIL_BLOCK, INITIAL_GUARDRAIL_REPLACEMENT, "initial isolation classification")
    text = replace_exact(text, REPAIR_GUARDRAIL_BLOCK, REPAIR_GUARDRAIL_REPLACEMENT, "repair isolation classification")
    text = replace_exact(
        text,
        'run_dir = repo / "results-local" / "amplify" / "capability-amplifier-001" / run_id',
        'run_dir = repo / "results-local" / "amplify" / "capability-amplifier-002-call-isolated" / run_id',
        "run directory",
    )
    text = replace_exact(
        text,
        '"experiment": "Capability Amplifier 001",',
        '"experiment": "Capability Amplifier 002 — Call-Isolated",',
        "experiment label",
    )
    text = replace_exact(
        text,
        '"amplifier": "frozen_initial_plus_deterministic_validation_plus_max_one_repair",',
        '"amplifier": "frozen_initial_plus_validation_plus_max_one_repair_plus_call_isolation",\n        "residency_policy": "ollama_stop_and_confirm_unloaded_between_every_model_call",',
        "residency metadata",
    )
    text = replace_exact(
        text,
        '"LOOM_MODE": "capability_amplifier_001",',
        '"LOOM_MODE": "capability_amplifier_002_call_isolated",',
        "scorer mode",
    )
    text = replace_exact(
        text,
        'print("LOOM Capability Amplifier 001")',
        'print("LOOM Capability Amplifier 002 — Call-Isolated")',
        "console label",
    )

    # The repair prompt label is intentionally NOT transformed: keeping the inherited
    # prompt byte-for-byte preserves the capability mechanism. Only residency changes.

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=source.parent,
            prefix=".capability_amplifier_002_runtime_",
            suffix=".py",
            delete=False,
        ) as handle:
            handle.write(text)
            temp_path = Path(handle.name)

        print("Call-isolation transform: PASS")
        print("Residency policy: unload + confirm absent from ollama ps between every model call")
        print("Inter-call >=70% recovery gate: NONE (single-factor design)")
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
