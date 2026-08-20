# Stretch 041 — current bottleneck attribution after S1_R8 and deferred cleanup

Date: 2026-08-20

Classification: **`STRETCH_041_CURRENT_BOTTLENECK_MAP_COMPLETE`**
Scope: investigation only. No treatment, scientific ABBA, promotion decision, cache purge, or rerun of Stretch 037/038/039/040 occurred.

Evidence: `results-local/stretch/current-bottleneck-attribution-041/20260820-213903/summary.json`.

## Frozen current runtime and source identity

- Qwen3-8B; affine 3-bit/group64; BF16; Apple M1 `applegpu_g13g` / gen13; M5; H36; full raw-weight persistence `3,583,928,320 B`; BF16 KV.
- `mlx`/`mlx-metal` 0.31.2, `mlx-lm` 0.31.3, `transformers` 5.12.1, literal launcher `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`.
- Current promoted control render SHA-256: `9f94787f7a002a8da95e8352f134eac11f1b072b9363fe600dcac1122080a54c`.
- Promoted S1_R8 render/injection SHA-256: `82888b134a6c4e0ba56bb24896bce2fd37c9d78c899380af35e0e823ad5fcbe3` / `a086806a314d387770dac54e9140b9526bf7fe9097819f449bba17b7fc1f3ad4`.
- Current runner blobs: S1_R8 runtime `a65776177b8e988939d1a95a821469e0a9c41f83`; Stretch-038 canonical renderer `97339280aec0a9bb2fb4b196795f05cd23ef52a4`.
- This diagnostic rendered SHA-256: `6426478771608d3d24b19603aef097f2eaec4ed457c908d2ae6a8459abcb2948` (recorded in the evidence summary). Four process-local S1_R8 specializations remained bit-exact and no target-time recompilation occurred.

## Exact promoted execution graph and materialization audit

For each M5 pass the persistent shared embedding is selected, explicitly `mx.eval`'d, applied and `mx.eval(h)`'d. Then each of 36 persistent blocks executes:

```text
input RMSNorm
→ q, k, v projections
→ q/k RMSNorm + reshape/transpose; v reshape/transpose
→ RoPE(q,k)
→ KV update/fetch
→ causal GQA SDPA
→ attention transpose/reshape
→ o projection
→ residual 1
→ post-attention RMSNorm
→ gate + up projections
→ SwiGLU
→ down projection
→ residual 2
```

The source then explicitly evaluates each block's `out`. It applies/evaluates final RMSNorm, applies/evaluates the persistent quantized LM head, and (only after M5 block 2) executes the frozen cleanup exactly:

```python
gc.collect()
mx.clear_cache()
gc.collect()
```

The ten-token constituent uses a fresh BF16 KV cache and two M5 passes. Prompt/oracle correctness work is outside the baseline target compute but inside the direct constituent wall after target start: fixed oracle IDs, all-target logit comparisons, top-1 checks, accepted-token checks, and sequence equality. Python orchestration includes block/cache construction/selection, records/snapshots, and the per-position oracle loop.

### Explicit forcing counts in the promoted source

| boundary | per layer | per M5 pass | per two-M5 / 10 accepted tokens |
|---|---:|---:|---:|
| `mx.eval(block.parameters())` | 1 | 36 | 72 |
| `mx.eval(out)` | 1 | 36 | 72 |
| embedding/final-norm/LM-head evals | 0 | 6 | 12 |
| target ID and correctness/oracle `mx.eval` | 0 | 15 | 30 |
| **all `mx.eval`** | **2** | **93** | **186** |
| `.item()` in target oracle correctness (promoted 038 path) | 0 | 24 | 48 |
| `mx.synchronize()` | 0 | 0 | 0 |

The 93/pass count includes one `make_ids` evaluation and fourteen target oracle evaluations (four prediction `token_value`, five logit-difference evaluations, five target `token_value`) in addition to the 78 full-forward evaluations. The 24 `.item()` calls/pass are four prediction reads plus four reads for each of five positions (max difference, mean difference, resident max, target top-1). The local staging/cache-memory calls and Python `int(...)` conversions are not MLX evaluation primitives. The source therefore has a real **per-layer materialization boundary** (`mx.eval(out)`) as well as a per-layer parameter-evaluation boundary; Stretch 041 did not alter either cadence.

## Fresh full-path diagnostic baseline

Six fresh canonical diagnostic cycles (each exactly ten accepted tokens/two M5 blocks, no purge) gave:

| metric | result |
|---|---:|
| mean target wall | 710.063 ms |
| median target wall | 707.791 ms |
| wall / accepted token | 71.006 ms |
| pooled diagnostic rate | 14.0833 tok/s |
| mean block-1 outer wall (no cleanup) | 311.148 ms |
| mean block-2 outer wall (includes cleanup) | 382.402 ms |
| block-2 cleanup wall | 50.611 ms |
| block-1 deferred-cleanup no-op wall | 0.000833 ms |
| minimum free memory / peak swap | 24% / 2076.19 MB |
| final MLX active / peak / cache | 3,665,291,272 B / 3,671,402,524 B / 2,867,740–2,868,252 B |

