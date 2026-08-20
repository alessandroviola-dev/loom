# Stretch 039 — GQA shared-KV SDPA feasibility

Date: 2026-08-20
Status: **INVESTIGATION_ONLY — no full-model integration or ABBA.**

## Scope and result

This is a bounded feasibility audit of the frozen Qwen3-8B M5 path only. It
kept Qwen3-8B affine 3-bit/group64 BF16, Apple M1 `applegpu_g13g`, MLX/
mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1, M5, H36, full raw-weight
persistence, BF16 KV, promoted S1_R8, and the once-per-two-M5-block cleanup
cadence. Installed MLX was read-only. No Stretch 037/038 workload was rerun,
and no full-model performance comparison was launched.

Classification: `STRETCH_039_GQA_SHARED_KV_SDPA_INVESTIGATION_ONLY`.

Evidence: `results-local/stretch/gqa-shared-kv-sdpa-039-feasibility/20260820-210451/summary.json`.

## Exact source and runtime payload audit

The pinned local upstream checkout is MLX v0.31.2 commit
`68cf2fddd8de5edd8ab3d926391772b2e2cedad8`. Audited files and SHA-256 are:

- `mlx/backend/metal/scaled_dot_product_attention.cpp` — `d09e7ec5…af95f66`
- `mlx/backend/metal/kernels/sdpa_vector.h` — `4a9d6b16…a369f9a250`
- `mlx/backend/metal/kernels/scaled_dot_product_attention.metal` — `bc32c424…bedf28c3`

A process-local observer wrapped Qwen3's already imported SDPA helper and
called the original helper unchanged. It captured the real post-RoPE Q/K/V
inputs for the canonical prompt `[1, 42, 2048, 151935]` followed by the first
canonical M5 oracle block `[1, 374, 264, 4647, 1483]`, at layers 0, 18 and 35.
Each layer had the same runtime metadata:

| field | actual value |
|---|---|
| Q | `[1, 32, 5, 128]` BF16 |
| K / V | `[1, 8, 9, 128]` BF16 |
| batch / Q heads / KV heads / GQA | `1 / 32 / 8 / 4` |
| q_len / kv_len / head dim / value dim | `5 / 9 / 128 / 128` |
| scale / mask / causal | `0.08838834764831845` / no array (`"causal"`) / true |
| Q layout | Qwen3 reshape `[B,L,H,D]`, then transpose to `[B,H,L,D]`; element strides `[20480,128,4096,1]` |
| K/V layout | `KVCache` 256-token allocation sliced to 9; element strides `[262144,32768,128,1]` |

The `q_len <= 8` route selects vector mode. For this payload the exact kernel
symbol is `sdpa_vector_bfloat16_t_128_128` with function constants
`_nomask_qt_c_nosinks`, i.e.
`sdpa_vector_bfloat16_t_128_128_nomask_qt_c_nosinks`. Its launch is
`[batch*Q_heads, q_len, 1] = [32,5,1]` threadgroups and `[1024,1,1]` threads
per threadgroup (32 SIMD groups); source-declared threadgroup float storage is
4,352 B.

## KV routing

MLX v0.31.2 sends vector payloads to `sdpa_vector_2pass` when either the
architecture suffix is `d`/`s` and `kv_len >= 1024`, or GQA is present and
`kv_len >= 4096`. The observed M1 suffix is `g`; therefore the current
`kv_len=9`, and fixed sanity lengths 256, 1024 and 2048, all remain on the
single-pass vector route. The M1 suffix does change the first condition: it
does **not** adopt the 1024 threshold used by `d`/`s`; GQA's 4096 threshold
remains. No 2-pass experiment was made.

## Canonical cost attribution

Every side had 40 excluded warmups and 120 synchronized samples, ordered
canonical → clone → clone → canonical without cache purge. Built-in MLX SDPA
median (p25–p75) on the actual payloads was:

| layer | MLX SDPA median |
|---:|---:|
| 0 | 371.979 µs (358.437–384.240) |
| 18 | 447.187 µs (425.167–477.199) |
| 35 | 363.979 µs (325.063–422.625) |

The three-payload mean median is 394.382 µs. Linear diagnostic weighting gives
14.198 ms per 36-layer M5 block, only 3.973% of the promoted Stretch-038
TREATMENT target wall (1.429526 s / four M5 blocks = 357.381 ms/block).
Even hypothetical complete elimination of this SDPA time cannot satisfy the
required >=5% full-target upside.

## GQA shared-KV source finding

`sdpa_vector.h` computes `kv_head_idx = q_batch_head_idx / gqa_factor`; four
logical Q heads therefore address the same K/V head. The canonical mapping,
however, places each Q-head/query-position in a separate 1024-thread,
32-SIMD-group threadgroup. Each such threadgroup performs its own K and V
loads. This is evidence of *logical duplicate device loads* across the four
threadgroups. It is not evidence of four independent physical DRAM reads:
Metal cache reuse is hardware-dependent and the source supplies neither a
DRAM counter nor cross-threadgroup cache guarantee.

There is explicit threadgroup reuse only within one Q head (the output/max/sum
arrays used for its 32-SIMD reduction). Threadgroup memory cannot be shared by
the four independent Q-head threadgroups. A faithful four-head grouping would
need 4 × 1024 = 4096 threads. Reducing/scheduling SIMD groups to fit changes
the per-head reduction/recurrence geometry and is not a mechanically justified
frozen-numerics treatment.

## Canonical-clone diagnostic and treatment decision

A process-local `mx.fast.metal_kernel` clone was constructed first, specializing
the vector recurrence to BF16 D=V=128, GQA4, M5, causal/no-array-mask and the
observed layouts. Factory cost was 0.544 ms; first invocation/evaluation was
266.469 ms and no later recompilation was observed. It did **not** pass clone
admission: shape/dtype matched, but it was non-bit-exact on all three real
payloads (layer 0 produced non-finite differences; layers 18/35 max/mean
absolute differences were `2.3046875/0.0883329` and
`12.9321289/0.6904371`). The apparent clone/canonical median ratios
`0.6683/0.6866/0.6732` are consequently non-representative and are not used as
performance evidence.

The same clone was non-bit-exact at the fixed single-pass sanity lengths 256,
1024 and 2048; those timings are diagnostic artifacts only, not treatment
results. Because the clone failed the required numerical/representativeness
gate, and because the full-target SDPA upper bound is below 5% even before a
sharing mechanism is credited, **no GQA-shared treatment was implemented or
benchmarked**. Thus there are no treatment numerics/timings to report and no
preregistration is created.

MLX memory after the diagnostic was 3,633,195,016 B active and 3,637,237,912 B
peak. The unimplemented treatment adds 0 B threadgroup memory, has no JIT cost
and no recompilation. No memory-safety risk was introduced.

## Decision and exact next step

`INVESTIGATION_ONLY`. Preserve the frozen canonical M5 SDPA path. Do not
integrate this clone, infer a speedup from it, patch MLX, or launch an ABBA.
A future GQA-SDPA factor would require fresh authorization, a source-supported
mapping that preserves the per-head FP operation/reduction sequence, a
bit-exact representative clone, and a new >=5% target-wall rationale.
