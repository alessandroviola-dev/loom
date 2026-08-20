# Stretch 029 — Gate+Up Quantized Fusion — PREREGISTRATION

Date: 2026-08-20
Status: READY AFTER HARNESS FREEZE

## Scientific question

Under the canonical Stretch 027 execution architecture, can Qwen3 MLP `gate_proj` and `up_proj` be represented as one persistent fused 3-bit/group64 quantized projection and evaluated with one `mx.quantized_matmul` per layer, while preserving frozen numerical exactness and improving target verification rate?

## Evidence motivating the test

Stretch 028 valid run `20260820-164802` measured:
- MLP path `0.3265953894588165 s/block`
- attention path `0.1231006117692838 s/block`
- MLP/attention `2.653076899982628x`
- gate_proj `0.0965807989705354 s/block`
- up_proj `0.09931493003387004 s/block`
- down_proj `0.09428692991302039 s/block`.

Frozen mlx-lm v0.31.3 Qwen3 computes:
`down_proj(swiglu(gate_proj(x), up_proj(x)))`.

Frozen MLX v0.31.2 `QuantizedLinear.__call__` delegates directly to `mx.quantized_matmul(..., transpose=True)` with the layer's packed weight, scales and affine quantization biases.

## Frozen architecture

Both variants keep:
- Qwen3-8B 3-bit/group64
- MLX 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- M=5
- H36
- full raw-weight persistence
- one final cleanup per pass
- ordinary BF16 KV
- prompt/oracle sequence
- exact numerical/top1/acceptance gates
- I/O and resource policy
- no cache purge
- no runtime/model download or upgrade.

## CONTROL

Canonical Stretch 027 SINGLE_PASS helper:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`

Frozen blob:
`6636456df5a773ac6062fdad66b7dc96abe8bd81`

## FUSED treatment

One scientific factor only:
- replace the two separate quantized calls `gate_proj(x)` and `up_proj(x)` with one fused quantized call;
- packed `weight`, `scales`, and affine quantization `biases` are concatenated by output row exactly once during block setup;
- after fused arrays materialize, the original gate/up module references are removed so steady-state raw quantized parameter payload is not intentionally duplicated;
- fused output is split exactly into gate and up halves;
- SwiGLU and `down_proj` remain unchanged.

No temporary per-forward weight concatenation is permitted.

## Exactness risk

The fused output dimension is different from each separate projection and may select a different MLX quantized kernel. Therefore bitwise/numerical equivalence is not assumed.

The inherited M5 oracle numerical parity gate is decisive.

If the first FUSED constituent returns frozen oracle numerical/top1/acceptance failure, classify the experiment as a valid scientific fusion-parity FAIL and stop. Do not run rescue variants.

## Balanced order

`CONTROL -> FUSED -> FUSED -> CONTROL`

No automatic retry.

## Primary performance metric

If all four constituents pass exactness/resource/provenance gates:
- pooled target-verification token/s
- `FUSED / CONTROL` ratio.

Secondary:
- median/mean target block wall
- min free memory
- peak swap
- fused setup provenance/payload telemetry.

## Scientific classifications

Success with complete ABBA:
`GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS`

Valid scientific numerical failure on FUSED:
`GATE_UP_QUANTIZED_FUSION_NUMERICAL_PARITY_FAIL`

Harness/resource/provenance/incomplete sequence:
`GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE`

## Interpretation

- FUSED exact + faster: promote fused gate/up as preferred MLP representation and continue from that baseline.
- FUSED exact + flat/slower: gate/up fusion is not preferred under MLX 0.31.2; close this implementation path.
- FUSED parity fail: preserve the fail and do not relax thresholds or try alternate output ordering/partial fusion post hoc.

A newer MLX runtime remains a separate future factor.
