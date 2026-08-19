#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q3 Auto-Fit Server Smoke 001.

Tests the existing Qwen3-8B Q3_K_M artifact at context 4096 through the pinned
llama-server while allowing llama.cpp's fit policy to choose device placement.
The established LOOM memory/swap guardrails remain unchanged.
"""

from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PINNED_COMMIT = "60addddf3c567c43ec3caf70fc953fba3572d96f"
HELPER_BLOB_SHA = "04e950019f95d31c1380ecab14aa42cca24c414d"
MODEL_FILE = "Qwen3-8B-Q3_K_M.gguf"
MODEL_SHA256 = "4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007"
MODEL_REPO = "unsloth/Qwen3-8B-GGUF"
MODEL_ALIAS = "loom-qwen3-8b-q3-autofit"
OLLAMA_MODEL = "qwen3.5:4b-mlx"
CTX = 4096
HOST = "127.0.0.1"
PORT = 18083
FIT_TARGET_MIB = 1024
READINESS_TIMEOUT_SECONDS = 180
REQUEST_TIMEOUT_SECONDS = 300


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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def post_chat(url: str) -> dict:
    payload = {
        "model": MODEL_ALIAS,
        "messages": [{"role": "user", "content": "Reply only with OK."}],
        "temperature": 0,
        "max_tokens": 8,
        "stream": False,
        "reasoning_effort": "none",
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return {
                "http_status": response.status,
                "wall_seconds": round(time.perf_counter() - started, 3),
                "request": payload,
                "response": json.loads(raw),
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
            "request": payload,
            "response": parsed,
            "error": f"HTTPError: {exc}",
        }
    except Exception as exc:
        return {
            "http_status": None,
            "wall_seconds": round(time.perf_counter() - started, 3),
            "request": payload,
            "error": f"{type(exc).__name__}: {exc}",
        }


def assistant_content(result: dict) -> str | None:
    response = result.get("response")
    if not isinstance(response, dict):
        return None
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None
    message = first.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    return content if isinstance(content, str) else None


def relevant_fit_lines(text: str) -> list[str]:
    needles = ("fit", "offload", "gpu layer", "gpu_layers", "n_gpu_layers", "metal")
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        low = line.lower()
        if line and any(needle in low for needle in needles):
            lines.append(line)
    return lines


def write_summary(path: Path, summary: dict) -> None:
    summary["finished_at_utc"] = utc_now()
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    helper_path = repo_root / "scripts" / "llama_cpp_8b_q2_server_smoke.py"
    helper_blob = git_blob(helper_path, repo_root) if helper_path.exists() else ""

    print("LOOM llama.cpp 8B Q3 Auto-Fit Server Smoke 001")

    if helper_blob != HELPER_BLOB_SHA:
        print("Helper verification: FAIL")
        print(f"Observed helper blob: {helper_blob or 'N/A'}")
        print(f"Expected helper blob: {HELPER_BLOB_SHA}")
        return 2

    helper = load_module(helper_path, "loom_q2_server_smoke_helper")

    llama_root = repo_root / "results-local" / "llama-cpp"
    source = llama_root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    server = build / "bin" / "llama-server"
    model_path = repo_root / "results-local" / "models" / "Qwen3-8B-GGUF" / MODEL_FILE

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = llama_root / "8b-q3-autofit-server-smoke" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "autofit-server-smoke-summary.json"
    stdout_path = out_dir / "llama-server-stdout.txt"
    stderr_path = out_dir / "llama-server-stderr.txt"

    disk_before = helper.disk_snapshot(repo_root)
    source_sha = helper.run(["git", "rev-parse", "HEAD"], source, timeout=30).get("stdout", "").strip() if source.exists() else ""

    summary: dict = {
        "run_id": run_id,
        "experiment": "llama.cpp 8B Q3 Auto-Fit Server Smoke 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "pinned_commit": PINNED_COMMIT,
        "source_commit_actual": source_sha,
        "helper_blob": helper_blob,
        "model": {
            "repo": MODEL_REPO,
            "file": MODEL_FILE,
            "path": str(model_path),
            "expected_sha256": MODEL_SHA256,
        },
        "context": CTX,
        "fit_policy": {
            "gpu_layers_override": None,
            "fit": "on",
            "fit_target_mib": FIT_TARGET_MIB,
            "fit_ctx": CTX,
            "kv_cache_types": "runtime defaults",
        },
        "guardrails": {
            "abort_below_memory_free_percent": helper.FREE_MEMORY_ABORT_PERCENT,
            "abort_above_swap_mb": helper.SWAP_ABORT_MB,
        },
        "disk_before": disk_before,
        "memory_before": helper.memory_snapshot(repo_root),
    }

    print(f"Disk free before: {disk_before['free_gib']:.3f} GiB")

    required = ["cmake", "sysctl", "ps", "memory_pressure"]
    missing = [name for name in required if shutil.which(name) is None]
    if missing or source_sha != PINNED_COMMIT or not build.exists():
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "preflight/build-tree verification failed"
        summary["missing_prerequisites"] = missing
        write_summary(summary_path, summary)
        print("Preflight: FAIL")
        print(f"Summary: {summary_path}")
        return 2

    if not model_path.exists():
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "local Q3 artifact missing"
        write_summary(summary_path, summary)
        print("Model preflight: FAIL — local Q3 artifact missing")
        print(f"Summary: {summary_path}")
        return 2

    print("Verifying model SHA256...", flush=True)
    digest = helper.sha256_file(model_path)
    summary["model"]["sha256"] = digest
    summary["model"]["size_bytes"] = model_path.stat().st_size
    summary["model"]["size_gib"] = round(model_path.stat().st_size / (1024 ** 3), 3)
    if digest != MODEL_SHA256:
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "model SHA256 mismatch"
        write_summary(summary_path, summary)
        print("Model SHA256: FAIL")
        print(f"Observed: {digest}")
        print(f"Expected: {MODEL_SHA256}")
        print(f"Summary: {summary_path}")
        return 1

    print("Model SHA256: PASS")
    print(f"Model size: {summary['model']['size_gib']:.3f} GiB")

    if not server.exists():
        print("Building llama-server target...", flush=True)
        build_result = helper.run(
            [
                "cmake", "--build", str(build), "--target", "llama-server",
                "--parallel", str(max(1, os.cpu_count() or 1)),
            ],
            source,
            timeout=1800,
        )
        summary["server_build"] = build_result
        if build_result.get("exit_code") != 0 or not server.exists():
            summary["classification"] = "FAIL"
            summary["failure_reason"] = "llama-server target build failed"
            write_summary(summary_path, summary)
            print("llama-server build: FAIL")
            print(f"Summary: {summary_path}")
            return 1
        print("llama-server build: PASS")
    else:
        summary["server_build"] = {"needed": False, "server_preexisting": True}
        print("llama-server target: PRESENT")

    if not helper.port_is_available(HOST, PORT):
        summary["classification"] = "FAIL"
        summary["failure_reason"] = f"local port {HOST}:{PORT} unavailable"
        write_summary(summary_path, summary)
        print(f"Port preflight: FAIL — {HOST}:{PORT} unavailable")
        print(f"Summary: {summary_path}")
        return 2

    if shutil.which("ollama"):
        summary["ollama_stop"] = helper.run(["ollama", "stop", OLLAMA_MODEL], repo_root, timeout=30)

    server_cmd = [
        str(server),
        "-m", str(model_path),
        "-c", str(CTX),
        "-fa", "auto",
        "--fit", "on",
        "--fit-target", str(FIT_TARGET_MIB),
        "--fit-ctx", str(CTX),
        "--host", HOST,
        "--port", str(PORT),
        "--alias", MODEL_ALIAS,
        "--no-webui",
        "--offline",
    ]
    summary["server_command"] = server_cmd
    print("Launching llama-server with automatic fit...", flush=True)

    samples: list[dict] = []
    health_history: list[dict] = []
    guard_abort_reason: str | None = None
    ready = False
    request_result: dict | None = None
    shutdown_result: dict | None = None
    proc: subprocess.Popen | None = None
    started = time.perf_counter()

    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
        proc = subprocess.Popen(
            server_cmd,
            cwd=source,
            stdout=stdout_file,
            stderr=stderr_file,
            text=True,
        )
        try:
            while time.perf_counter() - started < READINESS_TIMEOUT_SECONDS:
                elapsed = time.perf_counter() - started
                if proc.poll() is not None:
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
                    ready = True
                    break
                time.sleep(1.0)

            if guard_abort_reason or not ready:
                if proc.poll() is None:
                    shutdown_result = helper.terminate_process(proc)
            else:
                readiness_wall = round(time.perf_counter() - started, 3)
                summary["readiness_wall_seconds"] = readiness_wall
                print(f"Server readiness: PASS ({readiness_wall:.3f}s)")
                print("Sending /v1/chat/completions smoke...", flush=True)

                request_url = f"http://{HOST}:{PORT}/v1/chat/completions"
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(post_chat, request_url)
                    request_started = time.perf_counter()
                    while not future.done():
                        elapsed = time.perf_counter() - started
                        if proc.poll() is not None:
                            break
                        sample = helper.sample_process(proc.pid, repo_root, elapsed)
                        samples.append(sample)
                        reason = helper.guardrail_reason(sample)
                        if reason:
                            guard_abort_reason = reason
                            helper.terminate_process(proc)
                            break
                        if time.perf_counter() - request_started > REQUEST_TIMEOUT_SECONDS:
                            guard_abort_reason = f"request timeout after {REQUEST_TIMEOUT_SECONDS}s"
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

                if proc.poll() is None:
                    final_sample = helper.sample_process(proc.pid, repo_root, time.perf_counter() - started)
                    samples.append(final_sample)
                    reason = helper.guardrail_reason(final_sample)
                    if reason and not guard_abort_reason:
                        guard_abort_reason = reason
                    shutdown_result = helper.terminate_process(proc)
                else:
                    shutdown_result = {"already_exited": True, "exit_code": proc.returncode}
        finally:
            if proc is not None and proc.poll() is None:
                shutdown_result = helper.terminate_process(proc)

    stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    fit_lines = relevant_fit_lines(stderr_text)

    summary["health_history"] = health_history
    summary["server_ready"] = ready
    summary["guardrail_abort_reason"] = guard_abort_reason
    summary["request"] = request_result
    summary["shutdown"] = shutdown_result
    summary["samples"] = samples
    summary["fit_offload_log_lines"] = fit_lines

    rss_values = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap_values = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free_values = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    summary["telemetry"] = {
        "peak_rss_mb": max(rss_values) if rss_values else None,
        "peak_swap_used_mb": max(swap_values) if swap_values else None,
        "min_memory_free_percent": min(free_values) if free_values else None,
    }

    content = assistant_content(request_result or {})
    request_pass = (
        isinstance(request_result, dict)
        and request_result.get("http_status") == 200
        and isinstance(content, str)
        and bool(content.strip())
    )
    summary["assistant_content"] = content
    summary["request_pass"] = request_pass
    summary["disk_after"] = helper.disk_snapshot(repo_root)
    summary["memory_after"] = helper.memory_snapshot(repo_root)

    full_pass = ready and guard_abort_reason is None and request_pass
    summary["classification"] = "FULL_PASS" if full_pass else "FAIL"
    if not full_pass:
        if guard_abort_reason:
            summary["failure_reason"] = guard_abort_reason
        elif not ready:
            summary["failure_reason"] = "server did not reach healthy state before timeout/exit"
        else:
            summary["failure_reason"] = "chat completion API smoke failed"

    write_summary(summary_path, summary)
    (out_dir / "memory-samples.json").write_text(json.dumps(samples, indent=2) + "\n", encoding="utf-8")
    if request_result is not None:
        (out_dir / "chat-response.json").write_text(json.dumps(request_result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"API smoke: {'PASS' if request_pass else 'FAIL'}")
    if content is not None:
        print(f"Assistant content: {content!r}")
    print(f"Peak process RSS: {summary['telemetry']['peak_rss_mb']} MB")
    print(f"Peak observed swap: {summary['telemetry']['peak_swap_used_mb']} MB")
    print(f"Minimum observed free memory: {summary['telemetry']['min_memory_free_percent']}%")
    if fit_lines:
        print("Auto-fit/offload evidence:")
        for line in fit_lines[-12:]:
            print(f"  {line}")
    if guard_abort_reason:
        print(f"Guardrail: {guard_abort_reason}")
    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
    print(f"Run directory: {out_dir}")
    print(f"Summary: {summary_path}")
    return 0 if full_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
