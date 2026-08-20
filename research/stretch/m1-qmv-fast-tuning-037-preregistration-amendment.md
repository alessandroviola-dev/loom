# Stretch 037 — preregistration methodological amendment

Date: 2026-08-20
Status: **FROZEN BEFORE FULL-MODEL SCIENTIFIC EXECUTION**

## Reason

The approved feasibility observed that the custom canonical `s2_r4` clone is already slightly different in balanced timing from built-in `mx.quantized_matmul` (clone/canonical medians: Q `0.980823`, K `0.991391`, V `1.006870`, O `0.984109`, gate `0.975363`, up `0.979778`, down `0.982789`). Therefore the observed `s1_r8` versus built-in difference cannot be causally attributed to output-row execution geometry alone.

This amendment does not revise or erase the feasibility history. It freezes the correct full-model scientific claim before treatment source/harness preparation and before observing any full-model treatment result.

## Frozen scientific factor

| CONTROL | TREATMENT |
|---|---|
| Canonical MLX 0.31.2 built-in affine qmv_fast implementation, selecting `affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0` | M1-specific custom qmv_fast implementation `s1_r8`, process-local and based on the exact MLX v0.31.2 qmv_fast semantics |

The treatment is **not** interpreted as `s2_r4 → s1_r8 geometry alone`.

It preserves the same:

- real packed 3-bit checkpoint weights;
- affine group64 scales/biases and decode layout;
- float accumulation, source operation order, `simd_sum`, and BF16 store;
- Qwen3-8B model, M5, H36, full raw-weight persistence, single final cleanup and BF16 KV;
- canonical MLX/mlx-metal 0.31.2 runtime and all inherited oracle/numerical/resource gates.

The treatment's execution mapping is one SIMD group/threadgroup and eight output rows/SIMD with matching grid mapping. It is applied uniformly to all eligible q/k/v/o/gate/up/down projections across all 36 layers; no projection-selective routing, fallback or rescue is permitted.

## Consequence for interpretation

A valid full-model ABBA may support only this claim:

> The M1-specific custom `s1_r8` qmv_fast implementation produced the measured result versus canonical MLX 0.31.2 built-in qmv_fast under the frozen M5 Qwen3 workload.

It must not claim that geometry alone caused the measured difference. The feasibility `+5.2120%` matched-MLP and `+6.0239%` attention-inclusive estimates remain predictions, not ABBA acceptance thresholds.

All remaining controls, balanced order, stop conditions and classifications in `m1-qmv-fast-tuning-037-plan.md` remain unchanged.