This is absolute diagnostic evidence only and is not causally compared with any earlier experiment.

## Profiling perturbation and broad-stage map

The profiled form uses the same model, M5 payloads, cache/cadence and oracle workload, but adds broad stage evaluation boundaries within each transformer layer. Four fresh profiled cycles averaged 1,247.049 ms (8.0189 tok/s), a PROFILED/CANONICAL wall ratio of **1.75625x** (+75.625% wall perturbation). Its 288 layer records are attribution-only; their absolute values are explicitly not canonical wall.

| broad profiled stage, summed over 36 layers/M5 | ms/M5 profiled | canonical-wall fraction if used only as a scale reference |
|---|---:|---:|
| Q/K/V projection group | 57.381 | 8.081% |
| SDPA | 15.126 | 2.130% |
| attention output projection | 40.756 | 5.740% |
| norms + residuals (input, q/k, post, two residuals) | 67.877 | 9.559% |
| gate + up group | 174.401 | 24.561% |
| SwiGLU | 14.131 | 1.990% |
| down projection | 93.659 | 13.190% |
| KV update/fetch | 39.083 | 5.504% |
| RoPE/v/attention layouts | 24.805 | 3.493% |

Final norm and LM head are separated below. The listed fractions are **not** canonical attribution claims: the broad profile materially perturbs the graph. They identify where the exact current graph spends synchronized profile time and are checked against real-payload isolated samples next.

## Isolated real-payload measurements

All measurements used actual M5 intermediates captured at layers 0, 18 and 35, actual quantized tensors, 40 excluded warmups and 120 synchronized samples per kernel. Values are median ms (p25–p75).

| operation | layer 0 | layer 18 | layer 35 |
|---|---:|---:|---:|
| q | 0.869 (0.835–0.935) | 1.411 (1.390–1.436) | 1.462 (1.413–1.501) |
| k | 0.536 (0.494–0.605) | 0.678 (0.652–0.707) | 0.744 (0.697–0.778) |
| v | 0.652 (0.615–0.686) | 0.715 (0.688–0.756) | 0.672 (0.652–0.695) |
| o | 1.485 (1.426–1.521) | 1.448 (1.409–1.496) | 1.483 (1.425–1.522) |
| gate | 2.030 (1.942–2.158) | 2.035 (1.973–2.079) | 1.979 (1.937–2.207) |
| up | 2.051 (2.004–2.080) | 1.983 (1.941–2.051) | 2.055 (1.983–2.093) |
| down | 1.963 (1.916–2.027) | 2.027 (1.989–2.046) | 2.015 (1.945–2.045) |
| input RMSNorm | 0.259 (0.246–0.271) | 0.266 (0.241–0.285) | 0.267 (0.255–0.292) |
| post-attention RMSNorm | 0.316 (0.296–0.326) | 0.293 (0.281–0.307) | 0.321 (0.303–0.336) |
| residual add | 0.299 (0.289–0.313) | 0.307 (0.287–0.316) | 0.318 (0.308–0.331) |
| SwiGLU | 0.344 (0.331–0.356) | 0.340 (0.326–0.356) | 0.359 (0.345–0.378) |

The layer-sampled medians extrapolate only as rough current payload bounds: Q/K/V about 92.2 ms/two-M5 constituent, o about 53.0 ms, gate/up/down about 217.6 ms, two RMSNorm categories about 20.2 ms, residual adds about 22.1 ms, and SwiGLU about 12.5 ms. They intentionally do not replace the minimally instrumented total wall.

## SDPA, cleanup, LM head, KV, and unaccounted work

