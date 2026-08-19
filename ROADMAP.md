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
- [x] Pi 0.84.2 validated non-destructively
- [x] Pi Agentic Coding Benchmark 001: delivery-adjusted 77.15, delivery 6/6

## Phase 4 — llama.cpp frontier — CHARACTERIZED
- [x] 4B Q4 control PASS: pp512 230.85 t/s, tg128 22.33 t/s, min free 22%
- [x] 8B Q4/Q3/Q2 boundaries characterized
- [x] Preserve llama.cpp 4B as alternate Amplify capability/efficiency profile

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED
- [x] 8B 3-bit full session stable; quality not promoted
- [x] 8B 4-bit memory boundary characterized
- [x] Preserve verified 3-bit/4-bit artifacts

## Phase 6 — Amplify — ACTIVE / QUEUED BEHIND STRETCH

### Amplifier 001–003
- [x] Warm-resident validator + one repair: resource fail
- [x] Call isolation works but repair still resource-fails
- [x] Repair context 3072 still resource-fails from recovered 70% free
- [x] Do not descend automatically to 2048

### Repair prompt anatomy
- [x] Initial 1638 B
- [x] Repair 4573 B (2.792x)
- [x] Validation feedback 2762 B (~60.4%)

### Amplifier 004 — Compact Feedback — READY / QUEUED
- [x] Preregister bounded 768-byte failure-detail serialization
- [x] Runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- [ ] Run after current Stretch scaling sequence
- [ ] If resource fail, stop prompt/context rescue ladder on Ollama/MLX 4B
- [ ] If COMPLETE, freeze quality/resource/efficiency

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Research question:
**Can LOOM use SSD + RAM as an explicit model-memory hierarchy rather than requiring full weight residency?**

### Stretch 001 — Layer addressability — COMPLETE PASS
- [x] `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers exact
- [x] 907 tensors; total payload 3,583,928,320 B
- [x] Shared/non-layer 544,546,816 B (~519.32 MiB)
- [x] Every layer 84,427,264 B (~80.52 MiB), 25 tensors
- [x] Layer 18 exact selective read in 0.069784 s at 1153.794 MiB/s
- [x] Freeze result record

### Stretch 002 — Single-layer MLX materialization/eviction — COMPLETE PASS
- [x] `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] Pre-eval active delta 0 B
- [x] Post-eval active delta exactly 84,427,264 B
- [x] Post-clear active/cache 0/0 B
- [x] `mx.eval` 0.039611 s
- [x] Min free 67%; peak swap 850.5 MB
- [x] Freeze result record

### Stretch 003 — Repeated bounded residency — COMPLETE PASS
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] Same MLX process, layers 18 then 19
- [x] Layer 18: 0 -> 84,427,264 -> 0 B; cache 0 B
- [x] Layer 19: 0 -> 84,427,264 -> 0 B; cache 0 B
- [x] Min free 67%; peak swap 826.5 MB
- [x] Freeze result record
- [x] Close raw-weight prerequisite stage

### Stretch 004 — Two-layer streamed micro-forward parity — COMPLETE PASS
- [x] Use official mlx-lm 0.31.3 Qwen3 `TransformerBlock`
- [x] Use frozen 3-bit/group64 quantization path
- [x] Deterministic batch1/seq4/hidden4096 activation
- [x] Resident control layers 18+19
- [x] Streamed path 18 -> evict -> 19 -> evict
- [x] Run `20260819-162454`
- [x] Classification `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`
- [x] Resident materialized delta exactly 168,854,528 B
- [x] Stream layer 18 materialized 84,361,724 B; post-clear within tolerance; cache 0 B
- [x] Stream layer 19 materialized 84,427,264 B; post-clear 0 B; cache 0 B
- [x] Numerical parity max abs diff 0.0; mean abs diff 0.0
- [x] Min free 63%; peak swap 826.5 MB; peak child RSS 178.281 MB
- [x] Freeze `research/stretch/two-layer-streamed-micro-forward-parity-004-result.md`
- [x] Establish first real transformer-compute evidence for one-layer-at-a-time streamed weights

### Stretch 005 — Eight-layer streamed forward scaling — CURRENT / READY
- [x] Single changed factor vs 004: chain depth 2 -> 8
- [x] Freeze layers `[14,15,16,17,18,19,20,21]`
- [x] Preserve exact input, Qwen3 block implementation, quantization, parity and safety gates
- [x] Resident expected raw-weight delta 675,418,112 B +/-8 MiB
- [x] Streamed per-layer materialized delta 84,427,264 B +/-1 MiB
- [x] Streamed post-clear active within +/-4 MiB and cache <=4 MiB
- [x] Record resident/max-stream residency ratio and wall-time scaling
- [x] Preregister `research/stretch/eight-layer-streamed-forward-scaling-005-plan.md`
- [x] Add `scripts/stretch_eight_layer_streamed_forward_scaling_005.py`
- [x] Fix generalized-loop lingering-reference harness issue before execution
- [x] Freeze final runner blob `8bbfff727a0131c48d4ba71edc8de485182b7fbe`
- [ ] Run Stretch 005
- [ ] Freeze eight-layer parity/residency/efficiency result

### Stretch 006 — Full 36-block body parity — CONDITIONAL
- [ ] Only preregister if Stretch 005 passes
- [ ] Extend same tiny-activation resident-vs-streamed design to all 36 transformer blocks
- [ ] Keep embeddings/final norm/LM head/KV/token generation excluded
- [ ] Verify resident raw-weight growth vs one-layer-at-a-time streamed residency
- [ ] Preserve exact numerical parity and safety gates

### Stretch 007+ — end-to-end components if prerequisites continue passing
- [ ] Add shared embedding/final-norm residency policy
- [ ] Add LM head/logit parity
- [ ] Add KV-cache handling
- [ ] Add autoregressive token generation parity
- [ ] Add prefetch/double buffering
- [ ] Measure SSD bytes/token, RAM, swap, wall time and tok/s
- [ ] Explore cache/residency policies
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish research findings when ready
