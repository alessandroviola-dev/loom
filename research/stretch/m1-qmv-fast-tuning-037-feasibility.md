# Stretch 037 — M1-specific qmv_fast tuning feasibility

Date: 2026-08-20
Status: **GO — a separate preregistration is prepared; no scientific ABBA was run.**

## Scope and frozen conditions

This is a process-local `mx.fast.metal_kernel` feasibility probe on Apple M1 `applegpu_g13g` only. It does not modify installed mlx/mlx-metal, model code, weights, packing, 3-bit affine quantization, M5 geometry, BF16 activations, H36/full raw-weight persistence, single cleanup, or BF16 KV. No full-model cache and no full-model ABBA was created.

The child verified the literal canonical venv (`mlx`/`mlx-metal` `0.31.2`, `mlx-lm` `0.31.3`, `transformers` `5.12.1`), Apple M1/gen13 and real layer-0 Qwen3-8B checkpoint SHA-256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`. It retained only the 21 real q/k/v/o/gate/up/down layer-0 payload tensors (`84,410,368 B` setup active memory).

The source audit used the exact retained MLX v0.31.2 checkout `68cf2fddd8de5edd8ab3d926391772b2e2cedad8`: `quantized.cpp` SHA-256 `6ddd11e0…14a2b7`, `kernels/quantized.h` SHA-256 `c36c8c2d…067fe38b`.

## A. Exact qmv_fast source audit and invariants

For the non-batched, transpose-true M5 payloads, `QuantizedMatmul::eval_gpu → dispatch_qmv → qmv()` selects:

```text
affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0
```

`qmv()` fixes `bn=8`, `bk=32`, threadgroup `(32,2,1)`, and threadgroups `(M,N/8,B)`. Fast is legal only when `N % 8 == 0 && K % 512 == 0`; all seven requested shapes meet this. The non-batched wrapper only forwards arrays to `qmv_fast_impl`; it introduces no offset adjustment.

For bits=3/group64, `qmv_fast_impl()` and every called helper give the following source facts:

| Item | Source fact / classification |
|---|---|
| packed format | **Semantically fixed:** 3-bit decoding is 8 values/3 bytes; `get_pack_factor<3,32>()=8`, `get_bytes_per_pack<3,32>()=3`. |
| per-lane K work | **Semantically fixed for this clone:** 2 packs × 8 = 16 values/lane, a 512-value K block (`16 × SIMD_SIZE`). |
| scale/bias | **Semantically fixed:** group64; lane reads group `lane/4`; each qdot is exactly `scale * decoded_dot + sum(x) * bias`. |
| x reuse | **Implementation structure:** one lane loads/scales 16 BF16 x values once per K block, then reuses its register array and x-sum for each assigned output row. |
| packed/scales access | **Semantically fixed addressing:** row-major packed bytes; per row K stride `K*3/8`, scale/bias stride `K/64`; every 512 block advances 192 packed bytes and 8 affine groups. |
| arithmetic | **Semantically fixed for parity:** float accumulators, the source operation order in `load_vector`/`qdot`, `simd_sum`, then BF16 store. No intentional precision/reduction change is allowed. |
| canonical output tile | **Implementation assumption:** 2 SIMD groups × 4 output rows/SIMD = 8 output rows/threadgroup; `tid.y` selects that tile. |
| threadgroup memory | **Absent:** this path uses only lane registers and SIMD reduction; no threadgroup-memory allocation/barrier participates. |
| alignment / boundary guards | **Implementation assumption justified by dispatch:** fast has no N/K tail guards, relying on N multiple 8 and K multiple 512. |

Thus bits, group size, packing, affine formula, K block, values/lane, reduction order, output layout, x indexing and M are not tunable. The only bounded neutral execution degrees supported by the source structure are: number of independent SIMD groups/threadgroup, independent output rows retained per SIMD group, and the corresponding `tid.y`/grid output-row tile mapping. Each still gives one SIMD group all K contributions for an output row and preserves its float `simd_sum`.

## B. Canonical clone

A narrow source-body clone was made with `mx.fast.metal_kernel`. It is a literal specialization of `qmv_fast_impl` for BF16/affine/b3/gs64/non-batched/M5, with K/N source-specialized because the MLX API injects a Metal function body. It retains the MLX 3-bit unpack order, 16 values/lane, 512-K loop, affine correction, float operations, SIMD reduction, and BF16 output. Its canonical geometry is exactly two 32-lane SIMD groups and four output rows per group (`s2_r4`), hence eight output rows/threadgroup and the canonical grid mapping.

Clone admission was preregistered before tuning: strict bit-exactness for all 21 comparisons and no clone/canonical median above `1.50×`. The clone passed: all real-payload outputs were shape-equal BF16 and bit-exact (`max_abs=mean_abs=0`); its worst median ratio was `1.006870` (V), so it is performance-representative rather than structurally dominated by `metal_kernel` overhead.

## C. Canonical versus clone timing

40 warmups/side were excluded. Each row has 120 synchronized samples/side in `canonical → clone → clone → canonical` order, without cache purge. Values are median `[p25,p75]` µs, ratio `clone/canonical`.

| projection | canonical | clone | ratio |
|---|---:|---:|---:|
| q | 895.17 [884.05,915.95] | 878.00 [852.66,897.25] | 0.980823 |
| k | 488.83 [473.36,507.86] | 484.62 [471.25,509.07] | 0.991391 |
| v | 627.75 [601.85,658.60] | 632.06 [605.65,659.89] | 1.006870 |
| o | 1473.58 [1427.30,1534.31] | 1450.17 [1402.82,1524.75] | 0.984109 |
| gate | 2132.65 [2110.07,2187.48] | 2080.10 [2038.10,2138.45] | 0.975363 |
| up | 2154.21 [2118.83,2199.25] | 2110.65 [2057.00,2162.93] | 0.979778 |
| down | 2080.83 [2058.53,2125.68] | 2045.02 [2008.01,2097.58] | 0.982789 |

The absolute medians are host-state-dependent and are not compared to prior experiments; balanced ratios are the evidence.

## D. Limited preregistered tuning set

The following four, and only these four, configurations were declared in the runner before timing. They alter only neutral output-row ownership and grid/tile geometry:

| id | SIMD groups/TG | rows/SIMD | output rows/TG | rationale |
|---|---:|---:|---:|---|
| s1_r4 | 1 | 4 | 4 | halve TG SIMD groups, retain four accumulators |
| s4_r4 | 4 | 4 | 16 | four independent SIMD groups, 16 rows/TG |
| s2_r2 | 2 | 2 | 4 | reduce live accumulators to two |
| s1_r8 | 1 | 8 | 8 | canonical eight rows/TG with one SIMD group |

All 84 direct candidate comparisons (four variants × seven projections × three deterministic BF16 inputs) were shape-equal BF16 and bit-exact against canonical `mx.quantized_matmul`; every `max_abs_diff` and `mean_abs_diff` is `0.0`. No threshold was used or needed.

## E. Candidate timing and selected treatment

`s1_r8` is the sole concrete candidate. It robustly improves all three dominant MLP projections: its p75 remains below canonical p25 for gate, up, and down. Active/peak MLX allocations stayed about `85.0/85.2 MB`, the same scale as clone/canonical timing; it creates no persistent parameter cache.

| projection | canonical µs [p25,p75] | s1_r8 µs [p25,p75] | ratio | saved µs |
|---|---:|---:|---:|---:|
| q | 878.31 [863.28,902.17] | 835.12 [822.07,857.43] | 0.950828 | +43.19 |
| k | 531.56 [512.80,544.52] | 524.02 [506.81,540.33] | 0.985813 | +7.54 |
| v | 673.50 [645.72,692.60] | 667.65 [638.22,690.98] | 0.991308 | +5.85 |
| o | 1467.08 [1346.05,1520.84] | 1404.46 [1287.73,1457.22] | 0.957314 | +62.62 |
| gate | 2142.83 [2109.58,2193.19] | 2003.02 [1944.78,2062.91] | 0.934753 | +139.81 |
| up | 2138.67 [2105.71,2190.51] | 2011.19 [1966.76,2070.53] | 0.940393 | +127.48 |
| down | 2104.27 [2070.89,2151.16] | 1971.33 [1928.27,2027.10] | 0.936825 | +132.94 |

Other variants: s1_r4 estimates `+2.4801%`, s4_r4 `+2.8492%`; s2_r2 is `-30.0314%`. They are not candidates for integration.

## F. Weighted feasibility estimate

The direct x36 arithmetic saving for s1_r8 is Q `1.5548 ms`, K `0.2715 ms`, V `0.2107 ms`, O `2.2545 ms`, gate `5.0332 ms`, up `4.5892 ms`, down `4.7857 ms` per M5 block. Direct isolated timings are not assumed additive in the model.

For a conservative admission estimate, the measured per-projection fractions were applied to their matching Stretch-028 component telemetry for gate/up/down. Their matched MLP estimate is `0.01817795 s/block` (`5.2120%` of the canonical Stretch-031 `0.3487060 s` block). The mean q/k/v/o fraction applied to the whole Stretch-028 attention bucket is explicitly an optimistic bound, `0.00282769 s/block`. Combined bounded estimate: `0.02100564 s/block`, **`6.0239%`** of canonical block wall, implying arithmetic `~15.25 tok/s` from the `14.3307127237 tok/s` reference.

This clears the >=5% feasibility gate because matched MLP telemetry alone clears it; it is motivation for, not a replacement for, an exact full-model balanced ABBA. No material memory-pressure increase was observed in the isolated kernels.

## Decision

**`STRETCH_037_M1_QMV_FAST_TUNING_GO`** for exactly one treatment: **s1_r8**. It is strictly bit-exact over all real-payload probe comparisons, clone-representative, improves all MLP projections, has a `>=5%` matched-MLP projected block upside, and needs no installed-runtime patch or persistent memory expansion.

A separate preregistration is prepared in `research/stretch/m1-qmv-fast-tuning-037-plan.md`. It must be reviewed before any source integration or full-model ABBA. This feasibility artifact itself performed neither.

## Evidence

- Runner: `scripts/stretch_m1_qmv_fast_tuning_037_feasibility.py`
- Parent summary: `results-local/stretch/m1-qmv-fast-tuning-037-feasibility/20260820-211047/summary.json`
- Child summary, generated source hashes/full Metal sources, and stdout/stderr are colocated in that evidence directory.
