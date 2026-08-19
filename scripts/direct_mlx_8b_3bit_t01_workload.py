#!/usr/bin/env python3
"""LOOM Direct MLX 8B 3-bit T01 Workload Safety 001."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL_SHA256 = "b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1"
ADAPTER_BLOB_SHA = "62abab57f6463c5813809b43d8f1e7bdfec5f304"
MAX_KV_SIZE = 4096
MAX_TOKENS = 2048
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
POLL_SECONDS = 1.0
OLLAMA_MODEL = "qwen3.5:4b-mlx"

CHILD_CODE = r'''
import json
import sys
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, stream_generate

model_path = sys.argv[1]
prompt_path = sys.argv[2]
prompt_text = Path(prompt_path).read_text(encoding="utf-8")
mx.random.seed(0)
model, tokenizer = load(model_path)
messages = [{"role": "user", "content": prompt_text}]
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
    max_tokens=2048,
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


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60, env: dict | None = None) -> dict:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False, env=env)
        return {"command": cmd, "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"command": cmd, "error": f"{type(exc).__name__}: {exc}"}


def git_blob(path: Path, cwd: Path) -> str:
    p = subprocess.run(["git", "hash-object", str(path)], cwd=cwd, capture_output=True, text=True, timeout=30, check=False)
    return p.stdout.strip() if p.returncode == 0 else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_snapshot(path: Path) -> dict:
    u = shutil.disk_usage(path)
    return {"free_gib": round(u.free / (1024 ** 3), 3), "free_bytes": u.free}


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
    return (int(m.group(1)), f"System-wide memory free percentage: {m.group(1)}%") if m else (None, text.strip())


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
        return None, "required memory/swap telemetry unavailable"
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


def load_adapter(path: Path):
    spec = importlib.util.spec_from_file_location("loom_frozen_single_shot_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    adapter_path = repo / "scripts" / "ollama_single_shot.py"
    frozen = repo / "benchmarks" / "coding" / "v1"
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = mlx_root / "8b-3bit-t01-workload-001" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "t01-workload-summary.json"
    prompt_path = run_dir / "t01-frozen-prompt.txt"
    stdout_path = run_dir / "mlx-child-stdout.txt"
    stderr_path = run_dir / "mlx-child-stderr.txt"

    summary = {
        "run_id": run_id,
        "experiment": "Direct MLX 8B 3-bit T01 Workload Safety 001",
        "started_at_utc": utc_now(),
        "classification": None,
        "runtime": {"max_kv_size": MAX_KV_SIZE, "kv_bits": None, "max_tokens": MAX_TOKENS, "thinking": False},
        "guardrails": {"min_free_percent": MIN_FREE_PERCENT, "max_swap_mb": MAX_SWAP_MB},
        "disk_before": disk_snapshot(repo),
    }

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = disk_snapshot(repo)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary['classification']}")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("LOOM Direct MLX 8B 3-bit T01 Workload Safety 001")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "requires Darwin arm64"
        return finish(2)
    if not venv_py.exists() or not weight.exists() or not frozen.exists() or not adapter_path.exists():
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required validated environment/model/benchmark/adapter missing"
        return finish(2)

    versions = run([str(venv_py), "-c", "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))"], cwd=repo)
    try:
        observed_versions = json.loads(versions.get("stdout", "").strip())
    except Exception:
        observed_versions = {}
    summary["observed_versions"] = observed_versions
    if observed_versions != {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {observed_versions!r}"
        return finish(2)
    print(f"Version lock: PASS {observed_versions}")

    observed_sha = sha256_file(weight)
    summary["model_sha256"] = observed_sha
    if observed_sha != MODEL_SHA256:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "model SHA mismatch"
        return finish(2)
    print("Model SHA256: PASS")

    adapter_blob = git_blob(adapter_path, repo)
    summary["adapter_blob_sha"] = adapter_blob
    if adapter_blob != ADAPTER_BLOB_SHA:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"frozen adapter blob mismatch: {adapter_blob}"
        return finish(2)
    print("Frozen adapter blob: PASS")

    try:
        adapter = load_adapter(adapter_path)
        task = next(t for t in adapter.TASKS if t["id"] == "T01")
        task_dir = frozen / task["path"]
        prompt = adapter.build_prompt(task_dir, task)
    except Exception as exc:
        summary["classification"] = "INVALID_HARNESS"
        summary["failure_reason"] = f"cannot build frozen T01 prompt: {type(exc).__name__}: {exc}"
        return finish(2)
    prompt_path.write_text(prompt, encoding="utf-8")
    summary["t01"] = {"editable": task["editable"], "context": task["context"], "prompt_chars": len(prompt)}
    print(f"Frozen T01 prompt: PASS ({len(prompt)} chars)")

    swap_pre = swap_used_mb()
    free_pre, _ = memory_free_percent()
    summary["preflight_system"] = {"swap_used_mb": swap_pre, "memory_free_percent": free_pre}
    if swap_pre is None or free_pre is None:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = "required telemetry unavailable before launch"
        return finish(2)
    if free_pre < MIN_FREE_PERCENT or swap_pre > MAX_SWAP_MB:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"system outside frozen safety boundary before launch: free={free_pre}% swap={swap_pre} MB"
        return finish(2)
    print(f"Safety preflight: PASS (free={free_pre}% swap={swap_pre:.2f} MB)")

    if shutil.which("ollama"):
        summary["ollama_stop"] = run(["ollama", "stop", OLLAMA_MODEL], cwd=repo, timeout=30)

    env = dict(os.environ)
    env.update({
        "HF_HOME": str(mlx_root / "hf-home"),
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "PYTHONUNBUFFERED": "1",
    })
    cmd = [str(venv_py), "-c", CHILD_CODE, str(model_dir), str(prompt_path)]
    summary["child_command"] = [str(venv_py), "-c", "<embedded frozen child code>", str(model_dir), str(prompt_path)]
    samples: list[dict] = []
    guard_reason = None
    telemetry_reason = None
    started = time.perf_counter()

    print("Launching frozen T01 through Direct MLX...", flush=True)
    with stdout_path.open("w", encoding="utf-8") as out_f, stderr_path.open("w", encoding="utf-8") as err_f:
        proc = subprocess.Popen(cmd, cwd=repo, stdout=out_f, stderr=err_f, text=True, env=env)
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
        "telemetry_failure_reason": telemetry_reason,
        "child_result": child,
    }
    summary["memory_samples"] = samples
    summary["telemetry"] = summarize(samples)
    summary["stderr_tail"] = stderr.splitlines()[-80:]

    delivery = {"status": "not_evaluated", "error": None}
    if isinstance(child, dict) and isinstance(child.get("text"), str):
        try:
            files = adapter.extract_files({"response": child["text"]}, task["editable"])
            delivery["status"] = "written"
            delivery["files"] = sorted(files)
        except Exception as exc:
            delivery["status"] = "failed"
            delivery["error"] = f"{type(exc).__name__}: {exc}"
    summary["structured_delivery"] = delivery

    if guard_reason:
        summary["classification"] = "RESOURCE_FAIL"
        summary["failure_reason"] = guard_reason
    elif telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = telemetry_reason
    elif proc.returncode != 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"MLX child exited with code {proc.returncode}"
    elif not isinstance(child, dict) or not isinstance(child.get("text"), str) or not child.get("text").strip():
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "missing/non-empty generation result"
    elif not isinstance(child.get("generation_tokens"), int) or child.get("generation_tokens", 0) <= 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "generation statistics missing"
    else:
        summary["classification"] = "FULL_PASS"

    t = summary["telemetry"]
    print(f"T01 generation exit: {proc.returncode}")
    if isinstance(child, dict):
        print(f"T01 output chars: {len(child.get('text', ''))}")
        print(f"MLX stats: prompt={child.get('prompt_tokens')} tok @ {child.get('prompt_tps')} t/s | generation={child.get('generation_tokens')} tok @ {child.get('generation_tps')} t/s | peak_memory={child.get('peak_memory_gb')} GB | finish={child.get('finish_reason')}")
    print(f"Structured delivery: {delivery['status']}")
    if delivery.get("error"):
        print(f"Delivery error: {delivery['error']}")
    print(f"Peak process RSS: {t.get('peak_rss_mb')} MB")
    print(f"Peak observed swap: {t.get('peak_swap_used_mb')} MB")
    print(f"Minimum observed free memory: {t.get('min_memory_free_percent')}%")
    if guard_reason:
        print(f"Guardrail: {guard_reason}")
    if telemetry_reason:
        print(f"Telemetry failure: {telemetry_reason}")
    return finish(0 if summary["classification"] == "FULL_PASS" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
