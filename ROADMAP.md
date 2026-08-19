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

## Phase 6 — Amplify — ACTIVE / SECONDARY WHILE STRETCH CHECKPOINT RUNS

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
- [x] First launch locator mismatch only; no scientific result
- [x] Rerun using verified `results-local/mlx/models/Qwen3-8B-3bit`
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

### Stretch 002 — Single-Layer MLX Materialization + Eviction — CURRENT
- [x] Preregister `research/stretch/single-layer-mlx-materialization-002-plan.md`
- [x] Add `scripts/stretch_single_layer_mlx_materialization_002.py`
- [x] Freeze runner blob `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`
- [x] Probe layer 18 / 25 tensors / 84,427,264 B
- [x] No model construction, tokenizer, KV cache or generation
- [x] Measure lazy `mx.load` state before selected-layer `mx.eval`
- [x] Eager-load guard: pre-eval active delta <=32 MiB
- [x] Measure MLX active/cache/peak after materialization
- [x] Delete selected refs + GC + `mx.clear_cache()`
- [x] Eviction gate: final active/cache <= baseline +1 MiB
- [x] Host gate: 3 samples >=60% free; runtime free<5% / swap>5600 MB
- [ ] Run Stretch 002
- [ ] Freeze exact materialization and reclamation result

### Stretch 003 — Repeated bounded residency — CONDITIONAL
- [ ] Only preregister after Stretch 002 materialization/eviction result
- [ ] Sequentially materialize/evaluate/evict two different layers
- [ ] Demonstrate repeated bounded residency rather than one-off load
- [ ] Still no full token generation

### Stretch 004+ — later if prerequisites pass
- [ ] Build streamed sequential transformer forward prototype
- [ ] Compare against resident control for numerical/logit equivalence
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
