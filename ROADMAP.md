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
- [x] 4B Q4 control PASS: pp512 230.85 t/s, tg128 22.33 t/s, min free 22%
- [x] 8B Q4/Q3/Q2 boundaries characterized

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED
- [x] 8B 3-bit full session stable; quality not promoted
- [x] 8B 4-bit memory boundary characterized
- [x] Preserve verified artifacts

## Phase 6 — Amplify — ACTIVE / QUEUED BEHIND STRETCH

### Amplifier 001–003
- [x] Warm-resident repair resource fail
- [x] Call isolation works but repair still resource-fails
- [x] Repair context 3072 still resource-fails from recovered 70% free
- [x] Do not descend automatically to 2048

### Amplifier 004 — Compact Feedback — READY / QUEUED
- [x] Preregister 768-byte variable repair-feedback cap
- [x] Runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- [ ] Run after current Stretch sequence

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Research question:
**Can LOOM use SSD + RAM as an explicit model-memory hierarchy rather than requiring full weight residency?**

Frozen subject: Qwen3-8B 3-bit, 36 transformer layers, vocab 151936, `tie_word_embeddings=false`, 3-bit/group64.

### Stretch 001 — Layer addressability — COMPLETE PASS
- [x] `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers exact
- [x] Each transformer layer 84,427,264 B
- [x] Exact selective one-layer I/O

### Stretch 002 — Single-layer MLX materialization/eviction — COMPLETE PASS
- [x] `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] 0 -> 84,427,264 -> 0 B active
- [x] cache returns 0 B

### Stretch 003 — Repeated bounded residency — COMPLETE PASS
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] layers 18 and 19 independently 0 -> 84,427,264 -> 0 B
- [x] no cumulative active/cache growth

### Stretch 004 — Two-layer streamed real forward — COMPLETE PASS
- [x] `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`
- [x] Official Qwen3 TransformerBlock computation
- [x] Resident raw weights 168,854,528 B
- [x] Streamed near one 84.4 MB layer at a time
- [x] max/mean parity difference 0.0 / 0.0

### Stretch 005 — Eight-layer streamed scaling — COMPLETE PASS
- [x] `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`
- [x] Resident materialized delta 675,352,572 B
- [x] Max streamed one-layer delta 84,427,264 B
- [x] Resident/streamed ratio 7.999223710482908x
- [x] Numerical parity 0.0 / 0.0
- [x] No cumulative active/cache growth

### Stretch 006 — Full 36-layer transformer-body parity — COMPLETE PASS
- [x] Valid run `20260819-164605`
- [x] `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`
- [x] Resident materialized delta 3,039,315,964 B
- [x] Max streamed one-layer delta 84,427,264 B
- [x] Resident/streamed ratio 35.99922371048291x
- [x] Every streamed layer materializes exactly one payload and returns layer-weight active/cache to baseline
- [x] Numerical parity 0.0 / 0.0
- [x] Freeze result record

### Stretch 007A — Shared component anatomy — COMPLETE PASS
- [x] `SHARED_COMPONENT_ANATOMY_PASS`
- [x] Embedding: 272,269,312 B
- [x] Final RMSNorm: 8,192 B
- [x] LM head: 272,269,312 B
- [x] `tie_word_embeddings=false`
- [x] Other non-layer tensors: 0
- [x] Freeze result record

### Stretch 007B — Phase-streamed full-logit parity — COMPLETE PASS
- [x] Run `20260819-170334`
- [x] `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`
- [x] Resident official full-model materialized delta 3,583,928,320 B exact
- [x] Stream embedding 272,269,312 B -> evict
- [x] Stream all 36 transformer layers; max 84,427,264 B
- [x] Final RMSNorm 8,192 B
- [x] Stream LM head 272,269,312 B -> evict
- [x] Max streamed weight-stage delta 272,269,312 B
- [x] Resident/max-streamed-stage ratio 13.16317396798652x
- [x] Full logits `[1,4,151936]` max/mean diff 0.0 / 0.0
- [x] Top-1 equality true: `[[921,78,84,1]]`
- [x] Whole-run min free 25%; peak swap 1586.0 MB; includes resident control
- [x] Freeze `research/stretch/phase-streamed-full-logit-parity-007b-result.md`
- [x] Establish complete token-ID-to-logit phase-streamed parity against official resident model

### Stretch 008 — One-token KV autoregressive parity — CURRENT / READY
- [x] Verify mlx-lm v0.31.3 default Qwen3 cache semantics
- [x] Qwen3 has no custom cache; default is 36 ordinary `KVCache()` instances
- [x] Freeze prompt `[[1,42,2048,151935]]`
- [x] Deterministic next token via argmax only
- [x] Prefill prompt with real KV cache
- [x] Require resident and streamed cache offsets 4 after prefill
- [x] Require identical generated token
- [x] Feed exactly that token back through persisted cache
- [x] Require offsets 5 after feedback
- [x] Compare full prompt logits with cache
- [x] Compare full post-token logits after actual cache reuse
- [x] Expected default BF16 KV allocation ~37,748,736 B total across 36 layers
- [x] Preserve phase-streamed raw-weight gates with cache memory accounted separately
- [x] Preregister `research/stretch/one-token-kv-autoregressive-parity-008-plan.md`
- [x] Add `scripts/stretch_one_token_kv_autoregressive_parity_008.py`
- [x] Freeze runner blob `03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf`
- [x] Add diagnostic phase-scoped host telemetry buckets
- [ ] Run Stretch 008
- [ ] Freeze one-token KV/autoregressive parity result

### Stretch 009 — Short deterministic multi-token loop — CONDITIONAL
- [ ] Only after Stretch 008 PASS
- [ ] Extend same resident-vs-streamed cache loop to a short fixed argmax sequence
- [ ] Keep tokenizer/text and sampling excluded initially
- [ ] Measure per-token materialization, forward wall, cache growth, system memory and swap

### Stretch 010+ — usable streamed generation / optimization
- [ ] Add tokenizer/text prompt parity
- [ ] Add longer generation
- [ ] Add prefetch/double buffering
- [ ] Measure SSD bytes/token, RAM, swap, wall time and tok/s
- [ ] Explore cache quantization/residency policies
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