- **SDPA:** reuse Stretch 039 because source/payload semantics are unchanged: 14.198 ms/M5, 3.973% of its then-promoted wall. On this 710.063 ms two-M5 diagnostic it is about 4.00% if doubled (28.396 ms), below the 4.7619% independent-factor gate. Stretch 039 was not rerun.
- **Cleanup:** source identity is unchanged. Stretch 040's canonical components remain supporting evidence: first GC 19.805 ms, clear 0.333 ms, second GC 16.385 ms (36.190 ms/event). The new direct block-2 cleanup envelope is 50.611 ms and includes timing/record overhead; it does not supersede component attribution. Stretch 040's measured retained-clear-only result was +4.779%, below gate and unstable in Python objects; cleanup composition remains closed/no-go.
- **LM head:** `persistent_shared["head"].lm_head` is `mlx.nn.QuantizedLinear`, affine 3-bit/group64; packed U32 weight shape `[151936, 384]`, effective `K=4096`, `N=151936`, M=5 input. `QuantizedLinear.__call__` dispatches to `mx.quantized_matmul(..., transpose=True)`, hence the MLX built-in `qmv_fast` dispatch (not S1_R8): on gen13 at M=5, the source qmv batch limit is 6 for this N, and K/N satisfy the `K % 512 == 0` / `N % 8 == 0` fast predicates. S1_R8 is explicitly limited to four `(K,N)` transformer shapes and this `(4096,151936)` head is ineligible. Actual-M5-head median is **22.394 ms** (22.330–22.433), 3.154% of target wall. Its complete-elimination bound is 3.255% throughput: `CLOSED_BY_UPPER_BOUND` as an independent factor.
- **KV bookkeeping:** broad profiled update/fetch is 39.083 ms/M5 (perturbed; 5.50% scale reference). It is a candidate only for later bounded feasibility, not a canonical cost claim. BF16 KV and its cache update semantics remain frozen.
- **Final norm:** isolated median 0.322 ms (0.297–0.347), 0.045%; `CLOSED_BY_UPPER_BOUND`.
- **Python/orchestration/unaccounted:** the direct canonical wall necessarily includes forward-level dispatch/materialization, construction/selection, cache snapshots, 186 explicit evaluations, 48 item reads, target logit/oracle correctness, timing and records. It cannot be recovered by subtracting the synchronized isolated medians without double-counting/altering graph execution. It is therefore reported as a real residual, not falsely assigned to kernels. This is precisely why profile-stage absolute walls are not promoted to canonical attribution.

## Upper-bound gate and next-factor ranking

The required independent threshold is a 4.7619% wall fraction. `maximum gain = f/(1-f)`.

| candidate | current measured/bounded wall | fraction | maximum theoretical gain | realistic plausible gain | correctness / memory / complexity | recommendation |
|---|---:|---:|---:|---:|---|---|
| LM head | 22.394 ms | 3.154% | 3.255% | <3.255% | low / low / medium | `CLOSED_BY_UPPER_BOUND` |
| SDPA | reused 28.396 ms/two-M5 bound | ~4.00% | ~4.17% | <4.17% | medium / low / high | `CLOSED_BY_UPPER_BOUND` (Stretch 039 retained) |
| final norm | 0.322 ms | 0.045% | 0.045% | negligible | low / low / low | `CLOSED_BY_UPPER_BOUND` |
| SwiGLU | ~12.5 ms isolated extrapolation | ~1.76% | ~1.79% | below bound | medium / low / medium | `CLOSED_BY_UPPER_BOUND` |
| norms/residual aggregate | ~42.3 ms isolated extrapolation | ~5.96% | ~6.34% | not defensibly >=5% | correctness medium / memory low / high | do not select: only aggregate clears arithmetic and no safe single factor is identified |
| cleanup composition | 36.190 ms components | 5.10% | 5.37% | **4.779% measured** | Python stability risk / low / low | closed NO-GO by Stretch 040 |
| remaining S1_R8 qmv internals | MLP projections remain large (~217.6 ms isolated extrapolation) | ~30.6% | large bound | unproven after S1_R8 | numerical medium / memory low / high | no generic scale/bias caching; needs distinct local evidence before any proposal |
| KV bookkeeping | 39.083 ms/M5 profiled only | not canonical | unknown | unproven | correctness/high memory / high | do not select from perturbed profile |
| one-vs-two-layer materialization cadence | source proves 36 `mx.eval(out)` and 36 parameter-eval boundaries/M5 | scheduling portion unmeasured | unknown | unproven | correctness medium / memory currently unbounded / medium | do not select; a future feasibility must first bound peak memory and scheduling benefit |
| Python/orchestration | residual only | unassigned | unknown | unproven | low correctness / low memory / high | no isolated factor exists yet |

**Exact recommendation: no next optimization factor is defensibly recommended from Stretch 041.** No remaining low-risk, independently bounded factor has a defensible plausible >=5% upside. Further work should transition to a more radical kernel/model technique, speculative drafter/acceptance work, or product/end-to-end serving rather than accumulate sub-5% micro-optimizations.

## QMV metadata-caching warning

Record upstream MLX issue #3251 update: under MLX 0.31.2, g64 versus g128 generation penalty is effectively ~0%, and attempted register/`simd_shuffle` scale+bias caching regressed about 20–30%. Consequently Stretch 041 neither prototypes nor recommends generic scale/bias metadata caching. Only new local M1/3-bit evidence could overturn that rationale.

## Limitations and excluded runs

The first three 041 generated-source roots (`20260820-213704`, `20260820-213733`, `20260820-213802`, `20260820-213836`) are retained local harness-debug evidence and excluded: respectively class-name mangling/global binding/SDPA symbol defects. They produced no completed attribution payload and no optimization comparison. The successful fresh root above is the sole reported diagnostic result.
