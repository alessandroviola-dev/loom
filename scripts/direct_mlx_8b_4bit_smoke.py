#!/usr/bin/env python3
"""LOOM Direct MLX Qwen3 8B 4-bit Smoke 001."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL_REPO = "mlx-community/Qwen3-8B-4bit"
MODEL_REVISION = "545dc4251c05440727734bcd94334791f6ab0192"
MODEL_WEIGHT_FILE = "model.safetensors"
MODEL_WEIGHT_SHA256 = "f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8"
EXPECTED_BITS = 4
EXPECTED_GROUP_SIZE = 64
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
MAX_KV_SIZE = 4096
MAX_TOKENS = 16
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
MIN_DOWNLOAD_FREE_GIB = 10.0
POLL_SECONDS = 1.0
OLLAMA_MODEL = "qwen3.5:4b-mlx"

CHILD_CODE = r'''
import json
import sys
import mlx.core as mx
from mlx_lm import load, stream_generate

model_path = sys.argv[1]
mx.random.seed(0)
model, tokenizer = load(model_path)
messages = [{"role": "user", "content": "Reply only with OK."}]
prompt = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    enable_thinking=False,
)
parts = []
last = None
for response in stream_generate(
    model,
    tokenizer,
    prompt,
    max_tokens=16,
    max_kv_size=4096,
):
    parts.append(response.text)
    last = response
result = {
    "text": "".join(parts),
    "prompt_tokens": getattr(last, "prompt_tokens", None) if last is not None else None,
    "prompt_tps": getattr(last, "prompt_tps", None) if last is not None else None,
    "generation_tokens": getattr(last, "generation_tokens", None) if last is not None else 0,
    "generation_tps": getattr(last, "generation_tps", None) if last is not None else None,
    "peak_memory_gb": getattr(last, "peak_memory", None) if last is not None else None,
    "finish_reason": getattr(last, "finish_reason", None) if last is not None else None,
    "max_kv_size": 4096,
    "kv_bits": None,
    "thinking": False,
}
print("LOOM_CHILD_RESULT=" + json.dumps(result, ensure_ascii=False), flush=True)
'''


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def disk_snapshot(path: Path) -> dict:
    u = shutil.disk_usage(path)
    return {"free_bytes": u.free, "free_gib": round(u.free / (1024 ** 3), 3)}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def directory_size_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        try:
            if p.is_file() and not p.is_symlink():
                total += p.stat().st_size
        except OSError:
            pass
    return total


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120, env: dict | None = None) -> dict:
    started = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False, env=env)
        return {
            "command": cmd,
            "exit_code": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }


def parse_scaled_mb(value: str, unit: str) -> float:
    n = float(value.replace(",", "."))
    unit = unit.upper()
    if unit == "K":
        return n / 1024.0
    if unit == "M":
        return n
    if unit == "G":
        return n * 1024.0
    if unit == "T":
        return n * 1024.0 * 1024.0
    return n


def swap_used_mb() -> float | None:
    p = subprocess.run(["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=10, check=False)
    if p.returncode != 0:
        return None
    m = re.search(r"\bused\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])(?:B)?\b", p.stdout, re.IGNORECASE)
    if not m:
        return None
    return round(parse_scaled_mb(m.group(1), m.group(2)), 2)


def memory_free_percent() -> tuple[int | None, str]:
    p = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=15, check=False)
    text = p.stdout + p.stderr
    m = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    if not m:
        return None, text.strip()
    return int(m.group(1)), f"System-wide memory free percentage: {m.group(1)}%"


def process_rss_mb(pid: int) -> float | None:
    p = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True, timeout=10, check=False)
    if p.returncode != 0 or not p.stdout.strip():
        return None
    try:
        return float(p.stdout.strip().splitlines()[-1]) / 1024.0
    except ValueError:
        return None


def sample_process(pid: int, elapsed: float) -> dict:
    free, pressure = memory_free_percent()
    return {
        "elapsed_seconds": round(elapsed, 3),
        "rss_mb": process_rss_mb(pid),
        "swap_used_mb": swap_used_mb(),
        "memory_free_percent": free,
        "memory_pressure": pressure,
    }


def sample_failure(sample: dict) -> tuple[str | None, str | None]:
    free = sample.get("memory_free_percent")
    swap = sample.get("swap_used_mb")
    if free is None or swap is None:
        return None, "required free-memory/swap telemetry unavailable"
    if free < MIN_FREE_PERCENT:
        return f"memory free {free}% < {MIN_FREE_PERCENT}%", None
    if swap > MAX_SWAP_MB:
        return f"swap used {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB", None
    return None, None


def terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def summarize(samples: list[dict]) -> dict:
    rss = [s["rss_mb"] for s in samples if isinstance(s.get("rss_mb"), (int, float))]
    swap = [s["swap_used_mb"] for s in samples if isinstance(s.get("swap_used_mb"), (int, float))]
    free = [s["memory_free_percent"] for s in samples if isinstance(s.get("memory_free_percent"), int)]
    return {
        "peak_rss_mb": max(rss) if rss else None,
        "peak_swap_used_mb": max(swap) if swap else None,
        "min_memory_free_percent": min(free) if free else None,
    }


def parse_child(stdout: str) -> dict | None:
    prefix = "LOOM_CHILD_RESULT="
    for line in reversed(stdout.splitlines()):
        if line.startswith(prefix):
            try:
                return json.loads(line[len(prefix):])
            except json.JSONDecodeError:
                return None
    return None


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-4bit"
    weight = model_dir / MODEL_WEIGHT_FILE
    hf_home = mlx_root / "hf-home"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = mlx_root / "8b-4bit-smoke-001" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "smoke-summary.json"
    stdout_path = run_dir / "mlx-child-stdout.txt"
    stderr_path = run_dir / "mlx-child-stderr.txt"

    summary: dict = {
        "run_id": run_id,
        "experiment": "Direct MLX 8B 4-bit Smoke 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "model": {
            "repo": MODEL_REPO,
            "revision": MODEL_REVISION,
            "weight_file": MODEL_WEIGHT_FILE,
            "expected_weight_sha256": MODEL_WEIGHT_SHA256,
            "expected_bits": EXPECTED_BITS,
            "expected_group_size": EXPECTED_GROUP_SIZE,
            "local_dir": str(model_dir),
        },
        "runtime": {
            "max_kv_size": MAX_KV_SIZE,
            "kv_bits": None,
            "max_tokens": MAX_TOKENS,
            "thinking": False,
        },
        "guardrails": {"min_free_percent": MIN_FREE_PERCENT, "max_swap_mb": MAX_SWAP_MB},
        "disk_before": disk_snapshot(repo),
    }

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_final"] = disk_snapshot(repo)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        telemetry = summary.get("telemetry") or {}
        if telemetry:
            print(f"Peak process RSS: {telemetry.get('peak_rss_mb')} MB")
            print(f"Peak observed swap: {telemetry.get('peak_swap_used_mb')} MB")
            print(f"Minimum observed free memory: {telemetry.get('min_memory_free_percent')}%")
        print(f"Classification: {summary['classification']}")
        print(f"Disk free after: {summary['disk_final']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("LOOM Direct MLX 8B 4-bit Smoke 001")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)
    if not venv_py.exists():
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "validated Direct MLX venv missing"
        return finish(2)

    versions = run([
        str(venv_py), "-c",
        "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))"
    ], cwd=repo, timeout=30)
    try:
        observed_versions = json.loads(versions.get("stdout", "").strip())
    except Exception:
        observed_versions = {}
    summary["observed_versions"] = observed_versions
    if observed_versions != EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {observed_versions!r}"
        return finish(2)
    print(f"Version lock: PASS {observed_versions}")

    existing_verified = False
    if weight.exists():
        print("Existing model weight found; verifying before acquisition...", flush=True)
        observed = sha256_file(weight)
        summary["preexisting_weight_sha256"] = observed
        existing_verified = observed == MODEL_WEIGHT_SHA256
        print(f"Existing weight SHA256: {'PASS' if existing_verified else 'MISMATCH'}")
        if not existing_verified:
            summary["classification"] = "HASH_FAIL"
            summary["failure_reason"] = "pre-existing model.safetensors SHA256 mismatch; artifact left untouched"
            return finish(1)

    if not existing_verified and summary["disk_before"]["free_gib"] < MIN_DOWNLOAD_FREE_GIB:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"less than {MIN_DOWNLOAD_FREE_GIB:.0f} GiB free before first acquisition"
        return finish(2)

    model_dir.mkdir(parents=True, exist_ok=True)
    hf_home.mkdir(parents=True, exist_ok=True)
    download_env = dict(os.environ)
    download_env.update({"HF_HOME": str(hf_home), "HF_HUB_DISABLE_XET": "1", "PYTHONUNBUFFERED": "1"})
    download_code = (
        "from huggingface_hub import snapshot_download; "
        f"p=snapshot_download(repo_id={MODEL_REPO!r}, revision={MODEL_REVISION!r}, local_dir={str(model_dir)!r}); "
        "print(p)"
    )
    print("Acquiring/verifying pinned Hugging Face snapshot...", flush=True)
    download = run([str(venv_py), "-c", download_code], cwd=repo, timeout=3600, env=download_env)
    summary["download_result"] = download
    summary["disk_after_acquisition"] = disk_snapshot(repo)
    if download.get("exit_code") != 0:
        summary["classification"] = "DOWNLOAD_FAIL"
        summary["failure_reason"] = "snapshot_download failed"
        print("Snapshot acquisition: FAIL")
        return finish(1)
    print("Snapshot acquisition: PASS")
    print(f"Disk free after acquisition: {summary['disk_after_acquisition']['free_gib']:.3f} GiB")

    if not weight.exists():
        summary["classification"] = "DOWNLOAD_FAIL"
        summary["failure_reason"] = "model.safetensors missing after acquisition"
        return finish(1)

    observed_sha = sha256_file(weight)
    summary["model"]["observed_weight_sha256"] = observed_sha
    summary["model"]["weight_size_bytes"] = weight.stat().st_size
    summary["model"]["weight_size_gib"] = round(weight.stat().st_size / (1024 ** 3), 3)
    summary["model"]["directory_size_bytes"] = directory_size_bytes(model_dir)
    summary["model"]["directory_size_gib"] = round(summary["model"]["directory_size_bytes"] / (1024 ** 3), 3)
    if observed_sha != MODEL_WEIGHT_SHA256:
        summary["classification"] = "HASH_FAIL"
        summary["failure_reason"] = "downloaded model.safetensors SHA256 mismatch; artifact left untouched"
        print(f"Model SHA256: FAIL ({observed_sha})")
        return finish(1)
    print("Model SHA256: PASS")
    print(f"Model weight size: {summary['model']['weight_size_gib']:.3f} GiB")

    config_path = model_dir / "config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["classification"] = "MODEL_METADATA_FAIL"
        summary["failure_reason"] = f"cannot read config.json: {type(exc).__name__}: {exc}"
        return finish(1)
    quant = config.get("quantization") or config.get("quantization_config") or {}
    summary["model"]["quantization"] = quant
    metadata_ok = quant.get("bits") == EXPECTED_BITS and quant.get("group_size") == EXPECTED_GROUP_SIZE
    print(f"Quantization metadata: {'PASS' if metadata_ok else 'FAIL'} {quant}")
    if not metadata_ok:
        summary["classification"] = "MODEL_METADATA_FAIL"
        summary["failure_reason"] = f"expected 4-bit group-size 64, got {quant!r}"
        return finish(1)

    swap_pre = swap_used_mb()
    free_pre, _ = memory_free_percent()
    summary["preflight_system"] = {"swap_used_mb": swap_pre, "memory_free_percent": free_pre}
    if swap_pre is None or free_pre is None:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = "required free-memory/swap telemetry unavailable before launch"
        return finish(2)
    if free_pre < MIN_FREE_PERCENT or swap_pre > MAX_SWAP_MB:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"system outside safety boundary before launch: free={free_pre}% swap={swap_pre} MB"
        return finish(2)
    print(f"Safety preflight: PASS (free={free_pre}% swap={swap_pre:.2f} MB)")

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], cwd=repo, timeout=30)

    child_env = dict(os.environ)
    child_env.update({
        "HF_HOME": str(hf_home),
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "PYTHONUNBUFFERED": "1",
    })
    cmd = [str(venv_py), "-c", CHILD_CODE, str(model_dir)]
    summary["child_command"] = [str(venv_py), "-c", "<embedded frozen child code>", str(model_dir)]

    samples: list[dict] = []
    guard_reason = None
    telemetry_reason = None
    started = time.perf_counter()
    print("Launching direct MLX generation (max_kv_size=4096, KV unquantized)...", flush=True)
    with stdout_path.open("w", encoding="utf-8") as out_f, stderr_path.open("w", encoding="utf-8") as err_f:
        proc = subprocess.Popen(cmd, cwd=repo, stdout=out_f, stderr=err_f, text=True, env=child_env)
        try:
            while proc.poll() is None:
                sample = sample_process(proc.pid, time.perf_counter() - started)
                samples.append(sample)
                guard_reason, telemetry_reason = sample_failure(sample)
                if guard_reason or telemetry_reason:
                    terminate(proc)
                    break
                time.sleep(POLL_SECONDS)
        finally:
            if proc.poll() is None:
                terminate(proc)

    wall = round(time.perf_counter() - started, 3)
    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    child = parse_child(stdout)
    summary["runtime_result"] = {
        "exit_code": proc.returncode,
        "wall_seconds": wall,
        "guardrail_abort_reason": guard_reason,
        "telemetry_abort_reason": telemetry_reason,
        "child_result": child,
        "stderr_tail": stderr[-4000:],
    }
    summary["memory_samples"] = samples
    summary["telemetry"] = summarize(samples)

    if guard_reason:
        summary["classification"] = "RESOURCE_FAIL"
        summary["failure_reason"] = guard_reason
    elif telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = telemetry_reason
    elif proc.returncode != 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"Direct MLX child exited with code {proc.returncode}"
    elif not isinstance(child, dict) or not isinstance(child.get("text"), str) or not child.get("text").strip():
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "generation returned no non-empty text/result"
    elif not isinstance(child.get("prompt_tokens"), int) or not isinstance(child.get("generation_tokens"), int) or child.get("generation_tokens", 0) <= 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "generation statistics missing/incomplete"
    else:
        summary["classification"] = "FULL_PASS"

    print(f"Direct generation exit: {proc.returncode}")
    if isinstance(child, dict):
        print(f"Assistant content: {child.get('text')!r}")
        print(
            "MLX stats: "
            f"prompt={child.get('prompt_tokens')} tok @ {child.get('prompt_tps')} t/s | "
            f"generation={child.get('generation_tokens')} tok @ {child.get('generation_tps')} t/s | "
            f"peak_memory={child.get('peak_memory_gb')} GB | finish={child.get('finish_reason')}"
        )
    return finish(0 if summary["classification"] == "FULL_PASS" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
