# LOOM Roadmap

## Phase 0 — Project foundation
- [x] Choose project name: LOOM
- [x] Define research mission and handoff discipline
- [x] Create private repository `Ilcoach/loom`

## Phase 1 — Baseline
- [x] Validate canonical Ollama/MLX 4B baseline
- [x] Weighted prompt throughput 186.46 t/s; generation 16.01 t/s
- [x] Freeze Coding Baseline 001: artifact 40.71, strict/delivery-adjusted 30.00, delivery 3/6

## Phase 2 — Benchmark framework
- [x] Freeze Coding Benchmark 01 v1.0.1
- [ ] Define reasoning benchmark later

## Phase 3 — Local agent investigation
- [x] Validate Pi 0.84.2 non-destructively
- [x] Pi Agentic Coding Benchmark 001
- [x] Establish same-4B agentic reference: artifact/delivery 77.15, strict 60.00, delivery 6/6

## Phase 4 — llama.cpp runtime frontier — CHARACTERIZED
- [x] 4B Q4 control PASS: pp512 230.85 t/s, tg128 22.33 t/s
- [x] 8B Q4/Q3 max-offload frontier characterized
- [x] 8B Q2 technically runnable but poor structured coding delivery
- [x] Q3 NP1 + Q8_0 KV API smoke PASS
- [x] Q3 real Coding T01 RESOURCE FAIL at 4% free
- [x] Preserve llama.cpp 4B as future Amplify capability/efficiency control

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED / MAIN BRANCH CLOSED
- [x] Direct MLX environment validated
- [x] Qwen3-8B-3bit full session stable but not promoted on quality
- [x] Qwen3-8B-4bit continuous profile resource boundary characterized
- [x] Close 8B rescue ladder after preregistered attempts
- [x] Preserve verified models/results

## Phase 6 — Capability Amplification — ACTIVE

Research question:
**What is the greatest useful capability that can be produced by an 8 GB local system?**

Primary current subject: `qwen3.5:4b-mlx` via Ollama.
Alternate preserved subject: Qwen3-4B Q4 via llama.cpp.

### Amplifier 001 — warm-resident
- [x] Freeze exact baseline initial call + deterministic validation + max one repair
- [x] Run `20260819-142640`
- [x] T01 initial 6/6; T02 initial 3/7; repair triggered
- [x] `PARTIAL_RESOURCE_FAIL`: free 4% <5%, peak swap 2500.88 MB
- [x] Diagnose warm-resident profile as insufficient headroom
- [x] Do not claim memory leak

### Amplifier 002 — call-isolated
- [x] Preregister one-factor call-isolated profile
- [x] Confirm unload between calls
- [x] Valid run `20260819-144256`
- [x] T02 repair starts at 68% free and still reaches 4%
- [x] `PARTIAL_RESOURCE_FAIL`; peak swap 2611.50 MB
- [x] Conclude call isolation works but is insufficient
- [x] Do not add recovery gate as leading fix

### Amplifier 003 — repair context 3072
- [x] Preregister single 25% repair-context reduction
- [x] Initial calls remain 4096; repair calls 3072
- [x] Valid run `20260819-150342`
- [x] Confirm repair `call_context=3072`
- [x] Repair starts at 70% free / 2069.12 MB swap
- [x] Repair trajectory 70 -> 65 -> 31 -> 7 -> 6 -> 4% free
- [x] `PARTIAL_RESOURCE_FAIL`; peak swap 2318.12 MB
- [x] Freeze `research/amplify/capability-amplifier-003-resource-diagnostic.md`
- [x] Do not automatically descend to 2048
- [x] Note successful initial calls still reach only 6% free

### Repair-prompt anatomy
- [x] Measure T02 initial prompt: 1638 B
- [x] Measure T02 repair prompt: 4573 B
- [x] Freeze ratio: 2.792x
- [x] Measure validation feedback: 2762 B (~60.4% of repair prompt)
- [x] Freeze `research/amplify/capability-amplifier-003-prompt-anatomy-t02.md`
- [x] Conclude one bounded Compact Repair experiment is justified

