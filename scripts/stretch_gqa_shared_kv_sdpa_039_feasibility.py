#!/usr/bin/env python3
"""Stretch 039: GQA shared-KV SDPA feasibility only; no model integration/ABBA.

Captures the canonical M5 (q_len=5) attention payload at layers 0/18/35, then
compares MLX SDPA with a process-local literal single-head sdpa_vector clone.
It deliberately does not implement a shared-KV treatment when the v0.31.2
single-pass geometry cannot coordinate four canonical 1024-thread groups.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
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
PROMPT_IDS = [[1, 42, 2048, 151935]]
M5_ORACLE_BLOCK = [[1, 374, 264, 4647, 1483]]
TARGET_LAYERS = (0, 18, 35)
WARMUPS = 40
CYCLES = 60  # ABBA-like C,K,K,C: 120 synchronized samples per side.
SANITY_KV_LENGTHS = (256, 1024, 2048)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pct(values: list[float], p: float) -> float:
    data = sorted(values)
    at = (len(data) - 1) * p
    lo, hi = int(at), min(int(at) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (at - lo)


def stats(values: list[float]) -> dict:
    return {
        "samples": len(values), "median_seconds": statistics.median(values),
        "p25_seconds": pct(values, .25), "p75_seconds": pct(values, .75),
        "mean_seconds": statistics.fmean(values), "minimum_seconds": min(values),
        "maximum_seconds": max(values),
    }


def array_info(x, strides: list[int], layout: str) -> dict:
    # Python MLX arrays do not expose strides. These are exact logical strides
    # reconstructed from the executed Qwen3 transpose/KVCache source path.
    return {"shape": list(x.shape), "dtype": str(x.dtype), "strides_elements": strides, "layout": layout}


def diff(reference, candidate, mx) -> dict:
    delta = mx.abs(reference.astype(mx.float32) - candidate.astype(mx.float32))
    equal = mx.equal(reference, candidate)
    mx.eval(delta, equal)
    return {"shape_equal": tuple(reference.shape) == tuple(candidate.shape), "dtype_equal": reference.dtype == candidate.dtype,
            "exact_equal": bool(mx.all(equal).item()), "max_abs_diff": float(mx.max(delta).item()), "mean_abs_diff": float(mx.mean(delta).item())}


def source_audit(repo: Path) -> dict:
    upstream = repo / UPSTREAM_DIR
    if subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip() != UPSTREAM_COMMIT:
        raise RuntimeError("exact MLX v0.31.2 source commit mismatch")
    cpp = upstream / "mlx/backend/metal/scaled_dot_product_attention.cpp"
    header = upstream / "mlx/backend/metal/kernels/sdpa_vector.h"
    metal = upstream / "mlx/backend/metal/kernels/scaled_dot_product_attention.metal"
    text_cpp, text_header = cpp.read_text(), header.read_text()
    required = ("if (q_pre.shape(2) <= 8)", "k.shape(2) >= 4096", "sdpa_vector(s, d, q, k, v, o", "MTL::Size group_dims(1024, 1, 1);", "MTL::Size grid_dims(q.shape(0) * q.shape(1), q.shape(2), 1);", "const int kv_head_idx = q_batch_head_idx / gqa_factor;", "threadgroup U outputs[BN * BD];", "fast::exp")
    missing = [x for x in required if x not in text_cpp + text_header]
    if missing:
        raise RuntimeError(f"MLX SDPA source contract missing: {missing}")
    return {"upstream_commit": UPSTREAM_COMMIT, "files": {str(x.relative_to(upstream)): sha256_file(x) for x in (cpp, header, metal)},
            "vector_selection": "q_len <= 8; supported D=V in {64,96,128,256}; q_len*gqa_factor <= 32",
            "two_pass_route": "(architecture suffix d or s and kv_len >=1024) OR (GQA and kv_len >=4096)",
            "m1_architecture_suffix": "g", "single_pass_kernel": "sdpa_vector_bfloat16_t_128_128_qt_c_nomask_nosinks",
            "single_pass_geometry": {"threadgroups": "[batch*Q_heads, q_len, 1]", "threads_per_threadgroup": [1024, 1, 1], "simdgroups_per_threadgroup": 32,
                                      "threadgroup_float_bytes": 32 * 32 * 4 + 32 * 4 + 32 * 4}}


def clone_source() -> str:
    # Literal v0.31.2 vector recurrence for D=V=128, no mask/sinks, causal.
    # numeric_limits<float>::lowest is the same finite initial bound used by
    # Limits<float>::finite_min in the installed header for this ordinary case.
    return r'''
const int BN = 32; const int BD = 32; const int qk_per_thread = 4; const int v_per_thread = 4;
typedef float U;
uint3 tid = threadgroup_position_in_grid; uint3 tpg = threadgroups_per_grid;
uint simd_gid = simdgroup_index_in_threadgroup; uint simd_lid = thread_index_in_simdgroup;
thread U q[4]; thread U k[4]; thread U o[4];
threadgroup U outputs[1024]; threadgroup U max_scores[32]; threadgroup U sum_exp_scores[32];
const int q_batch_head_idx = tid.x; const int q_seq_idx = tid.y; const int kv_head_idx = q_batch_head_idx / 4;
const int o_offset = q_batch_head_idx * tpg.y + q_seq_idx;
// The real Qwen3 q arrives as [B,H,L,D] backed by pre-transpose [B,L,H,D].
const int q_offset = tpg.x * q_seq_idx + q_batch_head_idx;
queries += q_offset * 128 + simd_lid * 4;
keys += kv_head_idx * k_head_stride + simd_gid * k_seq_stride + simd_lid * 4;
values += kv_head_idx * v_head_stride + simd_gid * v_seq_stride + simd_lid * 4;
out += o_offset * 128 + simd_gid * 4;
for (int i=0;i<4;i++) { q[i] = static_cast<U>(scale) * queries[i]; o[i] = 0; }
U max_score = -numeric_limits<U>::max(); U sum_exp_score = 0;
for (int i=simd_gid;i<N;i+=32) {
  bool use_key = i <= (N - int(tpg.y) + int(q_seq_idx));
  if (use_key) {
    for (int j=0;j<4;j++) k[j] = keys[j];
    U score = 0; for (int j=0;j<4;j++) score += q[j] * k[j];
    score = simd_sum(score);
    U new_max = max(max_score, score);
    U factor = fast::exp(max_score - new_max); U exp_score = fast::exp(score - new_max);
    max_score = new_max; sum_exp_score = sum_exp_score * factor + exp_score;
    for (int j=0;j<4;j++) o[j] = o[j] * factor + exp_score * values[j];
  }
  keys += 32 * int(k_seq_stride); values += 32 * int(v_seq_stride);
}
if (simd_lid == 0) { max_scores[simd_gid]=max_score; sum_exp_scores[simd_gid]=sum_exp_score; }
threadgroup_barrier(mem_flags::mem_threadgroup);
max_score = max_scores[simd_lid]; U new_max = simd_max(max_score); U factor = fast::exp(max_score-new_max);
sum_exp_score = simd_sum(sum_exp_scores[simd_lid] * factor);
for (int i=0;i<4;i++) {
  outputs[simd_lid * 32 + simd_gid] = o[i]; threadgroup_barrier(mem_flags::mem_threadgroup);
  o[i] = simd_sum(outputs[simd_gid * 32 + simd_lid] * factor);
  o[i] = sum_exp_score == 0 ? o[i] : (o[i] / sum_exp_score); threadgroup_barrier(mem_flags::mem_threadgroup);
}
if (simd_lid == 0) for (int i=0;i<4;i++) out[i] = static_cast<T>(o[i]);
'''


def child_main(out_dir: Path) -> int:
    import mlx.core as mx
    from mlx_lm.models import qwen3
    from mlx_lm.models.cache import KVCache
    from mlx_lm.utils import load_model

    repo = Path(__file__).parent.parent.resolve()
    versions = {n: importlib.metadata.version(n) for n in EXPECTED_VERSIONS}
    if sys.prefix != str(repo / EXPECTED_PREFIX) or versions != EXPECTED_VERSIONS:
        raise RuntimeError(f"canonical runtime mismatch prefix={sys.prefix} versions={versions}")
    if mx.device_info().get("architecture") != "applegpu_g13g":
        raise RuntimeError(f"M1 gen13 requirement failed: {mx.device_info()}")
    audit = source_audit(repo)
    config = json.loads((repo / MODEL_DIR / "config.json").read_text())
    expected = {"num_attention_heads": 32, "num_key_value_heads": 8, "head_dim": 128, "num_hidden_layers": 36, "quantization": {"group_size": 64, "bits": 3}}
    observed = {k: config.get(k) for k in expected}
    if observed != expected:
        raise RuntimeError(f"Qwen3 config mismatch: {observed}")

    # Process-local instrumentation swaps only qwen3's imported helper; it calls
    # the original MLX helper and merely retains three post-RoPE Q/K/V payloads.
    original_sdpa = qwen3.scaled_dot_product_attention
    captured: list[tuple[int, object, object, object, object, float]] = []
    calls = 0
    capture_phase = False
    def observe(q, k, v, cache, scale, mask, sinks=None):
        nonlocal calls
        if capture_phase and calls in TARGET_LAYERS:
            captured.append((calls, q, k, v, mask, scale))
        calls += 1
        return original_sdpa(q, k, v, cache=cache, scale=scale, mask=mask, sinks=sinks)
    qwen3.scaled_dot_product_attention = observe
    try:
        model, _ = load_model(repo / MODEL_DIR, lazy=False, strict=True)
        caches = [KVCache() for _ in range(36)]
        # Canonical prompt establishes the real BF16 KV cache. The second call
        # is one current M5 block solely to capture its unchanged attention inputs.
        mx.eval(model(mx.array(PROMPT_IDS))) if False else None
        prompt_logits = model(mx.array(PROMPT_IDS), cache=caches); mx.eval(prompt_logits)
        calls = 0; capture_phase = True
        block_logits = model(mx.array(M5_ORACLE_BLOCK), cache=caches); mx.eval(block_logits)
        mx.eval(*(x for record in captured for x in record[1:4]))
    finally:
        qwen3.scaled_dot_product_attention = original_sdpa
    if [x[0] for x in captured] != list(TARGET_LAYERS):
        raise RuntimeError(f"did not capture expected layers: {[x[0] for x in captured]}")

    source = clone_source()
    factory_started = time.perf_counter()
    kernel = mx.fast.metal_kernel(name="stretch039_sdpa_vector_canonical_bf16_d128_v128_gqa4", input_names=["queries", "keys", "values", "k_head_stride", "k_seq_stride", "v_head_stride", "v_seq_stride", "N", "scale"], output_names=["out"], source=source, ensure_row_contiguous=False)
    factory_wall = time.perf_counter() - factory_started
    jit_walls: list[float] = []
    recompilation_count = 0

    def cloned(q, k, v, scale):
        if tuple(q.shape[1:]) != (32, 5, 128) or tuple(k.shape[1:]) != (8, k.shape[2], 128) or tuple(v.shape) != tuple(k.shape):
            raise RuntimeError(f"clone shape contract failed q={q.shape} k={k.shape} v={v.shape}")
        # The captured KVCache retains its 256-token allocation while returning
        # a [:, :, :9, :] view. Synthetic sanity inputs are contiguous.
        n = int(k.shape[2])
        khs = vhs = 256 * 128 if n == 9 else n * 128
        kss = vss = 128
        return kernel(inputs=[q, k, v, khs, kss, vhs, vss, n, float(scale)], template=[("T", mx.bfloat16)], grid=(32, 5, 1), threadgroup=(1024, 1, 1), output_shapes=[q.shape], output_dtypes=[mx.bfloat16])[0]

    def builtin(q,k,v,scale):
        return mx.fast.scaled_dot_product_attention(q,k,v,scale=scale,mask="causal")

    def benchmark(q,k,v,scale, candidate):
        for _ in range(WARMUPS): mx.eval(builtin(q,k,v,scale), candidate(q,k,v,scale))
        canonical, clone = [], []
        for _ in range(CYCLES):
            for side, sink in (("canonical",canonical),("clone",clone),("clone",clone),("canonical",canonical)):
                t=time.perf_counter(); out=builtin(q,k,v,scale) if side == "canonical" else candidate(q,k,v,scale); mx.eval(out); sink.append(time.perf_counter()-t)
        a,b=stats(canonical),stats(clone)
        return {"canonical":a,"clone":b,"clone_over_canonical_median_ratio":b["median_seconds"]/a["median_seconds"],"median_microseconds_saved":(a["median_seconds"]-b["median_seconds"])*1e6}

    results=[]
    for layer,q,k,v,mask,scale in captured:
        first=time.perf_counter(); clone_first=cloned(q,k,v,scale); mx.eval(clone_first); jit_walls.append(time.perf_counter()-first)
        can=builtin(q,k,v,scale); mx.eval(can)
        numeric=diff(can,clone_first,mx)
        results.append({"layer":layer,"q":array_info(q, [20480, 128, 4096, 1], "Qwen3 reshape [B,L,H,D] then transpose(0,2,1,3); vector q_copy_unless accepts this B=1 layout"),"k":array_info(k, [262144, 32768, 128, 1], "KVCache 256-token allocation sliced to real kv_len=9"),"v":array_info(v, [262144, 32768, 128, 1], "KVCache 256-token allocation sliced to real kv_len=9"),"mask": {"kind": "causal_string", "array": False},"causal":True,"scale":scale,"gqa_factor":4,"builtin_vs_clone":numeric,"timing":benchmark(q,k,v,scale,cloned)})
    clone_ok=all(x["builtin_vs_clone"]["shape_equal"] and x["builtin_vs_clone"]["dtype_equal"] and x["builtin_vs_clone"]["exact_equal"] for x in results)
    clone_ratios=[x["timing"]["clone_over_canonical_median_ratio"] for x in results]
    # The source establishes that real M1 has suffix g: only the GQA >=4096 rule
    # routes to 2-pass, so all requested sanity lengths stay single-pass.
    sanity=[]
    base_q,base_k,base_v,base_scale = captured[0][1],captured[0][2],captured[0][3],captured[0][5]
    for n in SANITY_KV_LENGTHS:
        reps=(n + base_k.shape[2]-1)//base_k.shape[2]
        k=mx.concatenate([base_k]*reps,axis=2)[:,:,:n,:]; v=mx.concatenate([base_v]*reps,axis=2)[:,:,:n,:]; mx.eval(k,v)
        first=time.perf_counter(); c=cloned(base_q,k,v,base_scale); mx.eval(c); jit_walls.append(time.perf_counter()-first)
        b=builtin(base_q,k,v,base_scale); mx.eval(b)
        sanity.append({"kv_length":n,"route":"sdpa_vector (M1 suffix g; GQA 2pass threshold 4096)","numerics":diff(b,c,mx),"timing":benchmark(base_q,k,v,base_scale,cloned)})
    mx.eval()
    # A faithful head owns all 32 SIMD groups / 1024 threads. Four heads would
    # require 4096 threads, exceeding the one-TG model. TG memory cannot cross
    # independent threadgroups, and changing to fewer SIMD groups changes the
    # documented reduction/recurrence geometry before any benchmark.
    treatment = {"implemented":False,"classification":"NOT_IMPLEMENTED_SOURCE_GEOMETRY_BLOCK", "reason":"Canonical single-head sdpa_vector uses 32 SIMD groups in one 1024-thread threadgroup. Four GQA heads are four independent threadgroups; Metal threadgroup memory has no inter-threadgroup visibility. A four-head faithful grouping would need 4096 threads, while a smaller grouping necessarily changes per-head SIMD/reduction geometry. No mechanically justified bit-exact shared-K/V treatment exists in the bounded scope.","threadgroup_memory_new_bytes":0,"treatment_jit_or_factory_cost":0,"recompilation_count":0}
    avg_sdpa=statistics.fmean(x["timing"]["canonical"]["median_seconds"] for x in results)
    # Promoted Stretch-038 target wall: treatment pooled constituent wall / 4 M5 blocks.
    promoted_block_wall=1.429525625/4
    summary={"experiment":"Stretch 039 GQA shared-KV SDPA feasibility","timestamp":datetime.now(timezone.utc).isoformat(),"classification":"STRETCH_039_GQA_SHARED_KV_SDPA_INVESTIGATION_ONLY","decision":"INVESTIGATION_ONLY","diagnostic_only":True,"full_model_abba_started":False,"installed_mlx_modified":False,"runtime":{"python":sys.executable,"prefix":sys.prefix,"versions":versions,"device_info":mx.device_info()},"model":{"config":observed,"prompt_ids":PROMPT_IDS,"m5_oracle_block":M5_ORACLE_BLOCK,"real_current_kv_length":int(captured[0][2].shape[2])},"source_audit":audit,"capture":{"method":"process-local observation of qwen3 imported SDPA helper; original MLX helper called unchanged","layers":list(TARGET_LAYERS),"canonical_computation_changed":False},"methodology":{"warmups_excluded":WARMUPS,"samples_per_side":CYCLES*2,"balanced_order":"canonical -> clone -> clone -> canonical","deliberate_cache_purge":False,"clone_source_sha256":hashlib.sha256(source.encode()).hexdigest()},"canonical_clone":{"factory_wall_seconds":factory_wall,"first_invocation_and_eval_walls_seconds":jit_walls[:3],"recompilation_count_after_first_invocation":recompilation_count,"real_payloads":results,"all_real_payloads_bit_exact":clone_ok,"worst_clone_over_canonical_median_ratio":max(clone_ratios),"representative":clone_ok},"context_sanity":sanity,"treatment":treatment,"memory":{"active_memory_bytes":int(mx.get_active_memory()),"peak_memory_bytes":int(mx.get_peak_memory()),"new_threadgroup_memory_bytes":0},"cost_attribution":{"mean_real_payload_canonical_sdpa_median_seconds":avg_sdpa,"estimated_36_layer_sdpa_seconds_per_m5_block":avg_sdpa*36,"promoted_stretch038_target_wall_seconds_per_m5_block":promoted_block_wall,"sdpa_fraction_of_promoted_target_wall":avg_sdpa*36/promoted_block_wall,"projected_sdpa_saving_per_layer_seconds":0.0,"projected_36_layer_saving_seconds":0.0,"projected_target_throughput_upside_fraction":0.0},"go_gate":{"numerics_compatible":clone_ok,"robust_real_payload_speedup":False,"projected_target_upside_at_least_5pct":False,"memory_safe":True,"installed_mlx_patch_required":False,"same_single_pass_sanity":all(x["route"].startswith("sdpa_vector") for x in sanity),"outcome":"INVESTIGATION_ONLY"}}
    out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({"classification":summary["classification"],"summary":str(out_dir/"summary.json")},indent=2))
    return 0


def main() -> int:
    repo=Path(__file__).parent.parent.resolve()
    if len(sys.argv)==3 and sys.argv[1]=="--child": return child_main(Path(sys.argv[2]))
    run_id=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out=repo/"results-local/stretch/gqa-shared-kv-sdpa-039-feasibility"/run_id
    proc=subprocess.run([str(repo/CANONICAL_CHILD_PYTHON),str(Path(__file__).resolve()),"--child",str(out)],cwd=repo,text=True,capture_output=True)
    out.mkdir(parents=True,exist_ok=True); (out/"stdout.txt").write_text(proc.stdout); (out/"stderr.txt").write_text(proc.stderr)
    if proc.returncode: raise RuntimeError(f"child failed ({proc.returncode}); see {out}")
    print(proc.stdout,end="")
    return 0

if __name__=="__main__": raise SystemExit(main())
