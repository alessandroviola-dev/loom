# Stretch 005 — Eight-Layer Streamed Forward Scaling — Result

Date: 2026-08-19
Run: `20260819-163413`
Classification: **EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS**

## Subject / frozen conditions

Artifact: `results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Frozen Qwen3 config:
- hidden size 4096
- 36 transformer layers
- 32 attention heads
- 8 KV heads
- head dim 128
- quantization 3-bit / group size 64.

Chain: layers `[14,15,16,17,18,19,20,21]`.
Input remained the frozen deterministic batch1 / sequence4 / hidden4096 activation. No tokenizer, embedding lookup, final norm, LM head, KV cache or token generation was included.

## Host / safety

Host gate:
- 65% free / 810.5 MB swap
- 63% free / 810.5 MB swap
- 63% free / 810.5 MB swap

Runtime:
- minimum observed free memory: 63%
- peak observed swap: 810.5 MB
- peak child RSS: 169.469 MB
- disk free: 36.294 -> 36.294 GiB.

No safety guardrail was approached.

## Resident control

Expected eight-layer tensor payload:
`8 * 84,427,264 = 675,418,112 B`.

Observed resident materialized delta:
**675,352,572 B**.

Difference from exact header-derived payload: -65,540 B, within the frozen +/-8 MiB gate.

## Streamed path

Maximum observed single-layer materialized delta:
**84,427,264 B**.

Observed resident / streamed materialized ratio:
**7.999223710482908x**.

Per-layer cycles:
- layer 14: pre -65,540 B; materialized 84,361,724 B; clear -65,540 B; cache 0 B
- layers 15–21: pre 0 B; materialized 84,427,264 B; clear 0 B; cache 0 B for every layer.

All eight layers passed the frozen lazy-load, materialization and eviction gates. There was no observed cumulative active/cache growth across the streamed chain.

Stream timing recorded by the runner:
- total parameter materialization wall: 0.042391 s
- total transformer forward wall: 0.067679 s.

These timings are micro-forward measurements and must not be interpreted as autoregressive token throughput.

## Numerical parity

Resident vs streamed final activation:
- parity pass: true
- max absolute difference: **0.0**
- mean absolute difference: **0.0**
- frozen threshold: `0.0008300000000000001`.

At the measured float32 comparison boundary, the resident and streamed eight-block paths were bit-identical.

## Canonical interpretation

Stretch 005 extends the Stretch 004 result from two to eight real Qwen3 transformer blocks while changing only chain depth.

For this frozen micro-forward, resident raw layer-weight materialization scales to approximately eight layer payloads while the streamed path remains approximately one layer payload at a time. The observed residency ratio is ~8x and the final numerical output is identical.

This is direct scaling evidence for bounded one-layer-at-a-time transformer-weight residency. It is still **not end-to-end streamed LLM inference**: shared embedding/final norm/LM head, KV cache, tokenizer, autoregressive generation and the remaining 28 transformer blocks are excluded.

## Decision

Proceed to one full 36-transformer-block body-parity experiment using the same tiny deterministic activation and resident-vs-streamed design before adding shared model components or KV/token generation.
