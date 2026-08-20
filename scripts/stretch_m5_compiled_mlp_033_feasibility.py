#!/usr/bin/env python3
"""Stretch 033 diagnostic-only mx.compile(M5 Qwen3 MLP) feasibility.

This cannot create a scientific runner or ABBA. It compares the same real
layer-0 MLP expression in eager form and through mlx 0.31.2 mx.compile.
"""
from __future__ import annotations

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
BITS = 3
GROUP_SIZE = 64
MODE = "affine"
M = 5
LAYER_IDS = (0, 1, 2)
WARMUP_ITERATIONS = 30
ABBA_CYCLES = 60
SEQUENCE_ABBA_CYCLES = 30
STRETCH_028_MLP_SECONDS_PER_BLOCK = 0.3265953894588165
STRETCH_031_M5_MEDIAN_BLOCK_SECONDS = 0.3487060
STRETCH_031_M5_TOKENS_PER_SECOND = 14.3307127237


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
        raise ValueError("empty sample")
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
    import inspect
    import os

    import mlx.core as mx
    from mlx_lm.models import qwen3
    from mlx_lm.models.activations import swiglu
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

    weight_path = model_dir / "model.safetensors"
    config_path = model_dir / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    observed_config = {name: config.get(name) for name in EXPECTED_CONFIG}
    if observed_config != EXPECTED_CONFIG:
        raise RuntimeError(f"config mismatch: {observed_config}")
    if config.get("quantization") != {"group_size": GROUP_SIZE, "bits": BITS}:
        raise RuntimeError(f"quantization mismatch: {config.get('quantization')}")

    qwen_source = Path(qwen3.__file__)
    qwen_source_text = qwen_source.read_text(encoding="utf-8")
    required_qwen_fragments = [
        "self.gate_proj = nn.Linear(dim, hidden_dim, bias=False)",
        "self.down_proj = nn.Linear(hidden_dim, dim, bias=False)",
        "self.up_proj = nn.Linear(dim, hidden_dim, bias=False)",
        "return self.down_proj(swiglu(self.gate_proj(x), self.up_proj(x)))",
    ]
    missing = [fragment for fragment in required_qwen_fragments if fragment not in qwen_source_text]
    if missing:
        raise RuntimeError(f"Qwen3 MLP source contract mismatch: {missing}")

    # Validate tensor headers before loading. The selected maps below contain
    # only real MLP payloads from layers 0, 1 and 2; no model module is built.
    headers: dict[str, dict] = {}
    with safe_open(str(weight_path), framework="np") as handle:
        keys = set(handle.keys())
        for layer_id in LAYER_IDS:
            layer_header: dict[str, dict] = {}
            for projection, k, n in (("gate_proj", 4096, 12288), ("up_proj", 4096, 12288), ("down_proj", 12288, 4096)):
                field_header = {}
                prefix = f"model.layers.{layer_id}.mlp.{projection}"
                for field in ("weight", "scales", "biases"):
                    key = f"{prefix}.{field}"
                    if key not in keys:
                        raise RuntimeError(f"missing tensor {key}")
                    view = handle.get_slice(key)
                    field_header[field] = {"key": key, "shape": list(view.get_shape()), "dtype": str(view.get_dtype())}
                packed = [n, (k * BITS) // 32]
                quant = [n, k // GROUP_SIZE]
                if field_header["weight"]["shape"] != packed or field_header["scales"]["shape"] != quant or field_header["biases"]["shape"] != quant:
                    raise RuntimeError(f"header mismatch layer={layer_id} projection={projection}: {field_header}")
                layer_header[projection] = {"k": k, "n": n, "packed_weight_geometry": packed, "quant_parameter_geometry": quant, "tensors": field_header}
            headers[str(layer_id)] = layer_header

    all_weights = mx.load(str(weight_path))
    layers = []
    for layer_id in LAYER_IDS:
        layer = {}
        for projection in ("gate_proj", "up_proj", "down_proj"):
            prefix = f"model.layers.{layer_id}.mlp.{projection}"
            layer[projection] = tuple(all_weights[f"{prefix}.{field}"] for field in ("weight", "scales", "biases"))
        layers.append(layer)
    del all_weights
    gc.collect()
    mx.eval(*(value for layer in layers for tensors in layer.values() for value in tensors))
    setup_active_memory = int(mx.get_active_memory())

    total = M * EXPECTED_CONFIG["hidden_size"]
    x = (
        ((mx.arange(total, dtype=mx.int32) % 257).astype(mx.float32) - 128.0) / 512.0
    ).reshape(1, M, EXPECTED_CONFIG["hidden_size"]).astype(mx.bfloat16)
    mx.eval(x)

    def qmatmul(x_value, tensors):
        weight, scales, biases = tensors
        return mx.quantized_matmul(
            x_value, weight, scales, biases, transpose=True,
            group_size=GROUP_SIZE, bits=BITS, mode=MODE,
        )

    # Pure expression matching mlx_lm.models.qwen3.MLP.__call__, with only
    # captured immutable real tensors substituted for module storage.
    layer0 = layers[0]

    def eager_mlp(x_value):
        gate = qmatmul(x_value, layer0["gate_proj"])
        up = qmatmul(x_value, layer0["up_proj"])
        hidden = swiglu(gate, up)
        return qmatmul(hidden, layer0["down_proj"])

    def eager_sequence(x_value):
        hidden = x_value
        for layer in layers:
            gate = qmatmul(hidden, layer["gate_proj"])
            up = qmatmul(hidden, layer["up_proj"])
            hidden = qmatmul(swiglu(gate, up), layer["down_proj"])
        return hidden

    # `inputs=` explicitly captures the otherwise closure-held immutable MLX
    # arrays. The resulting callable accepts only x, so weights cannot be
    # re-provided/retraced inside steady-state timing.
    first_compile_factory_started = time.perf_counter()
    compiled_mlp = mx.compile(eager_mlp, inputs=layer0)
    compile_factory_wall = time.perf_counter() - first_compile_factory_started
    compiled_id = id(compiled_mlp)
    first_invocation_started = time.perf_counter()
    compiled_first_output = compiled_mlp(x)
    mx.eval(compiled_first_output)
    first_invocation_and_eval_wall = time.perf_counter() - first_invocation_started

    # Establish diagnostic numerical equivalence before any timed comparison.
    eager_first_output = eager_mlp(x)
    mx.eval(eager_first_output)
    diff = mx.abs(eager_first_output.astype(mx.float32) - compiled_first_output.astype(mx.float32))
    equal = mx.equal(eager_first_output, compiled_first_output)
    mx.eval(diff, equal)
    exactness = {
        "top_level_shape_equal": tuple(eager_first_output.shape) == tuple(compiled_first_output.shape),
        "eager_shape": list(eager_first_output.shape),
        "compiled_shape": list(compiled_first_output.shape),
        "exact_equal": bool(mx.all(equal).item()),
        "max_abs_diff": float(mx.max(diff).item()),
        "mean_abs_diff": float(mx.mean(diff).item()),
        "top1": "not_applicable: MLP hidden-state output, not vocabulary logits",
    }

    warmup_walls: list[float] = []
    for _ in range(WARMUP_ITERATIONS):
        started = time.perf_counter()
        mx.eval(compiled_mlp(x))
        warmup_walls.append(time.perf_counter() - started)
    mx.reset_peak_memory()
    eager_times: list[float] = []
    compiled_times: list[float] = []
    for _ in range(ABBA_CYCLES):
        for side, sink in (("eager", eager_times), ("compiled", compiled_times), ("compiled", compiled_times), ("eager", eager_times)):
            started = time.perf_counter()
            out = eager_mlp(x) if side == "eager" else compiled_mlp(x)
            mx.eval(out)
            sink.append(time.perf_counter() - started)
    eager_stats = distribution(eager_times)
    compiled_stats = distribution(compiled_times)
    single_peak_memory = int(mx.get_peak_memory())
    single_active_memory = int(mx.get_active_memory())

    # Attribution: time the unchanged individual qmatmuls and the same SwiGLU
    # operation against precomputed real outputs. The residual is descriptive;
    # separately synchronized operations cannot prove internal kernel causality.
    gate_ref = qmatmul(x, layer0["gate_proj"])
    up_ref = qmatmul(x, layer0["up_proj"])
    hidden_ref = swiglu(gate_ref, up_ref)
    mx.eval(gate_ref, up_ref, hidden_ref)

    def time_operation(fun, cycles: int = 30) -> dict:
        for _ in range(10):
            mx.eval(fun())
        samples = []
        for _ in range(cycles):
            started = time.perf_counter()
            mx.eval(fun())
            samples.append(time.perf_counter() - started)
        return distribution(samples)

    attribution = {
        "gate_qmatmul": time_operation(lambda: qmatmul(x, layer0["gate_proj"])),
        "up_qmatmul": time_operation(lambda: qmatmul(x, layer0["up_proj"])),
        "swiglu_elementwise": time_operation(lambda: swiglu(gate_ref, up_ref)),
        "down_qmatmul": time_operation(lambda: qmatmul(hidden_ref, layer0["down_proj"])),
    }
    attribution_sum = sum(value["median_seconds"] for value in attribution.values())
    attribution["eager_full_minus_standalone_component_medians_seconds"] = eager_stats["median_seconds"] - attribution_sum
    attribution["interpretation_limit"] = "Descriptive synchronization/scheduling residual only; it does not identify or prove MLX internal kernel behavior."

    # Optional safe depth probe: three actual MLP weight sets in a direct MLP
    # chain. It does not represent a transformer block or alter the factor.
    sequence_factory_started = time.perf_counter()
    compiled_sequence = mx.compile(eager_sequence, inputs=layers)
    sequence_factory_wall = time.perf_counter() - sequence_factory_started
    sequence_first_started = time.perf_counter()
    compiled_sequence_first = compiled_sequence(x)
    mx.eval(compiled_sequence_first)
    sequence_first_wall = time.perf_counter() - sequence_first_started
    eager_sequence_first = eager_sequence(x)
    mx.eval(eager_sequence_first)
    sequence_diff = mx.abs(eager_sequence_first.astype(mx.float32) - compiled_sequence_first.astype(mx.float32))
    sequence_equal = mx.equal(eager_sequence_first, compiled_sequence_first)
    mx.eval(sequence_diff, sequence_equal)
    sequence_exactness = {
        "top_level_shape_equal": tuple(eager_sequence_first.shape) == tuple(compiled_sequence_first.shape),
        "exact_equal": bool(mx.all(sequence_equal).item()),
        "max_abs_diff": float(mx.max(sequence_diff).item()),
        "mean_abs_diff": float(mx.mean(sequence_diff).item()),
    }
    for _ in range(WARMUP_ITERATIONS):
        mx.eval(compiled_sequence(x))
    mx.reset_peak_memory()
    sequence_eager: list[float] = []
    sequence_compiled: list[float] = []
    for _ in range(SEQUENCE_ABBA_CYCLES):
        for side, sink in (("eager", sequence_eager), ("compiled", sequence_compiled), ("compiled", sequence_compiled), ("eager", sequence_eager)):
            started = time.perf_counter()
            out = eager_sequence(x) if side == "eager" else compiled_sequence(x)
            mx.eval(out)
            sink.append(time.perf_counter() - started)
    sequence_eager_stats = distribution(sequence_eager)
    sequence_compiled_stats = distribution(sequence_compiled)
    sequence_peak_memory = int(mx.get_peak_memory())
    sequence_active_memory = int(mx.get_active_memory())

    ratio = compiled_stats["median_seconds"] / eager_stats["median_seconds"]
    improvement_fraction = 1.0 - ratio
    estimate = {
        "method": "Apply single-M5-MLP steady-state fraction only to Stretch 028 MLP diagnostic time; not a scientific throughput result.",
        "compiled_over_eager_mlp_ratio": ratio,
        "mlp_improvement_fraction": improvement_fraction,
        "estimated_savings_seconds_per_target_block": STRETCH_028_MLP_SECONDS_PER_BLOCK * improvement_fraction,
        "estimated_fraction_of_stretch031_m5_median_block": (
            STRETCH_028_MLP_SECONDS_PER_BLOCK * improvement_fraction
        ) / STRETCH_031_M5_MEDIAN_BLOCK_SECONDS,
    }
    estimate["estimated_target_rate_tokens_per_second"] = STRETCH_031_M5_TOKENS_PER_SECOND / (
        1.0 - estimate["estimated_fraction_of_stretch031_m5_median_block"]
    )
    fixed_input = {
        "shape": list(x.shape),
        "dtype": str(x.dtype),
        "object_id": id(x),
        "compiled_object_id": compiled_id,
        "compiled_callable_created_once": True,
        "all_steady_state_calls_use_same_input_object": True,
        "all_steady_state_calls_use_same_captured_weight_objects": True,
        "shapeless": False,
        "timed_compiled_max_over_median": compiled_stats["maximum_seconds"] / compiled_stats["median_seconds"],
        "note": "MLX 0.31.2 exposes no public compilation-count API. Fixed rank/shape/dtype and captured objects, a separately measured first invocation, excluded warmups, and absence of a second compile-scale timed outlier are the available reuse evidence.",
    }
    memory_compatible = int(mx.get_peak_memory()) < 1_000_000_000
    go = (
        exactness["top_level_shape_equal"]
        and exactness["exact_equal"]
        and estimate["estimated_fraction_of_stretch031_m5_median_block"] >= 0.05
        and memory_compatible
    )
    decision = {
        "classification": "STRETCH_033_COMPILED_MLP_FEASIBILITY_GO" if go else "STRETCH_033_COMPILED_MLP_FEASIBILITY_NO_GO",
        "go": go,
        "criteria": {
            "diagnostic_exactness": exactness["exact_equal"],
            "estimated_end_to_end_upside_at_least_5_percent": estimate["estimated_fraction_of_stretch031_m5_median_block"] >= 0.05,
            "memory_compatible_diagnostic_threshold_1GB": memory_compatible,
            "same_compiled_callable_and_m5_bf16_input_in_timing": True,
        },
        "note": "Diagnostic feasibility only. It does not weaken scientific gates and cannot authorize an ABBA.",
    }
    final = {
        "experiment": "Stretch 033 M5 compiled MLP feasibility",
        "classification": decision["classification"],
        "diagnostic_only": True,
        "scientific_abba_started": False,
        "timestamp": utc_now(),
        "runtime_provenance": provenance,
        "model": {
            "model_dir": str(model_dir),
            "weight_sha256": sha256_file(weight_path),
            "model_config": observed_config,
            "quantization": {"bits": BITS, "group_size": GROUP_SIZE, "mode": MODE},
            "layers_loaded": list(LAYER_IDS),
            "headers": headers,
            "qwen3_source_path": str(qwen_source),
            "qwen3_source_sha256": sha256_file(qwen_source),
            "swiglu_source": inspect.getsource(swiglu).strip(),
        },
        "methodology": {
            "m": M,
            "input_dtype": str(x.dtype),
            "input_shape": list(x.shape),
            "control": "eager pure Qwen3 MLP expression: gate qmatmul + up qmatmul + swiglu + down qmatmul",
            "treatment": "same pure expression through mx.compile with real immutable weights explicitly captured via inputs=",
            "manual_qmatmul_fusion": False,
            "row_chunking": False,
            "warmup_excluded": True,
            "deliberate_cache_purge": False,
            "timed_samples_per_side": ABBA_CYCLES * 2,
            "timing_order": "(eager, compiled, compiled, eager) repeated",
        },
        "setup_active_memory_bytes": setup_active_memory,
        "compile_provenance": {
            "mlx_compile_signature": "mx.compile(fun, inputs=layer0); first execution materialized with mx.eval",
            "factory_wall_seconds": compile_factory_wall,
            "first_invocation_and_eval_wall_seconds": first_invocation_and_eval_wall,
            "compiled_warmup": distribution(warmup_walls),
            "steady_state_reuse": fixed_input,
        },
        "exactness": exactness,
        "single_mlp_benchmark": {
            "eager": eager_stats,
            "compiled": compiled_stats,
            "compiled_over_eager_median_ratio": ratio,
            "peak_memory_bytes_after_warmup": single_peak_memory,
            "active_memory_bytes_after_timing": single_active_memory,
        },
        "attribution": attribution,
        "three_real_mlp_sequence": {
            "layers": list(LAYER_IDS),
            "factory_wall_seconds": sequence_factory_wall,
            "first_invocation_and_eval_wall_seconds": sequence_first_wall,
            "exactness": sequence_exactness,
            "eager": sequence_eager_stats,
            "compiled": sequence_compiled_stats,
            "compiled_over_eager_median_ratio": sequence_compiled_stats["median_seconds"] / sequence_eager_stats["median_seconds"],
            "peak_memory_bytes_after_warmup": sequence_peak_memory,
            "active_memory_bytes_after_timing": sequence_active_memory,
        },
        "estimate": estimate,
        "decision": decision,
    }
    summary_path.write_text(json.dumps(final, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Classification: {decision['classification']}")
    print(f"Single MLP eager={eager_stats['median_seconds'] * 1000:.4f} ms compiled={compiled_stats['median_seconds'] * 1000:.4f} ms ratio={ratio:.6f}")
    print(f"Exact={exactness['exact_equal']} max_abs={exactness['max_abs_diff']}")
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
    run_dir = repo / "results-local/stretch/m5-compiled-mlp-033-feasibility" / run_id
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
        raise RuntimeError(f"compiled-MLP feasibility child failed returncode={proc.returncode}; stdout={stdout_path}; stderr={stderr_path}")
    child = json.loads(child_summary.read_text(encoding="utf-8"))
    parent = {
        "experiment": "Stretch 033 M5 compiled MLP feasibility",
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
    summary_path.write_text(json.dumps(parent, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(child_stdout, end="" if child_stdout.endswith("\n") else "\n")
    print(f"Parent summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
