#!/usr/bin/env python3
"""Stretch 034 diagnostic-only fused residual-add + RMSNorm feasibility.

This is intentionally not a scientific Stretch 034 source transform or ABBA.
It compares the canonical Qwen3 control pair against one MLX 0.31.2 custom
Metal kernel that emits both the raw residual and normalized result.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
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
    "rms_norm_eps": 1e-6,
}
B, M, D = 1, 5, 4096
EPS = 1e-6
THREADS = 256
WARMUP_ITERATIONS = 40
MEASURE_CYCLES = 60  # 120 samples per side in every balanced comparison.
RANDOM_SEEDS = (11, 29, 47)
# These are predeclared compatibility gates for a different FP32 reduction
# order, not post-run tolerances. h remains strictly bit-exact.
NORM_MAX_ABS_TOLERANCE = 2.0**-5
NORM_MEAN_ABS_TOLERANCE = 2.0**-10
STRETCH_031_M5_MEDIAN_BLOCK_SECONDS = 0.3487060
STRETCH_031_M5_TOKENS_PER_SECOND = 14.3307127237

# One 256-thread group owns one D=4096 row. Every thread writes 16 BF16 h
# values, accumulates those values in FP32, then a threadgroup tree-reduction
# produces the RMS reciprocal. Both output arrays are required by Qwen3.
METAL_SOURCE = r"""
    uint tid = thread_position_in_threadgroup.x;
    uint row = threadgroup_position_in_grid.y;
    uint base = row * 4096;
    threadgroup float partial[256];

    T h_values[16];
    float sum_sq = 0.0f;
    for (uint tile = 0; tile < 16; ++tile) {
        uint col = tid + tile * 256;
        uint idx = base + col;
        T h_value = x[idx] + residual[idx];
        h_values[tile] = h_value;
        raw_residual[idx] = h_value;
        float h_float = static_cast<float>(h_value);
        sum_sq += h_float * h_float;
    }
    partial[tid] = sum_sq;
    threadgroup_barrier(mem_flags::mem_threadgroup);

    if (tid < 128) partial[tid] += partial[tid + 128];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid < 64) partial[tid] += partial[tid + 64];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid < 32) partial[tid] += partial[tid + 32];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid < 16) partial[tid] += partial[tid + 16];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid < 8) partial[tid] += partial[tid + 8];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid < 4) partial[tid] += partial[tid + 4];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid < 2) partial[tid] += partial[tid + 2];
    threadgroup_barrier(mem_flags::mem_threadgroup);
    if (tid == 0) partial[0] += partial[1];
    threadgroup_barrier(mem_flags::mem_threadgroup);

    float inv_rms = metal::rsqrt(partial[0] * (1.0f / 4096.0f) + 1.0e-6f);
    for (uint tile = 0; tile < 16; ++tile) {
        uint col = tid + tile * 256;
        uint idx = base + col;
        normalized[idx] = static_cast<T>(static_cast<float>(h_values[tile]) * inv_rms * static_cast<float>(weight[col]));
    }
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("empty sample")
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
    import os

    import mlx.core as mx
    from safetensors import safe_open
    from mlx_lm.models import qwen3

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
    if config.get("quantization") != {"group_size": 64, "bits": 3}:
        raise RuntimeError(f"quantization mismatch: {config.get('quantization')}")

    qwen_source = Path(qwen3.__file__)
    qwen_text = qwen_source.read_text(encoding="utf-8")
    required_source = [
        "h = x + r",
        "r = self.mlp(self.post_attention_layernorm(h))",
        "out = h + r",
        "return self.norm(h)",
    ]
    missing = [fragment for fragment in required_source if fragment not in qwen_text]
    if missing:
        raise RuntimeError(f"Qwen3 residual/RMSNorm source contract mismatch: {missing}")

    norm_keys = {
        "input_layernorm": "model.layers.0.input_layernorm.weight",
        "post_attention_layernorm": "model.layers.0.post_attention_layernorm.weight",
        "final_model_norm": "model.norm.weight",
    }
    norm_headers: dict[str, dict] = {}
    with safe_open(str(weight_path), framework="np") as handle:
        keys = set(handle.keys())
        for name, key in norm_keys.items():
            if key not in keys:
                raise RuntimeError(f"missing real norm tensor {key}")
            tensor_slice = handle.get_slice(key)
            header = {"key": key, "shape": list(tensor_slice.get_shape()), "dtype": str(tensor_slice.get_dtype())}
            if header["shape"] != [D] or header["dtype"] != "BF16":
                raise RuntimeError(f"unexpected norm header for {name}: {header}")
            norm_headers[name] = header
    all_weights = mx.load(str(weight_path))
    weights = {name: all_weights[key] for name, key in norm_keys.items()}
    # Only three real norm vectors are materialized; no model module or full
    # checkpoint is built for this residual/RMSNorm microbenchmark.
    mx.eval(*weights.values())
    setup_active_memory = int(mx.get_active_memory())

    kernel_factory_started = time.perf_counter()
    kernel = mx.fast.metal_kernel(
        name="stretch034_fused_residual_rmsnorm_bf16_m5_d4096",
        input_names=["x", "residual", "weight"],
        output_names=["raw_residual", "normalized"],
        source=METAL_SOURCE,
        ensure_row_contiguous=True,
    )
    kernel_factory_wall = time.perf_counter() - kernel_factory_started
    kernel_object_id = id(kernel)

    def fused(x, residual, weight):
        if tuple(x.shape) != (B, M, D) or tuple(residual.shape) != (B, M, D):
            raise ValueError(f"custom kernel specializes [1,5,4096], got x={x.shape} residual={residual.shape}")
        if tuple(weight.shape) != (D,):
            raise ValueError(f"custom kernel requires [4096] weight, got {weight.shape}")
        if x.dtype != mx.bfloat16 or residual.dtype != mx.bfloat16 or weight.dtype != mx.bfloat16:
            raise ValueError(f"custom kernel requires BF16 inputs, got {x.dtype}, {residual.dtype}, {weight.dtype}")
        return kernel(
            inputs=[x, residual, weight],
            template=[("T", mx.bfloat16)],
            grid=(THREADS, M, 1),
            threadgroup=(THREADS, 1, 1),
            output_shapes=[x.shape, x.shape],
            output_dtypes=[mx.bfloat16, mx.bfloat16],
        )

    def control(x, residual, weight):
        h = x + residual
        n = mx.fast.rms_norm(h, weight, EPS)
        return h, n

    def difference(reference, candidate) -> dict:
        delta = mx.abs(reference.astype(mx.float32) - candidate.astype(mx.float32))
        exact = mx.equal(reference, candidate)
        mx.eval(delta, exact)
        return {
            "exact_equal": bool(mx.all(exact).item()),
            "max_abs_diff": float(mx.max(delta).item()),
            "mean_abs_diff": float(mx.mean(delta).item()),
        }

    def compare_case(label: str, x, residual, weight) -> dict:
        control_h, control_n = control(x, residual, weight)
        fused_h, fused_n = fused(x, residual, weight)
        mx.eval(control_h, control_n, fused_h, fused_n)
        return {
            "label": label,
            "input_shape": list(x.shape),
            "input_dtype": str(x.dtype),
            "weight_shape": list(weight.shape),
            "weight_dtype": str(weight.dtype),
            "h": difference(control_h, fused_h),
            "normalized": difference(control_n, fused_n),
        }

    # The first dispatch/eval records the JIT/materialization cost explicitly;
    # all diagnostics and steady samples reuse this exact kernel object/template.
    mx.random.seed(RANDOM_SEEDS[0])
    first_x = mx.random.normal((B, M, D)).astype(mx.bfloat16)
    first_r = mx.random.normal((B, M, D)).astype(mx.bfloat16)
    first_jit_started = time.perf_counter()
    first_h, first_n = fused(first_x, first_r, weights["input_layernorm"])
    mx.eval(first_h, first_n)
    first_invocation_and_eval_wall = time.perf_counter() - first_jit_started

    validation: list[dict] = []
    for seed in RANDOM_SEEDS:
        mx.random.seed(seed)
        x = mx.random.normal((B, M, D)).astype(mx.bfloat16)
        residual = mx.random.normal((B, M, D)).astype(mx.bfloat16)
        validation.append(compare_case(f"random_seed_{seed}_input_norm", x, residual, weights["input_layernorm"]))
        validation.append(compare_case(f"random_seed_{seed}_post_attention_norm", x, residual, weights["post_attention_layernorm"]))

    all_h_exact = all(case["h"]["exact_equal"] for case in validation)
    norm_max = max(case["normalized"]["max_abs_diff"] for case in validation)
    norm_mean_max = max(case["normalized"]["mean_abs_diff"] for case in validation)
    numerical_compatible = all_h_exact and norm_max <= NORM_MAX_ABS_TOLERANCE and norm_mean_max <= NORM_MEAN_ABS_TOLERANCE
    if not numerical_compatible:
        raise RuntimeError(
            "numerical feasibility gate failed before timing: "
            f"all_h_exact={all_h_exact} norm_max={norm_max} norm_mean_max={norm_mean_max}"
        )

    # Benchmark input uses a controlled random BF16 payload and the actual
    # layer-0 input_norm BF16 vector. No array identity changes in timing.
    mx.random.seed(101)
    bench_x = mx.random.normal((B, M, D)).astype(mx.bfloat16)
    bench_r = mx.random.normal((B, M, D)).astype(mx.bfloat16)
    bench_w = weights["input_layernorm"]
    bench_h = bench_x + bench_r
    mx.eval(bench_x, bench_r, bench_w, bench_h)

    def add_only():
        return bench_x + bench_r

    def rms_only():
        return mx.fast.rms_norm(bench_h, bench_w, EPS)

    # Warm every control/treatment component before resetting the peak-memory
    # telemetry. These warmups are excluded; nothing purges host or MLX cache.
    warmup_fused_walls: list[float] = []
    for _ in range(WARMUP_ITERATIONS):
        mx.eval(add_only())
        mx.eval(rms_only())
        mx.eval(*control(bench_x, bench_r, bench_w))
        started = time.perf_counter()
        mx.eval(*fused(bench_x, bench_r, bench_w))
        warmup_fused_walls.append(time.perf_counter() - started)

    mx.reset_peak_memory()
    add_times: list[float] = []
    rms_times: list[float] = []
    control_times: list[float] = []
    fused_times: list[float] = []
    # A mirrored order gives each operation 120 synchronized samples while
    # avoiding a one-sided run or a cache purge between control and treatment.
    for _ in range(MEASURE_CYCLES):
        for side, sink in (
            ("add", add_times), ("rms", rms_times), ("control", control_times), ("fused", fused_times),
            ("fused", fused_times), ("control", control_times), ("rms", rms_times), ("add", add_times),
        ):
            started = time.perf_counter()
            if side == "add":
                mx.eval(add_only())
            elif side == "rms":
                mx.eval(rms_only())
            elif side == "control":
                mx.eval(*control(bench_x, bench_r, bench_w))
            else:
                mx.eval(*fused(bench_x, bench_r, bench_w))
            sink.append(time.perf_counter() - started)
    pair_peak_memory = int(mx.get_peak_memory())
    pair_active_memory = int(mx.get_active_memory())
    add_stats = distribution(add_times)
    rms_stats = distribution(rms_times)
    control_stats = distribution(control_times)
    fused_stats = distribution(fused_times)
    pair_ratio = fused_stats["median_seconds"] / control_stats["median_seconds"]
    pair_saved = control_stats["median_seconds"] - fused_stats["median_seconds"]

    # The two-pair pattern contains no attention or MLP custom kernel. n_a is
    # materialized (as required for the real MLP consumer); h_a feeds pair B.
    def two_control():
        h_a, n_a = control(bench_x, bench_r, weights["post_attention_layernorm"])
        h_b, n_b = control(h_a, bench_r, weights["input_layernorm"])
        return h_a, n_a, h_b, n_b

    def two_fused():
        h_a, n_a = fused(bench_x, bench_r, weights["post_attention_layernorm"])
        h_b, n_b = fused(h_a, bench_r, weights["input_layernorm"])
        return h_a, n_a, h_b, n_b

    two_control_out = two_control()
    two_fused_out = two_fused()
    mx.eval(*two_control_out, *two_fused_out)
    two_exactness = {
        name: difference(control_out, fused_out)
        for name, control_out, fused_out in zip(("h_a", "n_a", "h_b", "n_b"), two_control_out, two_fused_out)
    }
    for _ in range(WARMUP_ITERATIONS):
        mx.eval(*two_control())
        mx.eval(*two_fused())
    mx.reset_peak_memory()
    two_control_times: list[float] = []
    two_fused_times: list[float] = []
    for _ in range(MEASURE_CYCLES):
        for side, sink in (("control", two_control_times), ("fused", two_fused_times), ("fused", two_fused_times), ("control", two_control_times)):
            started = time.perf_counter()
            mx.eval(*(two_control() if side == "control" else two_fused()))
            sink.append(time.perf_counter() - started)
    two_control_stats = distribution(two_control_times)
    two_fused_stats = distribution(two_fused_times)
    two_peak_memory = int(mx.get_peak_memory())
    two_active_memory = int(mx.get_active_memory())
    two_ratio = two_fused_stats["median_seconds"] / two_control_stats["median_seconds"]
    two_saved = two_control_stats["median_seconds"] - two_fused_stats["median_seconds"]

    # Each M5 target block visits 36 transformer layers. Opportunities are
    # deliberately separated by scheduling complexity; this does not claim a
    # source integration exists yet.
    opportunity_estimate = {
        "canonical_m5_median_block_seconds": STRETCH_031_M5_MEDIAN_BLOCK_SECONDS,
        "per_pair_median_savings_seconds": pair_saved,
        "intra_layer_simple_opportunities": 36,
        "cross_layer_scheduling_opportunities": 35,
        "final_residual_final_norm_opportunities": 1,
    }
    for label, opportunities in (("intra_layer_only", 36), ("intra_plus_cross_layer", 71), ("optimistic_with_final", 72)):
        saving = pair_saved * opportunities
        fraction = saving / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS
        opportunity_estimate[label] = {
            "opportunities": opportunities,
            "estimated_savings_seconds_per_target_block": saving,
            "estimated_fraction_of_canonical_m5_block": fraction,
            "arithmetic_target_tokens_per_second": STRETCH_031_M5_TOKENS_PER_SECOND / (1.0 - fraction) if fraction < 1.0 else None,
        }

    intra_go = opportunity_estimate["intra_layer_only"]["estimated_fraction_of_canonical_m5_block"] >= 0.05
    cross_go = opportunity_estimate["intra_plus_cross_layer"]["estimated_fraction_of_canonical_m5_block"] >= 0.05
    memory_compatible = max(pair_peak_memory, two_peak_memory) < 1_000_000_000
    # Two-pair correctness repeats the prescribed h-exact / normalized gate.
    two_pair_compatible = all(value["exact_equal"] for name, value in two_exactness.items() if name.startswith("h_")) and all(
        value["max_abs_diff"] <= NORM_MAX_ABS_TOLERANCE and value["mean_abs_diff"] <= NORM_MEAN_ABS_TOLERANCE
        for name, value in two_exactness.items() if name.startswith("n_")
    )
    if numerical_compatible and two_pair_compatible and memory_compatible and intra_go:
        classification = "STRETCH_034_FUSED_RESIDUAL_RMSNORM_FEASIBILITY_GO"
        decision = "GO"
    elif numerical_compatible and two_pair_compatible and memory_compatible and cross_go:
        classification = "STRETCH_034_FUSED_RESIDUAL_RMSNORM_FEASIBILITY_GO_CROSS_LAYER_ONLY"
        decision = "GO_CROSS_LAYER_ONLY"
    else:
        classification = "STRETCH_034_FUSED_RESIDUAL_RMSNORM_FEASIBILITY_NO_GO"
        decision = "NO-GO"

    final = {
        "experiment": "Stretch 034 fused residual add + fast RMSNorm feasibility",
        "classification": classification,
        "decision": decision,
        "diagnostic_only": True,
        "scientific_abba_started": False,
        "timestamp": utc_now(),
        "runtime_provenance": provenance,
        "model": {
            "model_dir": str(model_dir),
            "weight_sha256": sha256_file(weight_path),
            "model_config": observed_config,
            "quantization": {"bits": 3, "group_size": 64, "mode": "affine"},
            "qwen3_source_path": str(qwen_source),
            "qwen3_source_sha256": sha256_file(qwen_source),
            "norm_headers": norm_headers,
            "realistic_activation_validation": "Not run: a true layer activation requires executing attention/MLP or dequantizing the full quantized embedding table, neither is needed for this prescribed real-norm microbenchmark.",
        },
        "methodology": {
            "shape": [B, M, D],
            "dtype": "bfloat16",
            "eps": EPS,
            "control": "h = x + residual; n = mx.fast.rms_norm(h, weight, eps); both h and n evaluated",
            "treatment": "one mx.fast.metal_kernel dispatch emits raw h and normalized n",
            "fp32_accumulation": True,
            "threads_per_row": THREADS,
            "elements_per_thread": D // THREADS,
            "warmup_excluded": True,
            "warmup_iterations_per_operation": WARMUP_ITERATIONS,
            "timed_samples_per_side": MEASURE_CYCLES * 2,
            "timing_order": "add, rms, control, fused, fused, control, rms, add (repeated)",
            "deliberate_cache_purge": False,
            "outer_mlp_compile": False,
            "row_chunking": False,
            "gate_up_fusion": False,
        },
        "setup_active_memory_bytes": setup_active_memory,
        "custom_metal_kernel": {
            "api": "mx.fast.metal_kernel",
            "api_signature": str(inspect.signature(mx.fast.metal_kernel)),
            "name": "stretch034_fused_residual_rmsnorm_bf16_m5_d4096",
            "source_sha256": sha256_bytes(METAL_SOURCE.encode("utf-8")),
            "source": METAL_SOURCE.strip(),
            "factory_wall_seconds": kernel_factory_wall,
            "first_invocation_and_eval_wall_seconds": first_invocation_and_eval_wall,
            "kernel_object_id": kernel_object_id,
            "compiled_once_and_reused": True,
            "jit_reuse_evidence": "One metal_kernel object, one fixed BF16 template, fixed grid/threadgroup and no kernel recreation. MLX 0.31.2 exposes no public compilation-count API; factory and first dispatch are measured separately and all later calls reuse the object.",
            "excluded_fused_warmup": distribution(warmup_fused_walls),
        },
        "numerical_validation": {
            "h_required_exact": True,
            "normalized_reduction_order_tolerance": {"max_abs": NORM_MAX_ABS_TOLERANCE, "mean_abs": NORM_MEAN_ABS_TOLERANCE},
            "cases": validation,
            "all_h_exact": all_h_exact,
            "normalized_max_abs_over_cases": norm_max,
            "normalized_max_mean_abs_over_cases": norm_mean_max,
            "numerical_compatible": numerical_compatible,
        },
        "reference_microbenchmark": {
            "add_standalone": add_stats,
            "rms_norm_standalone": rms_stats,
            "control_pair": control_stats,
            "fused_pair": fused_stats,
            "fused_over_control_median_ratio": pair_ratio,
            "median_microseconds_saved_per_pair": pair_saved * 1_000_000.0,
            "peak_memory_bytes_after_warmup": pair_peak_memory,
            "active_memory_bytes_after_timing": pair_active_memory,
        },
        "two_pair_layer_pattern": {
            "description": "Pair A: attention residual + post_attention RMSNorm; Pair B: MLP residual + next layer input RMSNorm. Attention and MLP are placeholders outside the custom kernel.",
            "exactness": two_exactness,
            "numerical_compatible": two_pair_compatible,
            "control": two_control_stats,
            "fused": two_fused_stats,
            "fused_over_control_median_ratio": two_ratio,
            "median_microseconds_saved_per_two_pairs": two_saved * 1_000_000.0,
            "peak_memory_bytes_after_warmup": two_peak_memory,
            "active_memory_bytes_after_timing": two_active_memory,
        },
        "opportunity_estimate": opportunity_estimate,
        "decision_criteria": {
            "numerical_behavior_plausibly_compatible": numerical_compatible,
            "two_pair_pattern_compatible": two_pair_compatible,
            "memory_compatible_diagnostic_threshold_1GB": memory_compatible,
            "intra_layer_steady_estimate_at_least_5_percent": intra_go,
            "intra_plus_cross_steady_estimate_at_least_5_percent": cross_go,
            "no_recompile_per_pass_evidence": True,
            "cross_layer_scheduling_required": "To use the 35 cross-layer opportunities, TransformerBlock must return/expose its final raw residual h without immediately applying the next block input norm; the outer Qwen3Model traversal must feed h and the next layer's attention residual into the fused pair. The final residual+model.norm case needs a separate final traversal hook. Neither restructuring is implemented by this diagnostic.",
        },
    }
    summary_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Classification: {classification}")
    print(f"Pair control={control_stats['median_seconds'] * 1e6:.2f} us fused={fused_stats['median_seconds'] * 1e6:.2f} us ratio={pair_ratio:.6f}")
    print(f"h exact={all_h_exact}; normalized max={norm_max:.8g}, mean-max={norm_mean_max:.8g}")
    print(f"Summary: {summary_path}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child_main(Path(sys.argv[2]), Path(sys.argv[3]))

    repo = Path(__file__).resolve().parents[1]
    child_python = repo / CANONICAL_CHILD_PYTHON  # Preserve literal venv launcher; never resolve it.
    model_dir = repo / MODEL_DIR
    required = [child_python, model_dir / "model.safetensors", model_dir / "config.json"]
    if not all(path.is_file() for path in required):
        raise RuntimeError(f"missing required feasibility inputs: {required}")
    if not child_python.is_symlink():
        raise RuntimeError(f"canonical venv launcher unexpectedly not a symlink: {child_python}")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local/stretch/fused-residual-rmsnorm-034-feasibility" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    child_summary = run_dir / "child-summary.json"
    stdout_path = run_dir / "child-stdout.txt"
    stderr_path = run_dir / "child-stderr.txt"
    summary_path = run_dir / "summary.json"
    command = [str(child_python), str(Path(__file__).resolve()), "--child", str(model_dir), str(child_summary)]
    started = time.perf_counter()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        proc = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr, check=False)
    child_stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    child_stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    if proc.returncode != 0 or not child_summary.is_file():
        raise RuntimeError(
            f"fused residual/RMSNorm feasibility child failed returncode={proc.returncode}; "
            f"stdout={stdout_path}; stderr={stderr_path}"
        )
    child = json.loads(child_summary.read_text(encoding="utf-8"))
    parent = {
        "experiment": "Stretch 034 fused residual add + fast RMSNorm feasibility",
        "classification": child["classification"],
        "decision": child["decision"],
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
    summary_path.write_text(json.dumps(parent, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(child_stdout, end="" if child_stdout.endswith("\n") else "\n")
    print(f"Parent summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
