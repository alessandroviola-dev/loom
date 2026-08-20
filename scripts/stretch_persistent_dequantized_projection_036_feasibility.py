#!/usr/bin/env python3
"""Stretch 036 diagnostic-only persistent BF16 projection-cache feasibility.

This does not alter model code, quantization, global MLX, or launch a
full-model ABBA.  It compares a canonical M5 affine qmatmul with dense BF16
matmul using a persistent layer-0 weight produced only by mx.dequantize of the
real packed checkpoint payload.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_CHILD_PYTHON = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
MODEL_DIR = "results-local/mlx/models/Qwen3-8B-3bit"
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
BITS, GROUP_SIZE, MODE, M, LAYER_ID = 3, 64, "affine", 5, 0
WARMUP_ITERATIONS = 40
ABBA_CYCLES = 60  # Q -> BF16 -> BF16 -> Q: 120 synchronized samples / side.
MODEL_MEMORY_MIB = 8192.0
STRETCH_031_M5_MEDIAN_BLOCK_SECONDS = 0.3487060
STRETCH_031_M5_TOKENS_PER_SECOND = 14.3307127237
STRETCH_031_MINIMUM_FREE_PERCENT = 18.0
STRETCH_031_HARD_ABORT_FREE_PERCENT = 5.0
PROJECTIONS = {
    "q_proj": ("model.layers.0.self_attn.q_proj", 4096, 4096),
    "k_proj": ("model.layers.0.self_attn.k_proj", 4096, 1024),
    "v_proj": ("model.layers.0.self_attn.v_proj", 4096, 1024),
    "o_proj": ("model.layers.0.self_attn.o_proj", 4096, 4096),
    "gate_proj": ("model.layers.0.mlp.gate_proj", 4096, 12288),
    "up_proj": ("model.layers.0.mlp.up_proj", 4096, 12288),
    "down_proj": ("model.layers.0.mlp.down_proj", 12288, 4096),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("empty timing distribution")
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


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


def mib(byte_count: int | float) -> float:
    return float(byte_count) / (1024.0 * 1024.0)


def child_main(model_dir: Path, summary_path: Path) -> int:
    import os

    import mlx.core as mx
    from safetensors import safe_open

    repo = model_dir.parents[3]
    expected_prefix = str(repo / EXPECTED_PREFIX)
    observed_versions = {name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS}
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
    if config.get("quantization") != {"group_size": GROUP_SIZE, "bits": BITS}:
        raise RuntimeError(f"quantization mismatch: {config.get('quantization')}")

    # Prove the tensor shapes/dtypes directly from the actual safetensors
    # checkpoint before materializing only the 21 permitted layer-0 payloads.
    headers: dict[str, dict] = {}
    with safe_open(str(weight_path), framework="np") as handle:
        keys = set(handle.keys())
        for name, (prefix, k, n) in PROJECTIONS.items():
            tensors: dict[str, dict] = {}
            for field in ("weight", "scales", "biases"):
                key = f"{prefix}.{field}"
                if key not in keys:
                    raise RuntimeError(f"missing real checkpoint tensor {key}")
                view = handle.get_slice(key)
                tensors[field] = {
                    "key": key,
                    "shape": list(view.get_shape()),
                    "dtype": str(view.get_dtype()),
                }
            expected_packed, expected_quant = [n, k * BITS // 32], [n, k // GROUP_SIZE]
            if tensors["weight"]["shape"] != expected_packed or tensors["weight"]["dtype"] != "U32":
                raise RuntimeError(f"unexpected packed tensor for {name}: {tensors['weight']}")
            for field in ("scales", "biases"):
                if tensors[field]["shape"] != expected_quant or tensors[field]["dtype"] != "BF16":
                    raise RuntimeError(f"unexpected affine tensor for {name}/{field}: {tensors[field]}")
            headers[name] = {"K": k, "N": n, "tensors": tensors}

    all_weights = mx.load(str(weight_path))
    payloads = {
        name: tuple(all_weights[f"{prefix}.{field}"] for field in ("weight", "scales", "biases"))
        for name, (prefix, _k, _n) in PROJECTIONS.items()
    }
    del all_weights
    gc.collect()
    mx.eval(*(array for triple in payloads.values() for array in triple))
    setup_active_memory = int(mx.get_active_memory())

    # Three deterministic BF16 probes per K. A true intermediate activation is
    # deliberately not recovered: doing so economically would require a model
    # traversal and would expand this isolated projection feasibility scope.
    probes: dict[int, list[tuple[str, object]]] = {}
    for k in sorted({item[1] for item in PROJECTIONS.values()}):
        arange = (((mx.arange(M * k, dtype=mx.int32) % 257).astype(mx.float32) - 128.0) / 64.0)
        x_pattern = arange.reshape(1, M, k).astype(mx.bfloat16)
        probe_set: list[tuple[str, object]] = [("pattern_mod257", x_pattern)]
        for seed in (1103 + k, 2207 + k):
            mx.random.seed(seed)
            probe_set.append((f"normal_seed_{seed}", mx.random.normal((1, M, k)).astype(mx.bfloat16)))
        mx.eval(*(array for _label, array in probe_set))
        probes[k] = probe_set

    def qmatmul(x, tensors):
        packed, scales, biases = tensors
        return mx.quantized_matmul(
            x, packed, scales, biases, transpose=True,
            group_size=GROUP_SIZE, bits=BITS, mode=MODE,
        )

    def numerical_case(x, tensors, persistent_weight) -> dict:
        y_q = qmatmul(x, tensors)
        y_d = x @ persistent_weight.T
        mx.eval(y_q, y_d)
        delta = mx.abs(y_q.astype(mx.float32) - y_d.astype(mx.float32))
        equal = mx.equal(y_q, y_d)
        magnitude = mx.abs(y_q.astype(mx.float32))
        # Relative max magnitude is stable even for outputs that contain zero.
        mx.eval(delta, equal, magnitude)
        max_abs = float(mx.max(delta).item())
        max_magnitude = float(mx.max(magnitude).item())
        return {
            "input_shape": list(x.shape),
            "input_dtype": str(x.dtype),
            "shape_equal": tuple(y_q.shape) == tuple(y_d.shape),
            "quantized_shape": list(y_q.shape),
            "dense_shape": list(y_d.shape),
            "exact_equal": bool(mx.all(equal).item()),
            "max_abs_diff": max_abs,
            "mean_abs_diff": float(mx.mean(delta).item()),
            "quantized_output_dtype": str(y_q.dtype),
            "dense_output_dtype": str(y_d.dtype),
            "max_quantized_magnitude": max_magnitude,
            "max_abs_over_max_quantized_magnitude": max_abs / max_magnitude if max_magnitude else None,
        }

    projection_results: dict[str, dict] = {}
    for name, (_prefix, k, n) in PROJECTIONS.items():
        packed, scales, biases = payloads[name]
        source_bytes = {
            "packed_weight_bytes": int(packed.nbytes),
            "scales_bytes": int(scales.nbytes),
            "biases_bytes": int(biases.nbytes),
        }
        source_bytes["canonical_quantized_total_bytes"] = sum(source_bytes.values())

        # Exactly the mandated path: W originates only from these packed real
        # checkpoint arrays; no original floating-point model tensor is loaded.
        active_before_dequant = int(mx.get_active_memory())
        mx.reset_peak_memory()
        started = time.perf_counter()
        persistent_weight = mx.dequantize(
            packed, scales, biases, group_size=GROUP_SIZE, bits=BITS
        )
        dequantize_wall = time.perf_counter() - started
        started = time.perf_counter()
        if persistent_weight.dtype != mx.bfloat16:
            persistent_weight = persistent_weight.astype(mx.bfloat16)
        mx.eval(persistent_weight)
        materialization_wall = time.perf_counter() - started
        active_after_dequant = int(mx.get_active_memory())
        peak_after_dequant = int(mx.get_peak_memory())
        if tuple(persistent_weight.shape) != (n, k) or persistent_weight.dtype != mx.bfloat16:
            raise RuntimeError(
                f"{name} dequantization contract failed: shape={persistent_weight.shape} dtype={persistent_weight.dtype}"
            )
        persistent_bytes = int(persistent_weight.nbytes)
        memory = {
            **source_bytes,
            "persistent_bf16_dequantized_bytes": persistent_bytes,
            "incremental_bytes_if_both_quantized_source_and_bf16_cache_resident": persistent_bytes,
            "resident_bytes_if_both_remain": source_bytes["canonical_quantized_total_bytes"] + persistent_bytes,
            "net_incremental_bytes_if_future_runtime_discards_quantized_source": persistent_bytes - source_bytes["canonical_quantized_total_bytes"],
            "resident_bytes_if_future_runtime_discards_quantized_source": persistent_bytes,
        }
        one_time = {
            "dequantize_call_wall_seconds": dequantize_wall,
            "mx_eval_materialization_wall_seconds": materialization_wall,
            "one_time_total_wall_seconds": dequantize_wall + materialization_wall,
            "active_memory_before_bytes": active_before_dequant,
            "active_memory_after_bytes": active_after_dequant,
            "active_memory_delta_bytes": active_after_dequant - active_before_dequant,
            "peak_memory_bytes": peak_after_dequant,
            "peak_minus_active_before_bytes": peak_after_dequant - active_before_dequant,
            "result_dtype": str(persistent_weight.dtype),
            "result_shape": list(persistent_weight.shape),
        }

        numerical = {
            label: numerical_case(x, (packed, scales, biases), persistent_weight)
            for label, x in probes[k]
        }
        if not all(case["shape_equal"] for case in numerical.values()):
            raise RuntimeError(f"{name} numerical output shape mismatch: {numerical}")

        # A fixed deterministic probe and the same persistent W object are used
        # for all warmups/timed samples. No dequantization occurs below.
        bench_x = probes[k][0][1]
        for _ in range(WARMUP_ITERATIONS):
            mx.eval(qmatmul(bench_x, (packed, scales, biases)))
            mx.eval(bench_x @ persistent_weight.T)
        mx.reset_peak_memory()
        q_times: list[float] = []
        dense_times: list[float] = []
        for _ in range(ABBA_CYCLES):
            for side, sink in (("q", q_times), ("bf16", dense_times), ("bf16", dense_times), ("q", q_times)):
                started = time.perf_counter()
                output = qmatmul(bench_x, (packed, scales, biases)) if side == "q" else bench_x @ persistent_weight.T
                mx.eval(output)
                sink.append(time.perf_counter() - started)
        q_stats = distribution(q_times)
        dense_stats = distribution(dense_times)
        timing_peak = int(mx.get_peak_memory())
        timing_active = int(mx.get_active_memory())
        ratio = dense_stats["median_seconds"] / q_stats["median_seconds"]
        saved_seconds = q_stats["median_seconds"] - dense_stats["median_seconds"]
        projection_results[name] = {
            "geometry": {"K": k, "N": n, "m": M, "input_shape": [1, M, k], "output_shape": [1, M, n]},
            "tensor_headers": headers[name],
            "memory_accounting": memory,
            "one_time_dequantization": one_time,
            "numerical_validation": numerical,
            "steady_state_microbenchmark": {
                "control": "mx.quantized_matmul real packed affine group64 3-bit, transpose=True",
                "treatment": "same persistent BF16 mx.dequantize result: x @ W.T",
                "warmup_iterations_per_side_excluded": WARMUP_ITERATIONS,
                "timed_samples_per_side": ABBA_CYCLES * 2,
                "timing_order": "Q -> BF16 -> BF16 -> Q, repeated",
                "dequantization_in_timed_region": False,
                "quantized_m5": q_stats,
                "persistent_bf16_m5": dense_stats,
                "bf16_over_quantized_median_ratio": ratio,
                "median_seconds_saved": saved_seconds,
                "median_microseconds_saved": saved_seconds * 1_000_000.0,
                "quantized_effective_outputs_per_second": (M * n) / q_stats["median_seconds"],
                "persistent_bf16_effective_outputs_per_second": (M * n) / dense_stats["median_seconds"],
                "active_memory_bytes_after_timing": timing_active,
                "peak_memory_bytes_after_warmup": timing_peak,
            },
        }
        # This runner never forms a multi-layer cache. Releasing the single
        # layer-0 W after its evidence is captured is not a cache purge.
        del persistent_weight
        gc.collect()

    # Arithmetic only: direct independent per-projection microbench medians are
    # multiplied by one projection/layer and 36 frozen layers. It is not a
    # full-model timing or scientific ABBA, and cannot establish additivity.
    for result in projection_results.values():
        bench = result["steady_state_microbenchmark"]
        per_layer = bench["median_seconds_saved"]
        block_saving = per_layer * EXPECTED_CONFIG["num_hidden_layers"]
        result["full_model_projection"] = {
            "per_layer_median_seconds_saved": per_layer,
            "layers": EXPECTED_CONFIG["num_hidden_layers"],
            "estimated_block_seconds_saved": block_saving,
            "estimated_block_milliseconds_saved": block_saving * 1000.0,
            "estimated_fraction_of_canonical_block_wall": block_saving / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS,
            "estimated_target_tokens_per_second_arithmetic": (
                STRETCH_031_M5_TOKENS_PER_SECOND / (1.0 - block_saving / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS)
                if block_saving < STRETCH_031_M5_MEDIAN_BLOCK_SECONDS else None
            ),
        }
        incremental_mib = mib(result["memory_accounting"]["incremental_bytes_if_both_quantized_source_and_bf16_cache_resident"] * EXPECTED_CONFIG["num_hidden_layers"])
        estimated_free = STRETCH_031_MINIMUM_FREE_PERCENT - (100.0 * incremental_mib / MODEL_MEMORY_MIB)
        result["speed_per_memory"] = {
            "conservative_primary_scenario": "both quantized source and BF16 cache remain resident",
            "incremental_resident_mib_x36": incremental_mib,
            "estimated_block_milliseconds_saved": result["full_model_projection"]["estimated_block_milliseconds_saved"],
            "speed_gain_per_100_mib_ms": result["full_model_projection"]["estimated_block_milliseconds_saved"] / incremental_mib * 100.0,
            "estimated_minimum_free_memory_percent_linear_diagnostic": estimated_free,
            "memory_risky_against_5_percent_abort": estimated_free < STRETCH_031_HARD_ABORT_FREE_PERCENT,
        }

    def combination(label: str, members: tuple[str, ...]) -> dict:
        saved = sum(projection_results[name]["full_model_projection"]["estimated_block_seconds_saved"] for name in members)
        extra = sum(projection_results[name]["speed_per_memory"]["incremental_resident_mib_x36"] for name in members)
        free = STRETCH_031_MINIMUM_FREE_PERCENT - 100.0 * extra / MODEL_MEMORY_MIB
        one_time = sum(projection_results[name]["one_time_dequantization"]["one_time_total_wall_seconds"] for name in members)
        return {
            "label": label,
            "members": list(members),
            "estimated_block_seconds_saved": saved,
            "estimated_block_milliseconds_saved": saved * 1000.0,
            "estimated_fraction_of_canonical_block_wall": saved / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS,
            "additional_resident_mib_x36_both": extra,
            "speed_gain_per_100_mib_ms": saved * 1000.0 / extra * 100.0,
            "estimated_minimum_free_memory_percent_linear_diagnostic": free,
            "memory_risky_against_5_percent_abort": free < STRETCH_031_HARD_ABORT_FREE_PERCENT,
            "one_time_dequantization_seconds_x36": one_time * EXPECTED_CONFIG["num_hidden_layers"],
            "break_even_target_traversals": (
                (one_time * EXPECTED_CONFIG["num_hidden_layers"]) / saved if saved > 0 else None
            ),
        }

    combinations = {
        "K+V": combination("K+V", ("k_proj", "v_proj")),
        "Q+O": combination("Q+O", ("q_proj", "o_proj")),
    }
    for name, result in projection_results.items():
        one_time_x36 = result["one_time_dequantization"]["one_time_total_wall_seconds"] * EXPECTED_CONFIG["num_hidden_layers"]
        saved = result["full_model_projection"]["estimated_block_seconds_saved"]
        result["break_even"] = {
            "one_time_dequantization_seconds_x36": one_time_x36,
            "steady_state_seconds_saved_per_target_traversal": saved,
            "target_traversals_to_break_even": one_time_x36 / saved if saved > 0 else None,
        }

    pareto = []
    for label, item in list(projection_results.items()) + [("K+V", combinations["K+V"]), ("Q+O", combinations["Q+O"])]:
        if label in projection_results:
            projection = item
            speed = projection["full_model_projection"]
            memory_stats = projection["speed_per_memory"]
            pareto.append({
                "candidate": label,
                "projected_speed_gain_percent": 100.0 * speed["estimated_fraction_of_canonical_block_wall"],
                "additional_resident_mib": memory_stats["incremental_resident_mib_x36"],
                "speed_gain_per_100_mib_ms": memory_stats["speed_gain_per_100_mib_ms"],
                "estimated_minimum_free_memory_percent_linear_diagnostic": memory_stats["estimated_minimum_free_memory_percent_linear_diagnostic"],
                "memory_risky_against_5_percent_abort": memory_stats["memory_risky_against_5_percent_abort"],
            })
        else:
            pareto.append({
                "candidate": label,
                "projected_speed_gain_percent": 100.0 * item["estimated_fraction_of_canonical_block_wall"],
                "additional_resident_mib": item["additional_resident_mib_x36_both"],
                "speed_gain_per_100_mib_ms": item["speed_gain_per_100_mib_ms"],
                "estimated_minimum_free_memory_percent_linear_diagnostic": item["estimated_minimum_free_memory_percent_linear_diagnostic"],
                "memory_risky_against_5_percent_abort": item["memory_risky_against_5_percent_abort"],
            })

    def numerically_compatible(names: tuple[str, ...]) -> bool:
        # Exact equality is recorded but is not silently required. The observed
        # max/mean diagnostics are carried into the admission report.
        return all(all(case["shape_equal"] for case in projection_results[name]["numerical_validation"].values()) for name in names)

    candidates = {name: (name,) for name in PROJECTIONS} | {"K+V": ("k_proj", "v_proj"), "Q+O": ("q_proj", "o_proj")}
    qualifying = []
    for label, names in candidates.items():
        if label in projection_results:
            gain = projection_results[label]["full_model_projection"]["estimated_fraction_of_canonical_block_wall"]
            memory_risky = projection_results[label]["speed_per_memory"]["memory_risky_against_5_percent_abort"]
            break_even = projection_results[label]["break_even"]["target_traversals_to_break_even"]
        else:
            gain = combinations[label]["estimated_fraction_of_canonical_block_wall"]
            memory_risky = combinations[label]["memory_risky_against_5_percent_abort"]
            break_even = combinations[label]["break_even_target_traversals"]
        if numerically_compatible(names) and gain >= 0.05 and not memory_risky and break_even is not None:
            qualifying.append(label)
    if qualifying:
        classification = "GO_" + qualifying[0].replace("+", "")
        decision = "GO"
    else:
        # Feasibility may still be informative, but without a concrete safe
        # candidate it cannot authorize a scientific plan.
        classification, decision = "STRETCH_036_PERSISTENT_DEQUANTIZED_PROJECTION_FEASIBILITY_NO_GO", "NO-GO"

    final = {
        "experiment": "Stretch 036 persistent dequantized BF16 projection feasibility",
        "classification": classification,
        "decision": decision,
        "diagnostic_only": True,
        "scientific_abba_started": False,
        "full_model_abba_started": False,
        "timestamp": utc_now(),
        "runtime_provenance": provenance,
        "model": {
            "model_dir": str(model_dir),
            "weight_sha256": sha256_file(weight_path),
            "model_config": observed_config,
            "quantization": {"bits": BITS, "group_size": GROUP_SIZE, "mode": MODE},
            "layer": LAYER_ID,
        },
        "methodology": {
            "control": "canonical monolithic affine mx.quantized_matmul at M5",
            "treatment": "W = mx.dequantize(real_packed_weight, real_scales, real_biases, group_size=64, bits=3); persist BF16 W; x @ W.T",
            "no_original_fp16_or_bf16_weights_loaded": True,
            "no_requantization": True,
            "no_scale_or_bias_modification": True,
            "no_global_mlx_modification": True,
            "no_model_code_change": True,
            "no_deliberate_cache_purge": True,
            "no_36_layer_bf16_cache_materialized": True,
            "realistic_activation_input": "not recovered; true intermediate activation would require a model traversal and is outside this isolated feasibility probe",
            "numerical_inputs": "three deterministic BF16 inputs per K",
            "timed_input": "fixed deterministic BF16 pattern_mod257 per K",
        },
        "setup_active_memory_bytes": setup_active_memory,
        "projections": projection_results,
        "combinations": combinations,
        "pareto_table": pareto,
        "decision_gate": {
            "qualifying_candidates": qualifying,
            "target_upside_minimum_fraction": 0.05,
            "memory_reference": {
                "stretch031_observed_minimum_free_percent": STRETCH_031_MINIMUM_FREE_PERCENT,
                "historical_hard_abort_free_percent": STRETCH_031_HARD_ABORT_FREE_PERCENT,
                "system_memory_mib": MODEL_MEMORY_MIB,
                "note": "Minimum-free-memory projection linearly subtracts cache MiB from 8 GiB only as a diagnostic; it does not assume actual pressure is linear.",
            },
            "classification_rule": "GO only for a shape-compatible, >=5% arithmetic projection with non-risky diagnostic memory and finite positive break-even; otherwise NO-GO.",
        },
    }
    summary_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Classification: {classification}")
    for name, result in projection_results.items():
        bench = result["steady_state_microbenchmark"]
        print(
            f"{name}: q={bench['quantized_m5']['median_seconds'] * 1e6:.2f} us "
            f"bf16={bench['persistent_bf16_m5']['median_seconds'] * 1e6:.2f} us "
            f"ratio={bench['bf16_over_quantized_median_ratio']:.6f} "
            f"saved={bench['median_microseconds_saved']:.2f} us"
        )
    print(f"Summary: {summary_path}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child_main(Path(sys.argv[2]), Path(sys.argv[3]))

    repo = Path(__file__).resolve().parents[1]
    child_python = repo / CANONICAL_CHILD_PYTHON  # Preserve literal venv path; never resolve it.
    model_dir = repo / MODEL_DIR
    required = (child_python, model_dir / "model.safetensors", model_dir / "config.json")
    if not all(path.is_file() for path in required):
        raise RuntimeError(f"missing required feasibility inputs: {required}")
    if not child_python.is_symlink():
        raise RuntimeError(f"canonical venv launcher unexpectedly is not a symlink: {child_python}")

    run_dir = repo / "results-local/stretch/persistent-dequantized-projection-036-feasibility" / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    child_summary = run_dir / "child-summary.json"
    stdout_path, stderr_path = run_dir / "child-stdout.txt", run_dir / "child-stderr.txt"
    parent_summary = run_dir / "summary.json"
    command = [str(child_python), str(Path(__file__).resolve()), "--child", str(model_dir), str(child_summary)]
    started = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        proc = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr, check=False)
    if proc.returncode != 0 or not child_summary.is_file():
        raise RuntimeError(f"feasibility child failed returncode={proc.returncode}; stdout={stdout_path}; stderr={stderr_path}")
    child = json.loads(child_summary.read_text(encoding="utf-8"))
    parent = {
        "experiment": child["experiment"],
        "classification": child["classification"],
        "decision": child["decision"],
        "diagnostic_only": True,
        "scientific_abba_started": False,
        "full_model_abba_started": False,
        "canonical_launcher_literal": str(child_python),
        "command": command,
        "child_summary": str(child_summary),
        "child_stdout": str(stdout_path),
        "child_stderr": str(stderr_path),
        "child_wall_seconds": time.perf_counter() - started,
        "child": child,
    }
    parent_summary.write_text(json.dumps(parent, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(stdout_path.read_text(encoding="utf-8", errors="replace"), end="")
    print(f"Parent summary: {parent_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
