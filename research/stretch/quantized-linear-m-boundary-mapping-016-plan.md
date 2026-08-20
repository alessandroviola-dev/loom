# LOOM Stretch 016 — QuantizedLinear M-Boundary Mapping

Date: 2026-08-20
Status: READY

## Objective

Map the exact small-`M` transition at which the real frozen layer-0 quantized linear projections stop reproducing their `M=1` first-row result.

Stretch 015 established:

- `M=1` vs `M=4`: no layer-0 traced divergence
- `M=4` vs `M=8`: first divergence at `gate_proj`
- q/k/v/o remain exact at `M=8`
- gate/up/down are shape-dependent at `M=8`
- attention, RoPE, SDPA and KV state are not the first source of the Stretch 014 discrepancy.

## Frozen baseline

Preserve exactly:

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64 artifact
- mlx `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- layer-0 weights and quantization
- no runtime upgrade
- no strict-mode patch
- no threshold relaxation
- no model download.

Stretch 015 runner provenance:
`933c366220625e845e788b2ab1521ae78d9e7d15`.

Canonical Stretch 015 result:
`research/stretch/eight-token-divergence-attribution-015-result.md`.

## Experimental factor

The only changed independent variable is the number of rows/tokens `M` supplied to each already-frozen quantized projection.

Sweep:

`M = 1, 2, 3, ..., 16`.

For every `M`, compare only the first output row against the `M=1` first output row. The first input row is bit-identical across the sweep because the probe tensor is constructed once and only sliced along the sequence dimension.

## Projections

Test the actual quantized layer-0 modules independently:

- q_proj
- k_proj
- v_proj
- o_proj
- gate_proj
- up_proj
- down_proj.

The down-projection probe is constructed independently of gate/up so its own shape boundary is not confounded by upstream MLP divergence.

## Required measurements

For every projection and every `M`:

- exact first-row equality vs `M=1`
- max absolute difference
- mean absolute difference.

For every projection derive:

- largest exact `M` before first divergence
- first divergent `M`, if any in 1..16
- divergence magnitude at the first divergent `M`.

## Interpretation

Primary classification:

`QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`

if at least one of gate/up/down has a reproducible first divergent `M` and the sweep completes under the frozen environment.

The result may be compared with upstream MLX dispatch logic, but the runtime result is primary. Do not infer an exact internal kernel name solely from numerical behavior unless separately instrumented.

## Upstream context boundary

MLX documents shape-dependent quantized-matmul dispatch and different numerical reduction trees in the relevant 0.31.x family. Later `qmv_wide` work targets small-`M` speculative verification, but affine quantization is gated to newer GPU generations in that change. Therefore do not assume a newer wheel fixes the Apple M1 3-bit path without a separate preregistered environment experiment.

## Decision after run

- If a sharp M boundary is mapped, freeze it as the current maximum exact oracle block size under MLX 0.31.2.
- Then decide whether to preserve block size 4 as the exact baseline and explore another speed axis, or create a separate runtime-upgrade experiment.
- Do not contaminate the frozen 0.31.2 result with a package upgrade in this Stretch.
