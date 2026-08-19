#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q2 Server Smoke 001.

Builds the pinned llama-server target if necessary, verifies the existing Qwen3
8B Q2_K artifact, launches a localhost-only context-4096 Metal server, polls the
official /health endpoint, sends one OpenAI-compatible chat completion, and
captures memory/swap/disk telemetry under the established LOOM guardrails.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PINNED_COMMIT = "60addddf3c567c43ec3caf70fc953fba3572d96f"
MODEL_FILE = "Qwen3-8B-Q2_K.gguf"
MODEL_SHA256 = "7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf"
MODEL_REPO = "unsloth/Qwen3-8B-GGUF"
MODEL_ALIAS = "loom-qwen3-8b-q2"
OLLAMA_MODEL = "qwen3.5:4b-mlx"
CTX = 4096
HOST = "127.0.0.1"
PORT = 18081
FREE_MEMORY_ABORT_PERCENT = 5
SWAP_ABORT_MB = 5600.0
READINESS_TIMEOUT_SECONDS = 180
REQUEST_TIMEOUT_SECONDS = 300


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "error": f"{type(exc).__name__}: {exc}"}


def parse_swap_mb(text: str) -> float | None:
    m = re.search(r"used\s*=\s*([0-9.,]+)M", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def parse_free_percent(text: str) -> int | None:
    m = re.search(r"([0-9]+)%", text)
    return int(m.group(1)) if m else None


def disk_snapshot(path: Path) -> dict:
    d = shutil.disk_usage(path)
    return {
        "total_gib": round(d.total / (1024 ** 3), 3),
        "used_gib": round(d.used / (1024 ** 3), 3),
        "free_gib": round(d.free / (1024 ** 3), 3),
    }


def memory_snapshot(cwd: Path) -> dict:
    top = run(["top", "-l", "1", "-n", "0"], cwd, timeout=10)
    physmem = next(
        (x for x in top.get("stdout", "").splitlines() if x.startswith("PhysMem:")),
        "",
    )
    pressure = run(["memory_pressure"], cwd, timeout=10)
    pressure_line = next(
        (x.strip() for x in reversed(pressure.get("stdout", "").splitlines()) if x.strip()),
        "",
    )
    swap = run(["sysctl", "vm.swapusage"], cwd, timeout=10).get("stdout", "").strip()
    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "memory_free_percent": parse_free_percent(pressure_line),
        "swap": swap,
        "swap_used_mb": parse_swap_mb(swap),
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def process_rss_mb(pid: int, cwd: Path) -> float | None:
    result = run(["ps", "-o", "rss=", "-p", str(pid)], cwd, timeout=5)
    text = result.get("stdout", "").strip()
    try:
        return float(text) / 1024.0
    except ValueError:
        return None


def sample_process(pid: int, cwd: Path, elapsed: float, latest_free: int | None = None) -> dict:
    pressure = run(["memory_pressure"], cwd, timeout=5)
    line = next(
        (x.strip() for x in reversed(pressure.get("stdout", "").splitlines()) if x.strip()),
        "",
    )
    free = parse_free_percent(line)
    if free is None:
        free = latest_free
    swap_text = run(["sysctl", "vm.swapusage"], cwd, timeout=5).get("stdout", "").strip()
    return {
        "elapsed_seconds": round(elapsed, 3),
        "rss_mb": process_rss_mb(pid, cwd),
        "swap_used_mb": parse_swap_mb(swap_text),
        "memory_free_percent": free,
        "memory_pressure": line,
    }


def guardrail_reason(sample: dict) -> str | None:
    free = sample.get("memory_free_percent")
    swap = sample.get("swap_used_mb")
    if isinstance(free, int) and free < FREE_MEMORY_ABORT_PERCENT:
        return f"memory free {free}% < {FREE_MEMORY_ABORT_PERCENT}%"
    if isinstance(swap, (int, float)) and swap > SWAP_ABORT_MB:
        return f"swap {swap:.2f} MB > {SWAP_ABORT_MB:.0f} MB"
    return None


def port_is_available(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def http_get_json(url: str, timeout: int = 5) -> dict:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = raw
            return {"http_status": response.status, "body": body}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw
        return {"http_status": exc.code, "body": body}
    except urllib.error.URLError as exc:
        return {"http_status": None, "error": f"URLError: {exc}"}


def chat_completion(url: str) -> dict:
    payload = {
        "model": MODEL_ALIAS,
        "messages": [{"role": "user", "content": "Reply only with OK."}],
        "temperature": 0,
        "max_tokens": 8,
        "stream": False,
        "reasoning_effort": "none",
    }
    body = json.dumps(payload).encode("utf-8")
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
                "request": payload,
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


def terminate_process(proc: subprocess.Popen, timeout: int = 15) -> dict:
    if proc.poll() is not None:
        return {"already_exited": True, "exit_code": proc.returncode}
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
        return {"terminated": True, "exit_code": proc.returncode}
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=10)
        return {"terminated": False, "killed": True, "exit_code": proc.returncode}


def write_summary(path: Path, summary: dict) -> None:
    summary["finished_at_utc"] = utc_now()
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    llama_root = repo_root / "results-local" / "llama-cpp"
    source = llama_root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    server = build / "bin" / "llama-server"
    model_path = repo_root / "results-local" / "models" / "Qwen3-8B-GGUF" / MODEL_FILE

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = llama_root / "8b-q2-server-smoke" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "server-smoke-summary.json"
    stdout_path = out_dir / "llama-server-stdout.txt"
    stderr_path = out_dir / "llama-server-stderr.txt"

    source_sha = run(["git", "rev-parse", "HEAD"], source).get("stdout", "").strip() if source.exists() else ""
    disk_before = disk_snapshot(repo_root)
    summary: dict = {
        "run_id": run_id,
        "experiment": "llama.cpp 8B Q2 Server Smoke 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "pinned_commit": PINNED_COMMIT,
        "source_commit_actual": source_sha,
        "model": {
            "repo": MODEL_REPO,
            "file": MODEL_FILE,
            "path": str(model_path),
            "expected_sha256": MODEL_SHA256,
        },
        "context": CTX,
        "requested_gpu_layers": -1,
        "guardrails": {
            "abort_below_memory_free_percent": FREE_MEMORY_ABORT_PERCENT,
            "abort_above_swap_mb": SWAP_ABORT_MB,
        },
        "disk_before": disk_before,
        "memory_before": memory_snapshot(repo_root),
    }

    print("LOOM llama.cpp 8B Q2 Server Smoke 001")
    print(f"Disk free before: {disk_before['free_gib']:.3f} GiB")

    required = ["cmake", "sysctl", "ps", "memory_pressure"]
    missing = [x for x in required if shutil.which(x) is None]
    if missing or source_sha != PINNED_COMMIT or not build.exists():
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "preflight/build-tree verification failed"
        summary["missing_prerequisites"] = missing
        write_summary(summary_path, summary)
        print("Preflight: FAIL")
        print(f"Missing: {missing}")
        print(f"Source commit: {source_sha or 'N/A'}")
        print(f"Summary: {summary_path}")
        return 2

    if not model_path.exists():
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "verified Q2 model is not present"
        write_summary(summary_path, summary)
        print("Model preflight: FAIL — local Q2 artifact missing")
        print(f"Summary: {summary_path}")
        return 2

    print("Verifying model SHA256...", flush=True)
    digest = sha256_file(model_path)
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
        build_cmd = [
            "cmake", "--build", str(build), "--target", "llama-server",
            "--parallel", str(max(1, os.cpu_count() or 1)),
        ]
        build_result = run(build_cmd, source, timeout=1800)
        summary["server_build"] = build_result
        (out_dir / "server-build-stdout.txt").write_text(build_result.get("stdout", ""), encoding="utf-8")
        (out_dir / "server-build-stderr.txt").write_text(build_result.get("stderr", ""), encoding="utf-8")
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

    summary["server_version"] = run([str(server), "--version"], source, timeout=30)

    if not port_is_available(HOST, PORT):
        summary["classification"] = "FAIL"
        summary["failure_reason"] = f"local port {PORT} is already in use"
        write_summary(summary_path, summary)
        print(f"Port preflight: FAIL — {HOST}:{PORT} unavailable")
        print(f"Summary: {summary_path}")
        return 2

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], repo_root, timeout=30)

    server_cmd = [
        str(server),
        "-m", str(model_path),
        "-ngl", "-1",
        "-c", str(CTX),
        "-fa", "auto",
        "--host", HOST,
        "--port", str(PORT),
        "--alias", MODEL_ALIAS,
        "--no-webui",
    ]
    summary["server_command"] = server_cmd
    print("Launching llama-server...", flush=True)

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
                sample = sample_process(proc.pid, repo_root, elapsed)
                samples.append(sample)
                reason = guardrail_reason(sample)
                if reason:
                    guard_abort_reason = reason
                    break

                health = http_get_json(f"http://{HOST}:{PORT}/health", timeout=3)
                health["elapsed_seconds"] = round(elapsed, 3)
                health_history.append(health)
                if health.get("http_status") == 200:
                    ready = True
                    break
                time.sleep(1.0)

            if guard_abort_reason:
                shutdown_result = terminate_process(proc)
            elif not ready:
                shutdown_result = terminate_process(proc)
            else:
                readiness_wall = round(time.perf_counter() - started, 3)
                summary["readiness_wall_seconds"] = readiness_wall
                print(f"Server readiness: PASS ({readiness_wall:.3f}s)")
                print("Sending /v1/chat/completions smoke...", flush=True)

                request_url = f"http://{HOST}:{PORT}/v1/chat/completions"
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(chat_completion, request_url)
                    request_started = time.perf_counter()
                    while not future.done():
                        elapsed = time.perf_counter() - started
                        if proc.poll() is not None:
                            break
                        sample = sample_process(proc.pid, repo_root, elapsed)
                        samples.append(sample)
                        reason = guardrail_reason(sample)
                        if reason:
                            guard_abort_reason = reason
                            terminate_process(proc)
                            break
                        if time.perf_counter() - request_started > REQUEST_TIMEOUT_SECONDS:
                            guard_abort_reason = f"request timeout after {REQUEST_TIMEOUT_SECONDS}s"
                            terminate_process(proc)
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
                    final_sample = sample_process(proc.pid, repo_root, time.perf_counter() - started)
                    samples.append(final_sample)
                    reason = guardrail_reason(final_sample)
                    if reason and not guard_abort_reason:
                        guard_abort_reason = reason
                    shutdown_result = terminate_process(proc)
                else:
                    shutdown_result = {"already_exited": True, "exit_code": proc.returncode}
        finally:
            if proc.poll() is None:
                shutdown_result = terminate_process(proc)

    summary["health_history"] = health_history
    summary["server_ready"] = ready
    summary["guardrail_abort_reason"] = guard_abort_reason
    summary["request"] = request_result
    summary["shutdown"] = shutdown_result
    summary["samples"] = samples

    rss_values = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap_values = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free_values = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    summary["telemetry"] = {
        "peak_rss_mb": max(rss_values) if rss_values else None,
        "peak_swap_used_mb": max(swap_values) if swap_values else None,
        "min_memory_free_percent": min(free_values) if free_values else None,
    }
    (out_dir / "memory-samples.json").write_text(json.dumps(samples, indent=2) + "\n", encoding="utf-8")
    (out_dir / "health-history.json").write_text(json.dumps(health_history, indent=2) + "\n", encoding="utf-8")
    if request_result is not None:
        (out_dir / "chat-response.json").write_text(json.dumps(request_result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    content = assistant_content(request_result or {})
    request_pass = (
        isinstance(request_result, dict)
        and request_result.get("http_status") == 200
        and isinstance(content, str)
        and bool(content.strip())
    )
    summary["assistant_content"] = content
    summary["request_pass"] = request_pass
    summary["disk_after"] = disk_snapshot(repo_root)
    summary["memory_after"] = memory_snapshot(repo_root)

    full_pass = ready and guard_abort_reason is None and request_pass
    summary["classification"] = "FULL_PASS" if full_pass else "FAIL"
    if not full_pass:
        if guard_abort_reason:
            summary["failure_reason"] = guard_abort_reason
        elif not ready:
            summary["failure_reason"] = "server did not reach healthy state before timeout/exit"
        elif not request_pass:
            summary["failure_reason"] = "chat completion API smoke failed"

    write_summary(summary_path, summary)

    print(f"API smoke: {'PASS' if request_pass else 'FAIL'}")
    if content is not None:
        print(f"Assistant content: {content!r}")
    print(f"Peak process RSS: {summary['telemetry']['peak_rss_mb']} MB")
    print(f"Peak observed swap: {summary['telemetry']['peak_swap_used_mb']} MB")
    print(f"Minimum observed free memory: {summary['telemetry']['min_memory_free_percent']}%")
    if guard_abort_reason:
        print(f"Guardrail: {guard_abort_reason}")
    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
    print(f"Run directory: {out_dir}")
    print(f"Summary: {summary_path}")
    return 0 if full_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
