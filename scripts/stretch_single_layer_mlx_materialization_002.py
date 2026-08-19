#!/usr/bin/env python3
"""LOOM Stretch 002 — single-layer MLX materialization + eviction.

Materializes only the raw safetensors arrays belonging to transformer layer 18
inside the frozen Direct MLX environment. It does not construct the Qwen3 model,
create a KV cache, or generate tokens.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROBE_LAYER = 18
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
HOST_GATE_FREE_PERCENT = 60
HOST_GATE_SAMPLES = 3
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
POLL_SECONDS = 0.5
MAX_PRE_EVAL_ACTIVE_DELTA = 32 * 1024 * 1024
RECOVERY_TOLERANCE = 1 * 1024 * 1024
LAYER_RE = re.compile(r"(?:^|\.)layers\.(\d+)\.")

CHILD_CODE = r'''
import gc
import importlib.metadata as md
import json
import sys
import time
from pathlib import Path

import mlx.core as mx

weight_path = Path(sys.argv[1])
names_path = Path(sys.argv[2])
state_path = Path(sys.argv[3])
selected_names = json.loads(names_path.read_text(encoding="utf-8"))


def mem():
    return {
        "active_bytes": int(mx.get_active_memory()),
        "cache_bytes": int(mx.get_cache_memory()),
        "peak_bytes": int(mx.get_peak_memory()),
    }


def save(phase, **extra):
    payload = {"phase": phase, "memory": mem(), **extra}
    state_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("LOOM_CHILD_STATE=" + json.dumps(payload), flush=True)
    return payload

versions = {
    "mlx": md.version("mlx"),
    "mlx-lm": md.version("mlx-lm"),
    "transformers": md.version("transformers"),
}

required_api = [
    "load",
    "eval",
    "get_active_memory",
    "get_cache_memory",
    "get_peak_memory",
    "reset_peak_memory",
    "clear_cache",
]
missing_api = [name for name in required_api if not hasattr(mx, name)]
if missing_api:
    save("api_missing", versions=versions, missing_api=missing_api)
    raise SystemExit(4)

mx.clear_cache()
gc.collect()
mx.reset_peak_memory()
baseline = save("baseline", versions=versions)

weights = mx.load(str(weight_path))
if not isinstance(weights, dict):
    save("load_invalid", observed_type=type(weights).__name__)
    raise SystemExit(5)

missing = [name for name in selected_names if name not in weights]
if missing:
    save("selected_names_missing", missing=missing[:20], missing_count=len(missing))
    raise SystemExit(6)

selected = {name: weights[name] for name in selected_names}
del weights
gc.collect()
pre_eval = save("pre_eval", selected_count=len(selected))

started = time.perf_counter()
mx.eval(selected)
eval_wall = time.perf_counter() - started
post_eval = save("post_eval", selected_count=len(selected), eval_wall_seconds=round(eval_wall, 6))

del selected
gc.collect()
pre_clear = save("references_deleted")
mx.clear_cache()
gc.collect()
time.sleep(0.5)
post_clear = save("post_clear")

result = {
    "versions": versions,
    "baseline": baseline["memory"],
    "pre_eval": pre_eval["memory"],
    "post_eval": post_eval["memory"],
    "references_deleted": pre_clear["memory"],
    "post_clear": post_clear["memory"],
    "selected_count": len(selected_names),
    "eval_wall_seconds": round(eval_wall, 6),
}
print("LOOM_CHILD_COMPLETE=" + json.dumps(result), flush=True)
'''


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 30) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "command": cmd,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "wall_seconds": round(time.perf_counter() - started, 3),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": cmd,
            "error": f"{type(exc).__name__}: {exc}",
            "wall_seconds": round(time.perf_counter() - started, 3),
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


def memory_free_percent() -> int | None:
    result = run(["memory_pressure"], timeout=15)
    text = result.get("stdout", "") + result.get("stderr", "")
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    return int(match.group(1)) if match else None


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


def process_rss_mb(pid: int) -> float | None:
    result = run(["ps", "-o", "rss=", "-p", str(pid)], timeout=10)
    if result.get("exit_code") != 0 or not result.get("stdout", "").strip():
        return None
    try:
        return round(float(result["stdout"].strip().splitlines()[-1]) / 1024.0, 3)
    except ValueError:
        return None


def system_sample(pid: int | None = None) -> dict:
    return {
        "timestamp_utc": utc_now(),
        "memory_free_percent": memory_free_percent(),
        "swap_used_mb": swap_used_mb(),
        "child_rss_mb": process_rss_mb(pid) if pid is not None else None,
    }


def disk_snapshot(path: Path) -> dict:
    usage = shutil.disk_usage(path)
    return {"free_bytes": usage.free, "free_gib": round(usage.free / (1024 ** 3), 3)}


def read_safetensors_header(path: Path) -> dict:
    with path.open("rb") as handle:
        prefix = handle.read(8)
        if len(prefix) != 8:
            raise ValueError("missing safetensors header length")
        header_len = struct.unpack("<Q", prefix)[0]
        if header_len <= 0 or header_len > 256 * 1024 * 1024:
            raise ValueError(f"implausible safetensors header length {header_len}")
        raw = handle.read(header_len)
        if len(raw) != header_len:
            raise ValueError("truncated safetensors header")
    header = json.loads(raw.decode("utf-8"))
    if not isinstance(header, dict):
        raise ValueError("safetensors header is not an object")
    return header


def selected_layer_from_header(weight: Path, layer_id: int) -> tuple[list[str], int]:
    header = read_safetensors_header(weight)
    selected: list[tuple[int, str, int]] = []
    for name, meta in header.items():
        if name == "__metadata__" or not isinstance(meta, dict):
            continue
        match = LAYER_RE.search(name)
        if not match or int(match.group(1)) != layer_id:
            continue
        offsets = meta.get("data_offsets")
        if not isinstance(offsets, list) or len(offsets) != 2:
            raise ValueError(f"invalid offsets for {name}")
        begin, end = offsets
        if not isinstance(begin, int) or not isinstance(end, int) or begin < 0 or end <= begin:
            raise ValueError(f"invalid byte range for {name}: {offsets!r}")
        selected.append((begin, name, end - begin))
    selected.sort()
    return [name for _, name, _ in selected], sum(size for _, _, size in selected)


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def summarize_telemetry(samples: list[dict]) -> dict:
    free = [s["memory_free_percent"] for s in samples if isinstance(s.get("memory_free_percent"), int)]
    swap = [s["swap_used_mb"] for s in samples if isinstance(s.get("swap_used_mb"), (int, float))]
    rss = [s["child_rss_mb"] for s in samples if isinstance(s.get("child_rss_mb"), (int, float))]
    return {
        "sample_count": len(samples),
        "min_memory_free_percent": min(free) if free else None,
        "peak_swap_used_mb": max(swap) if swap else None,
        "peak_child_rss_mb": max(rss) if rss else None,
    }


def terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "single-layer-mlx-materialization-002" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    names_path = run_dir / "selected-layer-names.json"
    child_state_path = run_dir / "child-state.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 002 — Single-Layer MLX Materialization + Eviction",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "probe_layer": PROBE_LAYER,
        "expected_layer_bytes": EXPECTED_LAYER_BYTES,
        "expected_layer_tensors": EXPECTED_LAYER_TENSORS,
        "model_construction": False,
        "token_generation": False,
        "network_download": False,
        "disk_before": disk_snapshot(repo),
    }
    telemetry: list[dict] = []

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = disk_snapshot(repo)
        summary["telemetry"] = summarize_telemetry(telemetry)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        if summary.get("mlx_memory"):
            mem = summary["mlx_memory"]
            print(f"MLX baseline active/cache: {mem['baseline']['active_bytes']} / {mem['baseline']['cache_bytes']} B")
            print(f"MLX pre-eval active/cache: {mem['pre_eval']['active_bytes']} / {mem['pre_eval']['cache_bytes']} B")
            print(f"MLX post-eval active/cache: {mem['post_eval']['active_bytes']} / {mem['post_eval']['cache_bytes']} B")
            print(f"MLX post-clear active/cache: {mem['post_clear']['active_bytes']} / {mem['post_clear']['cache_bytes']} B")
        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")
        print(f"Peak observed swap: {summary['telemetry'].get('peak_swap_used_mb')} MB")
        print(f"Peak child RSS: {summary['telemetry'].get('peak_child_rss_mb')} MB")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("LOOM Stretch 002 — Single-Layer MLX Materialization + Eviction")
    print("Full model construction: NONE")
    print("Token generation: NONE")
    print("Network/download: NONE")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    if not venv_py.is_file() or not weight.is_file():
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"required frozen venv/weight missing: venv={venv_py.is_file()} weight={weight.is_file()}"
        return finish(2)

    versions_result = run([
        str(venv_py), "-c",
        "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
    ], cwd=repo, timeout=30)
    try:
        versions = json.loads(versions_result.get("stdout", "").strip())
    except (json.JSONDecodeError, AttributeError):
        versions = {}
    summary["versions"] = versions
    if versions != EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {versions!r}"
        return finish(2)
    print(f"Version lock: PASS {versions}")

    try:
        names, selected_bytes = selected_layer_from_header(weight, PROBE_LAYER)
    except Exception as exc:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"cannot recover selected layer from safetensors header: {type(exc).__name__}: {exc}"
        return finish(2)

    summary["selected_tensor_count"] = len(names)
    summary["selected_tensor_bytes"] = selected_bytes
    if len(names) != EXPECTED_LAYER_TENSORS or selected_bytes != EXPECTED_LAYER_BYTES:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = (
            f"layer provenance mismatch: tensors={len(names)} bytes={selected_bytes}; "
            f"expected tensors={EXPECTED_LAYER_TENSORS} bytes={EXPECTED_LAYER_BYTES}"
        )
        return finish(2)
    names_path.write_text(json.dumps(names, indent=2) + "\n", encoding="utf-8")
    print(f"Layer provenance: PASS layer={PROBE_LAYER} tensors={len(names)} bytes={selected_bytes}")

    for index in range(HOST_GATE_SAMPLES):
        sample = system_sample()
        sample["phase"] = "host_gate"
        telemetry.append(sample)
        free = sample.get("memory_free_percent")
        swap = sample.get("swap_used_mb")
        print(f"Host sample {index + 1}/{HOST_GATE_SAMPLES}: free={free}% swap={swap} MB")
        if free is None or swap is None:
            summary["classification"] = "TELEMETRY_FAIL"
            summary["failure_reason"] = "required host telemetry unavailable"
            return finish(3)
        if free < HOST_GATE_FREE_PERCENT or swap > MAX_SWAP_MB:
            summary["classification"] = "HOST_STATE_NOT_READY"
            summary["failure_reason"] = f"host state outside launch gate: free={free}% swap={swap} MB"
            return finish(3)
        if index + 1 < HOST_GATE_SAMPLES:
            time.sleep(1.0)
    print("Host-state gate: PASS")

    cmd = [str(venv_py), "-c", CHILD_CODE, str(weight), str(names_path), str(child_state_path)]
    started = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    guardrail_reason = None
    telemetry_reason = None

    while proc.poll() is None:
        sample = system_sample(proc.pid)
        sample["phase"] = (read_json(child_state_path) or {}).get("phase", "child_starting")
        sample["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        telemetry.append(sample)
        free = sample.get("memory_free_percent")
        swap = sample.get("swap_used_mb")
        if free is None or swap is None:
            telemetry_reason = "required runtime memory/swap telemetry unavailable"
            terminate(proc)
            break
        if free < MIN_FREE_PERCENT:
            guardrail_reason = f"memory free {free}% < {MIN_FREE_PERCENT}%"
            terminate(proc)
            break
        if swap > MAX_SWAP_MB:
            guardrail_reason = f"swap used {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB"
            terminate(proc)
            break
        time.sleep(POLL_SECONDS)

    stdout, stderr = proc.communicate(timeout=10)
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    summary["child_exit_code"] = proc.returncode
    summary["child_stdout_file"] = str(stdout_path)
    summary["child_stderr_file"] = str(stderr_path)

    if telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"
        summary["failure_reason"] = telemetry_reason
        return finish(4)
    if guardrail_reason:
        summary["classification"] = "PARTIAL_RESOURCE_FAIL"
        summary["failure_reason"] = guardrail_reason
        return finish(5)
    if proc.returncode != 0:
        state = read_json(child_state_path)
        summary["child_state"] = state
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"MLX child exited {proc.returncode}; state={state!r}"
        return finish(6)

    complete_line = None
    for line in (stdout or "").splitlines():
        if line.startswith("LOOM_CHILD_COMPLETE="):
            complete_line = line.split("=", 1)[1]
    if complete_line is None:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = "child completed without LOOM_CHILD_COMPLETE payload"
        return finish(6)
    try:
        child = json.loads(complete_line)
    except json.JSONDecodeError as exc:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"cannot parse child completion payload: {exc}"
        return finish(6)

    if child.get("versions") != EXPECTED_VERSIONS or child.get("selected_count") != EXPECTED_LAYER_TENSORS:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"child provenance mismatch: {child!r}"
        return finish(6)

    memory = {
        "baseline": child["baseline"],
        "pre_eval": child["pre_eval"],
        "post_eval": child["post_eval"],
        "references_deleted": child["references_deleted"],
        "post_clear": child["post_clear"],
    }
    summary["mlx_memory"] = memory
    summary["eval_wall_seconds"] = child.get("eval_wall_seconds")

    baseline_active = memory["baseline"]["active_bytes"]
    baseline_cache = memory["baseline"]["cache_bytes"]
    pre_delta = memory["pre_eval"]["active_bytes"] - baseline_active
    eval_delta = memory["post_eval"]["active_bytes"] - baseline_active
    final_active_delta = memory["post_clear"]["active_bytes"] - baseline_active
    final_cache_delta = memory["post_clear"]["cache_bytes"] - baseline_cache
    summary["mlx_deltas"] = {
        "pre_eval_active_bytes": pre_delta,
        "post_eval_active_bytes": eval_delta,
        "post_clear_active_bytes": final_active_delta,
        "post_clear_cache_bytes": final_cache_delta,
    }

    print(f"Pre-eval MLX active delta: {pre_delta} B")
    print(f"Post-eval MLX active delta: {eval_delta} B")
    print(f"Post-clear MLX active delta: {final_active_delta} B")
    print(f"Post-clear MLX cache delta: {final_cache_delta} B")
    print(f"Layer mx.eval wall: {child.get('eval_wall_seconds')} s")

    if pre_delta > MAX_PRE_EVAL_ACTIVE_DELTA:
        summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"
        summary["failure_reason"] = f"pre-eval active delta {pre_delta} B > {MAX_PRE_EVAL_ACTIVE_DELTA} B"
        return finish(7)
    if eval_delta <= 0:
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = f"selected layer materialization not observed in MLX active memory: delta={eval_delta}"
        return finish(6)

    eviction_pass = final_active_delta <= RECOVERY_TOLERANCE and final_cache_delta <= RECOVERY_TOLERANCE
    summary["materialization_observed"] = True
    summary["eviction_pass"] = eviction_pass
    summary["classification"] = (
        "SINGLE_LAYER_MLX_EVICTION_PASS"
        if eviction_pass
        else "SINGLE_LAYER_MLX_MATERIALIZATION_PASS_EVICTION_INCONCLUSIVE"
    )
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
