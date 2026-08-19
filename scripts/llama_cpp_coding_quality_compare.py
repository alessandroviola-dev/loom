#!/usr/bin/env python3
"""LOOM llama.cpp Coding Quality Compare 001.

Runs the frozen LOOM Coding Benchmark 01 v1.0.1 in single-shot mode against
Qwen3-8B Q2_K and Qwen3-4B Q4_K_M through the same pinned llama-server raw
/completion API. No task retries, test feedback, salvage, or prompt changes.
"""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PINNED_COMMIT = "60addddf3c567c43ec3caf70fc953fba3572d96f"
ADAPTER_BLOB_SHA = "62abab57f6463c5813809b43d8f1e7bdfec5f304"
SMOKE_HELPER_BLOB_SHA = "04e950019f95d31c1380ecab14aa42cca24c414d"

CTX = 4096
HOST = "127.0.0.1"
PORT = 18082
REQUEST_TIMEOUT_SECONDS = 600
READINESS_TIMEOUT_SECONDS = 180
COOLDOWN_SECONDS = 5
OLLAMA_MODEL = "qwen3.5:4b-mlx"

PROFILES = [
    {
        "key": "8b-q2",
        "label": "Qwen3 8B Q2_K",
        "model_file": "Qwen3-8B-Q2_K.gguf",
        "model_dir": "Qwen3-8B-GGUF",
        "model_repo": "unsloth/Qwen3-8B-GGUF",
        "sha256": "7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf",
        "quant": "Q2_K",
        "params": "8B",
        "alias": "loom-qwen3-8b-q2-quality",
    },
    {
        "key": "4b-q4",
        "label": "Qwen3 4B Q4_K_M",
        "model_file": "Qwen3-4B-Q4_K_M.gguf",
        "model_dir": "Qwen3-4B-GGUF",
        "model_repo": "Qwen/Qwen3-4B-GGUF",
        "sha256": "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5",
        "quant": "Q4_K_M",
        "params": "4B",
        "alias": "loom-qwen3-4b-q4-quality",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_blob(path: Path, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request_completion(url: str, prompt: str) -> dict:
    payload = {
        "prompt": prompt,
        "n_predict": 2048,
        "temperature": 0,
        "seed": 0,
        "stream": False,
        "cache_prompt": False,
        "json_schema": {},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw)
            return {
                "http_status": response.status,
                "wall_seconds": round(time.perf_counter() - started, 3),
                "response": parsed,
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return {
            "http_status": exc.code,
            "wall_seconds": round(time.perf_counter() - started, 3),
            "response": parsed,
            "error": f"HTTPError: {exc}",
        }
    except Exception as exc:
        return {
            "http_status": None,
            "wall_seconds": round(time.perf_counter() - started, 3),
            "error": f"{type(exc).__name__}: {exc}",
        }


def score_working_tree(working: Path, profile: dict, task_records: list[dict]) -> dict:
    env = dict(os.environ)
    env.update(
        {
            "LOOM_MODEL": f"{profile['params']} {profile['quant']}",
            "LOOM_RUNTIME": "llama.cpp",
            "LOOM_BACKEND": "metal",
            "LOOM_MODE": "single_shot",
            "LOOM_CONTEXT": str(CTX),
        }
    )
    proc = subprocess.run(
        [sys.executable, "runner.py"],
        cwd=working,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    result: dict = {
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.returncode != 0:
        return result

    parsed = json.loads(proc.stdout)
    result["benchmark_result"] = parsed
    result["artifact_score"] = parsed.get("score")
    status_by_id = {item["id"]: item.get("adapter_status") for item in task_records}
    result["delivery_adjusted_score"] = round(
        sum(
            item.get("points_earned", 0)
            for item in parsed.get("tasks", [])
            if status_by_id.get(item.get("id")) == "written"
        ),
        2,
    )
    return result


def summarize_samples(samples: list[dict]) -> dict:
    rss_values = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap_values = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free_values = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    return {
        "peak_rss_mb": max(rss_values) if rss_values else None,
        "peak_swap_used_mb": max(swap_values) if swap_values else None,
        "min_memory_free_percent": min(free_values) if free_values else None,
    }


def run_profile(profile: dict, repo_root: Path, source: Path, server: Path, frozen: Path, run_root: Path, adapter, helper) -> dict:
    profile_dir = run_root / profile["key"]
    raw_dir = profile_dir / "raw"
    working = profile_dir / "benchmarks" / "coding" / "v1"
    profile_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(frozen, working)

    model_path = repo_root / "results-local" / "models" / profile["model_dir"] / profile["model_file"]
    stdout_path = profile_dir / "llama-server-stdout.txt"
    stderr_path = profile_dir / "llama-server-stderr.txt"

    record: dict = {
        "profile": profile,
        "started_at_utc": utc_now(),
        "model_path": str(model_path),
        "memory_before": helper.memory_snapshot(repo_root),
        "tasks": [],
        "classification": None,
    }

    digest = helper.sha256_file(model_path)
    record["model_sha256"] = digest
    record["model_size_bytes"] = model_path.stat().st_size
    record["model_size_gib"] = round(model_path.stat().st_size / (1024 ** 3), 3)
    if digest != profile["sha256"]:
        record["classification"] = "PREFLIGHT_FAIL"
        record["failure_reason"] = "model SHA256 mismatch"
        record["finished_at_utc"] = utc_now()
        return record

    if not helper.port_is_available(HOST, PORT):
        record["classification"] = "PREFLIGHT_FAIL"
        record["failure_reason"] = f"port {HOST}:{PORT} unavailable"
        record["finished_at_utc"] = utc_now()
        return record

    if shutil.which("ollama"):
        record["ollama_stop"] = helper.run(["ollama", "stop", OLLAMA_MODEL], repo_root, timeout=30)

    server_cmd = [
        str(server),
        "-m", str(model_path),
        "-ngl", "-1",
        "-c", str(CTX),
        "-fa", "auto",
        "--host", HOST,
        "--port", str(PORT),
        "--alias", profile["alias"],
        "--no-webui",
        "--offline",
    ]
    record["server_command"] = server_cmd

    samples: list[dict] = []
    health_history: list[dict] = []
    guard_abort_reason: str | None = None
    server_ready = False
    execution_failure: str | None = None
    proc: subprocess.Popen | None = None
    server_started = time.perf_counter()

    print(f"[{profile['label']}] launching server...", flush=True)

    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
        proc = subprocess.Popen(server_cmd, cwd=source, stdout=stdout_file, stderr=stderr_file, text=True)
        try:
            while time.perf_counter() - server_started < READINESS_TIMEOUT_SECONDS:
                elapsed = time.perf_counter() - server_started
                if proc.poll() is not None:
                    execution_failure = f"server exited during readiness with code {proc.returncode}"
                    break
                sample = helper.sample_process(proc.pid, repo_root, elapsed)
                samples.append(sample)
                reason = helper.guardrail_reason(sample)
                if reason:
                    guard_abort_reason = reason
                    break
                health = helper.http_get_json(f"http://{HOST}:{PORT}/health", timeout=3)
                health["elapsed_seconds"] = round(elapsed, 3)
                health_history.append(health)
                if health.get("http_status") == 200:
                    server_ready = True
                    break
                time.sleep(1.0)

            if guard_abort_reason or not server_ready:
                if proc.poll() is None:
                    helper.terminate_process(proc)
            else:
                print(f"[{profile['label']}] server ready in {time.perf_counter() - server_started:.3f}s", flush=True)
                for index, task in enumerate(adapter.TASKS, start=1):
                    task_record = {
                        "id": task["id"],
                        "editable": task["editable"],
                        "started_at_utc": utc_now(),
                        "adapter_status": "not_run",
                    }
                    record["tasks"].append(task_record)

                    if guard_abort_reason or execution_failure or proc.poll() is not None:
                        task_record["error"] = guard_abort_reason or execution_failure or "server exited"
                        continue

                    task_dir = working / task["path"]
                    prompt = adapter.build_prompt(task_dir, task)
                    task_record["prompt_chars"] = len(prompt)
                    print(f"[{profile['label']}] [{index}/{len(adapter.TASKS)}] {task['id']} running...", flush=True)

                    request_url = f"http://{HOST}:{PORT}/completion"
                    request_result: dict | None = None
                    request_started = time.perf_counter()

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(request_completion, request_url, prompt)
                        while not future.done():
                            elapsed = time.perf_counter() - server_started
                            if proc.poll() is not None:
                                execution_failure = f"server exited with code {proc.returncode}"
                                break
                            sample = helper.sample_process(proc.pid, repo_root, elapsed)
                            samples.append(sample)
                            reason = helper.guardrail_reason(sample)
                            if reason:
                                guard_abort_reason = reason
                                helper.terminate_process(proc)
                                break
                            if time.perf_counter() - request_started > REQUEST_TIMEOUT_SECONDS:
                                execution_failure = f"request timeout after {REQUEST_TIMEOUT_SECONDS}s"
                                helper.terminate_process(proc)
                                break
                            time.sleep(1.0)

                        if future.done():
                            request_result = future.result()
                        else:
                            try:
                                request_result = future.result(timeout=10)
                            except Exception as exc:
                                request_result = {"http_status": None, "error": f"{type(exc).__name__}: {exc}"}

                    task_record["request"] = request_result
                    task_record["finished_at_utc"] = utc_now()
                    (raw_dir / f"{task['id']}-api.json").write_text(
                        json.dumps(request_result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8",
                    )

                    if guard_abort_reason:
                        task_record["adapter_status"] = "failed"
                        task_record["error"] = guard_abort_reason
                        print(f"[{profile['label']}] {task['id']} guardrail abort", flush=True)
                        continue
                    if execution_failure:
                        task_record["adapter_status"] = "failed"
                        task_record["error"] = execution_failure
                        print(f"[{profile['label']}] {task['id']} execution failure", flush=True)
                        continue

                    response = request_result.get("response") if isinstance(request_result, dict) else None
                    content = response.get("content") if isinstance(response, dict) else None
                    task_record["timings"] = response.get("timings") if isinstance(response, dict) else None
                    task_record["stop_type"] = response.get("stop_type") if isinstance(response, dict) else None
                    task_record["tokens_evaluated"] = response.get("tokens_evaluated") if isinstance(response, dict) else None
                    task_record["tokens_predicted"] = response.get("tokens_predicted") if isinstance(response, dict) else None

                    try:
                        if not isinstance(request_result, dict) or request_result.get("http_status") != 200:
                            raise RuntimeError(f"HTTP status {request_result.get('http_status') if isinstance(request_result, dict) else None}")
                        if not isinstance(content, str):
                            raise ValueError("llama-server response missing string 'content'")
                        files = adapter.extract_files({"response": content}, task["editable"])
                        for name, file_content in files.items():
                            (task_dir / name).write_text(file_content, encoding="utf-8")
                        task_record["adapter_status"] = "written"
                    except Exception as exc:
                        task_record["adapter_status"] = "failed"
                        task_record["error"] = f"{type(exc).__name__}: {exc}"

                    print(f"[{profile['label']}] {task['id']} {task_record['adapter_status']}", flush=True)

                if proc.poll() is None:
                    sample = helper.sample_process(proc.pid, repo_root, time.perf_counter() - server_started)
                    samples.append(sample)
                    reason = helper.guardrail_reason(sample)
                    if reason and not guard_abort_reason:
                        guard_abort_reason = reason
                    helper.terminate_process(proc)
        finally:
            if proc is not None and proc.poll() is None:
                helper.terminate_process(proc)

    record["server_ready"] = server_ready
    record["health_history"] = health_history
    record["guardrail_abort_reason"] = guard_abort_reason
    record["execution_failure"] = execution_failure
    record["samples"] = samples
    record["telemetry"] = summarize_samples(samples)

    scoring = score_working_tree(working, profile, record["tasks"])
    record["scoring"] = scoring
    record["artifact_score"] = scoring.get("artifact_score")
    record["delivery_adjusted_score"] = scoring.get("delivery_adjusted_score")
    attempted = sum(1 for x in record["tasks"] if x.get("adapter_status") != "not_run")
    written = sum(1 for x in record["tasks"] if x.get("adapter_status") == "written")
    record["attempted_tasks"] = attempted
    record["written_tasks"] = written

    complete = (
        server_ready
        and guard_abort_reason is None
        and execution_failure is None
        and attempted == len(adapter.TASKS)
        and scoring.get("exit_code") == 0
    )
    record["classification"] = "COMPLETE" if complete else "PARTIAL_OR_RESOURCE_FAIL"
    record["memory_after"] = helper.memory_snapshot(repo_root)
    record["finished_at_utc"] = utc_now()

    (profile_dir / "profile-summary.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (profile_dir / "memory-samples.json").write_text(
        json.dumps(samples, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        f"[{profile['label']}] artifact={record.get('artifact_score')}/100 "
        f"delivery={record.get('delivery_adjusted_score')}/100 class={record['classification']}",
        flush=True,
    )
    return record


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    adapter_path = scripts_dir / "ollama_single_shot.py"
    helper_path = scripts_dir / "llama_cpp_8b_q2_server_smoke.py"

    llama_root = repo_root / "results-local" / "llama-cpp"
    source = llama_root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    server = build / "bin" / "llama-server"
    bench = build / "bin" / "llama-bench"
    frozen = repo_root / "benchmarks" / "coding" / "v1"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = llama_root / "coding-quality-compare-001" / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    summary_path = run_root / "comparison-summary.json"

    print("LOOM llama.cpp Coding Quality Compare 001")
    print("Profiles: 8B Q2 first, then 4B Q4")
    print(f"Disk free before: {shutil.disk_usage(repo_root).free / (1024 ** 3):.3f} GiB")

    preflight_errors: list[str] = []
    if not adapter_path.exists() or git_blob(adapter_path, repo_root) != ADAPTER_BLOB_SHA:
        preflight_errors.append("single-shot adapter blob mismatch")
    if not helper_path.exists() or git_blob(helper_path, repo_root) != SMOKE_HELPER_BLOB_SHA:
        preflight_errors.append("server-smoke helper blob mismatch")
    if not frozen.exists():
        preflight_errors.append("frozen benchmark missing")
    else:
        manifest = json.loads((frozen / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("version") != "1.0.1":
            preflight_errors.append(f"benchmark version mismatch: {manifest.get('version')}")
        status = subprocess.run(
            ["git", "status", "--porcelain", "--", "benchmarks/coding/v1"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if status.returncode != 0 or status.stdout.strip():
            preflight_errors.append("frozen benchmark tree is modified")
    if not source.exists():
        preflight_errors.append("pinned llama.cpp source missing")
    else:
        actual = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=source,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        ).stdout.strip()
        if actual != PINNED_COMMIT:
            preflight_errors.append(f"llama.cpp commit mismatch: {actual}")
    if not server.exists():
        preflight_errors.append("llama-server binary missing")
    if not bench.exists():
        preflight_errors.append("llama-bench binary missing")
    else:
        devices = subprocess.run(
            [str(bench), "--list-devices"],
            cwd=source if source.exists() else repo_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        device_text = (devices.stdout + devices.stderr).lower()
        if devices.returncode != 0 or "mtl0" not in device_text or "metal" not in device_text:
            preflight_errors.append("Metal device preflight failed")

    for profile in PROFILES:
        path = repo_root / "results-local" / "models" / profile["model_dir"] / profile["model_file"]
        if not path.exists():
            preflight_errors.append(f"model missing: {profile['model_file']}")

    if preflight_errors:
        summary = {
            "run_id": run_id,
            "started_at_utc": utc_now(),
            "classification": "PREFLIGHT_FAIL",
            "errors": preflight_errors,
        }
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("Preflight: FAIL")
        for error in preflight_errors:
            print(f"- {error}")
        print(f"Summary: {summary_path}")
        return 2

    adapter = load_module(adapter_path, "loom_frozen_single_shot_adapter")
    helper = load_module(helper_path, "loom_server_smoke_helpers")

    summary: dict = {
        "run_id": run_id,
        "experiment": "llama.cpp Coding Quality Compare 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "pinned_commit": PINNED_COMMIT,
        "context": CTX,
        "profile_order": [x["key"] for x in PROFILES],
        "request_settings": {
            "endpoint": "/completion",
            "n_predict": 2048,
            "temperature": 0,
            "seed": 0,
            "stream": False,
            "cache_prompt": False,
            "json_schema": {},
        },
        "disk_before": helper.disk_snapshot(repo_root),
        "device_preflight": {
            "command": [str(bench), "--list-devices"],
            "exit_code": devices.returncode,
            "stdout": devices.stdout,
            "stderr": devices.stderr,
        },
        "profiles": [],
    }

    for idx, profile in enumerate(PROFILES):
        record = run_profile(profile, repo_root, source, server, frozen, run_root, adapter, helper)
        summary["profiles"].append(record)
        if idx < len(PROFILES) - 1:
            print(f"Cooldown: {COOLDOWN_SECONDS}s", flush=True)
            time.sleep(COOLDOWN_SECONDS)

    by_key = {x["profile"]["key"]: x for x in summary["profiles"]}
    score_8 = by_key.get("8b-q2", {}).get("delivery_adjusted_score")
    score_4 = by_key.get("4b-q4", {}).get("delivery_adjusted_score")
    relation = None
    delta = None
    if isinstance(score_8, (int, float)) and isinstance(score_4, (int, float)):
        delta = round(float(score_8) - float(score_4), 2)
        relation = "8B_HIGHER" if delta > 0 else "4B_HIGHER" if delta < 0 else "TIE"

    all_complete = all(x.get("classification") == "COMPLETE" for x in summary["profiles"])
    summary["quality_relation"] = relation
    summary["delivery_score_delta_8b_minus_4b"] = delta
    summary["disk_after"] = helper.disk_snapshot(repo_root)
    summary["classification"] = "COMPLETE" if all_complete else "PARTIAL"
    summary["finished_at_utc"] = utc_now()
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("=== COMPARISON ===")
    print(f"8B Q2 delivery-adjusted: {score_8}/100")
    print(f"4B Q4 delivery-adjusted: {score_4}/100")
    print(f"Delta 8B-4B: {delta}")
    print(f"Quality relation: {relation}")
    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
    print(f"Run directory: {run_root}")
    print(f"Summary: {summary_path}")

    return 0 if all_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
