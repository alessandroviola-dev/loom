# Stretch 004 — Two-Layer Streamed Micro-Forward Parity — Result

Date: 2026-08-19
Run: `20260819-162454`
Classification: **TWO_LAYER_STREAMED_FORWARD_PARITY_PASS**

## Subject / environment

Artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Model/config preflight:
- model type `qwen3`
- hidden size 4096
- 36 transformer layers
- 32 attention heads
- 8 KV heads
- head dim 128
- quantization 3-bit / group size 64.

No full Qwen construction, tokenizer, embedding lookup, KV cache, LM head or token generation occurred.

## Frozen micro-forward

Layers:
- 18
- 19

Each layer provenance:
- 25 tensors
- 84,427,264 B.

Input:
- deterministic synthetic activation
- batch 1
- sequence length 4
- hidden size 4096
- same input and official Qwen3 TransformerBlock implementation for resident and streamed paths.

## Host launch state

Host gate:
- 66% free / 826.5 MB swap
- 65% free / 826.5 MB swap
- 65% free / 826.5 MB swap

Gate: PASS.

## Resident control

Both layer 18 and layer 19 were materialized simultaneously.

Observed materialized delta:
**168,854,528 B**

This exactly equals:
`2 * 84,427,264 B`.

The resident control therefore exposed the expected two-layer raw weight residency.

## Streamed path

Layer 18:
- pre-eval delta: -65,540 B
- materialized delta: 84,361,724 B
- post-clear delta: -65,540 B
- post-clear cache: 0 B.

Layer 19:
- pre-eval delta: 0 B
- materialized delta: 84,427,264 B
- post-clear delta: 0 B
- post-clear cache: 0 B.

Both materialized deltas are within the frozen +/-1 MiB tolerance around the exact 84,427,264-byte layer payload, and both post-clear states are within the frozen +/-4 MiB activation/replacement allowance.

The small negative layer-18 deltas are allocator/accounting movement relative to that cycle's sampled pre-layer state; they are not interpreted as negative physical memory and do not change the preregistered PASS.

## Numerical parity

Resident vs streamed final output:
- parity pass: true
- max absolute difference: **0.0**
- mean absolute difference: **0.0**
- frozen threshold: `0.00043500000000000006`.

The two execution paths produced bit-identical values at the measured float32 comparison boundary.

## System telemetry

- minimum observed free memory: 63%
- peak observed swap: 826.5 MB
- peak child RSS: 178.281 MB
- disk free: 36.296 -> 36.296 GiB.

## Canonical interpretation

Stretch 004 is the first LOOM experiment to combine actual Qwen3 transformer computation with streamed one-layer-at-a-time weight residency and a resident numerical control.

For this frozen two-block micro-forward, the resident path held approximately two layer payloads simultaneously while the streamed path materialized approximately one layer payload at a time, evicted it, and continued with the next layer. The final output matched the resident control exactly.

This is direct evidence that **streamed transformer-block computation is operationally feasible for a two-layer Qwen3 path with bounded raw weight residency** on the reference system.

It is not yet evidence of end-to-end streamed LLM inference. The experiment excludes embeddings, final norm, LM head, tokenizer, KV cache, token generation and the other 34 transformer layers.

## Decision

Proceed to a longer controlled block chain before adding shared model components or KV/token generation.

The next experiment should preserve the same resident-vs-streamed numerical parity design and extend only the number of consecutive transformer blocks. Its purpose is to test whether resident raw-weight memory grows with chain depth while streamed raw-weight residency remains approximately one layer at a time.
