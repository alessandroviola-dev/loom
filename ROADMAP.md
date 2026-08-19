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
- [ ] Run Amplifier 004 after current Stretch architectural sequence

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
- [x] resident body delta 3,039,315,964 B
- [x] max streamed layer 84,427,264 B
- [x] ratio 35.99922371048291x
- [x] exact full-body activation parity

### Stretch 007A — COMPLETE PASS
- [x] `SHARED_COMPONENT_ANATOMY_PASS`
- [x] embedding 272,269,312 B
- [x] final norm 8,192 B
- [x] LM head 272,269,312 B
- [x] `tie_word_embeddings=false`

### Stretch 007B — COMPLETE PASS
- [x] `PHASE_STREAMED_FULL_LOGIT_PARITY_PASS`
- [x] official resident model 3,583,928,320 B
- [x] max streamed raw-weight stage 272,269,312 B
- [x] ratio 13.16317396798652x
- [x] exact full logits

### Stretch 008 — COMPLETE PASS
- [x] `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] persistent KV reuse offsets 4 -> 5
- [x] exact resident/streamed prompt and post-token logits
- [x] first launch stdout-pipe stall recorded as harness-only

### Stretch 009 — COMPLETE PASS
- [x] `FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] generated sequence `[1,374,264,4647]` identical
- [x] KV offsets 4 -> 8, allocation stable 37,748,736 B
- [x] exact logits at all four steps
- [x] mean 36-layer materialization 0.188658 s/token
- [x] mean 36-layer forward 0.192317 s/token
- [x] freeze result

### Stretch 010 — COMPLETE PASS
- [x] Valid run `20260819-183844`
- [x] `SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`
- [x] exact prompt + 16 feedback logits and identical sequence
- [x] final KV offset 20, allocation 37,748,736 B
- [x] resident model 3,583,928,320 B
- [x] max streamed stage 272,269,312 B
- [x] mean transformer forward 0.192486 s/token
- [x] mean full pass 2.888971 s/token
- [x] median full pass 3.350773 s/token
- [x] logical throughput 0.346144 token/s
- [x] identify materialization transition ~0.19 s early -> ~1.4 s late while forward stays stable
- [x] freeze result

### Stretch 011 — Materialization I/O attribution — COMPLETE PASS
- [x] Valid run `20260819-185036`
- [x] `MATERIALIZATION_IO_ATTRIBUTION_PASS`
- [x] Preserve exact 16-token Stretch 010 workload
- [x] All correctness/KV/weight gates remain PASS
- [x] Reproduce slow materialization regime
- [x] Late materialization process disk-read accounting ~3,039,395,840 B/token
- [x] Frozen transformer payload 3,039,381,504 B
- [x] Late full-pass process reads ~3.584 GB/token
- [x] Build/select reads negligible relative to materialization
- [x] Materialization page-ins remain zero
- [x] Materialization-time vs disk-read Pearson 0.9995866107996246
- [x] Mean transformer forward remains ~0.191414 s/token
- [x] Stream-token bucket min free 65%
- [x] Freeze `research/stretch/materialization-io-attribution-011-result.md`
- [x] Establish repeated weight traversal/I/O as dominant late materialization cost under current runtime/accounting
- [x] Preserve interpretation boundary: process disk-I/O accounting is not forensic per-file SSD tracing

### Stretch 012 — Eight-layer persistent hotset — CURRENT / READY
- [x] Single scientific change: retain transformer layers 0..7 across prompt + 16 autoregressive tokens
- [x] Layers 8..35 remain streamed/evicted
- [x] Embedding/norm/LM head remain streamed
- [x] Preserve exact 16-token prompt/argmax/KV/resident parity workload
- [x] Preserve Darwin I/O attribution
- [x] Preserve host/runtime guardrails
- [x] Expected hotset payload 675,418,112 B
- [x] Expected max simultaneous raw-weight budget ~947,687,424 B
- [x] Require hotset per-token materialized delta near zero
- [x] Require normal 84,427,264 B materialization for layers 8..35
- [x] Expected late transformer process reads may fall toward ~2,363,977,728 B/token
- [x] Expected late full-pass process reads may fall toward ~2.909 GB/token
- [x] No minimum speedup gate; latency/I/O reduction is an outcome
- [x] Preregister `research/stretch/eight-layer-persistent-hotset-012-plan.md`
- [x] Add runner `scripts/stretch_eight_layer_persistent_hotset_012.py`
- [x] Freeze runner blob `8e10660af778655a279f30e7d59785163bc204e3`
- [ ] Run Stretch 012
- [ ] Freeze result

### Stretch 013+ — conditional residency frontier / usability
- [ ] If 012 validates RAM-for-I/O tradeoff, preregister another retained-layer point separately (e.g. 16 layers) to build a small frontier
- [ ] If 012 loses more from memory pressure than it gains from fewer reads, preregister a smaller hotset separately
- [ ] Select practical RAM/I/O point before tokenizer integration
- [ ] Add tokenizer/text integration as isolated factor
- [ ] Test 256-position KV capacity boundary separately
- [ ] Test prefetch/double buffering separately
- [ ] Test KV quantization separately
- [ ] Only later study speculative decoding/layer skipping/early exit/MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
