#!/usr/bin/env python3
"""LOOM Direct MLX 8B 3-bit Smoke 001.

Acquires the preregistered mlx-community/Qwen3-8B-3bit snapshot into the
LOOM-controlled results-local tree, verifies the main weight SHA/config, then
runs one direct MLX generation in an isolated child process while monitoring
the frozen system memory/swap guardrails.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL_REPO = "mlx-community/Qwen3-8B-3bit"
MODEL_REVISION = "619ded3"
MODEL_WEIGHT_SHA256 = "b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1"
MODEL_WEIGHT_FILE = "model.safetensors"
EXPECTED_BITS = 3
EXPECTED_GROUP_SIZE = 64
MAX_KV_SIZE = 4096
MAX_TOKENS = 16
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
MIN_DOWNLOAD_FREE_GIB = 8.0
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


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120, env: dict | None = None) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
        return {
            "command": cmd,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
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


def disk_snapshot(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {
        "free_bytes": usage.free,
        "free_gib": round(usage.free / (1024 ** 3), 3),
        "total_gib": round(usage.total / (1024 ** 3), 3),
    }


def parse_scaled_mb(value: str, unit: str) -> float:
    unit = unit.upper()
    number = float(value)
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
    proc = subprocess.run(
        ["sysctl", "-n", "vm.swapusage"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0:
        return None
    match = re.search(r"used\s*=\s*([0-9.]+)([KMGT])", proc.stdout)
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def memory_free_percent() -> tuple[int | None, str]:
    proc = subprocess.run(
        ["memory_pressure"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    text = proc.stdout + proc.stderr
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    if not match:
        return None, text.strip()
    return int(match.group(1)), f"System-wide memory free percentage: {match.group(1)}%"


def process_rss_mb(pid: int) -> float | None:
    proc = subprocess.run(
        ["ps", "-o", "rss=", "-p", str(pid)],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        return float(proc.stdout.strip().splitlines()[-1]) / 1024.0
    except ValueError:
        return None


def sample_process(pid: int, elapsed: float) -> dict:
    free_pct, pressure_text = memory_free_percent()
    return {
        "elapsed_seconds": round(elapsed, 3),
        "rss_mb": process_rss_mb(pid),
        "swap_used_mb": swap_used_mb(),
        "memory_free_percent": free_pct,
        "memory_pressure": pressure_text,
    }


def guardrail_reason(sample: dict) -> str | None:
    free_pct = sample.get("memory_free_percent")
    swap_mb = sample.get("swap_used_mb")
    if isinstance(free_pct, int) and free_pct < MIN_FREE_PERCENT:
        return f"memory free {free_pct}% < {MIN_FREE_PERCENT}%"
    if isinstance(swap_mb, (int, float)) and swap_mb > MAX_SWAP_MB:
        return f"swap used {swap_mb:.2f} MB > {MAX_SWAP_MB:.0f} MB"
    return None


def terminate_process(proc: subprocess.Popen) -> None:
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


def summarize_samples(samples: list[dict]) -> dict:
    rss = [x["rss_mb"] for x in samples if isinstance(x.get("rss_mb"), (int, float))]
    swap = [x["swap_used_mb"] for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    free = [x["memory_free_percent"] for x in samples if isinstance(x.get("memory_free_percent"), int)]
    return {
        "peak_rss_mb": max(rss) if rss else None,
        "peak_swap_used_mb": max(swap) if swap else None,
        "min_memory_free_percent": min(free) if free else None,
    }


def parse_child_result(stdout: str) -> dict | None:
    prefix = "LOOM_CHILD_RESULT="
    for line in reversed(stdout.splitlines()):
        if line.startswith(prefix):
            try:
                return json.loads(line[len(prefix):])
            except json.JSONDecodeError:
                return None
    return None


def write_summary(path: Path, summary: dict) -> None:
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    mlx_root = repo_root / "results-local" / "mlx"
    venv = mlx_root / "venv-mlx-lm-0.31.3"
    venv_python = venv / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight_path = model_dir / MODEL_WEIGHT_FILE

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = mlx_root / "8b-3bit-smoke-001" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "smoke-summary.json"

    summary: dict = {
        "run_id": run_id,
        "experiment": "Direct MLX 8B 3-bit Smoke 001",
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
            "venv": str(venv),
            "max_kv_size": MAX_KV_SIZE,
            "kv_bits": None,
            "max_tokens": MAX_TOKENS,
            "enable_thinking": False,
            "memory_guardrail_free_percent": MIN_FREE_PERCENT,
            "swap_guardrail_mb": MAX_SWAP_MB,
        },
        "disk_before": disk_snapshot(repo_root),
    }

    print("LOOM Direct MLX 8B 3-bit Smoke 001")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        write_summary(summary_path, summary)
        print("Platform preflight: FAIL")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 2

    if not venv_python.exists():
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "validated Direct MLX venv missing"
        write_summary(summary_path, summary)
        print("Validated venv: MISSING")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 2

    version_check = run(
        [
            str(venv_python),
            "-c",
            "import importlib.metadata as m; import json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
        ],
        cwd=repo_root,
        timeout=30,
    )
    summary["version_check"] = version_check
    expected_versions = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
    try:
        observed_versions = json.loads(version_check.get("stdout", "").strip()) if version_check.get("exit_code") == 0 else {}
    except json.JSONDecodeError:
        observed_versions = {}
    summary["observed_versions"] = observed_versions
    if observed_versions != expected_versions:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {observed_versions!r}"
        write_summary(summary_path, summary)
        print(f"Version lock: FAIL {observed_versions}")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 2
    print(f"Version lock: PASS {observed_versions}")

    existing_verified = False
    if weight_path.exists():
        print("Existing model weight found; verifying before acquisition...", flush=True)
        existing_sha = sha256_file(weight_path)
        summary["preexisting_weight_sha256"] = existing_sha
        existing_verified = existing_sha == MODEL_WEIGHT_SHA256
        print(f"Existing weight SHA256: {'PASS' if existing_verified else 'MISMATCH'}")
        if not existing_verified:
            summary["classification"] = "HASH_FAIL"
            summary["failure_reason"] = "pre-existing model.safetensors SHA256 mismatch; artifact left untouched"
            summary["disk_final"] = disk_snapshot(repo_root)
            write_summary(summary_path, summary)
            print("Refusing automatic deletion/replacement of mismatching artifact.")
            print(f"Classification: {summary['classification']}")
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 1

    if not existing_verified and summary["disk_before"]["free_gib"] < MIN_DOWNLOAD_FREE_GIB:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"less than {MIN_DOWNLOAD_FREE_GIB:.0f} GiB free before model acquisition"
        write_summary(summary_path, summary)
        print("Disk preflight: FAIL")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 2

    model_dir.mkdir(parents=True, exist_ok=True)
    hf_home = mlx_root / "hf-home"
    hf_home.mkdir(parents=True, exist_ok=True)
    download_env = dict(os.environ)
    download_env.update(
        {
            "HF_HOME": str(hf_home),
            "HF_HUB_DISABLE_XET": "1",
            "PYTHONUNBUFFERED": "1",
        }
    )
    download_code = (
        "from huggingface_hub import snapshot_download; "
        f"p=snapshot_download(repo_id={MODEL_REPO!r}, revision={MODEL_REVISION!r}, local_dir={str(model_dir)!r}); "
        "print(p)"
    )
    print("Acquiring/verifying pinned Hugging Face snapshot...", flush=True)
    download_result = run(
        [str(venv_python), "-c", download_code],
        cwd=repo_root,
        timeout=3600,
        env=download_env,
    )
    summary["download_result"] = download_result
    summary["disk_after_acquisition"] = disk_snapshot(repo_root)
    if download_result.get("exit_code") != 0:
        summary["classification"] = "DOWNLOAD_FAIL"
        summary["failure_reason"] = "snapshot_download failed"
        summary["disk_final"] = disk_snapshot(repo_root)
        write_summary(summary_path, summary)
        print("Snapshot acquisition: FAIL")
        print(f"Classification: {summary['classification']}")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return 1
    print("Snapshot acquisition: PASS")
    print(f"Disk free after acquisition: {summary['disk_after_acquisition']['free_gib']:.3f} GiB")

    if not weight_path.exists():
        summary["classification"] = "DOWNLOAD_FAIL"
        summary["failure_reason"] = "model.safetensors missing after snapshot acquisition"
        summary["disk_final"] = disk_snapshot(repo_root)
        write_summary(summary_path, summary)
        print("Model weight: MISSING")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 1

    observed_sha = sha256_file(weight_path)
    summary["model"]["observed_weight_sha256"] = observed_sha
    summary["model"]["weight_size_bytes"] = weight_path.stat().st_size
    summary["model"]["weight_size_gib"] = round(weight_path.stat().st_size / (1024 ** 3), 3)
    summary["model"]["directory_size_bytes"] = directory_size_bytes(model_dir)
    summary["model"]["directory_size_gib"] = round(summary["model"]["directory_size_bytes"] / (1024 ** 3), 3)
    if observed_sha != MODEL_WEIGHT_SHA256:
        summary["classification"] = "HASH_FAIL"
        summary["failure_reason"] = "downloaded model.safetensors SHA256 mismatch"
        summary["disk_final"] = disk_snapshot(repo_root)
        write_summary(summary_path, summary)
        print(f"Model SHA256: FAIL ({observed_sha})")
        print("Artifact left untouched for diagnosis.")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 1
    print("Model SHA256: PASS")
    print(f"Model weight size: {summary['model']['weight_size_gib']:.3f} GiB")

    config_path = model_dir / "config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["classification"] = "MODEL_METADATA_FAIL"
        summary["failure_reason"] = f"cannot read config.json: {type(exc).__name__}: {exc}"
        summary["disk_final"] = disk_snapshot(repo_root)
        write_summary(summary_path, summary)
        print("Model metadata: FAIL")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 1

    quant = config.get("quantization") or config.get("quantization_config") or {}
    summary["model"]["quantization"] = quant
    metadata_ok = quant.get("bits") == EXPECTED_BITS and quant.get("group_size") == EXPECTED_GROUP_SIZE
    print(f"Quantization metadata: {'PASS' if metadata_ok else 'FAIL'} {quant}")
    if not metadata_ok:
        summary["classification"] = "MODEL_METADATA_FAIL"
        summary["failure_reason"] = f"expected 3-bit group-size 64, got {quant!r}"
        summary["disk_final"] = disk_snapshot(repo_root)
        write_summary(summary_path, summary)
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 1

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], cwd=repo_root, timeout=30)

    pre_runtime_sample = sample_process(os.getpid(), 0.0)
    summary["pre_runtime_system_sample"] = pre_runtime_sample
    pre_reason = guardrail_reason(pre_runtime_sample)
    if pre_reason:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"system already outside frozen guardrail before model launch: {pre_reason}"
        summary["disk_final"] = disk_snapshot(repo_root)
        write_summary(summary_path, summary)
        print(f"Runtime memory preflight: FAIL ({pre_reason})")
        print(f"Classification: {summary['classification']}")
        print(f"Summary: {summary_path}")
        return 2

    child_env = dict(os.environ)
    child_env.update(
        {
            "HF_HOME": str(hf_home),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "PYTHONUNBUFFERED": "1",
        }
    )
    stdout_path = run_dir / "mlx-child-stdout.txt"
    stderr_path = run_dir / "mlx-child-stderr.txt"
    child_cmd = [str(venv_python), "-c", CHILD_CODE, str(model_dir)]
    summary["child_command"] = [str(venv_python), "-c", "<embedded frozen child code>", str(model_dir)]

    print("Launching direct MLX generation (max_kv_size=4096, KV unquantized)...", flush=True)
    samples: list[dict] = []
    guard_abort_reason: str | None = None
    proc: subprocess.Popen | None = None
    started = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as out_f, stderr_path.open("w", encoding="utf-8") as err_f:
        proc = subprocess.Popen(
            child_cmd,
            cwd=repo_root,
            stdout=out_f,
            stderr=err_f,
            text=True,
            env=child_env,
        )
        try:
            while proc.poll() is None:
                sample = sample_process(proc.pid, time.perf_counter() - started)
                samples.append(sample)
                reason = guardrail_reason(sample)
                if reason:
                    guard_abort_reason = reason
                    terminate_process(proc)
                    break
                time.sleep(POLL_SECONDS)
            if proc.poll() is None:
                terminate_process(proc)
        finally:
            if proc is not None and proc.poll() is None:
                terminate_process(proc)

    wall = round(time.perf_counter() - started, 3)
    exit_code = proc.returncode if proc is not None else None
    stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace") if stdout_path.exists() else ""
    stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
    child_result = parse_child_result(stdout_text)

    summary["runtime_result"] = {
        "exit_code": exit_code,
        "wall_seconds": wall,
        "guardrail_abort_reason": guard_abort_reason,
        "child_result": child_result,
    }
    summary["memory_samples"] = samples
    summary["telemetry"] = summarize_samples(samples)
    summary["disk_final"] = disk_snapshot(repo_root)
    summary["finished_at_utc"] = utc_now()

    response_text = child_result.get("text") if isinstance(child_result, dict) else None
    stats_ok = (
        isinstance(child_result, dict)
        and isinstance(child_result.get("prompt_tokens"), int)
        and isinstance(child_result.get("generation_tokens"), int)
        and child_result.get("generation_tokens", 0) > 0
    )

    if guard_abort_reason:
        summary["classification"] = "RESOURCE_FAIL"
        summary["failure_reason"] = guard_abort_reason
    elif exit_code != 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"direct MLX child exited with code {exit_code}"
    elif not isinstance(response_text, str) or not response_text.strip():
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "generation returned no non-empty text"
    elif not stats_ok:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "generation statistics missing/incomplete"
    else:
        summary["classification"] = "FULL_PASS"

    write_summary(summary_path, summary)

    telemetry = summary["telemetry"]
    print(f"Direct generation exit: {exit_code}")
    if isinstance(child_result, dict):
        print(f"Assistant content: {child_result.get('text')!r}")
        print(
            "MLX stats: "
            f"prompt={child_result.get('prompt_tokens')} tok @ {child_result.get('prompt_tps')} t/s | "
            f"generation={child_result.get('generation_tokens')} tok @ {child_result.get('generation_tps')} t/s | "
            f"peak_memory={child_result.get('peak_memory_gb')} GB | finish={child_result.get('finish_reason')}"
        )
    print(f"Peak process RSS: {telemetry.get('peak_rss_mb')} MB")
    print(f"Peak observed swap: {telemetry.get('peak_swap_used_mb')} MB")
    print(f"Minimum observed free memory: {telemetry.get('min_memory_free_percent')}%")
    if guard_abort_reason:
        print(f"Guardrail: {guard_abort_reason}")
    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_final']['free_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")

    return 0 if summary["classification"] == "FULL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
