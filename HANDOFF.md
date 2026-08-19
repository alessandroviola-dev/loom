# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_010_SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_READY`

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
- Do not equate logical/repeated safetensors materialization time with physical SSD throughput; macOS page cache may satisfy reads.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Current Stretch disk is ~36.28 GiB free; no download is planned.

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

Valid run `20260819-173553`, `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`:
- prompt logits max/mean diff 0.0 / 0.0
- generated token equality true; token `[[1]]`
- resident/streamed KV after prompt: 37,748,736 B, offsets 4
- same token fed back through persisted caches
- resident/streamed KV after feedback: 37,748,736 B, offsets 5
- post-token logits max/mean diff 0.0 / 0.0
- resident full model 3,583,928,320 B
- max streamed raw-weight stage 272,269,312 B
- ratio 13.16317396798652x.

Canonical result:
`research/stretch/one-token-kv-autoregressive-parity-008-result.md`.

### 009 — COMPLETE PASS

Plan:
`research/stretch/four-token-kv-autoregressive-parity-009-plan.md`

Runner/blob:
- `scripts/stretch_four_token_kv_autoregressive_parity_009.py`
- `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Valid run `20260819-183143`:
`FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`.

Frozen prompt:
`[[1,42,2048,151935]]`.

Parity/generation:
- prompt max/mean logit diff **0.0 / 0.0**
- all four feedback steps max/mean diff **0.0 / 0.0**
- top-1 equality true at every step
- resident generated sequence **`[1,374,264,4647]`**
- streamed generated sequence **`[1,374,264,4647]`**
- sequence equality true.

KV:
- offsets advance `4 -> 5 -> 6 -> 7 -> 8`
- final resident offsets all 8
- final streamed offsets all 8
- final resident/streamed KV **37,748,736 / 37,748,736 B**
- no new capacity block below position 256.

Weight residency:
- resident full model **3,583,928,320 B**
- max streamed raw-weight stage **272,269,312 B**
- ratio **13.16317396798652x**.

Transformer-only per-feedback-token timing:
- layer materialization walls `[0.188703, 0.188927, 0.188051, 0.188951]` s; mean **0.188658 s/token**
- layer forward walls `[0.188268, 0.194739, 0.193971, 0.19229]` s; mean **0.192317 s/token**
- combined mean transformer-only materialization+forward **0.380975 s/token**.

Do not convert the transformer-only timing directly to end-to-end tok/s or physical SSD throughput. It excludes other stages/overhead and repeated reads may be page-cache served.

Host/resource:
- launch 67/67/68% free, swap 595.62 MB
- whole-run min free **21%**, peak swap **1401.94 MB**, peak child RSS **641.656 MB**
- resident bucket min free 21%
- stream prompt bucket min free **64%**
- stream tokens bucket min free **64%**, peak RSS **251.5 MB**
- disk **36.281 -> 36.281 GiB**.

Canonical result:
`research/stretch/four-token-kv-autoregressive-parity-009-result.md`.

Canonical interpretation:
> The phase-streamed Qwen3-8B path sustains a short four-token deterministic autoregressive sequence with persistent KV state and exact official-resident parity at every step while raw-weight stage residency remains bounded at ~272.27 MB.

Boundary: still no tokenizer/text integration, sampling, long-run stability, 256-position boundary, physical storage bytes/token or optimization.

## Stretch 010 — Sixteen-Token Autoregressive Stability — READY

Plan:
`research/stretch/sixteen-token-autoregressive-stability-010-plan.md`

Runner:
`scripts/stretch_sixteen_token_autoregressive_stability_010.py`

Runner blob:
`ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Frozen source:
- exact Stretch 009 blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Single scientific change:
- deterministic generated/feedback continuation depth **4 -> 16 tokens**.

Preserved:
- same prompt `[[1,42,2048,151935]]`
- same Qwen3-8B 3-bit artifact/environment
- same official resident control
- same ordinary BF16 36-layer KVCache policy
- same deterministic argmax
- same phase-streamed embedding/layers/norm/head
- same materialization/parity/cache gates
- same file-backed child transport
- same host/runtime guardrails
- no tokenizer/sampling/KV quantization/prefetch/download.

KV expectations:
- prompt offset 4
- 16 feedback passes advance final offset to **20**
- expected total allocation remains **37,748,736 B**, because offset 20 remains below the 256-position capacity boundary.

Instrumentation-only addition:
- expose `total_pass_wall_seconds` for each streamed token pass
- mean/median full-pass seconds/token
- logical streamed tok/s = `1 / mean_full_pass_seconds`.

Interpretation boundary:
logical tok/s is measured runtime wall under current host/cache state, not physical SSD throughput or a claim about bytes read from disk.

Primary PASS:
`SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`.

# Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_sixteen_token_autoregressive_stability_010.py
python3 scripts/stretch_sixteen_token_autoregressive_stability_010.py
```

No download is expected.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.