### Amplifier 004 — Compact Feedback — READY / QUEUED
- [x] Preregister `research/amplify/capability-amplifier-004-compact-feedback-plan.md`
- [x] Preserve initial context 4096 and repair context 3072
- [x] Preserve task prompt + current candidate in repair
- [x] Preserve isolation, validation, max one repair, scorer and guardrails
- [x] Change only variable failure-detail serialization
- [x] Freeze detail body budget at 768 UTF-8 bytes
- [x] Preserve first feedback line + deterministic UTF-8-safe detail tail
- [x] Add `scripts/capability_amplifier_004_compact_feedback.py`
- [x] Freeze runner blob `3f1f596fc2d6d66c73e5d434cb6e738bb93657b2`
- [ ] Run Amplifier 004 after current Stretch 001 checkpoint
- [ ] If PARTIAL_RESOURCE_FAIL, stop prompt-budget/context rescue ladder on Ollama/MLX profile
- [ ] If COMPLETE, freeze quality/resource/efficiency and apply prospective gates

### Later Amplify work
- [ ] Obtain first COMPLETE amplifier profile
- [ ] Compare capability/resource/efficiency against single-shot and Pi references
- [ ] Reassess llama.cpp 4B if Ollama/MLX 004 remains resource-bound
- [ ] Later candidate factors: planner/verifier, tool loop, retrieval
- [ ] Only later consider specialization / LoRA / SFT / distillation

## Phase 7 — Stretch / Memory Hierarchy — ACTIVE

Research direction:
**Can LOOM treat SSD + RAM as a model-memory hierarchy rather than requiring full weight residency?**

Principle:
- dense layer streaming = use all layers sequentially while keeping only a bounded subset resident;
- layer skipping / early exit = separate later research problem, not assumed safe for standard dense checkpoints.

### Stretch 001 — Dense Layer Streaming Feasibility — CURRENT
- [x] Select verified `mlx-community/Qwen3-8B-3bit` as preferred subject
- [x] No new download authorized
- [x] Preregister `research/stretch/layer-streaming-feasibility-001-plan.md`
- [x] Add standard-library runner `scripts/stretch_layer_streaming_feasibility_001.py`
- [x] Freeze runner blob `890444928abd6cc24e7194317c92b36b50fd994b`
- [x] Stage A design: safetensors header-only layer map
- [x] Stage A exact coverage gate against `num_hidden_layers`
- [x] Stage A exact per-layer / shared byte accounting
- [x] Stage B design: read only one middle layer's exact byte ranges
- [x] Stage B bounded 4 MiB I/O chunks + SHA-256 fingerprint
- [x] Record wall time / MiB/s / free memory / swap / disk
- [x] No model launch, no MLX model construction, no cache mutation
- [x] First launch `20260819-153944` returns `MODEL_NOT_FOUND` before inspecting weights
- [x] Classify first launch as locator mismatch / no scientific Stretch result
- [x] Recover verified Direct MLX artifact path: `results-local/mlx/models/Qwen3-8B-3bit`
- [x] Freeze locator note `research/stretch/layer-streaming-feasibility-001-locator-note.md`
- [x] Do not modify runner; use existing `--model-dir` override
- [ ] Rerun same frozen Stretch 001 with explicit verified model path
- [ ] Freeze exact layer layout and selective-I/O result

### Stretch 002 — Single-layer MLX materialization + eviction — CONDITIONAL
- [ ] Only preregister if Stretch 001 is `LAYER_ADDRESSABLE_IO_PASS`
- [ ] Materialize one transformer layer only
- [ ] Force MLX evaluation
- [ ] Measure MLX active/cache memory + system free/swap
- [ ] Release references and use version-safe GC/cache reclamation
- [ ] Verify memory recovery
- [ ] Do not run full generation yet

### Stretch 003+ — later if prerequisites pass
- [ ] Build streamed sequential forward prototype
- [ ] Verify numerical/logit equivalence against resident control
- [ ] Add prefetch / double-buffering
- [ ] Measure SSD traffic per token and throughput
- [ ] Explore cache/residency policy
- [ ] Only later investigate dynamic layer selection / early exit / MoE routing

## Phase 8 — Synthesis
- [ ] Build capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental large-model/streamed profile
- [ ] Publish research findings when ready
