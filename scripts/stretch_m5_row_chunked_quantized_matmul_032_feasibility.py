#!/usr/bin/env python3
"""Stretch 032 diagnostic-only M5 row-chunked quantized-matmul feasibility.

This is not a Stretch 032 scientific constituent and cannot create an ABBA.
It benchmarks one real Qwen3-8B 3-bit layer's packed affine weights with M=5
BF16 inputs: one qmatmul versus row chunks 2+2+1 plus concatenate.
"""
from __future__ import annotations

import hashlib
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_CHILD_PYTHON = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
MODEL_DIR = "results-local/mlx/models/Qwen3-8B-3bit"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
EXPECTED_VERSIONS = {
    "mlx": "0.31.2",
    "mlx-metal": "0.31.2",
    "mlx-lm": "0.31.3",
    "transformers": "5.12.1",
}
EXPECTED_CONFIG = {
    "model_type": "qwen3",
    "hidden_size": 4096,
    "intermediate_size": 12288,
    "num_hidden_layers": 36,
    "num_attention_heads": 32,
    "num_key_value_heads": 8,
    "head_dim": 128,
}
BITS = 3
GROUP_SIZE = 64
MODE = "affine"
M = 5
ROW_CHUNKS = (2, 2, 1)
LAYER_ID = 0
WARMUP_ITERATIONS = 40
ABBA_CYCLES = 60
PROJECTIONS = {
    "q_proj": ("model.layers.0.self_attn.q_proj", 4096, 4096),
    "k_proj": ("model.layers.0.self_attn.k_proj", 4096, 1024),
    "v_proj": ("model.layers.0.self_attn.v_proj", 4096, 1024),
    "o_proj": ("model.layers.0.self_attn.o_proj", 4096, 4096),
    "gate_proj": ("model.layers.0.mlp.gate_proj", 4096, 12288),
    "up_proj": ("model.layers.0.mlp.up_proj", 4096, 12288),
    "down_proj": ("model.layers.0.mlp.down_proj", 12288, 4096),
}
# Diagnostic attribution only, from Stretch 028's explicitly perturbed profile.
STRETCH_028_COMPONENT_SECONDS = {
    "attention": 0.09857969474978745,
    "gate_proj": 0.0965807989705354,
    "up_proj": 0.09931493003387004,
    "down_proj": 0.09428692991302039,
    "transformer_compute": 0.44969600122810033,
}
STRETCH_031_M5_MEDIAN_BLOCK_SECONDS = 0.3487060


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    """Inclusive percentile, stable for the fixed 120-sample side distribution."""
    if not values:
        raise ValueError("cannot calculate percentile for no samples")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def distribution(values: list[float]) -> dict:
    return {
        "samples": len(values),
        "median_seconds": statistics.median(values),
        "mean_seconds": statistics.fmean(values),
        "p25_seconds": percentile(values, 0.25),
        "p75_seconds": percentile(values, 0.75),
        "minimum_seconds": min(values),
        "maximum_seconds": max(values),
        "total_synchronized_wall_seconds": sum(values),
    }


