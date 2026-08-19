# Stretch 002 — Single-Layer MLX Materialization + Eviction — Result

Date: 2026-08-19
Run: `20260819-155641`
Classification: **SINGLE_LAYER_MLX_EVICTION_PASS**

## Subject

Local artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen Direct MLX environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

No Qwen model construction, tokenizer, KV cache, token generation, network access or download occurred.

## Provenance

Probe layer: 18

- selected tensors: 25
- expected tensor payload: 84,427,264 B
- header-derived provenance: PASS

## Host launch state

Three-sample host gate:
- 70% free / 850.5 MB swap
- 68% free / 850.5 MB swap
- 67% free / 850.5 MB swap

Gate: PASS.

## MLX materialization / eviction

MLX baseline active/cache:
- 0 / 0 B

After `mx.load()` and retaining only layer-18 lazy arrays, before `mx.eval()`:
- active delta: **0 B**
- eager-load guard: PASS

After `mx.eval(layer18)`:
- active delta: **84,427,264 B**
- this exactly matches the header-derived layer tensor payload
- eval wall: **0.039611 s**

After deleting layer references, `gc.collect()` and `mx.clear_cache()`:
- active delta: **0 B**
- cache delta: **0 B**
- eviction gate: PASS

## System telemetry

- minimum observed free memory: 67%
- peak observed swap: 850.5 MB
- peak child RSS: 40.25 MB
- disk free: 36.319 -> 36.319 GiB

Process RSS is diagnostic only; the MLX active/cache counters and system-wide memory/swap measurements are the relevant experimental signals here.

## Canonical interpretation

The selected Qwen3-8B 3-bit transformer layer can be represented as lazy safetensors-backed MLX arrays without observed active-memory materialization, then materialized independently to exactly its 84,427,264-byte tensor payload, and subsequently reclaimed back to baseline active/cache memory.

This establishes a second prerequisite for dense layer streaming: **single-layer MLX residency and reclamation are operationally feasible without constructing the full model.**

This is still not evidence of end-to-end streamed inference. No transformer forward computation, activations, shared embeddings/norm, KV cache, residual state, tokenizer or generation was included.

The next experiment must test repeated bounded residency in the same MLX process across at least two distinct consecutive layers before attempting a streamed forward path.
