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
- [x] full logits max/mean diff 0.0 / 0.0

### Stretch 008 — COMPLETE PASS
- [x] `ONE_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] persistent KV reuse offsets 4 -> 5
- [x] exact resident/streamed prompt and post-token logits
- [x] first launch stdout-pipe stall recorded as harness-only

### Stretch 009 — COMPLETE PASS
- [x] `FOUR_TOKEN_KV_AUTOREGRESSIVE_PARITY_PASS`
- [x] generated sequence `[1,374,264,4647]` identical
- [x] KV offsets 4 -> 8, allocation stable at 37,748,736 B
- [x] all four feedback logits exact parity
- [x] mean 36-layer materialization 0.188658 s/token
- [x] mean 36-layer forward 0.192317 s/token
- [x] freeze `research/stretch/four-token-kv-autoregressive-parity-009-result.md`

### Stretch 010 — Sixteen-token autoregressive stability — COMPLETE PASS
- [x] Valid run `20260819-183844`
- [x] `SIXTEEN_TOKEN_AUTOREGRESSIVE_STABILITY_PASS`
- [x] Scientific change 4 -> 16 generated/feedback tokens only
- [x] Prompt and all 16 feedback logits max/mean diff 0.0 / 0.0
- [x] Top-1 equality at every step
- [x] Resident/streamed sequence identical: `[1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]`
- [x] Final KV offsets all 20
- [x] KV allocation remains 37,748,736 B
- [x] Resident full model 3,583,928,320 B
- [x] Max streamed stage 272,269,312 B
- [x] Ratio 13.16317396798652x
- [x] Mean transformer forward 0.192486 s/token remains stable
- [x] Mean full streamed pass 2.888971 s/token
- [x] Median full streamed pass 3.350773 s/token
- [x] Logical streamed throughput 0.346144 token/s
- [x] Identify materialization regime change: ~0.19 s early -> ~1.4 s late while forward stays ~0.19 s
- [x] Do not attribute timing transition to SSD/page cache/allocator without direct instrumentation
- [x] Freeze `research/stretch/sixteen-token-autoregressive-stability-010-result.md`

### Stretch 011 — Materialization I/O attribution — CURRENT / READY
- [x] Keep exact 16-token Stretch 010 scientific workload unchanged
- [x] No tokenizer/sampling/KV quantization/prefetch/cache purge
- [x] Use Darwin `proc_pid_rusage(..., RUSAGE_INFO_V2)` instrumentation
- [x] Capture per-layer build/select and materialization disk-read/page-in deltas
- [x] Capture shared-stage and full-pass resource deltas
- [x] Compare tokens 1–4 vs tokens 8–16
- [x] Report diagnostic materialization-time vs disk-read/page-in correlation
- [x] Preserve all inherited correctness/cache/weight/resource gates
- [x] Preregister `research/stretch/materialization-io-attribution-011-plan.md`
- [x] Add `scripts/stretch_materialization_io_attribution_011.py`
- [x] Freeze runner blob `16125f7eb0b2fb662591e194de0498513a563a6d`
- [ ] Run Stretch 011
- [ ] Freeze attribution result

### Stretch 012+ — conditional
- [ ] If slow regime has large process disk-read/page-in deltas: characterize storage/page-cache policy before optimization
- [ ] If slow regime has flat disk/page-in counters: profile MLX allocation/materialization lifecycle
- [ ] If slowdown does not reproduce: mark timing transition host/cache-state dependent and decide whether replication is needed
- [ ] Tokenizer/text integration after this performance boundary is characterized
- [ ] Freeze unoptimized runtime baseline before prefetch/double buffering
- [ ] Test prefetch/double buffering as a separate factor
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
