# Stretch 007B — Phase-Streamed Full-Logit Parity — Result

Date: 2026-08-19
Run: `20260819-170334`
Classification: **PHASE_STREAMED_FULL_LOGIT_PARITY_PASS**

## Subject / environment

Artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

Config/layout preflight:
- qwen3
- hidden size 4096
- 36 transformer layers
- vocab size 151936
- 32 attention heads
- 8 KV heads
- head dim 128
- RMSNorm epsilon 1e-6
- `tie_word_embeddings=false`
- quantization 3-bit / group64
- total tensor bytes 3,583,928,320 B
- embedding 272,269,312 B
- final RMSNorm 8,192 B
- LM head 272,269,312 B
- 36/36 transformer-layer provenance PASS.

Runner:
`scripts/stretch_phase_streamed_full_logit_parity_007b.py`

Frozen runner blob:
`b08c9b44ae062ee259ab6641575e44c4d7d753e6`

## Frozen input

Token IDs:
`[[1, 42, 2048, 151935]]`

No tokenizer, KV cache or autoregressive generation was used.

## Resident official control

Control path:
`mlx_lm.utils.load_model(model_dir, lazy=False, strict=True)`

Observed full-model materialized delta:
**3,583,928,320 B**

This exactly matches the safetensors tensor payload.

## Phase-streamed path

Execution order:
`embedding -> evict -> layers 0..35 one at a time -> final RMSNorm -> LM head -> evict`

Observed weight-stage materialization:
- embedding: **272,269,312 B**
- max transformer layer: **84,427,264 B**
- final RMSNorm: **8,192 B** selected / **8,192 B** materialized
- LM head: **272,269,312 B**
- maximum streamed weight-stage delta: **272,269,312 B**.

Resident / maximum streamed weight-stage ratio:
**13.16317396798652x**.

## Full-logit numerical parity

Expected logits shape:
`[1, 4, 151936]`.

Resident vs phase-streamed logits:
- parity pass: true
- max absolute difference: **0.0**
- mean absolute difference: **0.0**
- threshold: `0.00018125000000000001`
- top-1 equality: true.

Resident top-1 per position:
`[[921, 78, 84, 1]]`

Streamed top-1 per position:
`[[921, 78, 84, 1]]`

The complete measured logits are bit-identical at the float32 comparison boundary.

## System telemetry

Launch host gate:
- 69% free / 1125.62 MB swap
- 69% free / 1125.62 MB swap
- 70% free / 1125.62 MB swap.

Whole-run telemetry:
- minimum observed free memory: **25%**
- peak observed swap: **1586.0 MB**
- peak child RSS: **1007.547 MB**
- disk free: **36.276 -> 36.276 GiB**.

These whole-run values include the official fully resident control and must not be attributed specifically to the streamed phase without phase-scoped evidence.

## Canonical interpretation

Stretch 007B establishes token-ID-to-final-logit execution for the complete Qwen3-8B 3-bit model using phase-streamed raw-weight residency:
- embedding and LM head are independently materialized only when needed;
- all 36 transformer blocks remain one-layer-at-a-time streamed;
- final RMSNorm is materialized separately;
- the complete logits match the official fully resident `mlx_lm` control exactly.

For this frozen forward, the official resident control materializes the full 3,583,928,320-byte tensor payload, while LOOM's largest single raw-weight stage is 272,269,312 B, an observed ~13.16x ratio.

This is **full forward parity**, but still not an autoregressive-generation result because no KV cache was used and no generated token was fed back into the model.

## Decision

Proceed to a one-token KV/autoregressive experiment before attempting a longer generation loop. The next experiment must:
1. prefill the same four-token prompt with a real per-layer KV cache;
2. compare resident vs streamed prompt logits;
3. deterministically select one next token via argmax;
4. feed that token through both paths using the same persisted cache state;
5. verify cache offsets and compare the post-token logits.

No tokenizer, sampling, multi-token generation, prefetch or cache quantization is introduced in this step.