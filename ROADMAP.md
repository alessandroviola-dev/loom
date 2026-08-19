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

## Phase 6 — Amplify — ACTIVE / SECONDARY WHILE STRETCH RUNS

### Amplifier 001
- [x] Warm-resident validation + max-one-repair
- [x] `PARTIAL_RESOURCE_FAIL` during T02 repair

### Amplifier 002
- [x] Call isolation
- [x] Isolation works; T02 repair still hits 4% free

### Amplifier 003
- [x] Repair context 3072
- [x] Valid run still hits 4% free from 70%-free start
- [x] Do not descend automatically to 2048

### Repair prompt anatomy
- [x] Initial 1638 B
- [x] Repair 4573 B (2.792x)
- [x] Validation feedback 2762 B (~60.4%)

### Amplifier 004 — Compact Feedback — READY / QUEUED
- [x] Preregister bounded 768-byte failure-detail serialization
- [x] Runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- [ ] Run after current Stretch checkpoint
- [ ] If resource fail, stop prompt/context rescue ladder on Ollama/MLX 4B
- [ ] If COMPLETE, freeze quality/resource/efficiency

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Research question:
**Can LOOM use SSD + RAM as an explicit model-memory hierarchy rather than requiring full weight residency?**

### Stretch 001 — Dense Layer Streaming Feasibility — COMPLETE PASS
- [x] Preregister header-only layer map + selective I/O
- [x] Classification `LAYER_ADDRESSABLE_IO_PASS`
- [x] 36/36 layers discovered exactly; no missing/unexpected IDs
- [x] 907 tensors; total payload 3,583,928,320 B
- [x] Shared/non-layer payload 544,546,816 B (~519.32 MiB)
- [x] Every layer exactly 84,427,264 B (~80.52 MiB)
- [x] Probe layer 18: 25 tensors, exact 84,427,264 B read
- [x] Probe wall 0.069784 s; 1153.794 MiB/s
- [x] Pre/post system state 68%/850.5 MB -> 69%/850.5 MB
- [x] Freeze `research/stretch/layer-streaming-feasibility-001-result.md`
- [x] Do not interpret single selective-I/O throughput as future token throughput

### Stretch 002 — Single-Layer MLX Materialization + Eviction — COMPLETE PASS
- [x] Preregister `research/stretch/single-layer-mlx-materialization-002-plan.md`
- [x] Runner blob `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`
- [x] Run `20260819-155641`
- [x] Classification `SINGLE_LAYER_MLX_EVICTION_PASS`
- [x] Layer 18 provenance exact: 25 tensors / 84,427,264 B
- [x] Host gate 70/68/67% free; swap 850.5 MB
- [x] Pre-eval MLX active delta 0 B
- [x] Post-eval MLX active delta exactly 84,427,264 B
- [x] Post-clear active/cache delta 0/0 B
- [x] `mx.eval` wall 0.039611 s
- [x] Minimum free memory 67%; peak swap 850.5 MB
- [x] Peak child RSS 40.25 MB
- [x] Disk unchanged 36.319 GiB
- [x] Freeze `research/stretch/single-layer-mlx-materialization-002-result.md`
- [x] Interpret as single-layer lazy residency + full reclamation prerequisite only

### Stretch 003 — Two-Layer Repeated Bounded Residency — CURRENT
- [x] Preregister `research/stretch/two-layer-bounded-residency-003-plan.md`
- [x] Add `scripts/stretch_two_layer_bounded_residency_003.py`
- [x] Freeze runner blob `5882b01c37616f668705713f46e5c30aa40c268a`
- [x] Freeze source provenance against Stretch 002 blob `e7bd6b...`
- [x] Probe layers exactly 18 then 19 in the same MLX child process
- [x] Preserve no-model/no-KV/no-generation boundary
- [x] Per-cycle lazy-load guard <=32 MiB pre-eval active delta
- [x] Per-cycle materialization gate: 84,427,264 B +/-1 MiB
- [x] Per-cycle eviction gate: post-clear active/cache <=1 MiB
- [ ] Run Stretch 003
- [ ] Freeze repeated-residency result

### Stretch 004 — Sequential forward prototype — CONDITIONAL
- [ ] Only preregister if Stretch 003 is `TWO_LAYER_BOUNDED_RESIDENCY_PASS`
- [ ] Introduce actual transformer-layer computation over a tiny frozen input
- [ ] Start with a minimal number of consecutive layers, not all 36
- [ ] Compare streamed outputs numerically against resident control
- [ ] Measure activations, shared weights, MLX active/cache, system free/swap and wall time
- [ ] Still no production-quality token generation claim

### Stretch 005+ — later if prerequisites pass
- [ ] Extend streamed sequential transformer forward
- [ ] Add shared embedding/norm residency policy
- [ ] Add KV-cache handling
- [ ] Compare against resident control for logit/token equivalence
- [ ] Add prefetch/double buffering
- [ ] Measure SSD bytes/token, RAM, swap, wall time and tok/s
- [ ] Explore layer cache/residency policies
- [ ] Only later study layer skipping/early exit or MoE routing

## Phase 8 — Synthesis
- [ ] Capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental streamed profile
- [ ] Publish research findings when ready
