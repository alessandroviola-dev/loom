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
- [x] 4B Q4 control PASS: pp512 230.85 t/s, tg128 22.33 t/s
- [x] 8B Q4/Q3/Q2 boundaries characterized

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED
- [x] 8B 3-bit full session stable; quality not promoted
- [x] 8B 4-bit memory boundary characterized
- [x] Preserve verified artifacts

## Phase 6 — Amplify — ACTIVE / QUEUED BEHIND STRETCH

### Amplifier 001–003
- [x] Canonical 4B repair path resource boundary characterized
- [x] Call isolation and repair-context 3072 individually insufficient
- [x] Do not claim leak/KV/allocator root cause

### Amplifier 004 — Compact Feedback — READY / QUEUED
- [x] Preregister 768-byte variable repair-feedback cap
- [x] Runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- [ ] Run after current Stretch sequence

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Frozen subject: Qwen3-8B 3-bit, 36 layers, vocab 151936, untied embedding/head, 3-bit/group64.

### Stretch 001 — Layer addressability — COMPLETE PASS
- [x] `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers exact
- [x] One-layer selective read exact

### Stretch 002 — Single-layer MLX materialization/eviction — COMPLETE PASS
- [x] `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] 0 -> 84,427,264 -> 0 B active

### Stretch 003 — Repeated bounded residency — COMPLETE PASS
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] two sequential one-layer cycles without accumulation

### Stretch 004 — Two-layer streamed forward — COMPLETE PASS
- [x] `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`
- [x] official Qwen3 block computation
- [x] exact numerical parity

### Stretch 005 — Eight-layer scaling — COMPLETE PASS
- [x] `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`
- [x] resident/streamed ratio ~8x
- [x] exact numerical parity

### Stretch 006 — Full 36-layer body — COMPLETE PASS
- [x] `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`
- [x] valid run `20260819-164605`
- [x] resident body delta 3,039,315,964 B
- [x] max streamed layer 84,427,264 B
- [x] ratio 35.99922371048291x
- [x] exact activation parity
- [x] earlier transform failure classified harness-only

### Stretch 007A — Shared component anatomy — COMPLETE PASS
- [x] `SHARED_COMPONENT_ANATOMY_PASS`
- [x] embedding 272,269,312 B
- [x] final norm 8,192 B
- [x] LM head 272,269,312 B
- [x] `tie_word_embeddings=false`

### Stretch 007B — Full token-ID-to-logit phase streaming — COMPLETE PASS
- [x] `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`
- [x] valid run `20260819-170334`
- [x] official resident model 3,583,928,320 B
- [x] max streamed raw-weight stage 272,269,312 B
- [x] ratio 13.16317396798652x
- [x] full logits max/mean diff 0.0 / 0.0
- [x] top-1 equality true

### Stretch 008 — One-token KV autoregressive parity — COMPLETE PASS
- [x] Preregister ordinary BF16 `KVCache`, frozen prompt and argmax one-token policy
- [x] Scientific runner blob `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`
- [x] First launch stalled on undrained captured stdout; classify harness I/O stall / no scientific result
- [x] Freeze harness note `research/stretch/one-token-kv-autoregressive-parity-008-harness-note.md`
- [x] Apply harness-only pipefix blob `8b2ce5902d3ed45c9120273fab415fe67a026d4a`
- [x] Valid run `20260819-173553`
- [x] `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] Prompt logits parity max/mean 0.0 / 0.0
- [x] Generated token equality true; token `[[1]]`
- [x] Resident/streamed KV bytes after prompt 37,748,736 / 37,748,736 B
- [x] Resident/streamed cache offsets after prompt all 4
- [x] Feed generated token through same cache state
- [x] Resident/streamed cache offsets after token all 5
- [x] KV bytes remain 37,748,736 B below 256-position capacity boundary
- [x] Post-token logits parity max/mean 0.0 / 0.0
- [x] Post-token top-1 equality true
- [x] Resident full-model delta 3,583,928,320 B
- [x] Max streamed raw-weight stage 272,269,312 B
- [x] Resident/max-streamed-stage ratio 13.16317396798652x
- [x] Valid whole-run min free 26%; peak swap 1583.75 MB
- [x] Freeze `research/stretch/one-token-kv-autoregressive-parity-008-result.md`
- [x] Establish actual persistent-KV autoregressive reuse in streamed path

### Stretch 009 — Short deterministic multi-token loop — CURRENT / PREREGISTRATION
- [ ] Single scientific change: continuation depth 1 -> short fixed multi-token sequence
- [ ] Freeze exact generated-token count before implementation
- [ ] Same prompt `[[1,42,2048,151935]]`
- [ ] Same ordinary BF16 `KVCache`
- [ ] Same resident official control and phase-streamed raw-weight path
- [ ] Argmax only; no tokenizer/sampling
- [ ] Numerical parity and generated-token equality at every step
- [ ] Cache offset/byte gates after every step
- [ ] Per-token parameter materialization and transformer-forward wall
- [ ] Phase/system memory and swap diagnostics
- [ ] Use file-backed child state/final result to avoid stdout pipe stalls
- [ ] Preregister plan
- [ ] Implement/freeze runner
- [ ] Run and freeze result

### Stretch 010+ — usable streamed generation / optimization
- [ ] Add tokenizer/text prompt parity
- [ ] Extend generation length after short-loop stability
- [ ] Measure bytes/token, RAM, swap, wall time and tok/s
- [ ] Add prefetch/double buffering as separate experiments
- [ ] Explore cache quantization/residency policies separately
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
