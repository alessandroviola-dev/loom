#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q4 Capability 001.

Downloads and SHA256-verifies the preregistered official Qwen3 8B Q4_K_M
GGUF, then runs a staged context-4096 smoke followed by llama-bench only if
the smoke succeeds. Captures macOS memory/swap/disk telemetry and enforces
frozen safety guardrails.
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
MODEL_REPO = "Qwen/Qwen3-8B-GGUF"
MODEL_FILE = "Qwen3-8B-Q4_K_M.gguf"
MODEL_QUANT = "Q4_K_M"
MODEL_SHA256 = "d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785"
MODEL_URL = f"https://huggingface.co/{MODEL_REPO}/resolve/main/{MODEL_FILE}?download=true"
OLLAMA_MODEL = "qwen3.5:4b-mlx"
CTX = 4096
DISK_GUARD_GIB = 12
FREE_MEMORY_ABORT_PERCENT = 5
SWAP_ABORT_MB = 5600.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {"command": args, "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
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


def memory_snapshot(cwd: Path) -> dict:
    top = run(["top", "-l", "1", "-n", "0"], cwd)
    physmem = next((x for x in top.get("stdout", "").splitlines() if x.startswith("PhysMem:")), "")
    pressure = run(["memory_pressure"], cwd)
    pressure_line = next((x.strip() for x in reversed(pressure.get("stdout", "").splitlines()) if x.strip()), "")
    swap = run(["sysctl", "vm.swapusage"], cwd).get("stdout", "").strip()
    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "memory_free_percent": parse_free_percent(pressure_line),
        "swap": swap,
        "swap_used_mb": parse_swap_mb(swap),
    }


def disk_snapshot(path: Path) -> dict:
    d = shutil.disk_usage(path)
    return {
        "total_gib": round(d.total / (1024 ** 3), 3),
        "used_gib": round(d.used / (1024 ** 3), 3),
        "free_gib": round(d.free / (1024 ** 3), 3),
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_model(model_path: Path, cwd: Path) -> dict:
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
    print(f"Downloading {MODEL_FILE} (~4.68 GiB; resumable)...", flush=True)
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=cwd, timeout=7200)
        exit_code = proc.returncode
        error = None
    except subprocess.TimeoutExpired:
        exit_code = None
        error = "download timed out after 7200 seconds"
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


def process_rss_mb(pid: int, cwd: Path) -> float | None:
    result = run(["ps", "-o", "rss=", "-p", str(pid)], cwd, timeout=5)
    try:
        return float(result.get("stdout", "").strip()) / 1024.0
    except ValueError:
        return None


def monitor_command(args: list[str], cwd: Path, timeout: int) -> dict:
    started = time.perf_counter()
    proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    samples: list[dict] = []
    timed_out = False
    guardrail_abort = False
    guardrail_reason: str | None = None
    latest_free: int | None = None
    last_pressure = 0.0

    while proc.poll() is None:
        elapsed = time.perf_counter() - started
        if elapsed > timeout:
            timed_out = True
            guardrail_reason = f"timeout after {timeout}s"
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            break

        now = time.perf_counter()
        if now - last_pressure >= 2.0:
            pressure = run(["memory_pressure"], cwd, timeout=5)
            line = next((x.strip() for x in reversed(pressure.get("stdout", "").splitlines()) if x.strip()), "")
            latest_free = parse_free_percent(line)
            last_pressure = now

        swap_text = run(["sysctl", "vm.swapusage"], cwd, timeout=5).get("stdout", "").strip()
        swap_mb = parse_swap_mb(swap_text)
        rss_mb = process_rss_mb(proc.pid, cwd)
        samples.append({
            "elapsed_seconds": round(elapsed, 3),
            "rss_mb": rss_mb,
            "swap_used_mb": swap_mb,
            "memory_free_percent": latest_free,
        })

        if latest_free is not None and latest_free < FREE_MEMORY_ABORT_PERCENT:
            guardrail_abort = True
            guardrail_reason = f"memory free {latest_free}% < {FREE_MEMORY_ABORT_PERCENT}%"
        if swap_mb is not None and swap_mb > SWAP_ABORT_MB:
            guardrail_abort = True
            guardrail_reason = f"swap {swap_mb:.2f} MB > {SWAP_ABORT_MB:.0f} MB"

        if guardrail_abort:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            break
        time.sleep(1.0)

    stdout, stderr = proc.communicate()
    rss_values = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap_values = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free_values = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    return {
        "command": args,
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "guardrail_abort": guardrail_abort,
        "guardrail_reason": guardrail_reason,
        "wall_seconds": round(time.perf_counter() - started, 3),
        "stdout": stdout,
        "stderr": stderr,
        "samples": samples,
        "peak_rss_mb": max(rss_values) if rss_values else None,
        "peak_swap_used_mb": max(swap_values) if swap_values else None,
        "min_memory_free_percent": min(free_values) if free_values else None,
    }


