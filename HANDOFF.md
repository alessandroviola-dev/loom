# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Apple M1 / 8 GB reference system; tracks **Amplify** and **Stretch**.

Current checkpoint: `STRETCH_009_MULTI_TOKEN_PREREGISTRATION`

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
- Change one experimental factor at a time where causal attribution matters.
- No automatic rescue ladders.
- No new large-model acquisition while existing artifacts suffice.
- Do not attribute whole-run host telemetry to a sub-phase without phase-scoped evidence.
- Avoid captured stdout/stderr deadlocks in long child processes; prefer file-backed state/final-result transfer.

Verified GGUF and Direct MLX 3-bit/4-bit artifacts remain retained. Stretch disk is ~36.29 GiB free; no download is planned.

# Frozen capability references

## Canonical Ollama/MLX 4B

`qwen3.5:4b-mlx`, context 4096.

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71
- delivery-adjusted 30.00
- delivery 3/6
- recovered semantic diagnostic 82.86
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- delivery-adjusted 77.15
- strict 60.00
- delivery 6/6
- protocol 4/6
- ~612 s.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4: pp512 230.85 tok/s, tg128 22.33 tok/s, minimum free 22%.

## Direct MLX 8B 3-bit reference

`mlx-community/Qwen3-8B-3bit` full coding benchmark:
- COMPLETE
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6.

Technically stable but not promoted on quality.

# Track A — Amplify

Amplifier 001–003 established that the canonical Ollama/MLX 4B repair path is resource-bound under the frozen workflow. Do not claim a leak or specific KV/allocator root cause.

Amplifier 004 — Compact Feedback remains preregistered/queued:
- plan `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- runner `scripts/capability_amplifier_004_compact_feedback.py`
- blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- single change: variable repair-feedback detail capped at 768 UTF-8 bytes.

Stretch remains primary while the architectural sequence continues to produce positive evidence.

# Track B — Stretch / Memory Hierarchy

Frozen subject:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Frozen environment/config:
- qwen3
- hidden size 4096
- 36 transformer layers
- vocab 151936
- 32 attention heads
- 8 KV heads
- head dim 128
- RMSNorm eps 1e-6
- `tie_word_embeddings=false`
- quantization 3-bit/group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Weight layout:
- complete tensor payload 3,583,928,320 B
- embedding 272,269,312 B
- transformer body 3,039,381,504 B
- each transformer layer 84,427,264 B / 25 tensors
- final RMSNorm 8,192 B
- LM head 272,269,312 B.

## Stretch 001 — COMPLETE PASS

Run `20260819-154335` — `LAYER_ADDRESSABLE_IO_PASS`.
- 36/36 layers exactly addressable in safetensors.
- one-layer selective read exact.

## Stretch 002 — COMPLETE PASS

Run `20260819-155641` — `SINGLE_LAYER_MLX_EVICTION_PASS`.
- one layer: 0 -> 84,427,264 -> 0 B active.
- cache returns to 0 B.

## Stretch 003 — COMPLETE PASS

Run `20260819-161134` — `TWO_LAYER_BOUNDED_RESIDENCY_PASS`.
- two sequential layer materialize/evict cycles in one MLX process.
- no cumulative active/cache growth.

## Stretch 004 — COMPLETE PASS

Run `20260819-162454` — `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.
- first real Qwen3 TransformerBlock compute.
- two resident layers vs one streamed layer at a time.
- final activation max/mean diff 0.0 / 0.0.

## Stretch 005 — COMPLETE PASS

Run `20260819-163413` — `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`.
- resident delta 675,352,572 B.
- max streamed layer 84,427,264 B.
- ratio 7.999223710482908x.
- exact final parity.

## Stretch 006 — COMPLETE PASS

Valid run `20260819-164605` — `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`.

Earlier transform-wrapper attempt is harness-only/no scientific result.

Valid run:
- resident transformer body 3,039,315,964 B
- max streamed layer 84,427,264 B
- ratio 35.99922371048291x
- all 36 streamed cycles return layer-weight active/cache to baseline
- activation parity max/mean 0.0 / 0.0.

Result:
`research/stretch/full-36-layer-streamed-body-parity-006-result.md`.

## Stretch 007A — COMPLETE PASS

Run `20260819-165247` — `SHARED_COMPONENT_ANATOMY_PASS`.

