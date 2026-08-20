# Stretch 035 — M5 quantized kernel-path investigation

Date: 2026-08-20

Status: **`STRETCH_035_KERNEL_PATH_INVESTIGATION_ONLY`**. This is source-trace and current-ceiling evidence only. It created no source transform, runtime patch, global package modification, preregistration, or scientific ABBA.

## Scope and provenance

The canonical child launcher verified MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`, Qwen3-8B 3-bit affine/group64 and BF16 inputs. The actual checkpoint SHA-256 is `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`. All measurements use real layer-0 packed `U32` weights plus real BF16 affine scales/biases; only controlled BF16 activations are generated.

Exact upstream source snapshots were cloned under ignored local evidence:

| Source | Immutable revision |
|---|---|
| MLX `v0.31.2` | `68cf2fddd8de5edd8ab3d926391772b2e2cedad8` |
| MLX `v0.32.0` | `7a1d4f5c12ac82f4b4d0a6e71538d89ca0605247` |
| PR #3764 reviewed head | `e8d2d4304867e8ef42abeefaa9c0cfec7ac75d3a` |

Relevant source hashes: v0.31.2 `quantized.cpp` `6ddd11e0…14a2b7`, `kernels/quantized.h` `c36c8c2d…7fe38b`; v0.32.0 equivalents `0897c0f2…ed4e90` and `4da52bf4…463c99`.

## A. Exact v0.31.2 dispatch on this machine

`mx.device_info()` reports `device_name: Apple M1`, `architecture: applegpu_g13g`, 8 GiB memory. This is not an inferred marketing mapping: MLX’s `Device` obtains `MTLDevice.architecture.name`; its parser reads `13` as generation and trailing `g` as architecture size. Thus the dispatch facts below are **gen 13 / size g**.

The host chain is `QuantizedMatmul::eval_gpu` → `dispatch_qmv` → `qmv` in `mlx/backend/metal/quantized.cpp`. Inputs are non-batched, row-contiguous and call `transpose=True`; all requested `K` values are neither 64 nor 128, so `qmv_quad` cannot apply. For gen 13/size g, literal `get_qmv_batch_limit(K,N,d)` returns 10 when both dimensions are at most 4096, otherwise 6.

At `M=5`, every requested projection is below that limit, hence is a qmv, not qmm or split-K. `qmv` selects `fast` when `N % 8 == 0 && K % 512 == 0`; all seven real shapes satisfy both predicates. It dispatches `(M, ceil(N/8), B)` threadgroups, threads `(32,2,1)`. With BF16, affine, gs64, b3 and `B=1`, the concrete symbol is:

```text
affine_qmv_fast_bfloat16_t_gs_64_b_3_batch_0
```

| Projection | K → N | M5 vector limit | M5 path / concrete symbol |
|---|---:|---:|---|
| q | 4096 → 4096 | 10 | qmv_fast / symbol above |
| k | 4096 → 1024 | 10 | qmv_fast / symbol above |
| v | 4096 → 1024 | 10 | qmv_fast / symbol above |
| o | 4096 → 4096 | 10 | qmv_fast / symbol above |
| gate | 4096 → 12288 | 6 | qmv_fast / symbol above |
| up | 4096 → 12288 | 6 | qmv_fast / symbol above |
| down | 12288 → 4096 | 6 | qmv_fast / symbol above |

The installed canonical `mlx.metallib` SHA-256 is `8c8bfcece8c0610745b68879771e5aa1b92b29fa5e17172e5508e4f5153d8d15`; a symbol-string audit finds that exact qmv symbol and the qmm/split-K fallback symbols. MLX 0.31.2 exposes no public verbose per-dispatch symbol log, so static source + device provenance is the exact dispatch evidence; no benchmark inference was used to identify M5.

For the required scaling map, M1–M5 retain qmv_fast for all projections. At M6/M8 q/o/k/v remain below 10 and qmv_fast; gate/up reach limit 6 and take plain aligned `affine_qmm_t_bfloat16_t_gs_64_b_3_alN_true_batch_0`; down reaches limit 6 and takes aligned `affine_qmm_t_splitk_bfloat16_t_gs_64_b_3_alN_true` followed by MLX’s strided split-K reduction. NAX is unavailable on this M1: source requires generation at least 17 (or 18 for phone) and a newer OS availability gate.

## D. Current-kernel ceiling map

40 warmups were excluded for every real payload/shape; every cell is the median of 100 `mx.eval`-synchronized calls, no deliberate cache purge. Cells are `µs (M/M1)`. The evidence JSON also records p25/p75, min/max, total synchronized wall and effective output elements/s for all 49 cells.

| Projection K→N | M1 | M2 | M3 | M4 | **M5 canonical** | M6 | M8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| q 4096→4096 | 460.02 (1.00) | 701.23 (1.52) | 998.92 (2.17) | 1282.98 (2.79) | **1533.38 (3.33)** | 1740.77 (3.78) | 2128.15 (4.63) |
| k 4096→1024 | 435.21 (1.00) | 549.73 (1.26) | 609.33 (1.40) | 667.58 (1.53) | **675.31 (1.55)** | 788.15 (1.81) | 889.75 (2.04) |
| v 4096→1024 | 475.31 (1.00) | 472.71 (1.00) | 575.33 (1.21) | 675.29 (1.42) | **731.48 (1.54)** | 784.08 (1.65) | 898.88 (1.89) |
| o 4096→4096 | 677.77 (1.00) | 838.21 (1.24) | 1121.85 (1.65) | 1348.69 (1.99) | **1527.06 (2.25)** | 1752.08 (2.59) | 2117.00 (3.12) |
| gate 4096→12288 | 1130.79 (1.00) | 1746.23 (1.54) | 2025.48 (1.79) | 1841.79 (1.63) | **2197.58 (1.94)** | 3496.98 (3.09) qmm | 3499.52 (3.10) qmm |
| up 4096→12288 | 785.54 (1.00) | 1223.00 (1.56) | 2037.50 (2.59) | 1926.06 (2.45) | **2195.92 (2.80)** | 3504.29 (4.46) qmm | 3493.98 (4.45) qmm |
| down 12288→4096 | 787.06 (1.00) | 1212.98 (1.54) | 2062.19 (2.62) | 2047.12 (2.60) | **2145.69 (2.73)** | 3703.17 (4.71) split-K | 3680.50 (4.68) split-K |

M5 effective output rates (G output elements/s) are q `0.0134`, k `0.0076`, v `0.0070`, o `0.0134`, gate `0.02796`, up `0.02798`, down `0.00954`. The discontinuity at M6 is predicted by the source limit for gate/up/down; it is not a geometry recommendation. M5 remains frozen canonical.

## B. What v0.32.0 changes—and does not change—on M1

v0.32.0 adds `qmv_wide`: it tiles 2–5 input vectors, decodes each affine quantized subchunk once and reuses it across vectors. For affine it compiles `affine_qmv_wide_bfloat16_t_gs_64_b_3_nv_5_kl_8_batch_0`; this symbol is present in the retained isolated 0.32 metallib.

However, its exact dispatch predicate is:

```cpp
use_qmv_wide(mode, d) = mode != "affine" || d.get_architecture_gen() >= 15;
if (M >= 2 && use_qmv_wide(mode, d)) qmv_wide(...); else qmv(...);
```

Our affine/gen13 M1 fails it. Therefore MLX 0.32.0 would also select old qmv/qmv_fast at M5 for all seven shapes, not qmv_wide. Its vector-limit function is unchanged for this gen/size regime. This is a path-selection statement, **not** a claim of bit-identical whole-runtime code or performance: source alone cannot causally explain Stretch 030’s valid `13.0748 → 12.3418 tok/s` (`0.94393`) regression. In particular, qmv_wide cannot be the direct improvement/regression mechanism on this M1 because it is not selected; multiple other backend/runtime changes exist between tags, and no new full-runtime comparison was run.

## C. Upstream evidence and transfer limits

- **PR #3764** says qmv_wide targets M=2–8 and amortizes a decoded group across vectors. Its affine benchmark table labels M2 Pro as `qmv` (not wide); wide affine gains begin on M3 Ultra/M4 Pro/M5 Max. The PR’s source comment explicitly says affine qmv_wide only beats qmv on gen 15+. It gives no M1 and no 3-bit/group64 result.
- **#3553** is M4 Pro, affine 4-bit/group64, and identifies nonlinear qmv_fast small-M costs. A comment supplies a separate M1 Pro / 0.31.2 / 4-bit observation, not an M1/3-bit result. It is motivation for the local map, not transfer proof.
- **#3839** is M4 Pro / 0.32.0 / BF16 affine 4-bit/group64. It reports qmv_wide improvement versus 0.31.2 but residual M4–M8 cost. Its author’s own generic skinny-M prototype was slower than qmv_wide. This is not evidence against a distinct M1-specific implementation.
- **#3852** is M4 Pro / 0.32.0 / group128 and 2-bit/4-bit, plus M3-Max comments. It concerns bit-width scaling and qmm tile plateaus, not our M1 3-bit/group64 case.

Thus upstream makes a literal qmv_wide backport non-plausible on gen13 affine, but it does **not** prove that no future M1-specific kernel can exist.

## E. Backport decision

No reliable prototype was implemented. Route A would need a self-contained, exact port of MLX’s packing/dequantization, simdgroup/reduction semantics and all seven shape specializations; route B would require an isolated local MLX build. Both are technically possible but are not justified by the upstream gen-15 affine gate, the retained M1 source path, or a demonstrated M1/3-bit upside. They would create a new custom-kernel factor rather than a small source observation.

Consequently no numerical/timing treatment exists, no weighted end-to-end saving is defensible, and the required `>=5%` GO condition cannot be evaluated or met. Classification is **INVESTIGATION_ONLY**, not a claim that all possible M1-specific future kernels are disproved.

## Evidence and next action

- Runner: `scripts/stretch_m5_quantized_kernel_path_035_feasibility.py`
- Benchmark evidence: `results-local/stretch/m5-quantized-kernel-path-035/20260820-202259/summary.json`
- Upstream source/issue snapshots: `results-local/stretch/m5-quantized-kernel-path-035/upstream/` (ignored local evidence)

Keep the canonical monolithic M5 `mx.quantized_matmul` path. Do not begin a Stretch 035 ABBA. A future custom M1 kernel would require new explicit authorization, a separately preregistered factor, and a correctness-first isolated prototype.
