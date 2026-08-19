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

Frozen subject: Qwen3-8B 3-bit, 36 transformer layers, each 84,427,264 B / 25 tensors.
Known non-layer payload: 544,546,816 B, exact composition pending Stretch 007A.

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
- [x] layers 18 and 19 each independently 0 -> 84,427,264 -> 0 B
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
- [x] Freeze result record

### Stretch 006 — Full 36-layer transformer-body parity — COMPLETE PASS
- [x] Preregister full layers `0..35`
- [x] First launch classified harness-only/no scientific result
- [x] Fix only transform-label invariant defect; scientific design unchanged
- [x] Corrected runner blob `ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`
- [x] Valid run `20260819-164605`
- [x] `FULL_36_LAYER_STREAMED_BODY_PARITY_PASS`
- [x] All 36 layer provenance checks PASS
- [x] Resident expected body payload 3,039,381,504 B
- [x] Resident observed materialized delta 3,039,315,964 B
- [x] Max streamed one-layer materialized delta 84,427,264 B
- [x] Resident/streamed ratio 35.99922371048291x
- [x] Every streamed layer: pre 0 / materialized 84,427,264 / post-clear 0 / cache 0
- [x] Numerical parity max/mean diff 0.0 / 0.0
- [x] Stream parameter materialization wall 1.207812 s
- [x] Stream transformer forward wall 0.440137 s
- [x] Whole-run min free 22%; peak swap 1325.69 MB; do not attribute these specifically to streamed phase
- [x] Freeze `research/stretch/full-36-layer-streamed-body-parity-006-result.md`
- [x] Establish full transformer-body dense layer streaming with exact resident parity

### Stretch 007A — Shared component anatomy — CURRENT / READY
- [x] Preregister `research/stretch/shared-component-anatomy-007a-plan.md`
- [x] Add read-only `scripts/stretch_shared_component_anatomy_007a.py`
- [x] Freeze runner blob `7e147476119766a5cf29b697120291b1b96b9bb9`
- [x] Require exact Stretch 001 helper blob `890444928abd6cc24e7194317c92b36b50fd994b`
- [x] No MLX import/model launch/tensor materialization/network
- [x] Capture config: vocab size, tie semantics, RMSNorm epsilon, quantization
- [x] Catalog all non-layer tensors with name/dtype/shape/bytes
- [x] Group embedding / final_norm / lm_head / other
- [x] Require exact non-layer total 544,546,816 B
- [ ] Run Stretch 007A
- [ ] Freeze shared-component physical layout

### Stretch 007B — Shared components + full-logit parity — CONDITIONAL
- [ ] Only after 007A PASS
- [ ] Use real token embedding according to observed local layout
- [ ] Execute all 36 transformer blocks streamed
- [ ] Add final RMSNorm
- [ ] Add output projection/LM head according to observed tie/head semantics
- [ ] Compare final logits against resident control
- [ ] Keep KV cache and autoregressive generation excluded
- [ ] Add phase-scoped resource telemetry where practical

### Stretch 008+ — end-to-end inference
- [ ] Add KV-cache handling
- [ ] Add autoregressive token-generation parity
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