Physical non-layer layout:
- embedding 272,269,312 B
- final norm 8,192 B
- LM head 272,269,312 B
- other 0
- `tie_word_embeddings=false`.

Result:
`research/stretch/shared-component-anatomy-007a-result.md`.

## Stretch 007B — COMPLETE PASS

Run `20260819-170334` — `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`.

Official resident control:
- full-model materialized delta exactly 3,583,928,320 B.

LOOM phase-streamed path:
- embedding -> evict
- all 36 transformer layers one at a time
- final norm
- LM head -> evict.

Max raw-weight stage:
- 272,269,312 B
- resident/max-streamed ratio 13.16317396798652x.

Full logits `[1,4,151936]`:
- max/mean diff 0.0 / 0.0
- top-1 equality true.

Result:
`research/stretch/phase-streamed-full-logit-parity-007b-result.md`.

## Stretch 008 — COMPLETE PASS

Plan:
`research/stretch/one-token-kv-autoregressive-parity-008-plan.md`

Scientific runner:
`scripts/stretch_one_token_kv_autoregressive_parity_008.py`

Scientific runner blob:
`03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`

Harness pipefix:
`scripts/stretch_one_token_kv_autoregressive_parity_008_pipefix.py`

Pipefix blob:
`8b2ce5902d3ed45c9120273fab415fe67a026d4a`

Result:
`research/stretch/one-token-kv-autoregressive-parity-008-result.md`

### First launch — HARNESS I/O STALL / NO SCIENTIFIC RESULT

The first launch reached `stream_token_layer_17_complete` with correct intermediate cache/weight measurements, then stalled. Demonstrated harness defect: verbose `LOOM_CHILD_STATE` JSON was written to captured stdout while the parent did not drain the pipe during execution. This is recorded separately in `research/stretch/one-token-kv-autoregressive-parity-008-harness-note.md`.

The pipefix suppressed only intermediate stdout state emission; `child-state.json`, final completion payload, scientific design, weights, KV policy, prompt, parity gates and guardrails remained unchanged.

### Valid run `20260819-173553`

Classification: **ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS**.

Frozen prompt:
`[[1,42,2048,151935]]`.

Prompt-with-KV parity:
- max/mean diff **0.0 / 0.0**
- token equality true
- generated token **`[[1]]`**.

Persistent ordinary BF16 KV cache after prompt:
- resident total **37,748,736 B**, all 36 offsets **4**
- streamed total **37,748,736 B**, all 36 offsets **4**.

The generated token was fed back through the same caches.

Post-token parity:
- max/mean diff **0.0 / 0.0**
- top-1 equality true.

Persistent KV after feedback:
- resident total **37,748,736 B**, all offsets **5**
- streamed total **37,748,736 B**, all offsets **5**.

Weight residency:
- resident full model **3,583,928,320 B**
- max streamed raw-weight stage **272,269,312 B**
- ratio **13.16317396798652x**.

Valid whole-run telemetry:
- launch gate 72/72/74% free, swap 1223.88 MB
- min free **26%**
- peak swap **1583.75 MB**
- peak child RSS **878.5 MB**
- disk **36.294 -> 36.290 GiB**.

Diagnostic phase polling:
- stream prompt: min free 64%, peak swap 1479.75 MB, peak child RSS 347.578 MB
- stream token: min free 69%, peak swap 1471.75 MB, peak child RSS 166.531 MB.

Canonical interpretation:
> LOOM has now demonstrated actual one-token autoregressive cache reuse with persistent per-layer KV state while raw Qwen3-8B weights remain phase-streamed. Resident and streamed prompt logits, generated token, cache offsets/bytes, and post-token logits all match exactly.

Boundary: this is one deterministic generated token, not yet long-run generation, tokenizer/text integration or a throughput claim.

# Exact next step

Preregister and implement **Stretch 009 — Short Deterministic Multi-Token Loop**.

Single scientific change from valid Stretch 008:
- autoregressive continuation depth: 1 generated token -> short fixed multi-token sequence.

Preserve:
- same local Qwen3-8B 3-bit artifact
- same frozen prompt
- ordinary BF16 `KVCache`
- argmax only
- resident official control
- phase-streamed embedding/layers/norm/head
- parity at every step
- same safety guardrails
- no tokenizer, sampling, cache quantization, prefetch or other optimization.

Use file-backed child state/final-result transfer rather than undrained captured verbose stdout.

After every meaningful result/decision, update `HANDOFF.md` and `ROADMAP.md` before advancing.