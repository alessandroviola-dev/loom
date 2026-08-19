#!/usr/bin/env python3
"""LOOM Stretch 004 — two-layer streamed micro-forward parity.

Compares an exact two-layer resident Qwen3 micro-forward (layers 18+19
materialized together) with a streamed path that materializes and evicts
one layer at a time in the same MLX process.

No full Qwen model construction, tokenizer, KV cache, or token generation.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SOURCE_002_BLOB = "e7bd6bf4c61b44664c0c8421bf230b938509e4ef"
LAYERS = [18, 19]
EXPECTED_LAYER_BYTES = 84_427_264
EXPECTED_LAYER_TENSORS = 25
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
EXPECTED_QUANTIZATION = {"group_size": 64, "bits": 3}
SEQ_LEN = 4
MIN_FREE_PERCENT = 5
MAX_SWAP_MB = 5600.0
HOST_GATE_FREE_PERCENT = 60
HOST_GATE_SAMPLES = 3
POLL_SECONDS = 0.5

CHILD_CODE = r'''
import gc
import hashlib
import importlib.metadata as md
import inspect
import json
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
from mlx_lm.models import qwen3
from mlx_lm.models.base import create_attention_mask

weight_path = Path(sys.argv[1])
config_path = Path(sys.argv[2])
state_path = Path(sys.argv[3])
layers = json.loads(sys.argv[4])
expected_layer_bytes = int(sys.argv[5])
expected_layer_tensors = int(sys.argv[6])
seq_len = int(sys.argv[7])

config = json.loads(config_path.read_text(encoding="utf-8"))
args = qwen3.ModelArgs.from_dict(config)
quant = config["quantization"]


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


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def selected_local_weights(layer_id):
    all_weights = mx.load(str(weight_path))
    marker = f"model.layers.{layer_id}."
    selected = {}
    for name, value in all_weights.items():
        if name.startswith(marker):
            selected[name[len(marker):]] = value
    del all_weights
    gc.collect()
    if len(selected) != expected_layer_tensors:
        raise RuntimeError(
            f"layer {layer_id} local tensor count {len(selected)} != {expected_layer_tensors}"
        )
    return selected


def build_block(layer_id):
    selected = selected_local_weights(layer_id)
    block = qwen3.TransformerBlock(args)

    def class_predicate(path, module):
        return hasattr(module, "to_quantized") and f"{path}.scales" in selected

    nn.quantize(
        block,
        group_size=quant["group_size"],
        bits=quant["bits"],
        mode=quant.get("mode", "affine"),
        class_predicate=class_predicate,
    )
    block.load_weights(list(selected.items()), strict=True)
    block.eval()
    return block, selected


def make_input():
    n = seq_len * args.hidden_size
    x = mx.sin(mx.arange(n, dtype=mx.float32) / 97.0)
    x = x.reshape(1, seq_len, args.hidden_size).astype(mx.bfloat16)
    mx.eval(x)
    return x


def source_sha(module):
    return sha256_file(Path(inspect.getfile(module)))


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
    save("api_missing", missing_api=missing_api)
    raise SystemExit(4)

versions = {
    "mlx": md.version("mlx"),
    "mlx-lm": md.version("mlx-lm"),
    "transformers": md.version("transformers"),
}

mx.clear_cache()
gc.collect()
mx.reset_peak_memory()
baseline = save(
    "baseline",
    versions=versions,
    qwen3_source_sha256=source_sha(qwen3),
    config={
        "model_type": config.get("model_type"),
        "hidden_size": config.get("hidden_size"),
        "num_hidden_layers": config.get("num_hidden_layers"),
        "num_attention_heads": config.get("num_attention_heads"),
        "num_key_value_heads": config.get("num_key_value_heads"),
        "head_dim": config.get("head_dim"),
        "quantization": quant,
    },
)

# Resident control: both blocks materialized together.
resident_input = make_input()
resident_mask = create_attention_mask(resident_input, None)
resident_base_active = int(mx.get_active_memory())
block18, w18 = build_block(layers[0])
block19, w19 = build_block(layers[1])
resident_pre_eval_active = int(mx.get_active_memory())
save(
    "resident_pre_eval",
    base_active=resident_base_active,
    pre_eval_active=resident_pre_eval_active,
)

started = time.perf_counter()
mx.eval({"layer18": block18.parameters(), "layer19": block19.parameters()})
resident_materialize_wall = time.perf_counter() - started
resident_post_materialize_active = int(mx.get_active_memory())
save(
    "resident_post_materialize",
    active_bytes=resident_post_materialize_active,
    materialize_wall_seconds=round(resident_materialize_wall, 6),
)

started = time.perf_counter()
resident_out = block18(resident_input, resident_mask, None)
resident_out = block19(resident_out, resident_mask, None)
mx.eval(resident_out)
resident_forward_wall = time.perf_counter() - started
save("resident_forward_complete", forward_wall_seconds=round(resident_forward_wall, 6))

del block18, block19, w18, w19, resident_input
gc.collect()
mx.clear_cache()
gc.collect()
resident_after_clear = int(mx.get_active_memory())
save("resident_weights_cleared", active_bytes=resident_after_clear)

# Streamed path: materialize/evaluate/evict one layer at a time.
stream_input = make_input()
stream_mask = create_attention_mask(stream_input, None)
stream_cycles = []

for layer_id in layers:
    pre_active = int(mx.get_active_memory())
    block, selected = build_block(layer_id)
    pre_eval_active = int(mx.get_active_memory())

    started = time.perf_counter()
    mx.eval(block.parameters())
    materialize_wall = time.perf_counter() - started
    post_materialize_active = int(mx.get_active_memory())

    started = time.perf_counter()
    out = block(stream_input, stream_mask, None)
    mx.eval(out)
    forward_wall = time.perf_counter() - started

    old_input = stream_input
    stream_input = out
    del old_input, block, selected
    gc.collect()
    mx.clear_cache()
    gc.collect()
    post_clear_active = int(mx.get_active_memory())
    post_clear_cache = int(mx.get_cache_memory())

    cycle = {
        "layer_id": layer_id,
        "pre_active_bytes": pre_active,
        "pre_eval_active_bytes": pre_eval_active,
        "post_materialize_active_bytes": post_materialize_active,
        "post_clear_active_bytes": post_clear_active,
        "post_clear_cache_bytes": post_clear_cache,
        "pre_eval_delta_bytes": pre_eval_active - pre_active,
        "materialized_delta_bytes": post_materialize_active - pre_active,
        "post_clear_delta_bytes": post_clear_active - pre_active,
        "materialize_wall_seconds": round(materialize_wall, 6),
        "forward_wall_seconds": round(forward_wall, 6),
    }
    stream_cycles.append(cycle)
    save(f"stream_layer_{layer_id}_complete", cycle=cycle)

stream_out = stream_input
diff = mx.abs(resident_out.astype(mx.float32) - stream_out.astype(mx.float32))
mx.eval(diff)
max_abs_diff = float(mx.max(diff).item())
mean_abs_diff = float(mx.mean(diff).item())
resident_norm = float(mx.max(mx.abs(resident_out.astype(mx.float32))).item())
parity_threshold = 1e-5 + 1e-5 * resident_norm
parity_pass = max_abs_diff <= parity_threshold

final = {
    "versions": versions,
    "baseline": baseline["memory"],
    "resident": {
        "base_active_bytes": resident_base_active,
        "pre_eval_active_bytes": resident_pre_eval_active,
        "post_materialize_active_bytes": resident_post_materialize_active,
        "materialized_delta_bytes": resident_post_materialize_active - resident_base_active,
        "after_clear_active_bytes": resident_after_clear,
        "materialize_wall_seconds": round(resident_materialize_wall, 6),
        "forward_wall_seconds": round(resident_forward_wall, 6),
    },
    "stream_cycles": stream_cycles,
    "parity": {
        "max_abs_diff": max_abs_diff,
        "mean_abs_diff": mean_abs_diff,
        "resident_max_abs": resident_norm,
        "threshold": parity_threshold,
        "pass": parity_pass,
    },
    "final_memory": mem(),
}
print("LOOM_CHILD_COMPLETE=" + json.dumps(final), flush=True)
'''


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("loom_stretch002_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import Stretch 002 helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source002 = repo / "scripts" / "stretch_single_layer_mlx_materialization_002.py"
    observed_blob = git_blob(source002, repo)
    print("LOOM Stretch 004 — Two-Layer Streamed Micro-Forward Parity")
    print(f"Stretch 002 source blob: {observed_blob}")
    if observed_blob != SOURCE_002_BLOB:
        print(f"Source provenance: FAIL expected {SOURCE_002_BLOB}", file=sys.stderr)
        return 2
    print("Source provenance: PASS")

    helpers = load_module(source002)
    mlx_root = repo / "results-local" / "mlx"
    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
    model_dir = mlx_root / "models" / "Qwen3-8B-3bit"
    weight = model_dir / "model.safetensors"
    config_path = model_dir / "config.json"

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "two-layer-micro-forward-parity-004" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = run_dir / "child-state.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"

    summary = {
        "experiment": "Stretch 004 — Two-Layer Streamed Micro-Forward Parity",
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "classification": None,
        "layers": LAYERS,
        "sequence_length": SEQ_LEN,
        "full_model_construction": False,
        "token_generation": False,
        "kv_cache": False,
        "network_download": False,
        "source_002_blob": observed_blob,
        "disk_before": helpers.disk_snapshot(repo),
    }
    telemetry = []

    def finish(code: int) -> int:
        summary["finished_at_utc"] = utc_now()
        summary["disk_after"] = helpers.disk_snapshot(repo)
        summary["telemetry"] = helpers.summarize_telemetry(telemetry)
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Classification: {summary.get('classification')}")
        if summary.get("failure_reason"):
            print(f"Failure reason: {summary['failure_reason']}")
        if summary.get("parity"):
            p = summary["parity"]
            print(
                f"Parity: pass={p.get('pass')} max_abs={p.get('max_abs_diff')} "
                f"mean_abs={p.get('mean_abs_diff')} threshold={p.get('threshold')}"
            )
        if summary.get("resident"):
            r = summary["resident"]
            print(f"Resident two-layer materialized delta: {r.get('materialized_delta_bytes')} B")
        for cycle in summary.get("stream_cycles", []):
            print(
                f"Stream layer {cycle['layer_id']}: pre={cycle['pre_eval_delta_bytes']} B "
                f"materialized={cycle['materialized_delta_bytes']} B "
                f"clear_delta={cycle['post_clear_delta_bytes']} B "
                f"cache={cycle['post_clear_cache_bytes']} B"
            )
        print(f"Minimum observed free memory: {summary['telemetry'].get('min_memory_free_percent')}%")
        print(f"Peak observed swap: {summary['telemetry'].get('peak_swap_used_mb')} MB")
        print(f"Peak child RSS: {summary['telemetry'].get('peak_child_rss_mb')} MB")
        print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    print("Full model construction: NONE")
    print("Tokenizer/KV/token generation: NONE")
    print("Resident control: layers 18+19 only")
    print("Streamed path: layer 18 -> evict -> layer 19 -> evict")
    print(f"Disk free before: {summary['disk_before']['free_gib']:.3f} GiB")

    if platform.system() != "Darwin" or platform.machine() != "arm64":
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"requires Darwin arm64, got {platform.system()} {platform.machine()}"
        return finish(2)

    if not source002.is_file() or not venv_py.is_file() or not weight.is_file() or not config_path.is_file():
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = "required frozen helper/venv/model/config path missing"
        return finish(2)

    versions_result = helpers.run(
        [
            str(venv_py),
            "-c",
            "import importlib.metadata as m,json; print(json.dumps({'mlx':m.version('mlx'),'mlx-lm':m.version('mlx-lm'),'transformers':m.version('transformers')}))",
        ],
        cwd=repo,
        timeout=30,
    )
    try:
        versions = json.loads(versions_result.get("stdout", "").strip())
    except Exception:
        versions = {}
    summary["versions"] = versions
    if versions != EXPECTED_VERSIONS:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"version lock mismatch: {versions!r}"
        return finish(2)
    print(f"Version lock: PASS {versions}")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = f"cannot parse config.json: {type(exc).__name__}: {exc}"
        return finish(2)

    expected_config = {
        "model_type": "qwen3",
        "hidden_size": 4096,
        "num_hidden_layers": 36,
        "num_attention_heads": 32,
        "num_key_value_heads": 8,
        "head_dim": 128,
    }
    observed_config = {k: config.get(k) for k in expected_config}
    summary["model_config"] = observed_config
    summary["quantization"] = config.get("quantization")
    if observed_config != expected_config or config.get("quantization") != EXPECTED_QUANTIZATION:
        summary["classification"] = "PREFLIGHT_FAIL"
        summary["failure_reason"] = (
            f"model config/quantization mismatch: config={observed_config!r} "
            f"quantization={config.get('quantization')!r}"
        )
        return finish(2)
    print(f"Model config/quantization: PASS {observed_config} quantization={EXPECTED_QUANTIZATION}")

    for layer_id in LAYERS:
        try:
            names, selected_bytes = helpers.selected_layer_from_header(weight, layer_id)
        except Exception as exc:
            summary["classification"] = "PREFLIGHT_FAIL"
            summary["failure_reason"] = f"layer {layer_id} header recovery failed: {type(exc).__name__}: {exc}"
            return finish(2)
        if len(names) != EXPECTED_LAYER_TENSORS or selected_bytes != EXPECTED_LAYER_BYTES:
            summary["classification"] = "PREFLIGHT_FAIL"
            summary["failure_reason"] = (
                f"layer {layer_id} provenance mismatch: tensors={len(names)} bytes={selected_bytes}"
            )
            return finish(2)
        print(f"Layer provenance: PASS layer={layer_id} tensors={len(names)} bytes={selected_bytes}")

    for index in range(HOST_GATE_SAMPLES):
        sample = helpers.system_sample()
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

    cmd = [
        str(venv_py),
        "-c",
        CHILD_CODE,
        str(weight),
        str(config_path),
        str(state_path),
        json.dumps(LAYERS),
        str(EXPECTED_LAYER_BYTES),
        str(EXPECTED_LAYER_TENSORS),
        str(SEQ_LEN),
    ]
    started = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    guardrail_reason = None
    telemetry_reason = None

    while proc.poll() is None:
        sample = helpers.system_sample(proc.pid)
        state = helpers.read_json(state_path) or {}
        sample["phase"] = state.get("phase", "child_starting")
        sample["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        telemetry.append(sample)
        free = sample.get("memory_free_percent")
        swap = sample.get("swap_used_mb")
        if free is None or swap is None:
            telemetry_reason = "required runtime memory/swap telemetry unavailable"
            helpers.terminate(proc)
            break
        if free < MIN_FREE_PERCENT:
            guardrail_reason = f"memory free {free}% < {MIN_FREE_PERCENT}%"
            helpers.terminate(proc)
            break
        if swap > MAX_SWAP_MB:
            guardrail_reason = f"swap used {swap:.2f} MB > {MAX_SWAP_MB:.0f} MB"
            helpers.terminate(proc)
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
        summary["classification"] = "RUNTIME_FAIL"
        summary["failure_reason"] = (
            f"MLX child exited {proc.returncode}; last_state={helpers.read_json(state_path)!r}"
        )
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
        summary["failure_reason"] = f"cannot parse child payload: {exc}"
        return finish(6)

    summary["resident"] = child["resident"]
    summary["stream_cycles"] = child["stream_cycles"]
    summary["parity"] = child["parity"]
    summary["child_baseline"] = child["baseline"]
    summary["child_final_memory"] = child["final_memory"]

    resident_delta = int(child["resident"]["materialized_delta_bytes"])
    expected_resident = 2 * EXPECTED_LAYER_BYTES
    if abs(resident_delta - expected_resident) > 2 * 1024 * 1024:
        summary["classification"] = "RESIDENT_CONTROL_SIZE_MISMATCH"
        summary["failure_reason"] = (
            f"resident materialized delta {resident_delta} B not near expected {expected_resident} B"
        )
        return finish(7)

    for cycle in child["stream_cycles"]:
        if cycle["pre_eval_delta_bytes"] > 32 * 1024 * 1024:
            summary["classification"] = "EAGER_FULL_FILE_LOAD_SUSPECTED"
            summary["failure_reason"] = (
                f"layer {cycle['layer_id']} pre-eval delta {cycle['pre_eval_delta_bytes']} B"
            )
            return finish(7)
        if abs(cycle["materialized_delta_bytes"] - EXPECTED_LAYER_BYTES) > 1 * 1024 * 1024:
            summary["classification"] = "STREAMED_MATERIALIZATION_SIZE_MISMATCH"
            summary["failure_reason"] = (
                f"layer {cycle['layer_id']} materialized delta "
                f"{cycle['materialized_delta_bytes']} B"
            )
            return finish(7)
        if abs(cycle["post_clear_delta_bytes"]) > 4 * 1024 * 1024:
            summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
            summary["failure_reason"] = (
                f"layer {cycle['layer_id']} post-clear delta "
                f"{cycle['post_clear_delta_bytes']} B exceeds 4 MiB"
            )
            return finish(7)
        if cycle["post_clear_cache_bytes"] > 4 * 1024 * 1024:
            summary["classification"] = "STREAMED_EVICTION_INCONCLUSIVE"
            summary["failure_reason"] = (
                f"layer {cycle['layer_id']} post-clear cache "
                f"{cycle['post_clear_cache_bytes']} B exceeds 4 MiB"
            )
            return finish(7)

    if not child["parity"]["pass"]:
        summary["classification"] = "NUMERICAL_PARITY_FAIL"
        summary["failure_reason"] = (
            f"max abs diff {child['parity']['max_abs_diff']} > "
            f"threshold {child['parity']['threshold']}"
        )
        return finish(8)

    summary["classification"] = "TWO_LAYER_STREAMED_FORWARD_PARITY_PASS"
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
