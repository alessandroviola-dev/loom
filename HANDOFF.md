# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_009_FOUR_TOKEN_READY`

## Mission

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / research constraints

- Never reset or replace production Pi configuration.
- Never silently delete verified models or canonical results.
- Record disk around model/runtime work.
- Runtime guardrail where applicable: free memory <5% OR swap >5600 MB abort.
- System-wide free memory/swap are decisive; process RSS is diagnostic.
- Harness/parser/capture defects are not model failures.
- Do not weaken guardrails post-hoc.
- Change one scientific factor at a time where causal attribution matters.
- No automatic rescue ladders or hidden retries.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute whole-run host telemetry to a sub-phase without phase-scoped evidence.
- Long child runs must not use undrained verbose stdout/stderr pipes; prefer file-backed state/final payloads.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Current Stretch disk is ~36.29 GiB free; no download is planned.

## Frozen capability references

Canonical Ollama/MLX 4B `qwen3.5:4b-mlx`, context 4096:
- Coding Baseline 001: artifact 40.71, delivery-adjusted 30.00, delivery 3/6, generation 16.01 tok/s
- Pi Agentic Coding 001: delivery-adjusted 77.15, strict 60.00, delivery 6/6, ~612 s.

llama.cpp 4B Q4 efficiency reference:
- pp512 230.85 tok/s
- tg128 22.33 tok/s.

Direct MLX Qwen3-8B 3-bit coding reference:
- COMPLETE
- min free 14%
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6
- technically stable but not promoted on quality.

## Track A — Amplify

Amplifier 001–003 characterized a resource boundary in the canonical 4B repair workflow. Do not claim a leak or specific KV/allocator cause.

