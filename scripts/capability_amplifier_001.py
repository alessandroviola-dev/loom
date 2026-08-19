#!/usr/bin/env python3
"""LOOM Capability Amplifier 001.

Primary subject: qwen3.5:4b-mlx via Ollama.

For every frozen Coding Benchmark 01 v1.0.1 task:
1. run the exact frozen single-shot prompt/request/parser once;
2. deterministically validate parser delivery or frozen task tests;
3. if needed, permit exactly one repair call with deterministic feedback;
4. select initial vs repair candidate by frozen test pass count, ties to initial;
5. score the final isolated benchmark tree with the exact frozen scorer.

No Pi, no human repair, no third call, no retrieval, no web access.
Standard library only.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL = "qwen3.5:4b-mlx"
CONTEXT = 4096
BASE_URL = "http://127.0.0.1:11434"
ADAPTER_BLOB = "62abab57f6463c5813809b43d8f1e7bdfec5f304"
SCORER_BLOB = "754e9a6506968d2b191bff57997710591efe8133"
MANIFEST_BLOB = "547050ecd0183b8d447dc3e21e724a8232f10297"
BENCHMARK_VERSION = "1.0.1"
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
HOST_GATE_FREE_PERCENT = 70
HOST_GATE_SAMPLES = 3
POLL_SECONDS = 1.0

BASELINE_ARTIFACT = 40.71
BASELINE_DELIVERY_SCORE = 30.00
BASELINE_DELIVERY_COUNT = 3
PI_REFERENCE_DELIVERY_SCORE = 77.15


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path | None = None, timeout: int = 30, env: dict | None = None) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": args,
            "error": f"{type(exc).__name__}: {exc}",
            "wall_seconds": round(time.perf_counter() - started, 3),
        }


def git_blob(path: Path, repo: Path) -> str:
    result = run(["git", "hash-object", str(path)], cwd=repo, timeout=20)
    return result.get("stdout", "").strip() if result.get("exit_code") == 0 else ""


def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def disk_snapshot(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {
        "free_bytes": usage.free,
        "free_gib": round(usage.free / (1024 ** 3), 3),
    }


def parse_scaled_mb(value: str, unit: str) -> float:
    number = float(value.replace(",", "."))
    unit = unit.upper()
    if unit == "K":
        return number / 1024.0
    if unit == "M":
        return number
    if unit == "G":
        return number * 1024.0
    if unit == "T":
        return number * 1024.0 * 1024.0
    return number


def swap_used_mb() -> float | None:
    result = run(["sysctl", "-n", "vm.swapusage"], timeout=10)
    if result.get("exit_code") != 0:
        return None
    match = re.search(
        r"\bused\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])(?:B)?\b",
        result.get("stdout", ""),
        re.IGNORECASE,
    )
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def memory_free_percent() -> tuple[int | None, str]:
    result = run(["memory_pressure"], timeout=15)
    text = result.get("stdout", "") + result.get("stderr", "")
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    if not match:
        return None, text.strip()
    value = int(match.group(1))
    return value, f"System-wide memory free percentage: {value}%"


def system_sample(task_id: str | None = None, phase: str | None = None) -> dict:
    free, pressure = memory_free_percent()
    return {
        "timestamp_utc": utc_now(),
        "task": task_id,
        "phase": phase,
        "memory_free_percent": free,
        "memory_pressure": pressure,
        "swap_used_mb": swap_used_mb(),
    }


def sample_failure(sample: dict) -> tuple[str | None, str | None]:
    free = sample.get("memory_free_percent")
    swap = sample.get("swap_used_mb")
    if free is None or swap is None:
        return None, "required memory/swap telemetry unavailable"
    if free < MIN_FREE_PERCENT:
        return f"memory free {free}% < {MIN_FREE_PERCENT}%", None
    if swap > MAX_SWAP_MB:
        return f"swap used {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB", None
    return None, None


class SafetyMonitor:
    def __init__(self, model: str, task_id: str, phase: str, sink: list[dict]):
        self.model = model
        self.task_id = task_id
        self.phase = phase
        self.sink = sink
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.guardrail_reason: str | None = None
        self.telemetry_reason: str | None = None

    def _loop(self) -> None:
        while not self.stop_event.is_set():
            sample = system_sample(self.task_id, self.phase)
            self.sink.append(sample)
            guardrail, telemetry = sample_failure(sample)
            if guardrail or telemetry:
                self.guardrail_reason = guardrail
                self.telemetry_reason = telemetry
                run(["ollama", "stop", self.model], timeout=20)
                return
            self.stop_event.wait(POLL_SECONDS)

    def start(self) -> None:
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=5)


def telemetry_summary(samples: list[dict]) -> dict:
    free = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    swap = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    return {
        "sample_count": len(samples),
        "min_memory_free_percent": min(free) if free else None,
        "peak_swap_used_mb": max(swap) if swap else None,
    }


def host_gate() -> tuple[bool, list[dict], str | None]:
    samples: list[dict] = []
    for index in range(HOST_GATE_SAMPLES):
        sample = system_sample(None, "host_gate")
        samples.append(sample)
        free = sample.get("memory_free_percent")
        swap = sample.get("swap_used_mb")
        print(f"Host sample {index + 1}/{HOST_GATE_SAMPLES}: free={free}% swap={swap} MB", flush=True)
        if free is None or swap is None:
            return False, samples, "required host telemetry unavailable"
        if free < HOST_GATE_FREE_PERCENT:
            return False, samples, f"host free {free}% < {HOST_GATE_FREE_PERCENT}%"
        if swap > MAX_SWAP_MB:
            return False, samples, f"host swap {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB"
        if index + 1 < HOST_GATE_SAMPLES:
            time.sleep(1.0)
    return True, samples, None


def snapshot_editables(task_dir: Path, editable: list[str]) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for name in editable:
        path = task_dir / name
        result[name] = path.read_text(encoding="utf-8") if path.exists() else None
    return result


def restore_editables(task_dir: Path, snapshot: dict[str, str | None]) -> None:
    for name, content in snapshot.items():
        path = task_dir / name
        if content is None:
            if path.exists():
                path.unlink()
        else:
            path.write_text(content, encoding="utf-8")


def write_files(task_dir: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        (task_dir / name).write_text(content, encoding="utf-8")


def validate_test_result(result: dict) -> None:
    if result.get("runner_probe_error"):
        raise RuntimeError(f"frozen test probe failed for {result.get('id')}")
    total = result.get("tests_total")
    passed = result.get("tests_passed")
    if not isinstance(total, int) or total <= 0 or not isinstance(passed, int):
        raise RuntimeError(f"invalid frozen test result for {result.get('id')}: {result!r}")


def build_repair_prompt(frozen_task: Path, working_task: Path, task: dict, kind: str, feedback: str) -> str:
    permitted = task["editable"]
    original_prompt = (frozen_task / "prompt.md").read_text(encoding="utf-8")
    chunks = [
        "LOOM Capability Amplifier 001 — single repair round.",
        "The first attempt failed deterministic validation. You get exactly ONE repair attempt.",
        "Fix the candidate using the validation feedback below.",
        "Return ONLY valid JSON in this exact outer shape:",
        '{"files": {"filename": "complete UTF-8 file contents"}}',
        "Every value inside files must be a JSON string containing the complete replacement file.",
        "Return exactly the permitted editable filenames and no others.",
        "Do not use Markdown fences or explanatory text outside the JSON.",
        "",
        "PERMITTED EDITABLE FILES:",
        *[f"- {name}" for name in permitted],
        "",
        "ORIGINAL TASK PROMPT:",
        original_prompt,
        "",
        f"VALIDATION FAILURE TYPE: {kind}",
        "VALIDATION FEEDBACK:",
        feedback[-3000:],
        "",
        "CURRENT EDITABLE CANDIDATE:",
    ]

    for name in permitted:
        path = working_task / name
        chunks.extend([
            f"--- FILE: {name} ---",
            path.read_text(encoding="utf-8") if path.exists() else "<MISSING>",
            f"--- END FILE: {name} ---",
            "",
        ])

    noneditable = [name for name in task["context"] if name not in permitted]
    if noneditable:
        chunks.append("ORIGINAL NON-EDITABLE SOURCE CONTEXT:")
        for name in noneditable:
            path = frozen_task / name
            chunks.extend([
                f"--- FILE: {name} ---",
                path.read_text(encoding="utf-8"),
                f"--- END FILE: {name} ---",
                "",
            ])

    return "\n".join(chunks)


def run_model_call(adapter, prompt: str, task_id: str, phase: str, telemetry: list[dict]):
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


def main() -> int:
    overall_started = time.perf_counter()
    repo = Path(__file__).resolve().parents[1]
    frozen = repo / "benchmarks" / "coding" / "v1"
    adapter_path = repo / "scripts" / "ollama_single_shot.py"
    scorer_path = frozen / "runner.py"
    manifest_path = frozen / "manifest.json"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "amplify" / "capability-amplifier-001" / run_id
    working = run_dir / "benchmarks" / "coding" / "v1"
    raw_dir = run_dir / "raw"
    prompt_dir = run_dir / "prompts"
    summary_path = run_dir / "run-summary.json"
    telemetry_path = run_dir / "telemetry.json"
    raw_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    summary: dict = {
        "run_id": run_id,
        "experiment": "Capability Amplifier 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "model": MODEL,
        "runtime": "ollama",
        "context": CONTEXT,
        "amplifier": "frozen_initial_plus_deterministic_validation_plus_max_one_repair",
        "guardrails": {"min_free_percent": MIN_FREE_PERCENT, "max_swap_mb": MAX_SWAP_MB},
        "host_gate": {"required_free_percent": HOST_GATE_FREE_PERCENT, "samples": HOST_GATE_SAMPLES},
        "disk_before": disk_snapshot(repo),
        "tasks": [],
        "model_calls": [],
    }
    telemetry: list[dict] = []

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["whole_wall_seconds"] = round(time.perf_counter() - overall_started, 3)
        summary["disk_after"] = disk_snapshot(repo)
        summary["telemetry"] = telemetry_summary(telemetry)
        telemetry_path.write_text(json.dumps(telemetry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary["telemetry_file"] = str(telemetry_path)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if "artifact_score" in summary:
            print(f"Artifact score: {summary.get('artifact_score')}/100")
            print(f"Delivery-adjusted score: {summary.get('delivery_adjusted_score')}/100")
            print(f"Structured delivery: {summary.get('final_delivery_count')}/6")
            print(f"Amplification gate: {summary.get('amplification_gate')}")
            print(f"PI reference reached: {summary.get('pi_reference_reached')}")
        print(f"Model calls: {summary.get('total_model_calls', len(summary.get('model_calls', [])))}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("LOOM Capability Amplifier 001")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    required = [frozen, adapter_path, scorer_path, manifest_path]
    if any(not path.exists() for path in required):
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required benchmark/adapter/scorer path missing"
        return finish(2)

    blobs = {
        "adapter": git_blob(adapter_path, repo),
        "scorer": git_blob(scorer_path, repo),
        "manifest": git_blob(manifest_path, repo),
    }
    summary["frozen_blobs"] = blobs
    expected_blobs = {"adapter": ADAPTER_BLOB, "scorer": SCORER_BLOB, "manifest": MANIFEST_BLOB}
    if blobs != expected_blobs:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"frozen blob mismatch: {blobs!r}"
        return finish(2)
    print(f"Frozen adapter/scorer/manifest blobs: PASS")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != BENCHMARK_VERSION or manifest.get("total_points") != 100:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"benchmark manifest mismatch: {manifest!r}"
        return finish(2)

    if shutil.which("ollama") is None:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "ollama executable not found"
        return finish(2)

    ollama_version = run(["ollama", "--version"], cwd=repo, timeout=20)
    summary["ollama_version"] = ollama_version.get("stdout", "").strip()
    ollama_list = run(["ollama", "list"], cwd=repo, timeout=30)
    if ollama_list.get("exit_code") != 0 or MODEL not in ollama_list.get("stdout", ""):
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"required Ollama model not found: {MODEL}"
        return finish(2)
    print(f"Model presence: PASS {MODEL}")

    adapter = import_file("loom_frozen_single_shot", adapter_path)
    scorer = import_file("loom_frozen_scorer", scorer_path)
    if adapter.TASKS != [
        {"id": "T01", "path": "tasks/t01_generation", "editable": ["solution.py"], "context": ["solution.py"]},
        {"id": "T02", "path": "tasks/t02_debugging", "editable": ["buggy.py"], "context": ["buggy.py"]},
        {"id": "T03", "path": "tasks/t03_comprehension", "editable": ["answer.json"], "context": ["source.py"]},
        {"id": "T04", "path": "tasks/t04_refactor", "editable": ["solution.py"], "context": ["solution.py"]},
        {"id": "T05", "path": "tasks/t05_multifile", "editable": ["order.py"], "context": ["order.py", "pricing.py"]},
        {"id": "T06", "path": "tasks/t06_constraints", "editable": ["solution.py"], "context": ["solution.py"]},
    ]:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "frozen adapter TASKS changed"
        return finish(2)

    shutil.copytree(frozen, working)

    # Cold model policy, then controlled launch-state gate.
    run(["ollama", "stop", MODEL], cwd=repo, timeout=30)
    gate_ok, gate_samples, gate_reason = host_gate()
    summary["host_gate_samples"] = gate_samples
    if not gate_ok:
        summary["classification"] = "HOST_STATE_NOT_READY"
        summary["failure_reason"] = gate_reason
        print(f"Host-state gate: NOT READY — {gate_reason}")
        print("MLX/Ollama benchmark launch: SKIPPED")
        return finish(3)
    print("Host-state gate: PASS")

    manifest_by_id = {task["id"]: task for task in manifest["tasks"]}

    for index, task in enumerate(adapter.TASKS, start=1):
        task_id = task["id"]
        frozen_task = frozen / task["path"]
        working_task = working / task["path"]
        fixture_snapshot = snapshot_editables(working_task, task["editable"])
        record: dict = {
            "id": task_id,
            "editable": task["editable"],
            "initial": {},
            "repair": {"attempted": False},
            "selected_candidate": None,
        }
        print(f"[{index}/6] {task_id} initial call...", flush=True)

        initial_prompt = adapter.build_prompt(frozen_task, task)
        (prompt_dir / f"{task_id}-initial.txt").write_text(initial_prompt, encoding="utf-8")
        response, call_error, monitor = run_model_call(adapter, initial_prompt, task_id, "initial", telemetry)
        if monitor.telemetry_reason:
            summary["classification"] = "TELEMETRY_FAIL"
            summary["failure_reason"] = monitor.telemetry_reason
            summary["tasks"].append(record)
            return finish(4)
        if monitor.guardrail_reason:
            summary["classification"] = "PARTIAL_RESOURCE_FAIL"
            summary["failure_reason"] = monitor.guardrail_reason
            summary["tasks"].append(record)
            return finish(5)
        if call_error or response is None:
            summary["classification"] = "RUNTIME_FAIL"
            summary["failure_reason"] = call_error or "initial Ollama call returned no response"
            summary["tasks"].append(record)
            return finish(6)

        (raw_dir / f"{task_id}-initial-api.json").write_text(
            json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        initial_metrics = adapter.metric_summary(response)
        summary["model_calls"].append({"task": task_id, "phase": "initial", "metrics": initial_metrics})
        record["initial"]["metrics"] = initial_metrics

        initial_valid = False
        initial_snapshot: dict[str, str | None] | None = None
        initial_test: dict | None = None
        initial_parser_error: str | None = None

        try:
            files = adapter.extract_files(response, task["editable"])
            write_files(working_task, files)
            initial_valid = True
            initial_snapshot = snapshot_editables(working_task, task["editable"])
            initial_test = scorer.run_task(manifest_by_id[task_id], working)
            validate_test_result(initial_test)
            record["initial"]["adapter_status"] = "written"
            record["initial"]["test_result"] = initial_test
        except (ValueError, json.JSONDecodeError) as exc:
            restore_editables(working_task, fixture_snapshot)
            initial_parser_error = f"{type(exc).__name__}: {exc}"
            record["initial"]["adapter_status"] = "failed"
            record["initial"]["parser_error"] = initial_parser_error
        except Exception as exc:
            summary["classification"] = "INVALID_HARNESS"
            summary["failure_reason"] = f"initial validation failed outside model parser contract: {type(exc).__name__}: {exc}"
            summary["tasks"].append(record)
            return finish(7)

        initial_all_pass = bool(
            initial_valid
            and initial_test
            and initial_test.get("tests_passed") == initial_test.get("tests_total")
        )

        if initial_all_pass:
            record["selected_candidate"] = "initial"
            record["final_delivery_success"] = True
            record["final_test_result"] = initial_test
            print(f"[{index}/6] {task_id} solved without repair", flush=True)
            summary["tasks"].append(record)
            continue

        # Exactly one deterministic repair is now authorized.
        record["repair"]["attempted"] = True
        if initial_valid and initial_test is not None:
            feedback_kind = "frozen_test_failure"
            feedback = (
                f"Passed {initial_test.get('tests_passed')}/{initial_test.get('tests_total')} frozen tests.\n"
                f"Failure summary:\n{initial_test.get('stderr', '')}"
            )
        else:
            feedback_kind = "structured_output_parser_failure"
            raw_output = response.get("response", "") if isinstance(response, dict) else ""
            feedback = f"Parser error: {initial_parser_error}\nInitial raw output:\n{raw_output}"

        repair_prompt = build_repair_prompt(frozen_task, working_task, task, feedback_kind, feedback)
        (prompt_dir / f"{task_id}-repair.txt").write_text(repair_prompt, encoding="utf-8")
        print(f"[{index}/6] {task_id} repair call ({feedback_kind})...", flush=True)
        repair_response, repair_call_error, repair_monitor = run_model_call(
            adapter, repair_prompt, task_id, "repair", telemetry
        )
        if repair_monitor.telemetry_reason:
            summary["classification"] = "TELEMETRY_FAIL"
            summary["failure_reason"] = repair_monitor.telemetry_reason
            summary["tasks"].append(record)
            return finish(4)
        if repair_monitor.guardrail_reason:
            summary["classification"] = "PARTIAL_RESOURCE_FAIL"
            summary["failure_reason"] = repair_monitor.guardrail_reason
            summary["tasks"].append(record)
            return finish(5)
        if repair_call_error or repair_response is None:
            summary["classification"] = "RUNTIME_FAIL"
            summary["failure_reason"] = repair_call_error or "repair Ollama call returned no response"
            summary["tasks"].append(record)
            return finish(6)

        (raw_dir / f"{task_id}-repair-api.json").write_text(
            json.dumps(repair_response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        repair_metrics = adapter.metric_summary(repair_response)
        summary["model_calls"].append({"task": task_id, "phase": "repair", "metrics": repair_metrics})
        record["repair"]["metrics"] = repair_metrics
        record["repair"]["feedback_kind"] = feedback_kind

        repair_valid = False
        repair_snapshot: dict[str, str | None] | None = None
        repair_test: dict | None = None
        try:
            repair_files = adapter.extract_files(repair_response, task["editable"])
            write_files(working_task, repair_files)
            repair_valid = True
            repair_snapshot = snapshot_editables(working_task, task["editable"])
            repair_test = scorer.run_task(manifest_by_id[task_id], working)
            validate_test_result(repair_test)
            record["repair"]["adapter_status"] = "written"
            record["repair"]["test_result"] = repair_test
        except (ValueError, json.JSONDecodeError) as exc:
            record["repair"]["adapter_status"] = "failed"
            record["repair"]["parser_error"] = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            summary["classification"] = "INVALID_HARNESS"
            summary["failure_reason"] = f"repair validation failed outside model parser contract: {type(exc).__name__}: {exc}"
            summary["tasks"].append(record)
            return finish(7)

        # Frozen deterministic candidate selection.
        if initial_valid and initial_snapshot is not None:
            initial_passed = int(initial_test.get("tests_passed", 0)) if initial_test else 0
            repair_passed = int(repair_test.get("tests_passed", 0)) if repair_valid and repair_test else -1
            if repair_valid and repair_snapshot is not None and repair_passed > initial_passed:
                restore_editables(working_task, repair_snapshot)
                record["selected_candidate"] = "repair"
                record["final_test_result"] = repair_test
            else:
                restore_editables(working_task, initial_snapshot)
                record["selected_candidate"] = "initial"
                record["final_test_result"] = initial_test
            record["final_delivery_success"] = True
        elif repair_valid and repair_snapshot is not None:
            restore_editables(working_task, repair_snapshot)
            record["selected_candidate"] = "repair"
            record["final_test_result"] = repair_test
            record["final_delivery_success"] = True
        else:
            restore_editables(working_task, fixture_snapshot)
            record["selected_candidate"] = "fixture"
            record["final_delivery_success"] = False
            record["final_test_result"] = None

        selected = record["selected_candidate"]
        final_test = record.get("final_test_result") or {}
        print(
            f"[{index}/6] {task_id} selected={selected} "
            f"tests={final_test.get('tests_passed', 'N/A')}/{final_test.get('tests_total', 'N/A')}",
            flush=True,
        )
        summary["tasks"].append(record)

    # Final exact frozen scoring pass.
    runner_env = os.environ.copy()
    runner_env.update(
        {
            "LOOM_MODEL": MODEL,
            "LOOM_RUNTIME": "ollama",
            "LOOM_BACKEND": "mlx",
            "LOOM_MODE": "capability_amplifier_001",
            "LOOM_CONTEXT": str(CONTEXT),
        }
    )
    final_runner = subprocess.run(
        [sys.executable, "runner.py", "--benchmark-root", str(working)],
        cwd=working,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        env=runner_env,
    )
    if final_runner.returncode != 0:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = "frozen final scorer process failed"
        summary["runner_error"] = {
            "exit_code": final_runner.returncode,
            "stdout": final_runner.stdout,
            "stderr": final_runner.stderr,
        }
        return finish(7)

    try:
        result = json.loads(final_runner.stdout)
    except json.JSONDecodeError as exc:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = f"cannot parse frozen final scorer output: {exc}"
        return finish(7)

    summary["benchmark_result"] = result
    summary["artifact_score"] = result.get("score")
    record_by_id = {record["id"]: record for record in summary["tasks"]}
    delivery_score = 0.0
    delivery_count = 0
    for scored in result.get("tasks", []):
        rec = record_by_id.get(scored.get("id"), {})
        rec["final_scorer_task"] = scored
        if rec.get("final_delivery_success"):
            delivery_count += 1
            delivery_score += scored.get("points_earned", 0) or 0

    summary["delivery_adjusted_score"] = round(delivery_score, 2)
    summary["final_delivery_count"] = delivery_count
    summary["total_model_calls"] = len(summary["model_calls"])
    summary["repair_calls"] = sum(1 for rec in summary["tasks"] if rec.get("repair", {}).get("attempted"))
    summary["repairs_selected"] = sum(1 for rec in summary["tasks"] if rec.get("selected_candidate") == "repair")
    summary["tasks_solved_without_repair"] = sum(
        1 for rec in summary["tasks"] if rec.get("selected_candidate") == "initial" and not rec.get("repair", {}).get("attempted")
    )

    total_prompt = 0
    total_generation = 0
    total_model_wall = 0.0
    for call in summary["model_calls"]:
        metrics = call.get("metrics") or {}
        total_prompt += metrics.get("prompt_eval_count", 0) or 0
        total_generation += metrics.get("eval_count", 0) or 0
        total_model_wall += metrics.get("wall_seconds", 0) or 0
    summary["total_prompt_tokens"] = total_prompt
    summary["total_generation_tokens"] = total_generation
    summary["total_model_wall_seconds"] = round(total_model_wall, 3)

    quality_improved = summary["delivery_adjusted_score"] > BASELINE_DELIVERY_SCORE
    strong = (
        quality_improved
        and isinstance(summary.get("artifact_score"), (int, float))
        and summary["artifact_score"] > BASELINE_ARTIFACT
        and delivery_count > BASELINE_DELIVERY_COUNT
    )
    if strong:
        gate = "STRONG_AMPLIFICATION"
    elif quality_improved:
        gate = "QUALITY_IMPROVED"
    else:
        gate = "NO_QUALITY_IMPROVEMENT"
    summary["amplification_gate"] = gate
    summary["pi_reference_reached"] = summary["delivery_adjusted_score"] >= PI_REFERENCE_DELIVERY_SCORE
    summary["classification"] = "COMPLETE"

    print("=== AMPLIFICATION RESULT ===")
    print(f"Artifact score: {summary['artifact_score']}/100")
    print(f"Delivery-adjusted score: {summary['delivery_adjusted_score']}/100")
    print(f"Structured delivery: {delivery_count}/6")
    print(f"Model calls: {summary['total_model_calls']} (repairs={summary['repair_calls']}, selected={summary['repairs_selected']})")
    print(f"Total prompt tokens: {total_prompt}")
    print(f"Total generation tokens: {total_generation}")
    print(f"Total model-call wall: {summary['total_model_wall_seconds']} s")
    print(f"Amplification gate: {gate}")
    print(f"PI reference reached: {summary['pi_reference_reached']}")
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
