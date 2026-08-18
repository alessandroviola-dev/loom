#!/usr/bin/env python3
"""LOOM llama.cpp 4B Runtime Control 001.

Downloads and SHA256-verifies the preregistered official Qwen3 4B Q4_K_M
GGUF, then benchmarks it with the pinned llama.cpp Metal build. Captures raw
llama-bench JSON/logs plus lightweight macOS memory/swap telemetry.

This is a runtime/instrumentation control, not a model-quality benchmark.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

PINNED_COMMIT = "60addddf3c567c43ec3caf70fc953fba3572d96f"
MODEL_REPO = "Qwen/Qwen3-4B-GGUF"
MODEL_FILE = "Qwen3-4B-Q4_K_M.gguf"
MODEL_QUANT = "Q4_K_M"
MODEL_SHA256 = "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}?download=true"
OLLAMA_MODEL = "qwen3.5:4b-mlx"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
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


def memory_snapshot(repo_root: Path) -> dict:
    top = run(["top", "-l", "1", "-n", "0"], repo_root)
    physmem = next(
        (line for line in top.get("stdout", "").splitlines() if line.startswith("PhysMem:")),
        "",
    )
    pressure = run(["memory_pressure"], repo_root)
    pressure_line = next(
        (line.strip() for line in reversed(pressure.get("stdout", "").splitlines()) if line.strip()),
        "",
    )
    swap = run(["sysctl", "vm.swapusage"], repo_root).get("stdout", "").strip()
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
        while True:
            chunk = f.read(8 * 1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download_model(model_path: Path, repo_root: Path) -> dict:
    if model_path.exists():
        digest = sha256_file(model_path)
        return {
            "downloaded": False,
            "existing": True,
            "exit_code": 0 if digest == MODEL_SHA256 else 2,
            "sha256": digest,
            "sha256_ok": digest == MODEL_SHA256,
            "path": str(model_path),
        }

    partial = model_path.with_suffix(model_path.suffix + ".part")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "curl", "-L", "--fail", "--retry", "3", "--retry-delay", "2",
        "-C", "-", "--progress-bar", "-o", str(partial), MODEL_URL,
    ]
    print(f"Downloading {MODEL_FILE} (~2.5 GB; resumable)...", flush=True)
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=repo_root, timeout=3600)
        exit_code = proc.returncode
        error = None
    except subprocess.TimeoutExpired:
        exit_code = None
        error = "download timed out after 3600 seconds"
    wall = round(time.perf_counter() - started, 3)

    if exit_code != 0 or not partial.exists():
        return {
            "downloaded": False,
            "existing": False,
            "exit_code": exit_code,
            "error": error or "curl download failed",
            "wall_seconds": wall,
            "partial_path": str(partial),
        }

    print("Verifying model SHA256...", flush=True)
    digest = sha256_file(partial)
    ok = digest == MODEL_SHA256
    if ok:
        partial.replace(model_path)
    return {
        "downloaded": True,
        "existing": False,
        "exit_code": 0 if ok else 3,
        "wall_seconds": wall,
        "sha256": digest,
        "sha256_ok": ok,
        "path": str(model_path if ok else partial),
    }


def process_rss_mb(pid: int, repo_root: Path) -> float | None:
    result = run(["ps", "-o", "rss=", "-p", str(pid)], repo_root, timeout=5)
    text = result.get("stdout", "").strip()
    try:
        return float(text) / 1024.0
    except ValueError:
        return None


def monitor_command(args: list[str], cwd: Path, timeout: int = 1200) -> dict:
    started = time.perf_counter()
    proc = subprocess.Popen(
        args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    samples: list[dict] = []
    timed_out = False
    last_pressure = 0.0
    latest_free: int | None = None

    while proc.poll() is None:
        elapsed = time.perf_counter() - started
        if elapsed > timeout:
            timed_out = True
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            break

        now = time.perf_counter()
        if now - last_pressure >= 2.0:
            pressure = run(["memory_pressure"], cwd, timeout=5)
            line = next(
                (x.strip() for x in reversed(pressure.get("stdout", "").splitlines()) if x.strip()),
                "",
            )
            latest_free = parse_free_percent(line)
            last_pressure = now

        swap_text = run(["sysctl", "vm.swapusage"], cwd, timeout=5).get("stdout", "").strip()
        samples.append({
            "elapsed_seconds": round(elapsed, 3),
            "rss_mb": process_rss_mb(proc.pid, cwd),
            "swap_used_mb": parse_swap_mb(swap_text),
            "memory_free_percent": latest_free,
        })
        time.sleep(1.0)

    stdout, stderr = proc.communicate()
    wall = round(time.perf_counter() - started, 3)
    rss_values = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap_values = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free_values = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    return {
        "command": args,
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "wall_seconds": wall,
        "stdout": stdout,
        "stderr": stderr,
        "samples": samples,
        "peak_rss_mb": max(rss_values) if rss_values else None,
        "peak_swap_used_mb": max(swap_values) if swap_values else None,
        "min_memory_free_percent": min(free_values) if free_values else None,
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    llama_root = repo_root / "results-local" / "llama-cpp"
    source = llama_root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    bench = build / "bin" / "llama-bench"
    cli = build / "bin" / "llama-cli"
    model_path = repo_root / "results-local" / "models" / "Qwen3-4B-GGUF" / MODEL_FILE

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = llama_root / "4b-control" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    required = ["curl", "sysctl", "ps", "memory_pressure"]
    missing = [x for x in required if shutil.which(x) is None]
    source_sha = run(["git", "rev-parse", "HEAD"], source).get("stdout", "").strip() if source.exists() else ""
    disk = shutil.disk_usage(repo_root)

    summary: dict = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "llama.cpp 4B Runtime Control 001",
        "pinned_commit": PINNED_COMMIT,
        "source_commit_actual": source_sha,
        "model": {
            "repo": MODEL_REPO,
            "file": MODEL_FILE,
            "quantization": MODEL_QUANT,
            "expected_sha256": MODEL_SHA256,
            "path": str(model_path),
        },
        "binaries": {"llama_bench": str(bench), "llama_cli": str(cli)},
        "missing_prerequisites": missing,
        "disk_free_gib_before": round(disk.free / (1024 ** 3), 3),
        "memory_before": memory_snapshot(repo_root),
    }

    print("LOOM llama.cpp 4B Runtime Control 001")

    if missing or source_sha != PINNED_COMMIT or not bench.exists() or not cli.exists():
        summary["success"] = False
        summary["failure_reason"] = "setup prerequisite/build verification failed"
        path = out_dir / "control-summary.json"
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Preflight: FAIL")
        print(f"Missing: {missing}")
        print(f"Source commit: {source_sha or 'N/A'}")
        print(f"Summary: {path}")
        return 2

    if not model_path.exists() and disk.free < 4 * (1024 ** 3):
        summary["success"] = False
        summary["failure_reason"] = "less than 4 GiB disk free before model download"
        path = out_dir / "control-summary.json"
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Disk guard: FAIL — only {summary['disk_free_gib_before']} GiB free")
        print(f"Summary: {path}")
        return 2

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], repo_root, timeout=30)

    download = download_model(model_path, repo_root)
    summary["model_download"] = download
    if not download.get("sha256_ok"):
        summary["success"] = False
        summary["failure_reason"] = "model download/hash verification failed"
        summary["finished_at_utc"] = utc_now()
        path = out_dir / "control-summary.json"
        path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Model SHA256: FAIL")
        print(f"Observed: {download.get('sha256')}")
        print(f"Expected: {MODEL_SHA256}")
        print(f"Summary: {path}")
        return 1

    model_size_gib = model_path.stat().st_size / (1024 ** 3)
    summary["model"]["size_bytes"] = model_path.stat().st_size
    summary["model"]["size_gib"] = round(model_size_gib, 3)
    summary["model"]["sha256"] = download.get("sha256")
    print(f"Model SHA256: PASS")
    print(f"Model size: {model_size_gib:.3f} GiB")

    devices = run([str(bench), "--list-devices"], source, timeout=60)
    summary["device_list"] = devices
    print("=== DEVICES ===")
    print((devices.get("stdout", "") + devices.get("stderr", "")).strip())

    benchmark_cmd = [
        str(bench),
        "-m", str(model_path),
        "-ngl", "-1",
        "-fa", "auto",
        "-p", "512",
        "-n", "128",
        "-r", "3",
        "-o", "json",
    ]
    print("=== BENCHMARK ===", flush=True)
    benchmark = monitor_command(benchmark_cmd, source, timeout=1200)
    (out_dir / "llama-bench-stdout.json").write_text(benchmark.get("stdout", ""), encoding="utf-8")
    (out_dir / "llama-bench-stderr.txt").write_text(benchmark.get("stderr", ""), encoding="utf-8")
    (out_dir / "memory-samples.json").write_text(json.dumps(benchmark.get("samples", []), indent=2) + "\n", encoding="utf-8")

    parsed = None
    parse_error = None
    try:
        parsed = json.loads(benchmark.get("stdout", ""))
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"

    rows = parsed if isinstance(parsed, list) else []
    pp_rows = [r for r in rows if isinstance(r, dict) and (r.get("n_prompt") or 0) > 0 and (r.get("n_gen") or 0) == 0]
    tg_rows = [r for r in rows if isinstance(r, dict) and (r.get("n_gen") or 0) > 0 and (r.get("n_prompt") or 0) == 0]
    positive = all(float(r.get("avg_ts", 0) or 0) > 0 for r in pp_rows + tg_rows) if pp_rows and tg_rows else False
    evidence_text = (
        devices.get("stdout", "") + devices.get("stderr", "") + benchmark.get("stderr", "") + json.dumps(rows)
    ).lower()
    metal_evidence = "metal" in evidence_text
    offload_lines = [line.strip() for line in benchmark.get("stderr", "").splitlines() if "offload" in line.lower() and "layer" in line.lower()]

    summary["benchmark"] = {
        "command": benchmark_cmd,
        "exit_code": benchmark.get("exit_code"),
        "timed_out": benchmark.get("timed_out"),
        "wall_seconds": benchmark.get("wall_seconds"),
        "parse_error": parse_error,
        "rows": rows,
        "pp_row_count": len(pp_rows),
        "tg_row_count": len(tg_rows),
        "positive_throughput": positive,
        "metal_evidence": metal_evidence,
        "offload_log_lines": offload_lines,
        "peak_rss_mb": benchmark.get("peak_rss_mb"),
        "peak_swap_used_mb": benchmark.get("peak_swap_used_mb"),
        "min_memory_free_percent": benchmark.get("min_memory_free_percent"),
    }
    summary["memory_after"] = memory_snapshot(repo_root)

    success = (
        benchmark.get("exit_code") == 0
        and not benchmark.get("timed_out")
        and parse_error is None
        and bool(pp_rows)
        and bool(tg_rows)
        and positive
        and metal_evidence
    )
    summary["success"] = success
    if not success:
        summary["failure_reason"] = "one or more runtime-control success criteria failed"
    summary["finished_at_utc"] = utc_now()

    print(f"Benchmark: {'PASS' if benchmark.get('exit_code') == 0 and parse_error is None else 'FAIL'}")
    for row in pp_rows + tg_rows:
        test = f"pp{row.get('n_prompt')}" if (row.get("n_prompt") or 0) else f"tg{row.get('n_gen')}"
        print(
            f"{test}: {float(row.get('avg_ts', 0) or 0):.2f} t/s "
            f"± {float(row.get('stddev_ts', 0) or 0):.2f} | "
            f"backend={row.get('backends')} ngl={row.get('n_gpu_layers')}"
        )
    print(f"Metal evidence: {metal_evidence}")
    if offload_lines:
        print("Offload evidence:")
        for line in offload_lines:
            print(f"  {line}")
    print(f"Peak process RSS: {benchmark.get('peak_rss_mb')} MB")
    print(f"Peak observed swap: {benchmark.get('peak_swap_used_mb')} MB")
    print(f"Minimum observed free memory: {benchmark.get('min_memory_free_percent')}%")
    print(f"Success: {success}")

    path = out_dir / "control-summary.json"
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Run directory: {out_dir}")
    print(f"Summary: {path}")
    if not success and benchmark.get("stderr", "").strip():
        print("--- llama-bench stderr ---")
        print(benchmark["stderr"].strip())

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
