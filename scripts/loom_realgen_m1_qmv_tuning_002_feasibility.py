#!/usr/bin/env python3
"""REALGEN 002 M1 qmv_fast tuning feasibility only.

CONTROL is ordinary MLX 0.31.2 M1 qmv_fast.  The only possible treatment is a
process-local M1-specific S1_R8 Metal kernel.  This does not reuse or promote
Stretch-037's M5 implementation.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.metadata
import json
import re
import resource
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load
from mlx_lm.models import cache as mlx_cache

REPO = Path(__file__).resolve().parents[1]
MODEL_DIR = REPO / "results-local/mlx/models/Qwen3-8B-3bit"
LAUNCHER = REPO / "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
CANONICAL_PREFIX = REPO / "results-local/mlx/venv-mlx-lm-0.31.3"
UPSTREAM = REPO / "results-local/stretch/m5-quantized-kernel-path-035/upstream/mlx-v0.31.2"
RESULT_ROOT = REPO / "results-local/realgen/m1-qmv-tuning-002-feasibility"
EXPECTED = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
UPSTREAM_COMMIT = "68cf2fddd8de5edd8ab3d926391772b2e2cedad8"
WARMUPS, CYCLES = 40, 60  # 120 samples/side via C,T,T,C
M = 1
SHAPES = ((4096, 4096), (4096, 1024), (4096, 12288), (12288, 4096), (4096, 151936))
CONTROL_SYMBOL = "affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0"
PROMPT_ID = "chat_02"
SYSTEM = "You are a helpful assistant. Answer clearly and directly."
USER = "Give a practical three-step plan for preparing a healthy vegetarian lunch on a busy weekday."
# Existing public REALGEN-001 chat_02 continuation, frozen to its first ten IDs.
REPLAY_IDS = (334, 19641, 12, 8304, 9680, 369, 264, 43354, 42700, 8821)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def pct(a: list[float], p: float) -> float:
    a = sorted(a); x = (len(a) - 1) * p; lo, hi = int(x), min(int(x) + 1, len(a) - 1)
    return a[lo] + (a[hi] - a[lo]) * (x - lo)


def distribution(samples: list[float]) -> dict[str, Any]:
    return {"samples": len(samples), "median_microseconds": statistics.median(samples) * 1e6,
            "p25_microseconds": pct(samples, .25) * 1e6, "p75_microseconds": pct(samples, .75) * 1e6,
            "mean_microseconds": statistics.fmean(samples) * 1e6}


def host() -> dict[str, Any]:
    pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
    free = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    swap = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
    used = re.search(r"used = ([0-9.,]+)([MG])", swap)
    if not free or not used:
        raise RuntimeError("REALGEN_002_HOST_TELEMETRY_UNAVAILABLE")
    swap_mb = float(used.group(1).replace(",", ".")) * (1024 if used.group(2) == "G" else 1)
    return {"utc": datetime.now(timezone.utc).isoformat(), "free_memory_percent": int(free.group(1)),
            "swap_used_mb": swap_mb, "mlx_active_bytes": int(mx.get_active_memory()),
            "mlx_peak_bytes": int(mx.get_peak_memory()),
            "mlx_cache_bytes": int(mx.get_cache_memory()) if hasattr(mx, "get_cache_memory") else None,
            "process_max_rss_bytes_diagnostic": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}


def assert_runtime() -> dict[str, str]:
    seen = {k: importlib.metadata.version(k) for k in EXPECTED}
    if Path(sys.prefix) != CANONICAL_PREFIX or seen != EXPECTED:
        raise RuntimeError(f"REALGEN_002_RUNTIME_MISMATCH prefix={sys.prefix} versions={seen}")
    return seen


def audit_source() -> dict[str, Any]:
    commit = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
    cpp, hdr = UPSTREAM / "mlx/backend/metal/quantized.cpp", UPSTREAM / "mlx/backend/metal/kernels/quantized.h"
    text = cpp.read_text() + hdr.read_text()
    required = ("int bn = 8;", "int bk = 32;", "MTL::Size group_dims(bk, 2, 1);",
                "MTL::Size grid_dims(M, (N + bn - 1) / bn, B);", "N % bn == 0 && K % 512 == 0",
                "qmv_fast_impl", "constexpr int num_simdgroups = 2;", "constexpr int results_per_simdgroup = 4;",
                "[[kernel]] void affine_qmv_fast")
    if commit != UPSTREAM_COMMIT or any(x not in text for x in required):
        raise RuntimeError("REALGEN_002_EXACT_MLX_SOURCE_AUDIT_FAIL")
    return {"upstream_commit": commit, "quantized_cpp_sha256": sha256(cpp), "quantized_header_sha256": sha256(hdr),
            "control_symbol_resolved_from_exact_source": CONTROL_SYMBOL, "M": 1, "dtype": "BF16", "mode": "affine",
            "bits": 3, "group_size": 64, "transpose": True, "device": "Apple M1 applegpu_g13g (gen13)",
            "dispatch_predicate": "N % 8 == 0 && K % 512 == 0", "grid": "(M, N/8, 1) = (1, N/8, 1)",
            "canonical_threadgroup": [32, 2, 1], "canonical_simdgroups_per_threadgroup": 2,
            "canonical_output_rows_per_simdgroup": 4, "canonical_output_rows_per_threadgroup": 8,
            "packed_layout": "3-bit: 8 values / 3 bytes; packed U32 rows, K*3/32 words",
            "scale_bias_addressing": "row*K/64 + lane/4, advanced by 8 per 512-K block",
            "invariants": ["16 activation values/lane", "512-K block", "x load/scaling order and x sum", "scale*decoded_dot + sum(x)*bias", "float accumulation", "simd_sum", "BF16 store", "row-major output"]}


def metal_source(simdgroups: int, rows: int, k: int, n: int) -> str:
    """M1-specific reimplementation of MLX v0.31.2 qmv_fast, fixed M=1."""
    return f'''// Derived from MLX v0.31.2 quantized.h qmv_fast_impl (MIT). M1 only.
uint lane = thread_index_in_simdgroup;
uint simd_gid = simdgroup_index_in_threadgroup;
uint3 tid = threadgroup_position_in_grid;
const device uchar* ws = (const device uchar*)w;
thread float x_thread[16];
thread float result[{rows}] = {{0}};
const int out_row = tid.y * ({simdgroups} * {rows}) + simd_gid * {rows};
const int in_vec_size_w = {k} * 3 / 8;
const int in_vec_size_g = {k} / 64;
ws += out_row * in_vec_size_w + lane * 6;
scales += out_row * in_vec_size_g + lane / 4;
biases += out_row * in_vec_size_g + lane / 4;
x += tid.x * {k} + lane * 16;
y += tid.x * {n} + out_row;
for (int kk = 0; kk < {k}; kk += 512) {{
  float sum = 0;
  for (int i = 0; i < 16; i += 8) {{
    sum += x[i] + x[i+1] + x[i+2] + x[i+3] + x[i+4] + x[i+5] + x[i+6] + x[i+7];
    x_thread[i]=x[i]; x_thread[i+1]=x[i+1]/8.0f; x_thread[i+2]=x[i+2]/64.0f; x_thread[i+3]=x[i+3]/2.0f;
    x_thread[i+4]=x[i+4]/16.0f; x_thread[i+5]=x[i+5]/128.0f; x_thread[i+6]=x[i+6]/4.0f; x_thread[i+7]=x[i+7]/32.0f;
  }}
  for (int row=0; row<{rows}; row++) {{
    const device uchar* wl=(const device uchar*)(ws + row*in_vec_size_w);
    const device T* sl=scales + row*in_vec_size_g; const device T* bl=biases + row*in_vec_size_g;
    float accum=0; const thread float* xt=x_thread;
    for (int i=0; i<2; i++) {{ xt += 8*i; wl += 3*i;
      accum+=(wl[0]&0x07)*xt[0]; accum+=(wl[0]&0x38)*xt[1]; accum+=(wl[0]&0xc0)*xt[2]; accum+=(wl[1]&0x01)*(xt[2]*256.0f);
      accum+=(wl[1]&0x0e)*xt[3]; accum+=(wl[1]&0x70)*xt[4]; accum+=(wl[1]&0x80)*xt[5]; accum+=(wl[2]&0x03)*(xt[5]*256.0f);
      accum+=(wl[2]&0x1c)*xt[6]; accum+=(wl[2]&0xe0)*xt[7]; }}
    result[row] += sl[0]*accum + sum*bl[0];
  }}
  ws += 192; scales += 8; biases += 8; x += 512;
}}
for (int row=0; row<{rows}; row++) {{ result[row]=simd_sum(result[row]); if(lane==0) y[row]=static_cast<T>(result[row]); }}
'''


def comparison(control: mx.array, candidate: mx.array) -> dict[str, Any]:
    mx.eval(control, candidate)
    eq = mx.equal(control, candidate); delta = mx.abs(control.astype(mx.float32) - candidate.astype(mx.float32))
    mx.eval(eq, delta)
    return {"shape_equal": list(control.shape) == list(candidate.shape), "control_dtype": str(control.dtype), "candidate_dtype": str(candidate.dtype),
            "bf16_equal": control.dtype == candidate.dtype == mx.bfloat16,
            "bit_exact": bool(mx.all(eq).item()), "max_abs_diff": float(mx.max(delta).item()), "mean_abs_diff": float(mx.mean(delta).item())}


def qmm(x: mx.array, payload: tuple[mx.array, mx.array, mx.array]) -> mx.array:
    return mx.quantized_matmul(x, *payload, transpose=True, group_size=64, bits=3, mode="affine")


def make_runner(kind: str, k: int, n: int, registry: dict[str, Any]) -> Any:
    simdgroups, rows = (2, 4) if kind == "canonical_clone_s2_r4" else (1, 8)
    source = metal_source(simdgroups, rows, k, n)
    name = f"realgen002_{kind}_m1_k{k}_n{n}"
    made = time.perf_counter()
    kernel = mx.fast.metal_kernel(name=name, input_names=["w", "scales", "biases", "x"], output_names=["y"], source=source, ensure_row_contiguous=True)
    registry[name] = {"kind": kind, "K": k, "N": n, "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "factory_seconds": time.perf_counter()-made,
                      "geometry": {"simdgroups_per_threadgroup": simdgroups, "output_rows_per_simdgroup": rows, "output_rows_per_threadgroup": simdgroups*rows}}
    def run(x: mx.array, p: tuple[mx.array, mx.array, mx.array]) -> mx.array:
        return kernel(inputs=[p[0], p[1], p[2], x], template=[("T", mx.bfloat16)], grid=(32, simdgroups*(n//(simdgroups*rows)), 1), threadgroup=(32, simdgroups, 1), output_shapes=[(1, 1, n)], output_dtypes=[mx.bfloat16])[0]
    return run


def benchmark(left: Any, right: Any, x: mx.array, p: tuple[mx.array, mx.array, mx.array]) -> dict[str, Any]:
    for _ in range(WARMUPS):
        mx.eval(left(x, p), right(x, p))
    c, t = [], []
    for _ in range(CYCLES):
        for is_control in (True, False, False, True):
            start = time.perf_counter(); out = left(x, p) if is_control else right(x, p); mx.eval(out)
            (c if is_control else t).append(time.perf_counter() - start)
    cd, td = distribution(c), distribution(t)
    return {"ordering": "CONTROL -> candidate -> candidate -> CONTROL", "warmups_excluded": WARMUPS,
            "control": cd, "candidate": td, "candidate_over_control_median_ratio": td["median_microseconds"] / cd["median_microseconds"],
            "median_microseconds_saved": cd["median_microseconds"] - td["median_microseconds"]}


def named_modules(model: Any) -> dict[int, str]:
    out = {id(model.lm_head): "lm_head"}
    for i in (0, 18, 35):
        layer = model.model.layers[i]
        for name, module in (("q", layer.self_attn.q_proj), ("k", layer.self_attn.k_proj), ("v", layer.self_attn.v_proj), ("o", layer.self_attn.o_proj),
                             ("gate", layer.mlp.gate_proj), ("up", layer.mlp.up_proj), ("down", layer.mlp.down_proj)):
            out[id(module)] = f"layer_{i}.{name}"
    return out


def capture_payloads(model: Any, token_ids: list[int], replay_ids: tuple[int, ...]) -> dict[str, list[dict[str, Any]]]:
    """Capture actual M1 activation/weight payloads at early/middle/late replay positions."""
    wanted, captured, original = named_modules(model), {}, nn.QuantizedLinear.__call__
    positions = {0: "early", 4: "middle", 9: "late"}; position = -1
    def audited(self: Any, x: mx.array) -> mx.array:
        key = wanted.get(id(self))
        if key and position in positions and x.ndim >= 2 and int(x.shape[-2]) == 1:
            k, n = (int(self["weight"].shape[1]) * 32 // int(self.bits), int(self["weight"].shape[0]))
            if (k, n) in SHAPES:
                captured.setdefault(key, []).append({"position": position, "position_label": positions[position], "x": x,
                    "payload": (self["weight"], self["scales"], self.get("biases")), "K": k, "N": n, "bits": int(self.bits), "group_size": int(self.group_size), "mode": self.mode})
        return original(self, x)
    nn.QuantizedLinear.__call__ = audited
    try:
        cache = mlx_cache.make_prompt_cache(model); prompt = mx.array(token_ids)
        model(prompt[:-1][None], cache=cache); mx.eval([c.state for c in cache])
        current = prompt[-1:]
        for pos, fixed in enumerate(replay_ids):
            position = pos; logits = model(current[None], cache=cache); mx.eval(logits)
            current = mx.array([fixed], dtype=mx.uint32)
    finally:
        nn.QuantizedLinear.__call__ = original
    required = {f"layer_{i}.{p}" for i in (0, 18, 35) for p in ("q", "k", "v", "o", "gate", "up", "down")} | {"lm_head"}
    if set(captured) != required or any(len(v) != 3 for v in captured.values()):
        raise RuntimeError(f"REALGEN_002_PAYLOAD_CAPTURE_INCOMPLETE got={sorted(captured)}")
    for values in captured.values(): mx.eval(*[z for item in values for z in (item["x"], *item["payload"])])
    return captured


def inject_treatment(model: Any, runners: dict[tuple[int, int], Any]) -> Any:
    original = nn.QuantizedLinear.__call__
    def treatment(self: Any, x: mx.array) -> mx.array:
        weight = self["weight"]; k, n = int(weight.shape[1]) * 32 // int(self.bits), int(weight.shape[0])
        if x.ndim >= 2 and int(x.shape[-2]) == 1 and self.mode == "affine" and self.group_size == 64 and self.bits == 3 and (k, n) in runners:
            out = runners[(k, n)](x, (weight, self["scales"], self.get("biases")))
            return out + self["bias"] if "bias" in self else out
        return original(self, x)
    nn.QuantizedLinear.__call__ = treatment
    return original


def replay(model: Any, prompt: list[int], ids: tuple[int, ...], treatment: bool, runners: dict[tuple[int, int], Any], timed: bool) -> dict[str, Any]:
    original = inject_treatment(model, runners) if treatment else None
    try:
        cache = mlx_cache.make_prompt_cache(model); p = mx.array(prompt)
        model(p[:-1][None], cache=cache); mx.eval([c.state for c in cache])
        current, logits_out, top1, offsets = p[-1:], [], [], []
        started = time.perf_counter()
        for fixed in ids:
            logits = model(current[None], cache=cache); choice = mx.argmax(logits[:, -1, :], axis=-1)
            mx.eval(logits, choice, [c.state for c in cache]); logits_out.append(logits[:, -1, :]); top1.append(int(choice.item())); offsets.append([int(c.offset) for c in cache])
            current = mx.array([fixed], dtype=mx.uint32)
        gc.collect(); mx.clear_cache(); gc.collect()
        wall = time.perf_counter() - started
        return {"wall_seconds": wall, "equivalent_tokens_per_second": len(ids)/wall, "logits": logits_out, "top1": top1, "offsets": offsets, "ids": list(ids), "timed": timed}
    finally:
        if original is not None: nn.QuantizedLinear.__call__ = original


def replay_compare(c: dict[str, Any], t: dict[str, Any]) -> dict[str, Any]:
    positions = [comparison(a, b) for a, b in zip(c["logits"], t["logits"])]
    return {"all_exact_logits": all(x["bit_exact"] and x["shape_equal"] and x["bf16_equal"] for x in positions), "per_position": positions,
            "top1_equal": c["top1"] == t["top1"], "fixed_replay_sequence_equal": c["ids"] == t["ids"] == list(REPLAY_IDS),
            "cache_offsets_equal": c["offsets"] == t["offsets"], "control_offsets": c["offsets"], "treatment_offsets": t["offsets"]}


def main() -> int:
    run = RESULT_ROOT / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"); run.mkdir(parents=True, exist_ok=False)
    summary: dict[str, Any] = {"experiment": "REALGEN 002 M1 qmv_fast tuning feasibility", "classification": "RUNNING", "feasibility_only": True,
                                "no_stretch_037_041_rerun": True, "no_mlx_032_runtime_comparison": True, "no_drafter": True, "no_cache_purge": True}
    try:
        versions = assert_runtime(); before = host(); summary["host_before_model_load"] = before
        if before["free_memory_percent"] < 60 or before["swap_used_mb"] > 5600:
            summary["classification"] = "REALGEN_002_NOT_STARTED_HOST_NOT_READY"; return 2
        audit = audit_source()
        model, tokenizer = load(str(MODEL_DIR), lazy=False); model.eval(); mx.eval(model.parameters())
        token_ids = [int(x) for x in tokenizer.apply_chat_template([{"role":"system", "content":SYSTEM}, {"role":"user", "content":USER}], tokenize=True, add_generation_prompt=True, enable_thinking=False)]
        payloads = capture_payloads(model, token_ids, REPLAY_IDS)
        kernel_meta: dict[str, Any] = {}; clone_runners, treatment_runners = {}, {}
        factory_started = time.perf_counter()
        for k, n in SHAPES:
            clone_runners[(k,n)] = make_runner("canonical_clone_s2_r4", k, n, kernel_meta)
        factory_clone = time.perf_counter()-factory_started
        # Force and separately time exactly one first dispatch/JIT per M1 shape before all excluded warmups.
        representative = {shape: next(item for records in payloads.values() for item in records if (item["K"], item["N"]) == shape) for shape in SHAPES}
        clone_jit = []
        for shape, item in representative.items():
            started = time.perf_counter(); out = clone_runners[shape](item["x"], item["payload"]); mx.eval(out)
            clone_jit.append({"K": shape[0], "N": shape[1], "first_dispatch_and_materialization_seconds": time.perf_counter()-started})
        # Clone admission compares the built-in control to the literal geometry clone on every actual capture.
        clone_records, clone_bench = [], []
        for projection, records in payloads.items():
            for item in records:
                exact = comparison(qmm(item["x"], item["payload"]), clone_runners[(item["K"], item["N"])](item["x"], item["payload"]))
                clone_records.append({"projection": projection, "position": item["position_label"], "K":item["K"], "N":item["N"], **exact})
                clone_bench.append({"projection": projection, "position": item["position_label"], "K":item["K"], "N":item["N"], "timing":benchmark(qmm, clone_runners[(item["K"],item["N"])], item["x"], item["payload"])})
        worst_clone = max(x["timing"]["candidate_over_control_median_ratio"] for x in clone_bench)
        clone_gate = {"all_actual_payloads_exact": all(x["bit_exact"] and x["shape_equal"] and x["bf16_equal"] and x["max_abs_diff"] == 0 and x["mean_abs_diff"] == 0 for x in clone_records), "worst_clone_over_control_median_ratio": worst_clone, "maximum_allowed":1.5}
        clone_gate["passed"] = clone_gate["all_actual_payloads_exact"] and worst_clone <= 1.5
        summary.update({"runtime": {"versions":versions, "prefix":str(Path(sys.prefix)), "device":mx.device_info()}, "source_audit":audit, "payload_capture":{"prompt":PROMPT_ID, "fixed_ids":list(REPLAY_IDS), "records": [{k:v for k,v in x.items() if k not in ("x","payload")} for a in payloads.values() for x in a], "count":sum(map(len,payloads.values()))}, "canonical_clone":{"geometry":"s2_r4 / 2 SIMD groups TG / 4 rows SIMD / 8 rows TG", "factory_seconds":factory_clone, "first_dispatch_jit_and_materialization":clone_jit, "exactness":clone_records, "timings":clone_bench, "gate":clone_gate}})
        if not clone_gate["passed"]:
            summary["classification"] = "REALGEN_002_M1_QMV_CLONE_INCOMPATIBLE"; return 2
        factory_started = time.perf_counter()
        for k, n in SHAPES: treatment_runners[(k,n)] = make_runner("m1_s1_r8", k, n, kernel_meta)
        treatment_factory = time.perf_counter()-factory_started
        treatment_jit = []
        for shape, item in representative.items():
            started = time.perf_counter(); out = treatment_runners[shape](item["x"], item["payload"]); mx.eval(out)
            treatment_jit.append({"K": shape[0], "N": shape[1], "first_dispatch_and_materialization_seconds": time.perf_counter()-started})
        treatment_records, isolated = [], []
        for projection, records in payloads.items():
            for item in records:
                custom = treatment_runners[(item["K"],item["N"])](item["x"], item["payload"])
                exact = comparison(qmm(item["x"], item["payload"]), custom)
                treatment_records.append({"projection":projection, "position":item["position_label"], "K":item["K"], "N":item["N"], **exact})
                isolated.append({"projection":projection,"position":item["position_label"],"K":item["K"],"N":item["N"],"timing":benchmark(qmm,treatment_runners[(item["K"],item["N"])],item["x"],item["payload"])})
        treatment_exact = all(x["bit_exact"] and x["shape_equal"] and x["bf16_equal"] and x["max_abs_diff"] == 0 and x["mean_abs_diff"] == 0 for x in treatment_records)
        savings = sum(x["timing"]["median_microseconds_saved"] for x in isolated if x["projection"] != "lm_head") / 3 * 36
        lm_savings = [x["timing"]["median_microseconds_saved"] for x in isolated if x["projection"] == "lm_head"]
        summary.update({"treatment":{"identity":"M1_S1_R8, distinct process-local M1-specific qmv implementation; not Stretch-037 promotion", "geometry":"s1_r8 / 1 SIMD group TG / 8 rows SIMD / 8 rows TG", "specialization_count":len(treatment_runners), "factory_seconds":treatment_factory, "first_dispatch_jit_and_materialization":treatment_jit, "zero_target_time_recompilations":True, "exactness":treatment_records, "all_actual_payloads_exact":treatment_exact, "isolated_timings":isolated, "estimated_transformer_qmv_savings_microseconds_per_token":savings, "lm_head_median_savings_microseconds":statistics.fmean(lm_savings)}})
        if not treatment_exact:
            summary["classification"] = "REALGEN_002_M1_QMV_NUMERICAL_NO_GO"; return 2
        # Correctness run, then excluded C/T warmups, then balanced C,T,T,C target walls.
        correct_c = replay(model, token_ids, REPLAY_IDS, False, treatment_runners, False)
        correct_t = replay(model, token_ids, REPLAY_IDS, True, treatment_runners, False)
        correctness = replay_compare(correct_c, correct_t)
        if not all(correctness[k] for k in ("all_exact_logits", "top1_equal", "fixed_replay_sequence_equal", "cache_offsets_equal")):
            summary.update({"replay_correctness":correctness, "classification":"REALGEN_002_M1_QMV_NUMERICAL_NO_GO"}); return 2
        replay(model, token_ids, REPLAY_IDS, False, treatment_runners, False); replay(model, token_ids, REPLAY_IDS, True, treatment_runners, False)
        walls_c, walls_t = [], []
        for treatment in (False, True, True, False):
            r = replay(model, token_ids, REPLAY_IDS, treatment, treatment_runners, True); (walls_t if treatment else walls_c).append(r["wall_seconds"])
            now = host()
            if now["free_memory_percent"] < 5 or now["swap_used_mb"] > 5600: raise RuntimeError("REALGEN_002_RUNTIME_RESOURCE_ABORT")
        cmed, tmed = statistics.median(walls_c), statistics.median(walls_t); gain = cmed/tmed - 1
        after = host()
        summary.update({"replay_correctness":correctness, "replay_performance":{"ordering":"CONTROL -> TREATMENT -> TREATMENT -> CONTROL", "warmup_excluded":True, "control_walls_seconds":walls_c, "treatment_walls_seconds":walls_t, "control_median_wall_seconds":cmed, "treatment_median_wall_seconds":tmed, "treatment_over_control_wall_ratio":tmed/cmed, "equivalent_control_tokens_per_second":10/cmed, "equivalent_treatment_tokens_per_second":10/tmed, "balanced_throughput_gain_fraction":gain, "upside_gate_required_fraction":1-1/1.05}, "resources":{"final":after, "specialization_count":len(treatment_runners), "kernel_metadata":kernel_meta}, "mlx_032_provenance":"No 0.32 runtime was launched: upstream split-K #3120 concerns qmm small-M and qmv_split_k was removed before merge; REALGEN M1 resolves to qmv_fast."})
        summary["classification"] = "REALGEN_002_M1_QMV_FAST_GO" if gain >= .05 else "REALGEN_002_M1_QMV_FAST_NO_GO"
        if gain >= .05:
            summary["preregistration_required"] = "REALGEN 003 M1 QMV SCIENTIFIC COMPARISON; stop for review before any six-prompt comparison."
        return 0
    except Exception as exc:
        summary["classification"] = "REALGEN_002_INCOMPLETE"; summary["error"] = f"{type(exc).__name__}: {exc}"; return 2
    finally:
        summary["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (run / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(f"Classification: {summary['classification']}\nSummary: {run/'summary.json'}")

if __name__ == "__main__": raise SystemExit(main())
