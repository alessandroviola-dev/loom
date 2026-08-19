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

Frozen subject: Qwen3-8B 3-bit, 36 layers, each 84,427,264 B / 25 tensors.

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
- [x] min free 63%; peak swap 826.5 MB

### Stretch 005 — Eight-layer streamed scaling — COMPLETE PASS
- [x] Change depth only: 2 -> 8 layers `[14..21]`
- [x] Run `20260819-163413`
- [x] `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`
- [x] Resident materialized delta 675,352,572 B
- [x] Max streamed one-layer delta 84,427,264 B
- [x] Resident/streamed ratio 7.999223710482908x
- [x] Layers 15–21 clear exactly to 0 active/cache; layer 14 small -65,540 B bookkeeping delta within gate
- [x] Numerical parity max/mean diff 0.0 / 0.0
- [x] Stream materialization wall 0.042391 s
- [x] Stream forward wall 0.067679 s
- [x] Min free 63%; peak swap 810.5 MB; disk unchanged
- [x] Freeze `research/stretch/eight-layer-streamed-forward-scaling-005-result.md`

### Stretch 006 — Full 36-layer transformer-body parity — CURRENT / HARNESS FIX READY
- [x] Single changed scientific factor: depth 8 -> 36 layers `0..35`
- [x] Preserve same tiny activation / official block / quantization / parity / streamed gates / safety
- [x] Keep tokenizer, embedding, final norm, LM head, KV and generation excluded
- [x] Preregister `research/stretch/full-36-layer-streamed-body-parity-006-plan.md`
- [x] Implement frozen transform runner `scripts/stretch_full_36_layer_streamed_body_parity_006.py`
- [x] Require exact Stretch 005 source blob `8bbfff727a0131c48d4ba71edc8de485182b7fbe`
- [x] Resident expected body payload 3,039,381,504 B (~2.831 GiB)
- [x] Resident tolerance +/-36 MiB, preserving +/-1 MiB-per-layer scale
- [x] Streamed per-layer gate remains 84,427,264 B +/-1 MiB
- [x] Post-clear active/cache gates unchanged
- [x] Numerical parity formula unchanged
- [x] First launch stopped before benchmark execution on transform invariant mismatch
- [x] Classify first launch as harness transform failure / no scientific result
- [x] Freeze harness note `research/stretch/full-36-layer-streamed-body-parity-006-harness-note.md`
- [x] Fix only demonstrated defect: split console and summary label transform invariants
- [x] Scientific design/gates unchanged
- [x] Freeze corrected runner blob `ab5d74b37111b7ceae6e5c00a47c10f1e1086ca6`
- [ ] Rerun Stretch 006
- [ ] Freeze full-body parity/residency result

### Stretch 007 — Shared components / logits — CONDITIONAL
- [ ] Only after Stretch 006 PASS
- [ ] Add token embedding residency policy
- [ ] Add final RMSNorm
- [ ] Add tied embedding/LM-head logit projection
- [ ] Compare final logits against resident control
- [ ] Keep KV/autoregressive generation excluded initially

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
