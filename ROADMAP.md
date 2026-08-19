# LOOM Roadmap

## Phase 0 — Foundation
- [x] Project name / mission / handoff discipline
- [x] Private repository `Ilcoach/loom`

## Phase 1 — Baseline
- [x] Canonical Ollama/MLX 4B baseline
- [x] Coding Baseline 001: artifact 40.71, delivery-adjusted 30.00, delivery 3/6

## Phase 2 — Benchmark framework
- [x] Coding Benchmark 01 v1.0.1
- [ ] Reasoning benchmark later

## Phase 3 — Local agent investigation
- [x] Pi Agentic Coding Benchmark 001: delivery-adjusted 77.15, delivery 6/6

## Phase 4 — llama.cpp frontier — CHARACTERIZED
- [x] 4B Q4 efficiency control
- [x] 8B Q4/Q3/Q2 memory/quality boundaries characterized

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED
- [x] 8B 3-bit full session stable; quality not promoted
- [x] 8B 4-bit memory boundary characterized
- [x] Preserve verified artifacts

## Phase 6 — Amplify — ACTIVE / QUEUED BEHIND STRETCH
- [x] Amplifier 001–003 resource boundary characterized
- [x] Do not claim leak/KV/allocator root cause
- [x] Amplifier 004 compact-feedback plan/runner frozen
- [ ] Run Amplifier 004 after current Stretch sequence

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Frozen subject: Qwen3-8B 3-bit, 36 layers, vocab 151936, untied embedding/head, 3-bit/group64.

### Stretch 001 — COMPLETE PASS
- [x] `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers exact and selectively readable

### Stretch 002 — COMPLETE PASS
- [x] `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] one layer 0 -> 84,427,264 -> 0 B active

### Stretch 003 — COMPLETE PASS
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] repeated one-layer cycles remain bounded

### Stretch 004 — COMPLETE PASS
- [x] `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`
- [x] real Qwen3 block compute
- [x] exact numerical parity

### Stretch 005 — COMPLETE PASS
- [x] `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`
- [x] resident/streamed ratio ~8x
- [x] exact numerical parity

### Stretch 006 — COMPLETE PASS
- [x] `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`
- [x] valid run `20260819-164605`
- [x] resident body delta 3,039,315,964 B
- [x] max streamed layer 84,427,264 B
- [x] ratio 35.99922371048291x
- [x] exact full-body activation parity
- [x] earlier transform failure classified harness-only

### Stretch 007A — COMPLETE PASS
- [x] `SHARED_COMPONENT_ANATOMY_PASS`
- [x] embedding 272,269,312 B
- [x] final norm 8,192 B
- [x] LM head 272,269,312 B
- [x] `tie_word_embeddings=false`

### Stretch 007B — COMPLETE PASS
- [x] `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`
- [x] valid run `20260819-170334`
- [x] official resident model 3,583,928,320 B
- [x] max streamed raw-weight stage 272,269,312 B
- [x] ratio 13.16317396798652x
- [x] full logits max/mean diff 0.0 / 0.0
- [x] top-1 equality true

### Stretch 008 — COMPLETE PASS
- [x] Scientific runner blob `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`
- [x] First launch stalled on undrained verbose stdout pipe; harness-only/no scientific result
- [x] Freeze harness note
- [x] Harness-only pipefix blob `8b2ce5902d3ed45c9120273fab415fe67a026d4a`
- [x] Valid run `20260819-173553`
- [x] `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] Prompt and post-token logits exact parity
- [x] Cache offsets 4 -> 5 and total KV 37,748,736 B
- [x] Resident model 3,583,928,320 B vs max streamed stage 272,269,312 B
- [x] Establish persistent-KV one-token autoregressive reuse

### Stretch 009 — Four-token KV autoregressive parity — COMPLETE PASS
- [x] Valid run `20260819-183143`
- [x] `FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] Prompt full-logit parity max/mean 0.0 / 0.0
- [x] Four feedback steps each max/mean 0.0 / 0.0
- [x] Top-1 equality at every step
- [x] Resident/streamed generated sequence equal: `[1,374,264,4647]`
- [x] Cache offsets advance 4 -> 5 -> 6 -> 7 -> 8
- [x] Final resident/streamed KV 37,748,736 / 37,748,736 B
- [x] Resident full model 3,583,928,320 B
- [x] Max streamed raw-weight stage 272,269,312 B
- [x] Ratio 13.16317396798652x
- [x] Mean 36-layer materialization 0.188658 s/token
- [x] Mean 36-layer forward 0.192317 s/token
- [x] Whole-run min free 21%; streamed-token bucket min free 64%
- [x] Freeze `research/stretch/four-token-kv-autoregressive-parity-009-result.md`

### Stretch 010 — Sixteen-token autoregressive stability — CURRENT / READY
- [x] Single scientific change: continuation depth 4 -> 16 tokens
- [x] Preserve exact Stretch 009 source blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- [x] Preserve prompt, deterministic argmax, ordinary BF16 KVCache, resident control, streamed weight policy and guardrails
- [x] Expected final cache offset 20
- [x] Expected KV allocation remains 37,748,736 B below 256-position boundary
- [x] Require prompt + 16 feedback full-logit parity and top-1 equality
- [x] Require identical 16-token sequence
- [x] Preserve weight-stage gates on all passes
- [x] Expose existing full streamed pass wall per token
- [x] Summarize mean/median full-pass latency and logical streamed tok/s
- [x] Explicitly distinguish logical tok/s from physical SSD throughput
- [x] Preregister `research/stretch/sixteen-token-autoregressive-stability-010-plan.md`
- [x] Add frozen-transform runner `scripts/stretch_sixteen_token_autoregressive_stability_010.py`
- [x] Runner blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`
- [ ] Run Stretch 010
- [ ] Freeze result

### Stretch 011+ — usable streamed generation / optimization
- [ ] After Stretch 010, likely add tokenizer/text integration as one isolated factor
- [ ] Test 256-position cache-capacity boundary separately
- [ ] Measure/characterize physical storage I/O separately from page-cache-assisted logical reads
- [ ] Freeze unoptimized end-to-end logical tok/s baseline before optimization
- [ ] Test prefetch/double buffering separately
- [ ] Test KV quantization separately
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
