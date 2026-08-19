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

Frozen subject: Qwen3-8B 3-bit, 36 transformer layers, 151936 vocab, `tie_word_embeddings=false`, 3-bit/group64.

### Stretch 001 — Layer addressability — COMPLETE PASS
- [x] `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers exact
- [x] Shared/non-layer payload 544,546,816 B
- [x] One layer exact selective read

### Stretch 002 — Single-layer MLX materialization/eviction — COMPLETE PASS
- [x] `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] 0 -> 84,427,264 -> 0 B active
- [x] cache returns 0 B

### Stretch 003 — Repeated bounded residency — COMPLETE PASS
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] layers 18 and 19 independently 0 -> 84,427,264 -> 0 B
- [x] no cumulative cache/active growth

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
- [x] Numerical parity max/mean diff 0.0 / 0.0
- [x] No cumulative active/cache growth

### Stretch 006 — Full 36-layer transformer-body parity — COMPLETE PASS
- [x] Valid run `20260819-164605`
- [x] `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`
- [x] Resident materialized delta 3,039,315,964 B
- [x] Max streamed one-layer delta 84,427,264 B
- [x] Resident/streamed ratio 35.99922371048291x
- [x] Every streamed layer: pre 0 / materialized 84,427,264 / post-clear 0 / cache 0
- [x] Numerical parity max/mean diff 0.0 / 0.0
- [x] Stream parameter materialization wall 1.207812 s
- [x] Stream transformer forward wall 0.440137 s
- [x] Whole-run min free 22%; peak swap 1325.69 MB; do not attribute specifically to streamed phase
- [x] Freeze result record

### Stretch 007A — Shared component anatomy — COMPLETE PASS
- [x] Run `20260819-165247`
- [x] `SHARED_COMPONENT_ANATOMY_PASS`
- [x] Read-only; no MLX/model launch/tensor materialization/network
- [x] Config: vocab 151936, `tie_word_embeddings=false`, RMSNorm eps 1e-6, 3-bit/group64
- [x] Total tensor bytes 3,583,928,320 B
- [x] Transformer-layer bytes 3,039,381,504 B
- [x] Non-layer bytes 544,546,816 B exact
- [x] Embedding: 3 tensors / 272,269,312 B
- [x] Final RMSNorm: 1 tensor / 8,192 B
- [x] LM head: 3 tensors / 272,269,312 B
- [x] Other: 0
- [x] Freeze `research/stretch/shared-component-anatomy-007a-result.md`
- [x] Establish phase-streamable shared layout: embedding and LM head are separate and used at opposite ends

### Stretch 007B — Phase-streamed full-logit parity — CURRENT / READY
- [x] Verify official mlx-lm v0.31.3 Qwen3 flow: embedding -> 36 blocks -> final RMSNorm -> lm_head when untied
- [x] Verify official loader quantization predicate based on matching `.scales` tensors
- [x] Preregister `research/stretch/phase-streamed-full-logit-parity-007b-plan.md`
- [x] Add `scripts/stretch_phase_streamed_full_logit_parity_007b.py`
- [x] Freeze runner blob `b08c9b44ae062ee259ab6641575e44c4d7d753e6`
- [x] Resident control uses official `mlx_lm.utils.load_model(..., lazy=False, strict=True)`
- [x] Frozen token IDs `[[1,42,2048,151935]]`
- [x] Stream embedding 272,269,312 B -> evict
- [x] Stream all 36 transformer layers with existing per-layer gates
- [x] Load final RMSNorm 8,192 B
- [x] Stream separate LM head 272,269,312 B -> logits -> evict
- [x] Compare full logits `[1,4,151936]` in float32 against official resident control
- [x] Record top-1 token IDs as diagnostic
- [x] Keep tokenizer/KV/autoregressive generation excluded
- [ ] Run Stretch 007B
- [ ] Freeze full-logit parity/residency result

### Stretch 008 — First KV/autoregressive token — CONDITIONAL
- [ ] Only after 007B PASS
- [ ] Add a tiny frozen prompt with explicit KV-cache policy
- [ ] Compare resident vs streamed one-step next-token logits/token
- [ ] Generate exactly one new token first
- [ ] Preserve guardrails and explicit phase memory accounting

### Stretch 009+ — usable streamed generation
- [ ] Extend autoregressive generation loop
- [ ] Add tokenizer/text prompt parity
- [ ] Add prefetch/double buffering
- [ ] Measure SSD bytes/token, RAM, swap, wall time and tok/s
- [ ] Explore residency/cache policies
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish findings when ready
