# Stretch 003 — Two-Layer Repeated Bounded Residency — Result

Date: 2026-08-19
Run: `20260819-161134`
Classification: **TWO_LAYER_BOUNDED_RESIDENCY_PASS**

## Subject / environment

Local artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen Direct MLX environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Stretch 002 source provenance:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef` — PASS.

No full-model construction, tokenizer, KV cache, token generation, network access or download occurred.

## Frozen probe

Same MLX child process.

Exactly two consecutive layers:
- layer 18
- layer 19

Each layer provenance:
- 25 tensors
- 84,427,264 B.

## Host launch state

Three-sample gate:
- 67% free / 826.5 MB swap
- 67% free / 826.5 MB swap
- 67% free / 826.5 MB swap

Gate: PASS.

## Layer 18 cycle

- pre-eval active delta: 0 B
- post-eval active delta: 84,427,264 B
- post-clear active delta: 0 B
- post-clear cache delta: 0 B
- `mx.eval` wall: 0.039539 s

## Layer 19 cycle

- pre-eval active delta: 0 B
- post-eval active delta: 84,427,264 B
- post-clear active delta: 0 B
- post-clear cache delta: 0 B
- `mx.eval` wall: 0.041369 s

## System telemetry

- minimum observed free memory: 67%
- peak observed swap: 826.5 MB
- peak child RSS: 40.469 MB
- disk free: 36.299 -> 36.299 GiB

## Canonical interpretation

Repeated raw-weight residency is bounded across two different consecutive transformer layers in the same MLX process. Layer 18 can be materialized and fully reclaimed, then layer 19 can repeat the same cycle without observed MLX active/cache accumulation.

This moves the Stretch branch beyond one-off lazy loading and establishes the third prerequisite for a streamed transformer runtime: **sequential per-layer materialization and eviction can repeat in-process while keeping weight residency bounded.**

This still does not prove streamed transformer inference. No attention/MLP forward computation, activation stream, shared embedding/norm weights, KV cache or token generation was included.

The next experiment should introduce actual Qwen3 transformer-block computation on a tiny deterministic input and compare a streamed two-layer path numerically against an exact resident two-layer control while preserving bounded layer-weight residency.