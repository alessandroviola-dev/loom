#!/usr/bin/env python3
"""Stretch 037 M1 qmv_fast tuning feasibility; diagnostic only, never an ABBA.

It clones the MLX v0.31.2 affine BF16/3-bit/group64 qmv_fast inner algorithm
for fixed non-batched M=5 geometry using mx.fast.metal_kernel.  The installed
MLX runtime is read only; all treatment kernels are isolated process-local
Metal source strings.
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
UPSTREAM_DIR = "results-local/stretch/m5-quantized-kernel-path-035/upstream/mlx-v0.31.2"
UPSTREAM_COMMIT = "68cf2fddd8de5edd8ab3d926391772b2e2cedad8"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
EXPECTED_CONFIG = {"model_type": "qwen3", "hidden_size": 4096, "intermediate_size": 12288, "num_hidden_layers": 36}
BITS, GROUP_SIZE, M, LAYER_ID = 3, 64, 5, 0
WARMUPS, ABBA_CYCLES = 40, 60
# Predeclared clone admission: all shapes must be strictly bit-exact and no
# clone median may exceed 1.50x canonical. This deliberately conservative
# structural-overhead screen is evaluated before any treatment instantiation.
CLONE_REPRESENTATIVE_MAX_RATIO = 1.50
STRETCH_028_COMPONENT_SECONDS = {
    "attention": 0.09857969474978745,
    "gate_proj": 0.0965807989705354,
    "up_proj": 0.09931493003387004,
    "down_proj": 0.09428692991302039,
}
STRETCH_031_BLOCK_SECONDS = 0.3487060
STRETCH_031_TOKENS_PER_SECOND = 14.3307127237
PROJECTIONS = {
    "q_proj": ("model.layers.0.self_attn.q_proj", 4096, 4096),
    "k_proj": ("model.layers.0.self_attn.k_proj", 4096, 1024),
    "v_proj": ("model.layers.0.self_attn.v_proj", 4096, 1024),
    "o_proj": ("model.layers.0.self_attn.o_proj", 4096, 4096),
    "gate_proj": ("model.layers.0.mlp.gate_proj", 4096, 12288),
    "up_proj": ("model.layers.0.mlp.up_proj", 4096, 12288),
    "down_proj": ("model.layers.0.mlp.down_proj", 12288, 4096),
}
# These are the complete, predeclared maximum-four treatment configurations.
# Every change only repartitions independent output rows among SIMD groups;
# K=512 blocks, 16 values/lane, packed layout and float simd reduction stay
# exactly as in MLX qmv_fast_impl.
VARIANTS = (
    {"id": "s1_r4", "num_simdgroups": 1, "results_per_simdgroup": 4, "rationale": "halve TG SIMD groups; retain four independent rows per SIMD group"},
    {"id": "s4_r4", "num_simdgroups": 4, "results_per_simdgroup": 4, "rationale": "four SIMD groups/TG; 16 independent output rows/TG"},
    {"id": "s2_r2", "num_simdgroups": 2, "results_per_simdgroup": 2, "rationale": "reduce live accumulators from four to two per SIMD group"},
    {"id": "s1_r8", "num_simdgroups": 1, "results_per_simdgroup": 8, "rationale": "one SIMD group/TG with canonical eight output rows/TG"},
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def percentile(values: list[float], p: float) -> float:
    data = sorted(values)
    at = (len(data) - 1) * p
    lo, hi = int(at), min(int(at) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (at - lo)


def stats(values: list[float]) -> dict:
    return {"samples": len(values), "median_seconds": statistics.median(values), "mean_seconds": statistics.fmean(values), "p25_seconds": percentile(values, .25), "p75_seconds": percentile(values, .75), "minimum_seconds": min(values), "maximum_seconds": max(values), "total_synchronized_wall_seconds": sum(values)}


def metal_source(num_simdgroups: int, results_per_simdgroup: int, k_value: int, n_value: int) -> str:
    """Faithful qmv_fast body, specialized per real K/N because metal_kernel source is a function body."""
    return f'''// Derived from MLX v0.31.2 quantized.h qmv_fast_impl (MIT).
// Fixed feasibility specialization: BF16 affine, bits=3, gs=64, M=5.
uint lane = thread_index_in_simdgroup;
uint simd_gid = simdgroup_index_in_threadgroup;
uint3 tid = threadgroup_position_in_grid;
const device uchar* ws = (const device uchar*)w;
thread float x_thread[16];
thread float result[{results_per_simdgroup}] = {{0}};
const int out_row = tid.y * ({num_simdgroups} * {results_per_simdgroup}) + simd_gid * {results_per_simdgroup};
const int in_vec_size_w = {k_value} * 3 / 8;
const int in_vec_size_g = {k_value} / 64;
ws += out_row * in_vec_size_w + lane * 6;
scales += out_row * in_vec_size_g + lane / 4;
biases += out_row * in_vec_size_g + lane / 4;
x += tid.x * {k_value} + lane * 16;
y += tid.x * {n_value} + out_row;
for (int k = 0; k < {k_value}; k += 512) {{
  float sum = 0;
  for (int i = 0; i < 16; i += 8) {{
    sum += x[i] + x[i + 1] + x[i + 2] + x[i + 3] + x[i + 4] + x[i + 5] + x[i + 6] + x[i + 7];
    x_thread[i] = x[i]; x_thread[i + 1] = x[i + 1] / 8.0f;
    x_thread[i + 2] = x[i + 2] / 64.0f; x_thread[i + 3] = x[i + 3] / 2.0f;
    x_thread[i + 4] = x[i + 4] / 16.0f; x_thread[i + 5] = x[i + 5] / 128.0f;
    x_thread[i + 6] = x[i + 6] / 4.0f; x_thread[i + 7] = x[i + 7] / 32.0f;
  }}
  for (int row = 0; row < {results_per_simdgroup}; row++) {{
    const device uchar* wl = (const device uchar*)(ws + row * in_vec_size_w);
    const device T* sl = scales + row * in_vec_size_g;
    const device T* bl = biases + row * in_vec_size_g;
    float accum = 0;
    const thread float* xt = x_thread;
    for (int i = 0; i < 2; i++) {{
      xt += 8 * i; wl += 3 * i;
      accum += (wl[0] & 0x07) * xt[0]; accum += (wl[0] & 0x38) * xt[1];
      accum += (wl[0] & 0xc0) * xt[2]; accum += (wl[1] & 0x01) * (xt[2] * 256.0f);
      accum += (wl[1] & 0x0e) * xt[3]; accum += (wl[1] & 0x70) * xt[4];
      accum += (wl[1] & 0x80) * xt[5]; accum += (wl[2] & 0x03) * (xt[5] * 256.0f);
      accum += (wl[2] & 0x1c) * xt[6]; accum += (wl[2] & 0xe0) * xt[7];
    }}
    result[row] += sl[0] * accum + sum * bl[0];
  }}
  ws += 192; scales += 8; biases += 8; x += 512;
}}
for (int row = 0; row < {results_per_simdgroup}; row++) {{
  result[row] = simd_sum(result[row]);
  if (lane == 0) y[row] = static_cast<T>(result[row]);
}}
'''


def source_audit(repo: Path) -> dict:
    upstream = repo / UPSTREAM_DIR
    commit = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if commit != UPSTREAM_COMMIT:
        raise RuntimeError(f"unexpected MLX source commit {commit}")
    cpp, header = upstream / "mlx/backend/metal/quantized.cpp", upstream / "mlx/backend/metal/kernels/quantized.h"
    text_cpp, text_header = cpp.read_text(), header.read_text()
    required = ("int bn = 8;", "int bk = 32;", "MTL::Size group_dims(bk, 2, 1);", "MTL::Size grid_dims(M, (N + bn - 1) / bn, B);", "bool fast = N % bn == 0 && K % 512 == 0;", "METAL_FUNC void qmv_fast_impl(", "constexpr int packs_per_thread = bits == 2 ? 1 : 2;", "constexpr int num_simdgroups = 2;", "constexpr int results_per_simdgroup = 4;", "[[kernel]] void affine_qmv_fast(")
    missing = [fragment for fragment in required if fragment not in text_cpp + text_header]
    if missing:
        raise RuntimeError(f"MLX source audit fragments missing: {missing}")
    return {"upstream_commit": commit, "quantized_cpp": {"path": str(cpp), "sha256": sha256_file(cpp)}, "quantized_header": {"path": str(header), "sha256": sha256_file(header)}, "canonical_symbol": "affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0", "dispatch": {"bn": 8, "bk": 32, "threadgroup": [32, 2, 1], "threadgroups": "(M, N/8, B)"}, "qmv_fast_specialization": {"packs_per_thread": 2, "pack_factor": 8, "bytes_per_pack": 3, "values_per_thread": 16, "K_block": 512, "num_simdgroups": 2, "results_per_simdgroup": 4, "outputs_per_threadgroup": 8, "float_accumulation_and_simd_sum": True, "threadgroup_memory": "none"}}


def child_main(model_dir: Path, summary_path: Path) -> int:
    import os
    import mlx.core as mx
    from safetensors import safe_open

    repo = model_dir.parents[3]
    versions = {name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS}
    if sys.prefix != str(repo / EXPECTED_PREFIX) or versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"runtime provenance mismatch: prefix={sys.prefix}, versions={versions}")
    info = mx.device_info()
    if info.get("device_name") != "Apple M1" or info.get("architecture") != "applegpu_g13g":
        raise RuntimeError(f"M1-only feasibility observed {info}")
    audit = source_audit(repo)
    config = json.loads((model_dir / "config.json").read_text())
    if {k: config.get(k) for k in EXPECTED_CONFIG} != EXPECTED_CONFIG or config.get("quantization") != {"group_size": 64, "bits": 3}:
        raise RuntimeError("model/config quantization mismatch")
    weight_path = model_dir / "model.safetensors"
    headers = {}
    with safe_open(str(weight_path), framework="np") as handle:
        keys = set(handle.keys())
        for name, (prefix, k, n) in PROJECTIONS.items():
            fields = {}
            for field in ("weight", "scales", "biases"):
                key = f"{prefix}.{field}"
                if key not in keys: raise RuntimeError(f"missing {key}")
                view = handle.get_slice(key); fields[field] = {"key": key, "shape": list(view.get_shape()), "dtype": str(view.get_dtype())}
            if fields["weight"] != {"key": f"{prefix}.weight", "shape": [n, k * 3 // 32], "dtype": "U32"}:
                raise RuntimeError(f"packed header mismatch {name}: {fields['weight']}")
            if any(fields[f]["shape"] != [n, k // 64] or fields[f]["dtype"] != "BF16" for f in ("scales", "biases")):
                raise RuntimeError(f"affine header mismatch {name}: {fields}")
            headers[name] = fields
    weights = mx.load(str(weight_path))
    payloads = {name: tuple(weights[f"{prefix}.{field}"] for field in ("weight", "scales", "biases")) for name, (prefix, _, _) in PROJECTIONS.items()}
    del weights; gc.collect(); mx.eval(*(x for p in payloads.values() for x in p))
    setup_active = int(mx.get_active_memory())

    probes = {}
    for k in sorted({x[1] for x in PROJECTIONS.values()}):
        pattern = (((mx.arange(M*k, dtype=mx.int32) % 257).astype(mx.float32) - 128.0) / 64.0).reshape(1, M, k).astype(mx.bfloat16)
        values = [("pattern_mod257", pattern)]
        for seed in (3701 + k, 4703 + k):
            mx.random.seed(seed); values.append((f"normal_seed_{seed}", mx.random.normal((1, M, k)).astype(mx.bfloat16)))
        mx.eval(*(x for _, x in values)); probes[k] = values

    def qmatmul(x, p):
        return mx.quantized_matmul(x, p[0], p[1], p[2], transpose=True, group_size=64, bits=3, mode="affine")

    kernel_meta = {}
    def build_kernel(config, k, n):
        source = metal_source(config["num_simdgroups"], config["results_per_simdgroup"], k, n)
        kernel = mx.fast.metal_kernel(name=f"stretch037_{config['id']}_k{k}_n{n}", input_names=["w", "scales", "biases", "x"], output_names=["y"], source=source, ensure_row_contiguous=True)
        source_id = f"{config['id']}_k{k}_n{n}"
        kernel_meta[source_id] = {"config": config, "K": k, "N": n, "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "source": source}
        def run(x, p, n_arg):
            rows_per_tg = config["num_simdgroups"] * config["results_per_simdgroup"]
            if n_arg != n or n % rows_per_tg: raise RuntimeError(f"{config['id']} geometry mismatch")
            return kernel(inputs=[p[0], p[1], p[2], x], template=[("T", mx.bfloat16)], grid=(32*M, config["num_simdgroups"] * (n // rows_per_tg), 1), threadgroup=(32, config["num_simdgroups"], 1), output_shapes=[(1, M, n)], output_dtypes=[mx.bfloat16])[0]
        return run

    canonical_config = {"id": "canonical_clone_s2_r4", "num_simdgroups": 2, "results_per_simdgroup": 4, "rationale": "literal qmv_fast_impl execution geometry"}
    def compare(reference, candidate):
        mx.eval(reference, candidate)
        delta, equal = mx.abs(reference.astype(mx.float32) - candidate.astype(mx.float32)), mx.equal(reference, candidate)
        mx.eval(delta, equal)
        return {"shape_equal": tuple(reference.shape) == tuple(candidate.shape), "canonical_shape": list(reference.shape), "candidate_shape": list(candidate.shape), "canonical_dtype": str(reference.dtype), "candidate_dtype": str(candidate.dtype), "exact_equal": bool(mx.all(equal).item()), "max_abs_diff": float(mx.max(delta).item()), "mean_abs_diff": float(mx.mean(delta).item())}
    def bench(left, right, x, p, n):
        for _ in range(WARMUPS): mx.eval(left(x, p), right(x, p, n))
        mx.reset_peak_memory(); a, b = [], []
        for _ in range(ABBA_CYCLES):
            for side, sink in (("a", a), ("b", b), ("b", b), ("a", a)):
                started = time.perf_counter(); out = left(x, p) if side == "a" else right(x, p, n); mx.eval(out); sink.append(time.perf_counter()-started)
        return {"canonical": stats(a), "candidate": stats(b), "candidate_over_canonical_median_ratio": statistics.median(b)/statistics.median(a), "median_microseconds_saved": (statistics.median(a)-statistics.median(b))*1e6, "active_memory_bytes": int(mx.get_active_memory()), "peak_memory_bytes": int(mx.get_peak_memory())}

    clone_results = {}
    for name, (_prefix, k, n) in PROJECTIONS.items():
        p, x = payloads[name], probes[k][0][1]
        clone = build_kernel(canonical_config, k, n)
        numerical = {label: compare(qmatmul(z, p), clone(z, p, n)) for label, z in probes[k]}
        clone_results[name] = {"headers": headers[name], "numerical": numerical, "timing": bench(qmatmul, clone, x, p, n)}
    clone_exact = all(case["exact_equal"] for r in clone_results.values() for case in r["numerical"].values())
    clone_ratios = [r["timing"]["candidate_over_canonical_median_ratio"] for r in clone_results.values()]
    clone_representative = max(clone_ratios) <= CLONE_REPRESENTATIVE_MAX_RATIO
    clone_gate = {"all_21_comparisons_bit_exact": clone_exact, "worst_clone_over_canonical_median_ratio": max(clone_ratios), "predeclared_max_ratio": CLONE_REPRESENTATIVE_MAX_RATIO, "performance_representative": clone_representative, "passed": clone_exact and clone_representative}

    variants_results = {}
    if clone_gate["passed"]:
        for config in VARIANTS:
            per_projection = {}
            for name, (_prefix, k, n) in PROJECTIONS.items():
                runner = build_kernel(config, k, n)
                p, x = payloads[name], probes[k][0][1]
                numerical = {label: compare(qmatmul(z, p), runner(z, p, n)) for label, z in probes[k]}
                per_projection[name] = {"numerical": numerical, "timing": bench(qmatmul, runner, x, p, n)}
            exact = all(case["exact_equal"] for r in per_projection.values() for case in r["numerical"].values())
            saving = {name: r["timing"]["median_microseconds_saved"] / 1e6 * 36 for name, r in per_projection.items()}
            # Matching Stretch-028 telemetry is used for gate/up/down. Applying
            # the mean Q/K/V/O fraction to whole attention is an explicit upper
            # bound, not a causal claim.
            fractions = {name: per_projection[name]["timing"]["median_microseconds_saved"] / 1e6 / per_projection[name]["timing"]["canonical"]["median_seconds"] for name in PROJECTIONS}
            mlp = sum(STRETCH_028_COMPONENT_SECONDS[name] * fractions[name] for name in ("gate_proj", "up_proj", "down_proj"))
            attention_bound = STRETCH_028_COMPONENT_SECONDS["attention"] * statistics.fmean(fractions[name] for name in ("q_proj", "k_proj", "v_proj", "o_proj"))
            estimate = {"x36_direct_projection_savings_seconds": saving, "mlp_matched_component_estimated_seconds_per_block": mlp, "attention_projection_optimistic_bound_seconds_per_block": attention_bound, "mlp_plus_attention_bound_seconds_per_block": mlp + attention_bound, "mlp_plus_attention_bound_fraction_of_stretch031_block": (mlp + attention_bound) / STRETCH_031_BLOCK_SECONDS}
            variants_results[config["id"]] = {"predeclared_config": config, "per_projection": per_projection, "all_21_comparisons_bit_exact": exact, "weighted_estimate": estimate}

    qualifying = [name for name, r in variants_results.items() if r["all_21_comparisons_bit_exact"] and r["weighted_estimate"]["mlp_plus_attention_bound_fraction_of_stretch031_block"] >= .05]
    if not clone_gate["passed"]:
        classification, decision = "STRETCH_037_M1_QMV_FAST_TUNING_INVESTIGATION_ONLY", "INVESTIGATION_ONLY"
    elif qualifying:
        classification, decision = "STRETCH_037_M1_QMV_FAST_TUNING_GO", "GO"
    else:
        classification, decision = "STRETCH_037_M1_QMV_FAST_TUNING_NO_GO", "NO-GO"
    final = {"experiment": "Stretch 037 M1-specific qmv_fast tuning feasibility", "classification": classification, "decision": decision, "diagnostic_only": True, "scientific_abba_started": False, "full_model_abba_started": False, "timestamp": datetime.now(timezone.utc).isoformat(), "runtime": {"python": sys.executable, "prefix": sys.prefix, "versions": versions, "device_info": info}, "model": {"weight_sha256": sha256_file(weight_path), "layer": LAYER_ID, "quantization": {"bits": 3, "group_size": 64, "mode": "affine"}}, "source_audit": audit, "methodology": {"M": M, "non_batched": True, "transpose": True, "canonical_clone_gate": "strict bit exact all inputs and no projection clone/canonical median >1.50", "warmups_excluded": WARMUPS, "samples_per_side": ABBA_CYCLES*2, "balanced_order": "canonical -> candidate -> candidate -> canonical", "no_cache_purge": True, "no_installed_runtime_modification": True, "predeclared_variants": list(VARIANTS), "no_bruteforce": True}, "setup_active_memory_bytes": setup_active, "canonical_clone": {"kernel_source_ids": [key for key in kernel_meta if key.startswith(canonical_config["id"])], "per_projection": clone_results, "gate": clone_gate}, "variants": variants_results, "qualifying_variants": qualifying, "kernel_sources": kernel_meta}
    summary_path.write_text(json.dumps(final, indent=2)+"\n")
    print(f"Classification: {classification}")
    print(f"Clone gate: exact={clone_exact} worst_ratio={max(clone_ratios):.6f} pass={clone_gate['passed']}")
    print(f"Summary: {summary_path}")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--child": return child_main(Path(sys.argv[2]), Path(sys.argv[3]))
    repo = Path(__file__).resolve().parents[1]; launcher, model = repo/CANONICAL_CHILD_PYTHON, repo/MODEL_DIR
    if not launcher.is_symlink() or not (model/"model.safetensors").is_file(): raise RuntimeError("missing canonical launcher/model")
    run_dir = repo/"results-local/stretch/m1-qmv-fast-tuning-037-feasibility"/datetime.now().strftime("%Y%m%d-%H%M%S"); run_dir.mkdir(parents=True, exist_ok=False)
    child_summary, stdout, stderr = run_dir/"child-summary.json", run_dir/"child-stdout.txt", run_dir/"child-stderr.txt"
    command = [str(launcher), str(Path(__file__).resolve()), "--child", str(model), str(child_summary)]
    started=time.perf_counter()
    with stdout.open("w") as out, stderr.open("w") as err: proc=subprocess.run(command, cwd=repo, stdout=out, stderr=err, check=False)
    if proc.returncode or not child_summary.is_file(): raise RuntimeError(f"child failure {proc.returncode}; stdout={stdout}; stderr={stderr}")
    child=json.loads(child_summary.read_text())
    summary={"experiment": child["experiment"], "classification": child["classification"], "decision": child["decision"], "diagnostic_only": True, "scientific_abba_started": False, "full_model_abba_started": False, "canonical_launcher_literal": str(launcher), "command": command, "child_summary": str(child_summary), "child_stdout": str(stdout), "child_stderr": str(stderr), "child_wall_seconds": time.perf_counter()-started, "child": child}
    (run_dir/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(stdout.read_text(), end=""); print(f"Parent summary: {run_dir/'summary.json'}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
