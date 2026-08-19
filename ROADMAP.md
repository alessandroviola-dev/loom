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
- [x] Prompt logits max/mean diff 0.0 / 0.0
- [x] Generated token equality true; token `[[1]]`
- [x] Resident/streamed KV after prompt 37,748,736 B; offsets all 4
- [x] Feed generated token through same cache
- [x] Resident/streamed KV after feedback 37,748,736 B; offsets all 5
- [x] Post-token logits max/mean diff 0.0 / 0.0
- [x] Post-token top-1 equality true
- [x] Resident model delta 3,583,928,320 B
- [x] Max streamed raw-weight stage 272,269,312 B
- [x] Ratio 13.16317396798652x
- [x] Whole-run min free 26%; peak swap 1583.75 MB
- [x] Freeze `research/stretch/one-token-kv-autoregressive-parity-008-result.md`
- [x] Establish real persistent-KV autoregressive reuse in streamed path

### Stretch 009 — Four-token KV autoregressive parity — CURRENT / READY
- [x] Freeze single scientific change: continuation depth 1 -> 4 tokens
- [x] Keep prompt `[[1,42,2048,151935]]`
- [x] Keep ordinary BF16 `KVCache`
- [x] Keep official resident control and phase-streamed raw-weight path
- [x] Keep argmax only; no tokenizer/sampling/cache quantization/prefetch
- [x] Expected offsets 4 -> 5 -> 6 -> 7 -> 8
- [x] Expected KV allocation remains ~37,748,736 B below 256-position boundary
- [x] Require numerical parity and top-1 equality at every step
- [x] Require identical four-token generated sequence
- [x] Record per-token layer materialization/forward wall
- [x] Use `child-state.json` + `child-final.json`; stdout/stderr file-backed
- [x] Preregister `research/stretch/four-token-kv-autoregressive-parity-009-plan.md`
- [x] Add `scripts/stretch_four_token_kv_autoregressive_parity_009.py`
- [x] Freeze runner blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`
- [ ] Run Stretch 009
- [ ] Freeze result

### Stretch 010+ — usable streamed generation / optimization
- [ ] Decide next single factor after Stretch 009 result
- [ ] Candidate: tokenizer/text integration OR longer deterministic loop
- [ ] Measure bytes/token, RAM, swap, wall time and tok/s
- [ ] Test prefetch/double buffering separately
- [ ] Test KV quantization separately
- [ ] Test 256-position cache-capacity boundary separately
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
