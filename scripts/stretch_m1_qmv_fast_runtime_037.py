#!/usr/bin/env python3
"""Stretch 037 final-source launcher; CONTROL or isolated custom S1_R8 treatment."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from pathlib import Path

CANONICAL_LAUNCHER = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
MODEL_DIR = "results-local/mlx/models/Qwen3-8B-3bit"
SOURCE_HARNESS = "scripts/stretch_single_pass_geometry_harness_031_fix3.py"
SOURCE_HARNESS_BLOB = "f5d8b4f65c2d994de06f1c2ba08417ebaf4a048c"  # verified by prepared preflight
TREATMENT_MODE = "treatment"
ELIGIBLE = ((4096, 4096, "model.layers.0.self_attn.q_proj"), (4096, 1024, "model.layers.0.self_attn.k_proj"), (4096, 12288, "model.layers.0.mlp.gate_proj"), (12288, 4096, "model.layers.0.mlp.down_proj"))


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def git_blob(repo: Path, path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=repo, text=True).strip()


def treatment_injection() -> str:
    # This text is injected after final M5 source rendering. It deliberately
    # patches only in-process QuantizedLinear M=5 calls whose K/N are among the
    # four true Qwen3 projection shape classes.
    return '''    # Stretch 037 treatment: process-local M1 custom qmv_fast S1_R8 only.
    from stretch_m1_qmv_fast_tuning_037_feasibility import metal_source as __stretch037_metal_source
    __stretch037_kernel_specs = {}
    __stretch037_metadata = {"mode": "M1_specific_custom_qmv_fast_s1_r8", "kernel_count": 0, "factory_wall_seconds": 0.0, "jit_wall_seconds": 0.0, "recompilation_count_during_target": 0, "specializations": [], "real_weight_parity": []}
    __stretch037_shapes = {(4096, 4096), (4096, 1024), (4096, 12288), (12288, 4096)}

    def __stretch037_build(k, n):
        key = (k, n)
        if key in __stretch037_kernel_specs:
            return __stretch037_kernel_specs[key]
        source = __stretch037_metal_source(1, 8, k, n)
        started = time.perf_counter()
        kernel = mx.fast.metal_kernel(
            name=f"stretch037_s1_r8_k{k}_n{n}",
            input_names=["w", "scales", "biases", "x"], output_names=["y"],
            source=source, ensure_row_contiguous=True,
        )
        __stretch037_metadata["factory_wall_seconds"] += time.perf_counter() - started
        def run(x_value, weight, scales, biases):
            return kernel(
                inputs=[weight, scales, biases, x_value], template=[("T", mx.bfloat16)],
                grid=(32 * 5, n // 8, 1), threadgroup=(32, 1, 1),
                output_shapes=[(1, 5, n)], output_dtypes=[mx.bfloat16],
            )[0]
        __stretch037_kernel_specs[key] = (run, source)
        __stretch037_metadata["kernel_count"] = len(__stretch037_kernel_specs)
        __stretch037_metadata["specializations"].append({"name": f"stretch037_s1_r8_k{k}_n{n}", "K": k, "N": n, "source_sha256": __import__("hashlib").sha256(source.encode()).hexdigest()})
        return __stretch037_kernel_specs[key]

    def __stretch037_startup():
        # This runs before resident model load and before target timing. It uses
        # real layer-0 payloads for the four shape classes and proves strict
        # parity while forcing one compilation/materialization per specialization.
        all_payloads = mx.load(str(weight_path))
        startup = time.perf_counter()
        for k, n, prefix in ((4096, 4096, "model.layers.0.self_attn.q_proj"), (4096, 1024, "model.layers.0.self_attn.k_proj"), (4096, 12288, "model.layers.0.mlp.gate_proj"), (12288, 4096, "model.layers.0.mlp.down_proj")):
            weight, scales, biases = (all_payloads[f"{prefix}.{field}"] for field in ("weight", "scales", "biases"))
            x_value = (((mx.arange(5 * k, dtype=mx.int32) % 257).astype(mx.float32) - 128.0) / 64.0).reshape(1, 5, k).astype(mx.bfloat16)
            run, source = __stretch037_build(k, n)
            started = time.perf_counter(); custom = run(x_value, weight, scales, biases); mx.eval(custom); __stretch037_metadata["jit_wall_seconds"] += time.perf_counter() - started
            canonical = mx.quantized_matmul(x_value, weight, scales, biases, transpose=True, group_size=64, bits=3, mode="affine")
            delta, equal = mx.abs(canonical.astype(mx.float32) - custom.astype(mx.float32)), mx.equal(canonical, custom)
            mx.eval(delta, equal)
            record = {"K": k, "N": n, "shape_equal": tuple(canonical.shape) == tuple(custom.shape), "exact_equal": bool(mx.all(equal).item()), "max_abs_diff": float(mx.max(delta).item()), "mean_abs_diff": float(mx.mean(delta).item())}
            __stretch037_metadata["real_weight_parity"].append(record)
            if not record["shape_equal"] or not record["exact_equal"]:
                raise RuntimeError(f"Stretch037 startup parity failure: {record}")
        __stretch037_metadata["startup_wall_seconds"] = time.perf_counter() - startup
        del all_payloads

    __stretch037_startup()
    __stretch037_builtin_quantized_linear = nn.QuantizedLinear.__call__
    def __stretch037_custom_quantized_linear(self, x_value):
        weight = self["weight"]
        bits = self.bits
        k_value = (weight.shape[1] * 32) // bits
        n_value = weight.shape[0]
        eligible = (x_value.ndim >= 2 and x_value.shape[-2] == 5 and self.group_size == 64 and bits == 3 and self.mode == "affine" and (k_value, n_value) in __stretch037_shapes)
        if not eligible:
            return __stretch037_builtin_quantized_linear(self, x_value)
        run, _source = __stretch037_kernel_specs[(k_value, n_value)]
        result = run(x_value, weight, self["scales"], self.get("biases"))
        if "bias" in self:
            result = result + self["bias"]
        return result
    nn.QuantizedLinear.__call__ = __stretch037_custom_quantized_linear

'''


def render(repo: Path, mode: str) -> tuple[str, dict]:
    sys.path.insert(0, str(repo / "scripts"))
    from stretch_single_pass_geometry_harness_031_fix3 import render_final_source, source_facts
    control, phase = render_final_source(repo, "M5")
    facts = source_facts(control, "M5")
    if mode == "control":
        return control, {"control_sha256": sha256(control), "treatment_sha256": None, "normalized_equal": None, "phase": phase, "facts": facts}
    anchor = "    def select_weights(prefix: str, strip_prefix: str = \"\") -> dict:\n"
    injection = treatment_injection()
    if control.count(anchor) != 1:
        raise RuntimeError("Stretch037 treatment source anchor missing")
    treatment = control.replace(anchor, injection + anchor, 1)
    if "\"ok\": True," not in treatment:
        raise RuntimeError("Stretch037 final result anchor missing")
    treatment = treatment.replace('        "ok": True,\n', '        "ok": True,\n        "custom_qmv": __stretch037_metadata,\n', 1)
    normalized = treatment.replace(injection, "", 1).replace('        "custom_qmv": __stretch037_metadata,\n', "", 1)
    if normalized != control:
        raise RuntimeError("Stretch037 normalized source diff contains more than custom implementation factor")
    return treatment, {"control_sha256": sha256(control), "treatment_sha256": sha256(treatment), "normalized_equal": True, "phase": phase, "facts": facts, "injection_sha256": sha256(injection)}


def dispatch_preflight(repo: Path, mode: str, output: Path) -> int:
    source, provenance = render(repo, mode)
    output.write_text(json.dumps({"classification": "STRETCH_037_NO_MODEL_DISPATCH_PASS", "mode": mode, "model_loaded": False, "target_compute_executed": False, "source_provenance": provenance, "source_compiles": bool(compile(source, str(Path(__file__).resolve()), "exec")), "launcher": sys.executable, "prefix": sys.prefix}, indent=2) + "\n")
    return 0


def jit_preflight(repo: Path, output: Path) -> int:
    """Force the four real-shape treatment kernels without building a model."""
    import mlx.core as mx
    sys.path.insert(0, str(repo / "scripts"))
    from stretch_m1_qmv_fast_tuning_037_feasibility import metal_source
    model_dir = repo / MODEL_DIR
    weight_path = model_dir / "model.safetensors"
    payloads = mx.load(str(weight_path))
    records, specs = [], []
    factory_wall = jit_wall = 0.0
    for k, n, prefix in ELIGIBLE:
        source = metal_source(1, 8, k, n)
        started = time.perf_counter()
        kernel = mx.fast.metal_kernel(name=f"stretch037_s1_r8_k{k}_n{n}", input_names=["w", "scales", "biases", "x"], output_names=["y"], source=source, ensure_row_contiguous=True)
        factory_wall += time.perf_counter() - started
        weight, scales, biases = (payloads[f"{prefix}.{field}"] for field in ("weight", "scales", "biases"))
        x = (((mx.arange(5*k, dtype=mx.int32) % 257).astype(mx.float32)-128.0)/64.0).reshape(1,5,k).astype(mx.bfloat16)
        started = time.perf_counter()
        custom = kernel(inputs=[weight, scales, biases, x], template=[("T", mx.bfloat16)], grid=(160, n//8, 1), threadgroup=(32,1,1), output_shapes=[(1,5,n)], output_dtypes=[mx.bfloat16])[0]
        mx.eval(custom); jit_wall += time.perf_counter() - started
        canonical = mx.quantized_matmul(x, weight, scales, biases, transpose=True, group_size=64, bits=3, mode="affine")
        delta, equal = mx.abs(canonical.astype(mx.float32)-custom.astype(mx.float32)), mx.equal(canonical, custom)
        mx.eval(delta, equal)
        record = {"K": k, "N": n, "shape_equal": tuple(canonical.shape)==tuple(custom.shape), "exact_equal": bool(mx.all(equal).item()), "max_abs_diff": float(mx.max(delta).item()), "mean_abs_diff": float(mx.mean(delta).item())}
        if not record["shape_equal"] or not record["exact_equal"]: raise RuntimeError(f"JIT preflight parity failed: {record}")
        records.append(record); specs.append({"name": f"stretch037_s1_r8_k{k}_n{n}", "K": k, "N": n, "source_sha256": sha256(source)})
    output.write_text(json.dumps({"classification": "STRETCH_037_CUSTOM_KERNEL_STARTUP_PASS", "model_loaded": False, "target_compute_executed": False, "kernel_count": len(specs), "factory_wall_seconds": factory_wall, "jit_wall_seconds": jit_wall, "specializations": specs, "real_weight_parity": records, "active_memory_bytes": int(mx.get_active_memory()), "peak_memory_bytes": int(mx.get_peak_memory())}, indent=2)+"\n")
    return 0


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    mode = os.environ.get("STRETCH037_MODE", "control")
    if mode not in ("control", TREATMENT_MODE):
        raise RuntimeError(f"invalid STRETCH037_MODE={mode}")
    observed_versions = {name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS}
    if sys.prefix != str(repo / EXPECTED_PREFIX) or observed_versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"canonical runtime mismatch: prefix={sys.prefix}, versions={observed_versions}")
    if len(sys.argv) == 3 and sys.argv[1] == "--dispatch-preflight":
        return dispatch_preflight(repo, mode, Path(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "--jit-preflight":
        if mode != TREATMENT_MODE: raise RuntimeError("JIT preflight is treatment-only")
        return jit_preflight(repo, Path(sys.argv[2]))
    source, _provenance = render(repo, mode)
    namespace = {"__name__": "__main__", "__file__": str(Path(__file__).resolve()), "__package__": None, "__cached__": None}
    exec(compile(source, str(Path(__file__).resolve()), "exec"), namespace)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
