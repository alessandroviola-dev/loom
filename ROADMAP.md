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
- [ ] Run after current Stretch checkpoint sequence
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
- [x] Preregister layers 18 -> 19 same MLX process
- [x] Run `20260819-161134`
- [x] `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [x] Layer 18: 0 -> 84,427,264 -> 0 B; cache 0 B; eval 0.039539 s
- [x] Layer 19: 0 -> 84,427,264 -> 0 B; cache 0 B; eval 0.041369 s
- [x] Min free 67%; peak swap 826.5 MB; disk unchanged
- [x] Freeze `research/stretch/two-layer-bounded-residency-003-result.md`
- [x] Close raw-weight prerequisite stage

### Stretch 004 — Two-layer streamed micro-forward parity — CURRENT / READY
- [x] Verify official mlx-lm 0.31.3 Qwen3 `TransformerBlock` implementation
- [x] Verify official loader quantizes modules before weight loading
- [x] Freeze subject config: qwen3, hidden4096, 36 layers, 32 heads, 8 KV heads, head_dim128, 3-bit/group64
- [x] Preregister `research/stretch/two-layer-streamed-micro-forward-parity-004-plan.md`
- [x] Add `scripts/stretch_two_layer_streamed_micro_forward_parity_004.py`
- [x] Freeze runner blob `426423c9d9b7bd7bd1c6a3620197ad5212c678e6`
- [x] Resident control: materialize layers 18+19 together and run real block forward
- [x] Streamed path: materialize 18 -> forward -> evict -> materialize 19 -> forward -> evict
- [x] Deterministic input batch1/seq4/hidden4096; official attention mask
- [x] No full model, tokenizer, embedding, KV cache or generation
- [x] Resident weight delta gate ~168,854,528 B +/-2 MiB
- [x] Per streamed layer weight delta gate ~84,427,264 B +/-1 MiB
- [x] Per-cycle post-clear active/cache bounded gate
- [x] Numerical parity gate frozen
- [ ] Run Stretch 004
- [ ] Freeze resource + numerical parity result

### Stretch 005 — Longer streamed block chain — CONDITIONAL
- [ ] Only preregister if Stretch 004 reaches `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`
- [ ] Expand number of consecutive real transformer blocks while retaining resident numerical control
- [ ] Keep embeddings/KV/token generation excluded initially
- [ ] Measure peak active memory vs resident control and wall-time cost

### Stretch 006+ — end-to-end components if prerequisites continue passing
- [ ] Add shared embedding/final-norm residency policy
- [ ] Add KV-cache handling
- [ ] Compare streamed logits/tokens against resident control
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