Amplifier 004 remains preregistered/queued:
- `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- one change: variable repair-feedback detail capped at 768 UTF-8 bytes.

Stretch remains primary while architectural evidence continues to improve.

# Track B — Stretch / Memory Hierarchy

Frozen subject:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Environment/config:
- Qwen3, hidden 4096, 36 layers, vocab 151936
- 32 attention heads, 8 KV heads, head dim 128
- RMSNorm eps 1e-6
- `tie_word_embeddings=false`
- 3-bit/group64
- mlx 0.31.2, mlx-lm 0.31.3, transformers 5.12.1.

Weight layout:
- complete tensor payload 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each layer 84,427,264 B / 25 tensors
- final norm 8,192 B
- LM head 272,269,312 B.

## Frozen Stretch results

### 001 — COMPLETE PASS
`LAYER_ADDRESSABLE_IO_PASS`: all 36 layers exactly addressable; selective one-layer read works.

### 002 — COMPLETE PASS
`SINGLE_LAYER_MLX_EVICTION_PASS`: one layer 0 -> 84,427,264 -> 0 B active.

### 003 — COMPLETE PASS
`TWO_LAYER_BOUNDED_RESIDENCY_PASS`: repeated one-layer materialize/evict remains bounded.

### 004 — COMPLETE PASS
`TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`: first real Qwen3 block compute; exact resident/streamed activation parity.

### 005 — COMPLETE PASS
`EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`: resident/streamed raw-layer ratio 7.999223710482908x; exact parity.

### 006 — COMPLETE PASS
Valid run `20260819-164605`, `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`:
- resident body 3,039,315,964 B
- max streamed layer 84,427,264 B
- ratio 35.99922371048291x
- all 36 layer cycles reclaim layer weights
- max/mean activation diff 0.0 / 0.0.

Earlier transform launch is harness-only/no scientific result.

### 007A — COMPLETE PASS
Run `20260819-165247`, `SHARED_COMPONENT_ANATOMY_PASS`:
- embedding 272,269,312 B
- final norm 8,192 B
- LM head 272,269,312 B
- other 0
- untied embedding/head.

### 007B — COMPLETE PASS
Run `20260819-170334`, `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`:
- official resident full model 3,583,928,320 B
- max streamed raw-weight stage 272,269,312 B
- ratio 13.16317396798652x
- full logits `[1,4,151936]` max/mean diff 0.0 / 0.0
- top-1 equality true.

### 008 — COMPLETE PASS

Plan:
`research/stretch/one-token-kv-autoregressive-parity-008-plan.md`

Scientific runner/blob:
- `scripts/stretch_one_token_kv_autoregressive_parity_008.py`
- `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`.

Harness pipefix/blob:
- `scripts/stretch_one_token_kv_autoregressive_parity_008_pipefix.py`
- `8b2ce5902d3ed45c9120273fab415fe67a026d4a`.

First launch stalled after `stream_token_layer_17_complete` because verbose child-state JSON filled an undrained captured stdout pipe. It is recorded as harness I/O stall / no scientific result.

Valid run `20260819-173553`:
`ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`.

Frozen prompt:
`[[1,42,2048,151935]]`.

Results:
- prompt logits max/mean diff 0.0 / 0.0
- generated token equality true; token `[[1]]`
- resident/streamed KV after prompt: 37,748,736 B, all offsets 4
- same token fed back through persisted caches
- resident/streamed KV after feedback: 37,748,736 B, all offsets 5
- post-token logits max/mean diff 0.0 / 0.0
- post-token top-1 equality true
- resident full model 3,583,928,320 B
- max streamed raw-weight stage 272,269,312 B
- ratio 13.16317396798652x
- whole-run min free 26%, peak swap 1583.75 MB, peak child RSS 878.5 MB
- disk 36.294 -> 36.290 GiB.

Diagnostic streamed buckets:
- prompt min free 64%, peak swap 1479.75 MB, peak RSS 347.578 MB
- token min free 69%, peak swap 1471.75 MB, peak RSS 166.531 MB.

Canonical result:
`research/stretch/one-token-kv-autoregressive-parity-008-result.md`.

Canonical interpretation:
> LOOM has demonstrated actual one-token autoregressive cache reuse with persistent per-layer KV state while raw Qwen3-8B weights remain phase-streamed, with exact resident parity.

Boundary: one deterministic token only; not yet tokenizer/text integration, sampling, long-run stability, cache-capacity boundary, physical SSD bytes/token or optimized tok/s.

## Stretch 009 — Four-Token KV Autoregressive Parity — READY

Plan:
`research/stretch/four-token-kv-autoregressive-parity-009-plan.md`

Runner:
`scripts/stretch_four_token_kv_autoregressive_parity_009.py`

Runner blob:
`3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Single scientific change vs valid Stretch 008:
- autoregressive continuation depth **1 -> 4 generated/feedback tokens**.

Preserved:
- same Qwen3-8B 3-bit artifact/environment
- same prompt `[[1,42,2048,151935]]`
- same ordinary BF16 `KVCache`
- same deterministic argmax policy
- same official resident control
- same phase-streamed embedding/layers/norm/head
- same weight-stage gates and host guardrails
- no tokenizer, sampling, KV quantization, prefetch or optimization.

Expected cache offsets:
- after prompt: 4
- after feedback tokens: 5, 6, 7, 8.

Expected KV allocation remains ~37,748,736 B because offset 8 is below the first 256-position capacity boundary.

Primary gates:
- full prompt parity + first token equality
- four feedback full-logit parity gates
- top-1 equality at every feedback step
- identical four-token generated sequence
- cache count/offset/byte gates after every step
- raw-weight stage gates on every pass
- per-token layer materialization/forward timing.

Harness architecture:
- progress -> `child-state.json`
- final scientific payload -> `child-final.json`
- stdout/stderr -> file-backed handles
- no undrained verbose captured pipe.

Primary PASS:
`FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_four_token_kv_autoregressive_parity_009.py
python3 scripts/stretch_four_token_kv_autoregressive_parity_009.py
```

No download is expected.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.