def child_main(model_dir: Path, summary_path: Path) -> int:
    import gc
    import importlib.metadata as metadata
    import os

    import mlx.core as mx
    from safetensors import safe_open
    from mlx_lm.models import qwen3

    # The parent passes absolute paths; derive the repository from the frozen
    # model directory, not from (and never by dereferencing) the venv launcher.
    repo = model_dir.parents[3]
    expected_prefix = str(repo / EXPECTED_PREFIX)
    observed_versions = {name: metadata.version(name) for name in EXPECTED_VERSIONS}
    provenance = {
        "child_python_executable": sys.executable,
        "sys_prefix": sys.prefix,
        "expected_prefix": expected_prefix,
        "runtime_versions": observed_versions,
        "pid": os.getpid(),
    }
    if sys.prefix != expected_prefix or observed_versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"canonical runtime provenance mismatch: {provenance}")

    config_path = model_dir / "config.json"
    weight_path = model_dir / "model.safetensors"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    observed_config = {name: config.get(name) for name in EXPECTED_CONFIG}
    if observed_config != EXPECTED_CONFIG:
        raise RuntimeError(f"config mismatch: {observed_config}")
    quantization = config.get("quantization")
    if quantization != {"group_size": GROUP_SIZE, "bits": BITS}:
        raise RuntimeError(f"quantization mismatch: {quantization}")

    qwen_source = Path(qwen3.__file__)
    qwen_source_text = qwen_source.read_text(encoding="utf-8")
    required_qwen_fragments = [
        "self.q_proj = nn.Linear(dim, n_heads * head_dim, bias=False)",
        "self.k_proj = nn.Linear(dim, n_kv_heads * head_dim, bias=False)",
        "self.v_proj = nn.Linear(dim, n_kv_heads * head_dim, bias=False)",
        "self.o_proj = nn.Linear(n_heads * head_dim, dim, bias=False)",
        "self.gate_proj = nn.Linear(dim, hidden_dim, bias=False)",
        "self.up_proj = nn.Linear(dim, hidden_dim, bias=False)",
        "self.down_proj = nn.Linear(hidden_dim, dim, bias=False)",
    ]
    missing_qwen_fragments = [x for x in required_qwen_fragments if x not in qwen_source_text]
    if missing_qwen_fragments:
        raise RuntimeError(f"Qwen3 source contract mismatch: {missing_qwen_fragments}")

    headers: dict[str, dict] = {}
    with safe_open(str(weight_path), framework="np") as handle:
        for name, (prefix, k, n) in PROJECTIONS.items():
            header = {}
            for field in ("weight", "scales", "biases"):
                key = f"{prefix}.{field}"
                if key not in handle.keys():
                    raise RuntimeError(f"missing real tensor {key}")
                tensor_slice = handle.get_slice(key)
                header[field] = {
                    "key": key,
                    "shape": list(tensor_slice.get_shape()),
                    "dtype": str(tensor_slice.get_dtype()),
                }
            expected_weight = [n, (k * BITS) // 32]
            expected_quant = [n, k // GROUP_SIZE]
            if header["weight"]["shape"] != expected_weight:
                raise RuntimeError(f"{name} packed weight shape {header['weight']['shape']} != {expected_weight}")
            if header["scales"]["shape"] != expected_quant or header["biases"]["shape"] != expected_quant:
                raise RuntimeError(f"{name} quant parameter shape mismatch: {header}")
            headers[name] = {
                "input_k": k,
                "output_n": n,
                "output_geometry": [1, M, n],
                "packed_weight_geometry": expected_weight,
                "quant_parameter_geometry": expected_quant,
                "tensors": header,
            }

    # mx.load exposes the safetensors array map lazily. Only the 21 selected
    # layer-0 qmatmul payload tensors are retained and materialized; no model
    # module and no other layer's parameters are constructed.
    all_weights = mx.load(str(weight_path))
    selected: dict[str, tuple] = {}
    for name, (prefix, _k, _n) in PROJECTIONS.items():
        selected[name] = tuple(all_weights[f"{prefix}.{field}"] for field in ("weight", "scales", "biases"))
    del all_weights
    gc.collect()
    mx.eval(*(value for tensors in selected.values() for value in tensors))
    setup_active_memory = int(mx.get_active_memory())

    probes: dict[int, object] = {}
    for _name, (_prefix, k, _n) in PROJECTIONS.items():
        if k not in probes:
            total = M * k
            probe = (
                ((mx.arange(total, dtype=mx.int32) % 257).astype(mx.float32) - 128.0) / 64.0
            ).reshape(1, M, k).astype(mx.bfloat16)
            mx.eval(probe)
            probes[k] = probe

    def monolithic(x, tensors):
        weight, scales, biases = tensors
        return mx.quantized_matmul(
            x, weight, scales, biases, transpose=True,
            group_size=GROUP_SIZE, bits=BITS, mode=MODE,
        )

    def chunked(x, tensors):
        start = 0
        outputs = []
        for rows in ROW_CHUNKS:
            outputs.append(monolithic(x[:, start:start + rows, :], tensors))
            start += rows
        return mx.concatenate(outputs, axis=1)

    projection_results: dict[str, dict] = {}
    for name, (_prefix, k, _n) in PROJECTIONS.items():
        tensors = selected[name]
        x = probes[k]

        # Exactness is evaluated before performance. This uses the actual M=5
        # payload and the same BF16 values; rows are never regenerated.
        mono_output = monolithic(x, tensors)
        chunk_output = chunked(x, tensors)
        mx.eval(mono_output, chunk_output)
        diff = mx.abs(mono_output.astype(mx.float32) - chunk_output.astype(mx.float32))
        equal = mx.equal(mono_output, chunk_output)
        mx.eval(diff, equal)
        exactness = {
            "top_level_shape_equal": tuple(mono_output.shape) == tuple(chunk_output.shape),
            "monolithic_shape": list(mono_output.shape),
            "chunked_shape": list(chunk_output.shape),
            "exact_equal": bool(mx.all(equal).item()),
            "max_abs_diff": float(mx.max(diff).item()),
            "mean_abs_diff": float(mx.mean(diff).item()),
        }
        if not exactness["top_level_shape_equal"]:
            raise RuntimeError(f"{name} chunked shape mismatch: {exactness}")

        # Warm both paths before any timed sample. No cache clear/purge happens
        # between sides or projections. ABBA cycles interleave every sample.
        for _ in range(WARMUP_ITERATIONS):
            mx.eval(monolithic(x, tensors))
            mx.eval(chunked(x, tensors))
        mx.reset_peak_memory()
        mono_times: list[float] = []
        chunk_times: list[float] = []
        for _ in range(ABBA_CYCLES):
            for side, sink in (("monolithic", mono_times), ("chunked", chunk_times), ("chunked", chunk_times), ("monolithic", mono_times)):
                started = time.perf_counter()
                out = monolithic(x, tensors) if side == "monolithic" else chunked(x, tensors)
                mx.eval(out)
                sink.append(time.perf_counter() - started)
        mono_stats = distribution(mono_times)
        chunk_stats = distribution(chunk_times)
        ratio = chunk_stats["median_seconds"] / mono_stats["median_seconds"]
        projection_results[name] = {
            "geometry": headers[name],
            "exactness": exactness,
            "warmup_iterations_per_side": WARMUP_ITERATIONS,
            "timing_order": "(monolithic, chunked, chunked, monolithic) repeated",
            "abba_cycles": ABBA_CYCLES,
            "monolithic": mono_stats,
            "chunked_2_2_1": chunk_stats,
            "chunked_over_monolithic_median_ratio": ratio,
            "median_savings_fraction": 1.0 - ratio,
            "peak_memory_bytes_after_warmup": int(mx.get_peak_memory()),
            "active_memory_bytes_after_timing": int(mx.get_active_memory()),
        }
        del mono_output, chunk_output, diff, equal

    # Apply known Stretch 028 component durations only to their matching MLP
    # projections. Attention's aggregate includes non-projection work, so it is
    # reported as an explicit optimistic bound, not a primary estimate.
    mlp_savings_seconds = sum(
        STRETCH_028_COMPONENT_SECONDS[name] * projection_results[name]["median_savings_fraction"]
        for name in ("gate_proj", "up_proj", "down_proj")
    )
    attention_ratios = [projection_results[name]["chunked_over_monolithic_median_ratio"] for name in ("q_proj", "k_proj", "v_proj", "o_proj")]
    attention_mean_savings_fraction = 1.0 - statistics.fmean(attention_ratios)
    attention_optimistic_savings_seconds = STRETCH_028_COMPONENT_SECONDS["attention"] * attention_mean_savings_fraction
    weighted_estimate = {
        "method": "Stretch 028 diagnostic component weighting; not a scientific throughput result",
        "mlp_only_estimated_savings_seconds_per_block": mlp_savings_seconds,
        "mlp_only_fraction_of_stretch031_m5_median_block": mlp_savings_seconds / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS,
        "mlp_only_fraction_of_stretch028_transformer_compute": mlp_savings_seconds / STRETCH_028_COMPONENT_SECONDS["transformer_compute"],
        "attention_projection_optimistic_bound_savings_seconds_per_block": attention_optimistic_savings_seconds,
        "attention_bound_note": "Applies mean q/k/v/o microbench saving to total Stretch 028 attention time, which includes non-qmatmul work; it is an upper bound, not an estimate.",
        "mlp_plus_attention_bound_fraction_of_stretch031_m5_median_block": (
            mlp_savings_seconds + attention_optimistic_savings_seconds
        ) / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS,
    }
    all_exact = all(result["exactness"]["exact_equal"] for result in projection_results.values())
    # A positive 5% MLP-only estimate is deliberately required: an attention
    # upper bound cannot turn a weak result into GO.
    go = all_exact and weighted_estimate["mlp_only_fraction_of_stretch031_m5_median_block"] >= 0.05
    decision = {
        "classification": "STRETCH_032_ROW_CHUNKED_FEASIBILITY_GO" if go else "STRETCH_032_ROW_CHUNKED_FEASIBILITY_NO_GO",
        "go": go,
        "criteria": {
            "all_projection_outputs_exact": all_exact,
            "mlp_only_estimated_end_to_end_savings_at_least_5_percent": weighted_estimate["mlp_only_fraction_of_stretch031_m5_median_block"] >= 0.05,
        },
        "note": "Diagnostic feasibility only. It neither changes scientific gates nor authorizes a Stretch 032 ABBA.",
    }
    final = {
        "experiment": "Stretch 032 M5 row-chunked quantized-matmul feasibility",
        "classification": decision["classification"],
        "diagnostic_only": True,
        "scientific_abba_started": False,
        "timestamp": utc_now(),
        "runtime_provenance": provenance,
        "model": {
            "model_dir": str(model_dir),
            "model_config": observed_config,
            "quantization": {"bits": BITS, "group_size": GROUP_SIZE, "mode": MODE},
            "layer": LAYER_ID,
            "weight_sha256": sha256_file(weight_path),
            "qwen3_source_path": str(qwen_source),
            "qwen3_source_sha256": sha256_file(qwen_source),
        },
        "methodology": {
            "m": M,
            "input_dtype": "bfloat16",
            "row_chunks": list(ROW_CHUNKS),
            "control": "one mx.quantized_matmul over all M=5 rows",
            "treatment": "three mx.quantized_matmul calls over 2+2+1 rows then mx.concatenate(axis=1)",
            "real_weight_scope": "layer-0 payload only; no model module/full-model load",
            "warmup_excluded": True,
            "deliberate_cache_purge": False,
            "timed_samples_per_side_per_projection": ABBA_CYCLES * 2,
        },
        "setup_active_memory_bytes": setup_active_memory,
        "projections": projection_results,
        "weighted_estimate": weighted_estimate,
        "decision": decision,
    }
    summary_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Classification: {decision['classification']}")
    for name, result in projection_results.items():
        print(
            f"{name}: mono={result['monolithic']['median_seconds'] * 1000:.4f} ms "
            f"chunked={result['chunked_2_2_1']['median_seconds'] * 1000:.4f} ms "
            f"ratio={result['chunked_over_monolithic_median_ratio']:.6f} "
            f"exact={result['exactness']['exact_equal']}"
        )
    print(f"Summary: {summary_path}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child_main(Path(sys.argv[2]), Path(sys.argv[3]))

    repo = Path(__file__).resolve().parents[1]
    child_python = repo / CANONICAL_CHILD_PYTHON  # Do not resolve this venv launcher.
    model_dir = repo / MODEL_DIR
    required = [child_python, model_dir / "model.safetensors", model_dir / "config.json"]
    if not all(path.is_file() for path in required):
        raise RuntimeError(f"missing required feasibility input: {required}")
    if not child_python.is_symlink():
        raise RuntimeError(f"canonical child launcher unexpectedly is not a venv symlink: {child_python}")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local/stretch/m5-row-chunked-quantized-matmul-032-feasibility" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    child_summary = run_dir / "child-summary.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    parent_summary = run_dir / "summary.json"
    command = [str(child_python), str(Path(__file__).resolve()), "--child", str(model_dir), str(child_summary)]
    started = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        proc = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr, check=False)
    child_stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    child_stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    if proc.returncode != 0 or not child_summary.is_file():
        raise RuntimeError(
            f"feasibility child failed returncode={proc.returncode}; stdout={stdout_path}; stderr={stderr_path}"
        )
    child = json.loads(child_summary.read_text(encoding="utf-8"))
    parent = {
        "experiment": "Stretch 032 M5 row-chunked quantized-matmul feasibility",
        "classification": child["classification"],
        "diagnostic_only": True,
        "scientific_abba_started": False,
        "canonical_launcher_literal": str(child_python),
        "command": command,
        "child_summary": str(child_summary),
        "child_stdout": str(stdout_path),
        "child_stderr": str(stderr_path),
        "child_wall_seconds": time.perf_counter() - started,
        "child": child,
    }
    parent_summary.write_text(json.dumps(parent, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(child_stdout, end="" if child_stdout.endswith("\n") else "\n")
    print(f"Parent summary: {parent_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
