# LOOM Stretch 016 — QuantizedLinear M-Boundary Mapping — Result

Date: 2026-08-20
Status: COMPLETE PASS
Classification: `QUANTIZED_LINEAR_M_BOUNDARY_MAPPED`

## Run

Valid run:
`results-local/stretch/quantized-linear-m-boundary-mapping-016/20260820-125212`

Runner:
`scripts/stretch_quantized_linear_m_boundary_mapping_016.py`

Frozen runner blob:
`a5c3f4acd6a4150d2db7477f3f20d01a00b4f759`

Stretch 015 provenance:
`933c366220625e845e788b2ab1521ae78d9e7d15`

Stretch 002 helper provenance:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef`

## Frozen environment

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- layer-0 frozen model weights
- no MLX upgrade
- no strict mode
- no threshold relaxation
- no download

All source, version, model/config, quantization and layer-0 provenance gates passed.

Host launch gate passed:
- sample 1: 70% free, 1096.62 MB swap
- sample 2: 70% free, 1096.62 MB swap
- sample 3: 70% free, 1096.62 MB swap

## Scientific result

The M=1..16 sweep mapped two distinct exactness boundaries.

### Attention-side projections

`q_proj`
- largest exact M: 9
- first divergent M: 10
- first divergence max abs: 0.00390625
- first divergence mean abs: 0.00017721284530125558

`k_proj`
- largest exact M: 9
- first divergent M: 10
- first divergence max abs: 0.00390625
- first divergence mean abs: 0.0002411347086308524

`v_proj`
- largest exact M: 9
- first divergent M: 10
- first divergence max abs: 0.0009765625
- first divergence mean abs: 0.00016859316383488476

`o_proj`
- largest exact M: 9
- first divergent M: 10
- first divergence max abs: 0.001220703125
- first divergence mean abs: 0.00015858907136134803

### MLP projections

`gate_proj`
- largest exact M: 5
- first divergent M: 6
- first divergence max abs: 0.001220703125
- first divergence mean abs: 0.00015750739839859307

`up_proj`
- largest exact M: 5
- first divergent M: 6
- first divergence max abs: 0.0009765625
- first divergence mean abs: 0.00014882815594319254

`down_proj`
- largest exact M: 5
- first divergent M: 6
- first divergence max abs: 1.75
- first divergence mean abs: 0.16764232516288757

Peak MLX memory:
272,437,320 B.

Disk free after:
36.694 GiB.

## Canonical interpretation

The frozen MLX 0.31.2 / Apple M1 / Qwen3-8B 3-bit path has a reproducible shape-dependent numerical boundary.

The first system-relevant boundary is the MLP boundary:

> The actual frozen layer-0 quantized MLP projections reproduce the M=1 first-row result exactly through `M=5` and change numerically starting at `M=6`.

The attention-side q/k/v/o projections remain exact longer, through `M=9`, and first change at `M=10`.

Therefore the MLP is the limiting component for an exact small-M oracle-verification path under the current frozen runtime.

This explains the Stretch 014 M=8 numerical-parity failure and refines Stretch 015's M4/M8 attribution into an exact boundary.

## Boundary / non-claims

- This result maps numerical behavior; it does not by itself name the exact internal Metal kernel selected at each M.
- Do not infer that every layer is guaranteed exact at M=5 solely from this layer-0 probe; full-model oracle verification remains the appropriate end-to-end confirmation.
- Do not relax numerical parity thresholds to admit M>=6.
- Do not silently upgrade MLX and compare the result as though it were the same experiment.
- Later MLX small-M work may change performance/numerics, but any runtime upgrade is a separate scientific factor.

## Decision

1. Freeze `M=5` as the largest exact layer-0 quantized-linear candidate under the current runtime.
2. Do not continue to M=8 or M=16 under MLX 0.31.2 as an exact-oracle path.
3. Next, confirm M=5 end-to-end across the full streamed/hotset target path before treating block size 5 as a usable exact verification point.
4. Keep any newer-MLX experiment separate from the frozen 0.31.2 baseline.