def save_monitored(out_dir: Path, prefix: str, result: dict) -> None:
    (out_dir / f"{prefix}-stdout.txt").write_text(result.get("stdout", ""), encoding="utf-8")
    (out_dir / f"{prefix}-stderr.txt").write_text(result.get("stderr", ""), encoding="utf-8")
    (out_dir / f"{prefix}-memory-samples.json").write_text(
        json.dumps(result.get("samples", []), indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    llama_root = repo_root / "results-local" / "llama-cpp"
    source = llama_root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    cli = build / "bin" / "llama-cli"
    bench = build / "bin" / "llama-bench"
    model_path = repo_root / "results-local" / "models" / "Qwen3-8B-GGUF" / MODEL_FILE

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = llama_root / "8b-q4" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    source_sha = run(["git", "rev-parse", "HEAD"], source).get("stdout", "").strip() if source.exists() else ""
    required = ["curl", "sysctl", "ps", "memory_pressure"]
    missing = [x for x in required if shutil.which(x) is None]
    disk_before = disk_snapshot(repo_root)

    summary: dict = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "llama.cpp 8B Q4 Capability 001",
        "classification": None,
        "pinned_commit": PINNED_COMMIT,
        "source_commit_actual": source_sha,
        "context": CTX,
        "guardrails": {
            "fresh_download_min_free_gib": DISK_GUARD_GIB,
            "abort_below_memory_free_percent": FREE_MEMORY_ABORT_PERCENT,
            "abort_above_swap_mb": SWAP_ABORT_MB,
        },
        "model": {
            "repo": MODEL_REPO,
            "file": MODEL_FILE,
            "quantization": MODEL_QUANT,
            "expected_sha256": MODEL_SHA256,
            "path": str(model_path),
        },
        "disk_before": disk_before,
        "memory_before": memory_snapshot(repo_root),
        "missing_prerequisites": missing,
    }

    print("LOOM llama.cpp 8B Q4 Capability 001")
    print(f"Disk free before: {disk_before['free_gib']:.3f} GiB")

    if missing or source_sha != PINNED_COMMIT or not cli.exists() or not bench.exists():
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "preflight/build verification failed"
        path = out_dir / "capability-summary.json"
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("Preflight: FAIL")
        print(f"Summary: {path}")
        return 2

    if not model_path.exists() and disk_before["free_gib"] < DISK_GUARD_GIB:
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "disk guard failed before fresh model download"
        path = out_dir / "capability-summary.json"
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Disk guard: FAIL — {disk_before['free_gib']:.3f} GiB < {DISK_GUARD_GIB} GiB")
        print(f"Summary: {path}")
        return 2

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], repo_root, timeout=30)

    download = download_model(model_path, repo_root)
    summary["model_download"] = download
    if not download.get("sha256_ok"):
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "model download/hash verification failed"
        summary["disk_after"] = disk_snapshot(repo_root)
        summary["finished_at_utc"] = utc_now()
        path = out_dir / "capability-summary.json"
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("Model SHA256: FAIL")
        print(f"Observed: {download.get('sha256')}")
        print(f"Expected: {MODEL_SHA256}")
        print(f"Summary: {path}")
        return 1

    model_size_gib = model_path.stat().st_size / (1024 ** 3)
    summary["model"].update({
        "size_bytes": model_path.stat().st_size,
        "size_gib": round(model_size_gib, 3),
        "sha256": download.get("sha256"),
    })
    print("Model SHA256: PASS")
    print(f"Model size: {model_size_gib:.3f} GiB")

    devices = run([str(bench), "--list-devices"], source, timeout=60)
    summary["device_list"] = devices
    print("=== DEVICES ===")
    print((devices.get("stdout", "") + devices.get("stderr", "")).strip())

    smoke_cmd = [
        str(cli), "-m", str(model_path), "-ngl", "-1", "-c", str(CTX),
        "-n", "8", "-p", "Reply only with OK.", "--temp", "0", "--perf",
    ]
    print("=== STAGE A — CONTEXT 4096 SMOKE ===", flush=True)
    smoke = monitor_command(smoke_cmd, source, timeout=300)
    save_monitored(out_dir, "stage-a-smoke", smoke)
    smoke_text = (smoke.get("stdout", "") + smoke.get("stderr", "")).lower()
    smoke_output_nonempty = bool(smoke.get("stdout", "").strip())
    smoke_metal = "metal" in smoke_text or "mtl" in smoke_text
    context_evidence = "4096" in smoke_text
    smoke_pass = (
        smoke.get("exit_code") == 0
        and not smoke.get("timed_out")
        and not smoke.get("guardrail_abort")
        and smoke_output_nonempty
        and smoke_metal
        and context_evidence
    )
    summary["stage_a"] = {
        **{k: v for k, v in smoke.items() if k != "samples"},
        "output_nonempty": smoke_output_nonempty,
        "metal_evidence": smoke_metal,
        "context_4096_evidence": context_evidence,
        "pass": smoke_pass,
    }
    print(f"Stage A: {'PASS' if smoke_pass else 'FAIL'}")
    print(f"  wall={smoke.get('wall_seconds')}s peak_rss={smoke.get('peak_rss_mb')} MB peak_swap={smoke.get('peak_swap_used_mb')} MB min_free={smoke.get('min_memory_free_percent')}%")
    if smoke.get("guardrail_reason"):
        print(f"  guardrail={smoke.get('guardrail_reason')}")

    if not smoke_pass:
        summary["classification"] = "FAIL"
        summary["failure_reason"] = "Stage A context-4096 smoke failed"
        summary["memory_after"] = memory_snapshot(repo_root)
        summary["disk_after"] = disk_snapshot(repo_root)
        summary["finished_at_utc"] = utc_now()
        path = out_dir / "capability-summary.json"
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("Stage B: SKIPPED")
        print("Classification: FAIL")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {out_dir}")
        print(f"Summary: {path}")
        return 1

    bench_cmd = [
        str(bench), "-m", str(model_path), "-ngl", "-1", "-fa", "auto",
        "-p", "512", "-n", "128", "-r", "3", "-o", "json",
    ]
    print("=== STAGE B — BENCHMARK ===", flush=True)
    benchmark = monitor_command(bench_cmd, source, timeout=1800)
    save_monitored(out_dir, "stage-b-benchmark", benchmark)
    (out_dir / "stage-b-benchmark-stdout.json").write_text(benchmark.get("stdout", ""), encoding="utf-8")

    parsed = None
    parse_error = None
    try:
        parsed = json.loads(benchmark.get("stdout", ""))
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"
    rows = parsed if isinstance(parsed, list) else []
    pp_rows = [r for r in rows if isinstance(r, dict) and (r.get("n_prompt") or 0) > 0 and (r.get("n_gen") or 0) == 0]
    tg_rows = [r for r in rows if isinstance(r, dict) and (r.get("n_gen") or 0) > 0 and (r.get("n_prompt") or 0) == 0]
    positive = bool(pp_rows and tg_rows) and all(float(r.get("avg_ts", 0) or 0) > 0 for r in pp_rows + tg_rows)
    bench_evidence = (devices.get("stdout", "") + devices.get("stderr", "") + benchmark.get("stderr", "") + json.dumps(rows)).lower()
    metal_evidence = "metal" in bench_evidence or "mtl" in bench_evidence
    bench_pass = (
        benchmark.get("exit_code") == 0
        and not benchmark.get("timed_out")
        and not benchmark.get("guardrail_abort")
        and parse_error is None
        and positive
        and metal_evidence
    )
    summary["stage_b"] = {
        **{k: v for k, v in benchmark.items() if k != "samples"},
        "parse_error": parse_error,
        "rows": rows,
        "pp_row_count": len(pp_rows),
        "tg_row_count": len(tg_rows),
        "positive_throughput": positive,
        "metal_evidence": metal_evidence,
        "pass": bench_pass,
    }

    for row in pp_rows + tg_rows:
        test = f"pp{row.get('n_prompt')}" if (row.get("n_prompt") or 0) else f"tg{row.get('n_gen')}"
        print(f"{test}: {float(row.get('avg_ts', 0) or 0):.2f} t/s ± {float(row.get('stddev_ts', 0) or 0):.2f} | backend={row.get('backends')} ngl={row.get('n_gpu_layers')}")
    print(f"Stage B: {'PASS' if bench_pass else 'FAIL'}")
    print(f"  peak_rss={benchmark.get('peak_rss_mb')} MB peak_swap={benchmark.get('peak_swap_used_mb')} MB min_free={benchmark.get('min_memory_free_percent')}%")
    if benchmark.get("guardrail_reason"):
        print(f"  guardrail={benchmark.get('guardrail_reason')}")

    summary["classification"] = "FULL_PASS" if bench_pass else "LAUNCH_PASS_BENCH_FAIL"
    summary["memory_after"] = memory_snapshot(repo_root)
    summary["disk_after"] = disk_snapshot(repo_root)
    summary["finished_at_utc"] = utc_now()
    path = out_dir / "capability-summary.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
    print(f"Run directory: {out_dir}")
    print(f"Summary: {path}")
    return 0 if summary["classification"] == "FULL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
