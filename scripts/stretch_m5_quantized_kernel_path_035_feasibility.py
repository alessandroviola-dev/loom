#!/usr/bin/env python3
"""Stretch 035 diagnostic kernel-path map; no source transform or scientific ABBA."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_CHILD_PYTHON = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
MODEL_DIR = "results-local/mlx/models/Qwen3-8B-3bit"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
BITS, GROUP_SIZE, MODE, LAYER_ID = 3, 64, "affine", 0
M_VALUES = (1, 2, 3, 4, 5, 6, 8)
WARMUP_ITERATIONS = 40
MEASURE_CYCLES = 50  # 100 synchronized samples per shape.
PROJECTIONS = {
    "q_proj": ("model.layers.0.self_attn.q_proj", 4096, 4096),
    "k_proj": ("model.layers.0.self_attn.k_proj", 4096, 1024),
    "v_proj": ("model.layers.0.self_attn.v_proj", 4096, 1024),
    "o_proj": ("model.layers.0.self_attn.o_proj", 4096, 4096),
    "gate_proj": ("model.layers.0.mlp.gate_proj", 4096, 12288),
    "up_proj": ("model.layers.0.mlp.up_proj", 4096, 12288),
    "down_proj": ("model.layers.0.mlp.down_proj", 12288, 4096),
}
UPSTREAM_V0312_TAG = "68cf2fddd8de5edd8ab3d926391772b2e2cedad8"
UPSTREAM_V0320_TAG = "7a1d4f5c12ac82f4b4d0a6e71538d89ca0605247"
UPSTREAM_PR3764_HEAD = "e8d2d4304867e8ef42abeefaa9c0cfec7ac75d3a"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def percentile(values: list[float], p: float) -> float:
    data = sorted(values)
    at = (len(data) - 1) * p
    lo, hi = int(at), min(int(at) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (at - lo)


def stats(values: list[float]) -> dict:
    return {
        "samples": len(values), "median_seconds": statistics.median(values),
        "mean_seconds": statistics.fmean(values), "p25_seconds": percentile(values, .25),
        "p75_seconds": percentile(values, .75), "minimum_seconds": min(values),
        "maximum_seconds": max(values), "total_synchronized_wall_seconds": sum(values),
    }


def vector_limit(k: int, n: int, architecture: str) -> int:
    """Literal v0.31.2 get_qmv_batch_limit branch for applegpu architecture."""
    match = re.fullmatch(r"applegpu_g(\d\d)([a-z])", architecture)
    if not match:
        raise RuntimeError(f"unrecognized MLX Metal architecture: {architecture!r}")
    generation, size = int(match.group(1)), match.group(2)
    older_rule = generation in (13, 14)
    if size == "d":
        return 32 if k <= 2048 and n <= 2048 else 18 if k <= 4096 and n <= 4096 else 12
    if k <= 2048 and n <= 2048:
        return 14 if older_rule else 18
    if k <= 4096 and n <= 4096:
        return 10 if older_rule else 12
    return 6 if older_rule else 10


def dispatch_for(k: int, n: int, m: int, architecture: str) -> dict:
    limit = vector_limit(k, n, architecture)
    if m < limit:
        # Every requested projection is K != 64/128, N % 8 == 0 and K % 512 == 0.
        return {"vector_limit": limit, "path": "qmv_fast", "kernel_symbol": "affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0", "extra_kernel": None}
    # v0.31.2 qmm_splitk: its desired ~512 TG count falls to one for N=12288,
    # so it calls qmm. All other requested N are split-K with aligned N.
    if n == 12288:
        return {"vector_limit": limit, "path": "qmm", "kernel_symbol": "affine_qmm_t_bfloat16_t_gs_64_b_3_alN_true_batch_0", "extra_kernel": None}
    return {"vector_limit": limit, "path": "qmm_splitk", "kernel_symbol": "affine_qmm_t_splitk_bfloat16_t_gs_64_b_3_alN_true", "extra_kernel": "MLX strided sum reduction over split_k"}


def child(model_dir: Path, evidence_path: Path) -> int:
    import gc
    import os
    import mlx.core as mx
    from safetensors import safe_open

    repo = model_dir.parents[3]
    versions = {x: importlib.metadata.version(x) for x in EXPECTED_VERSIONS}
    if sys.prefix != str(repo / EXPECTED_PREFIX) or versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"canonical runtime mismatch: prefix={sys.prefix}, versions={versions}")
    info = mx.device_info()
    architecture = info.get("architecture")
    if info.get("device_name") != "Apple M1" or architecture != "applegpu_g13g":
        raise RuntimeError(f"Stretch 035 is an M1-only diagnosis; observed {info}")
    config = json.loads((model_dir / "config.json").read_text())
    if config.get("quantization") != {"group_size": GROUP_SIZE, "bits": BITS}:
        raise RuntimeError(f"unexpected quantization: {config.get('quantization')}")
    weight_path = model_dir / "model.safetensors"
    headers = {}
    with safe_open(str(weight_path), framework="np") as handle:
        keys = set(handle.keys())
        for name, (prefix, k, n) in PROJECTIONS.items():
            tensors = {}
            for field in ("weight", "scales", "biases"):
                key = f"{prefix}.{field}"
                if key not in keys:
                    raise RuntimeError(f"missing {key}")
                sl = handle.get_slice(key)
                tensors[field] = {"key": key, "shape": list(sl.get_shape()), "dtype": str(sl.get_dtype())}
            if tensors["weight"]["shape"] != [n, k * BITS // 32] or tensors["weight"]["dtype"] != "U32":
                raise RuntimeError(f"unexpected packed payload for {name}: {tensors}")
            if (tensors["scales"]["shape"] != [n, k // GROUP_SIZE] or tensors["scales"]["dtype"] != "BF16" or tensors["biases"]["shape"] != [n, k // GROUP_SIZE] or tensors["biases"]["dtype"] != "BF16"):
                raise RuntimeError(f"unexpected affine payload for {name}: {tensors}")
            headers[name] = {"K": k, "N": n, "payload": tensors}

    loaded = mx.load(str(weight_path))
    payloads = {name: tuple(loaded[f"{prefix}.{field}"] for field in ("weight", "scales", "biases")) for name, (prefix, _, _) in PROJECTIONS.items()}
    del loaded
    gc.collect()
    mx.eval(*(t for values in payloads.values() for t in values))
    probes = {}
    for k in {shape[1] for shape in PROJECTIONS.values()}:
        mx.random.seed(1000 + k)
        probes[k] = {m: mx.random.normal((1, m, k)).astype(mx.bfloat16) for m in M_VALUES}
    mx.eval(*(x for by_m in probes.values() for x in by_m.values()))

    results = {}
    for name, (_, k, n) in PROJECTIONS.items():
        w, scales, biases = payloads[name]
        by_m = {}
        m1_median = None
        for m in M_VALUES:
            x = probes[k][m]
            def run():
                return mx.quantized_matmul(x, w, scales, biases, transpose=True, group_size=GROUP_SIZE, bits=BITS, mode=MODE)
            for _ in range(WARMUP_ITERATIONS):
                mx.eval(run())
            timings = []
            for _ in range(MEASURE_CYCLES):
                # Same operation repeated in paired order only to keep command-buffer
                # cadence symmetrical; there is no treatment or scientific ABBA.
                for _side in range(2):
                    started = time.perf_counter(); output = run(); mx.eval(output); timings.append(time.perf_counter() - started)
            result = stats(timings)
            if m1_median is None:
                m1_median = result["median_seconds"]
            mapping = dispatch_for(k, n, m, architecture)
            result.update(mapping)
            result.update({"M": m, "input_shape": [1, m, k], "output_shape": [1, m, n], "median_over_M1": result["median_seconds"] / m1_median, "effective_output_elements_per_second": (m * n) / result["median_seconds"]})
            by_m[str(m)] = result
        results[name] = {"header": headers[name], "measurements": by_m}

    evidence = {
        "experiment": "Stretch 035 current quantized_matmul kernel-path investigation",
        "classification": "STRETCH_035_KERNEL_PATH_INVESTIGATION_ONLY",
        "scientific_abba_started": False,
        "runtime": {"python": sys.executable, "prefix": sys.prefix, "versions": versions, "device_info": info},
        "model": {"directory": str(model_dir), "weight_sha256": sha256_file(weight_path), "quantization": {"mode": MODE, "bits": BITS, "group_size": GROUP_SIZE}, "layer": LAYER_ID},
        "source_provenance": {"v0_31_2_tag_commit": UPSTREAM_V0312_TAG, "v0_32_0_tag_commit": UPSTREAM_V0320_TAG, "pr_3764_head": UPSTREAM_PR3764_HEAD, "v0312_dispatch_file": "mlx/backend/metal/quantized.cpp", "v0312_dispatch_function": "QuantizedMatmul::eval_gpu -> dispatch_qmv -> qmv", "v0312_fast_predicate": "N % 8 == 0 && K % 512 == 0", "v0312_qmv_grid": "threadgroups=(M, ceil(N/8), B); threads=(32,2,1)"},
        "method": {"actual_layer0_packed_weights_scales_biases": True, "activations": "controlled BF16", "M_values": list(M_VALUES), "warmups_excluded": WARMUP_ITERATIONS, "synchronized_samples_per_shape": MEASURE_CYCLES * 2, "deliberate_cache_purge": False, "no_global_runtime_modification": True},
        "projection_results": results,
    }
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"classification: {evidence['classification']}")
    print(f"device: {info}")
    print(f"evidence: {evidence_path}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        return child(Path(sys.argv[2]), Path(sys.argv[3]))
    repo = Path(__file__).resolve().parents[1]
    launcher = repo / CANONICAL_CHILD_PYTHON
    model = repo / MODEL_DIR
    if not launcher.is_symlink() or not (model / "model.safetensors").is_file():
        raise RuntimeError("missing canonical venv launcher or 3-bit model")
    run_dir = repo / "results-local/stretch/m5-quantized-kernel-path-035" / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    child_evidence = run_dir / "child-summary.json"
    stdout, stderr = run_dir / "child-stdout.txt", run_dir / "child-stderr.txt"
    command = [str(launcher), str(Path(__file__).resolve()), "--child", str(model), str(child_evidence)]
    started = time.perf_counter()
    with stdout.open("w") as out, stderr.open("w") as err:
        proc = subprocess.run(command, cwd=repo, stdout=out, stderr=err, check=False)
    if proc.returncode or not child_evidence.exists():
        raise RuntimeError(f"child failure {proc.returncode}; see {stdout} and {stderr}")
    child_json = json.loads(child_evidence.read_text())
    parent = {"experiment": child_json["experiment"], "classification": child_json["classification"], "scientific_abba_started": False, "command": command, "child_wall_seconds": time.perf_counter() - started, "child_summary": str(child_evidence), "child_stdout": str(stdout), "child_stderr": str(stderr), "child": child_json}
    (run_dir / "summary.json").write_text(json.dumps(parent, indent=2) + "\n")
    print(stdout.read_text(), end="")
    print(f"summary: {run_dir / 'summary.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
