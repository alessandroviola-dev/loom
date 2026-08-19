#!/usr/bin/env python3
"""LOOM Stretch 003 — repeated bounded two-layer MLX residency.

Uses Stretch 002's frozen telemetry/header helpers. In one MLX child process,
materializes and evicts layers 18 then 19. No Qwen model construction, KV cache,
or token generation.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SOURCE_002_BLOB = "e7bd6bf4c61b44664c0c8421bf230b938509e4ef"
PROBE_LAYERS = [18, 19]
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
MATERIALIZATION_TOLERANCE = 1 * 1024 * 1024

CHILD_CODE = r'''
import gc
import importlib.metadata as md
import json
import sys
import time
from pathlib import Path
import mlx.core as mx

weight_path = Path(sys.argv[1])
names_map = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
state_path = Path(sys.argv[3])

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
required = ["load", "eval", "get_active_memory", "get_cache_memory", "get_peak_memory", "reset_peak_memory", "clear_cache"]
missing = [name for name in required if not hasattr(mx, name)]
if missing:
    save("api_missing", versions=versions, missing_api=missing)
    raise SystemExit(4)

mx.clear_cache(); gc.collect(); mx.reset_peak_memory()
baseline = save("baseline", versions=versions)
cycles = []

for layer_id in (18, 19):
    names = names_map[str(layer_id)]
    weights = mx.load(str(weight_path))
    if not isinstance(weights, dict):
        save("load_invalid", layer=layer_id, observed_type=type(weights).__name__)
        raise SystemExit(5)
    missing_names = [name for name in names if name not in weights]
    if missing_names:
        save("selected_names_missing", layer=layer_id, missing=missing_names[:20])
        raise SystemExit(6)

    selected = {name: weights[name] for name in names}
    del weights; gc.collect()
    pre = save(f"layer_{layer_id}_pre_eval", layer=layer_id, selected_count=len(selected))

    mx.reset_peak_memory()
    started = time.perf_counter()
    mx.eval(selected)
    wall = time.perf_counter() - started
    post = save(f"layer_{layer_id}_post_eval", layer=layer_id, eval_wall_seconds=round(wall, 6))

    del selected; gc.collect()
    deleted = save(f"layer_{layer_id}_references_deleted", layer=layer_id)
    mx.clear_cache(); gc.collect(); time.sleep(0.5)
    cleared = save(f"layer_{layer_id}_post_clear", layer=layer_id)

    cycles.append({
        "layer": layer_id,
        "selected_count": len(names),
        "pre_eval": pre["memory"],
        "post_eval": post["memory"],
        "references_deleted": deleted["memory"],
        "post_clear": cleared["memory"],
        "eval_wall_seconds": round(wall, 6),
    })

print("LOOM_CHILD_COMPLETE=" + json.dumps({"versions": versions, "baseline": baseline["memory"], "cycles": cycles}), flush=True)
'''

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(["git", "hash-object", str(path)], cwd=repo, capture_output=True, text=True, timeout=30, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else ""

def load_source(path: Path):
    spec = importlib.util.spec_from_file_location("loom_stretch002_frozen", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Stretch 002 source")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source_path = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"
    observed_blob = git_blob(source_path, repo)

    print("LOOM Stretch 003 — Two-Layer Repeated Bounded Residency")
    print(f"Stretch 002 source blob: {observed_blob}")
    if observed_blob != SOURCE_002_BLOB:
        print(f"Source provenance: FAIL expected {SOURCE_002_BLOB}", file=sys.stderr)
        return 2
    print("Source provenance: PASS")

    try:
        s2 = load_source(source_path)
    except Exception as exc:
        print(f"Source import: FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    weight = mlx_root / "models" / "Qwen3-8B-3bit" / "model.safetensors"
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "two-layer-bounded-residency-003" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    names_path = run_dir / "selected-layer-names.json"
    state_path = run_dir / "child-state.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary = {
        "experiment": "Stretch 003 — Two-Layer Repeated Bounded Residency",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "probe_layers": PROBE_LAYERS,
        "same_mlx_process": True,
        "model_construction": False,
        "token_generation": False,
        "network_download": False,
        "source_002_blob": observed_blob,
        "disk_before": s2.disk_snapshot(repo),
    }
    telemetry = []

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = s2.disk_snapshot(repo)
        summary["telemetry"] = s2.summarize_telemetry(telemetry)
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        for c in summary.get("cycles", []):
            print(f"Layer {c['layer']}: pre={c['pre_eval_active_delta']} B post={c['post_eval_active_delta']} B clear={c['post_clear_active_delta']} B cache={c['post_clear_cache_delta']} B eval={c['eval_wall_seconds']} s")
        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")
        print(f"Peak observed swap: {summary['telemetry'].get('peak_swap_used_mb')} MB")
        print(f"Peak child RSS: {summary['telemetry'].get('peak_child_rss_mb')} MB")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("Same MLX process: YES")
    print("Full model construction: NONE")
    print("Token generation: NONE")
    print("Network/download: NONE")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if not venv_py.is_file() or not weight.is_file():
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required frozen venv/model weight missing"
        return finish(2)

    versions_result = s2.run([str(venv_py), "-c", "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))"], cwd=repo, timeout=30)
    try:
        versions = json.loads(versions_result.get("stdout", "").strip())
    except Exception:
        versions = {}
    if versions != s2.EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {versions!r}"
        return finish(2)
    print(f"Version lock: PASS {versions}")

    names_map = {}
    for layer_id in PROBE_LAYERS:
        try:
            names, byte_count = s2.selected_layer_from_header(weight, layer_id)
        except Exception as exc:
            summary["classification"] = "PREFLIGHT_FAIL"
            summary["failure_reason"] = f"layer {layer_id} header recovery failed: {type(exc).__name__}: {exc}"
            return finish(2)
        if len(names) != EXPECTED_LAYER_TENSORS or byte_count != EXPECTED_LAYER_BYTES:
            summary["classification"] = "PREFLIGHT_FAIL"
            summary["failure_reason"] = f"layer {layer_id} provenance mismatch: tensors={len(names)} bytes={byte_count}"
            return finish(2)
        names_map[str(layer_id)] = names
        print(f"Layer provenance: PASS layer={layer_id} tensors={len(names)} bytes={byte_count}")
    names_path.write_text(json.dumps(names_map, indent=2) + "\n", encoding="utf-8")

    for index in range(s2.HOST_GATE_SAMPLES):
        sample = s2.system_sample(); sample["phase"] = "host_gate"; telemetry.append(sample)
        free, swap = sample.get("memory_free_percent"), sample.get("swap_used_mb")
        print(f"Host sample {index + 1}/{s2.HOST_GATE_SAMPLES}: free={free}% swap={swap} MB")
        if free is None or swap is None:
            summary["classification"] = "TELEMETRY_FAIL"; summary["failure_reason"] = "required host telemetry unavailable"; return finish(3)
        if free < s2.HOST_GATE_FREE_PERCENT or swap > s2.MAX_SWAP_MB:
            summary["classification"] = "HOST_STATE_NOT_READY"; summary["failure_reason"] = f"host state outside launch gate: free={free}% swap={swap} MB"; return finish(3)
        if index + 1 < s2.HOST_GATE_SAMPLES:
            time.sleep(1.0)
    print("Host-state gate: PASS")

    cmd = [str(venv_py), "-c", CHILD_CODE, str(weight), str(names_path), str(state_path)]
    started = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    guardrail_reason = telemetry_reason = None
    while proc.poll() is None:
        sample = s2.system_sample(proc.pid)
        sample["phase"] = (s2.read_json(state_path) or {}).get("phase", "child_starting")
        sample["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        telemetry.append(sample)
        free, swap = sample.get("memory_free_percent"), sample.get("swap_used_mb")
        if free is None or swap is None:
            telemetry_reason = "required runtime memory/swap telemetry unavailable"; s2.terminate(proc); break
        if free < s2.MIN_FREE_PERCENT:
            guardrail_reason = f"memory free {free}% < {s2.MIN_FREE_PERCENT}%"; s2.terminate(proc); break
        if swap > s2.MAX_SWAP_MB:
            guardrail_reason = f"swap used {swap:.2f} MB > {s2.MAX_SWAP_MB:.0f} MB"; s2.terminate(proc); break
        time.sleep(s2.POLL_SECONDS)

    stdout, stderr = proc.communicate(timeout=10)
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    if telemetry_reason:
        summary["classification"] = "TELEMETRY_FAIL"; summary["failure_reason"] = telemetry_reason; return finish(4)
    if guardrail_reason:
        summary["classification"] = "PARTIAL_RESOURCE_FAIL"; summary["failure_reason"] = guardrail_reason; return finish(5)
    if proc.returncode != 0:
        summary["classification"] = "RUNTIME_FAIL"; summary["failure_reason"] = f"MLX child exited {proc.returncode}; state={s2.read_json(state_path)!r}"; return finish(6)

    payload = None
    for line in (stdout or "").splitlines():
        if line.startswith("LOOM_CHILD_COMPLETE="):
            payload = line.split("=", 1)[1]
    if payload is None:
        summary["classification"] = "RUNTIME_FAIL"; summary["failure_reason"] = "missing child completion payload"; return finish(6)
    child = json.loads(payload)
    if child.get("versions") != s2.EXPECTED_VERSIONS or [x.get("layer") for x in child.get("cycles", [])] != PROBE_LAYERS:
        summary["classification"] = "RUNTIME_FAIL"; summary["failure_reason"] = f"child provenance mismatch: {child!r}"; return finish(6)

    baseline_active = child["baseline"]["active_bytes"]
    baseline_cache = child["baseline"]["cache_bytes"]
    cycles = []
    for cycle in child["cycles"]:
        pre = cycle["pre_eval"]["active_bytes"] - baseline_active
        post = cycle["post_eval"]["active_bytes"] - baseline_active
        clear_active = cycle["post_clear"]["active_bytes"] - baseline_active
        clear_cache = cycle["post_clear"]["cache_bytes"] - baseline_cache
        error = abs(post - EXPECTED_LAYER_BYTES)
        rec = {"layer": cycle["layer"], "pre_eval_active_delta": pre, "post_eval_active_delta": post, "post_clear_active_delta": clear_active, "post_clear_cache_delta": clear_cache, "materialization_error_bytes": error, "eval_wall_seconds": cycle["eval_wall_seconds"]}
        cycles.append(rec)
        if pre > s2.MAX_PRE_EVAL_ACTIVE_DELTA:
            summary["cycles"] = cycles; summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"; summary["failure_reason"] = f"layer {cycle['layer']} pre-eval delta {pre} B"; return finish(7)
        if error > MATERIALIZATION_TOLERANCE:
            summary["cycles"] = cycles; summary["classification"] = "MATERIALIZATION_SIZE_MISMATCH"; summary["failure_reason"] = f"layer {cycle['layer']} post-eval delta {post} B expected {EXPECTED_LAYER_BYTES} B"; return finish(8)
        rec["eviction_pass"] = clear_active <= s2.RECOVERY_TOLERANCE and clear_cache <= s2.RECOVERY_TOLERANCE

    summary["cycles"] = cycles
    passed = all(c["eviction_pass"] for c in cycles)
    summary["repeated_bounded_residency_pass"] = passed
    summary["classification"] = "TWO_LAYER_BOUNDED_RESIDENCY_PASS" if passed else "TWO_LAYER_MATERIALIZATION_PASS_EVICTION_INCONCLUSIVE"
    return finish(0)

if __name__ == "__main__":
    raise SystemExit(main())
