# Stretch 006 — Full 36-Layer Streamed Body Parity — Result

Date: 2026-08-19
Run: `20260819-164605`
Classification: **FULL_36_LAYER_STREAMED_BODY_PARITY_PASS**

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

No tokenizer, token embedding lookup, final model norm, LM head, KV cache or autoregressive token generation occurred.

## Provenance

Corrected Stretch 006 wrapper blob:
`ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`

Frozen Stretch 005 source blob:
`8bbfff727a0131c48d4ba71edc8de485182b7fbe`

Transform preflight:
- source provenance PASS
- frozen transform PASS
- layer policy exact 0..35
- resident tolerance +/-36 MiB
- streamed/parity/safety gates unchanged.

The earlier transform-invariant launch is separately recorded as a harness failure with no scientific result.

## Full transformer-body control

All 36 transformer blocks were materialized simultaneously in the resident control.

Per-layer frozen payload:
`84,427,264 B`.

Exact 36-layer payload:
`3,039,381,504 B`.

Observed resident materialized delta:
**3,039,315,964 B**.

Difference from exact payload:
`-65,540 B`, within the preregistered +/-36 MiB resident tolerance and consistent with the small allocator/accounting movement seen in earlier Stretch controls.

## Streamed path

Layers 0 through 35 were executed sequentially with one block materialized at a time.

For every streamed layer:
- pre-eval active delta: **0 B**
- materialized delta: **84,427,264 B**
- post-clear active delta: **0 B**
- post-clear cache: **0 B**.

Maximum one-layer streamed materialized delta:
**84,427,264 B**.

No cumulative active/cache growth was observed across the 36 streamed cycles.

Resident / streamed raw-weight materialization ratio:
**35.99922371048291x**.

## Numerical parity

Resident vs streamed final activation:
- parity pass: true
- max absolute difference: **0.0**
- mean absolute difference: **0.0**
- frozen threshold: `0.011210000000000001`.

The measured final outputs are bit-identical at the float32 comparison boundary.

## Timing

Streamed path totals:
- parameter materialization wall: **1.207812 s**
- transformer forward wall: **0.440137 s**.

These are micro-forward measurements for batch1/sequence4 and must not be interpreted as autoregressive token throughput.

## System telemetry

Launch host gate:
- 66% free / 802.5 MB swap
- 66% free / 802.5 MB swap
- 66% free / 802.5 MB swap.

Whole-run telemetry:
- minimum observed free memory: **22%**
- peak observed swap: **1325.69 MB**
- peak child RSS: **381.844 MB**
- disk free: **36.297 -> 36.293 GiB**.

The system-wide minimum-free and peak-swap values cover both the memory-heavy resident control and the streamed phase. They must not be attributed specifically to the streamed path without phase-scoped telemetry.

## Canonical interpretation

Stretch 006 establishes that the **entire 36-block Qwen3 transformer body** can execute with one-layer-at-a-time streamed raw-weight residency while producing the same final activation as a control holding all 36 block weights simultaneously.

For this frozen micro-forward:
- resident raw transformer-block weight materialization is ~2.831 GiB;
- streamed raw transformer-block materialization remains ~80.52 MiB at a time;
- observed residency ratio is ~36x;
- every streamed layer returns active/cache deltas to baseline;
- numerical parity is exact.

This is direct evidence for full-body dense layer streaming on the reference Apple M1 / 8 GB system.

It is **not yet end-to-end LLM inference**. Shared/non-layer weights remain outside the experiment: token embeddings, final RMSNorm and output projection/LM head, plus tokenizer, KV cache and autoregressive generation.

## Decision

Proceed to shared-component anatomy before implementing full-logit parity. The next read-only step must identify the exact non-layer tensor layout and config semantics (`tie_word_embeddings`, embedding/output-head tensor presence, quantization and byte cost) of the local artifact. Then preregister shared-component + final-logit parity without guessing the storage policy.
