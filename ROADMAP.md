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
- [x] 8B Q4/Q3 max-offload memory frontier characterized
- [x] 8B Q2 technically runnable but poor structured coding delivery
- [x] Q3 NP1 + Q8_0 KV API smoke PASS
- [x] Q3 real Coding T01 RESOURCE FAIL at 4% free
- [x] Preserve llama.cpp 4B as future Amplify speed/efficiency control

## Phase 5 — Direct MLX 8B frontier — CHARACTERIZED / MAIN BRANCH CLOSED
- [x] Direct MLX environment validated
- [x] Qwen3-8B-3bit smoke + T01 + full six-task session stable
- [x] 3-bit full benchmark COMPLETE: min free 14%, peak swap 1683.38 MB
- [x] Freeze 3-bit quality: artifact 38.57, delivery-adjusted 27.86, delivery 2/6
- [x] Do not promote 3-bit on quality
- [x] Qwen3-8B-4bit smoke PASS and standalone T01 PASS
- [x] Original 4-bit full benchmark resource-fails
- [x] Host-state-controlled 4-bit replication reaches T04 then resource-fails at 4% free
- [x] Close exact 4-bit / 4096 / unquantized-KV continuous profile as RESOURCE FAIL
- [x] Attempt one final KV8 rescue; operator reports failure
- [x] Do not assign a canonical KV8 failure type without its missing detailed log
- [x] Close 8B 4-bit rescue ladder; no KV6/KV4/context cascade
- [x] Preserve all verified models/results for future reference

## Phase 6 — Capability Amplification — ACTIVE

Research question:
**What is the greatest useful capability that can be produced by an 8 GB local system?**

Primary subject: `qwen3.5:4b-mlx` via Ollama.

- [x] Adopt Amplify / Stretch research pivot
- [x] Freeze `research/notes/capability-amplification-pivot-2026-08-19.md`
- [x] Select canonical Ollama/MLX 4B as primary Amplify subject
- [x] Keep faster llama.cpp 4B as later secondary control
- [x] Preregister `research/amplify/capability-amplifier-001-plan.md`
- [x] Add `scripts/capability_amplifier_001.py`
- [x] Freeze Amplify 001 mechanism: exact baseline Call 1 + deterministic validation + max one repair
- [x] Freeze deterministic candidate selection by frozen test pass count; ties retain initial
- [x] Freeze host gate: 3 consecutive samples >=70% free before cold-model launch
- [x] Freeze runtime guardrails: free<5% / swap>5600 MB
- [x] Freeze quality gates: delivery-adjusted >30 = QUALITY_IMPROVED; plus artifact >40.71 and delivery >3/6 = STRONG_AMPLIFICATION
- [ ] Run Capability Amplifier 001
- [ ] Freeze full per-task repair trajectory, total model calls/tokens/wall/resource metrics
- [ ] Compare Amplify 001 to frozen 4B single-shot baseline
- [ ] If amplification is established, choose exactly one next capability factor
- [ ] Candidate later factors: planner/verifier, tool loop, retrieval
- [ ] Only later consider specialization / LoRA / SFT / distillation after inference-time amplification is characterized
- [ ] After mechanism is established, port the same amplifier to llama.cpp 4B for capability/efficiency comparison

## Phase 7 — Stretch / Memory Hierarchy
- [ ] Reframe Colibrì / SSD streaming / MoE as explicit memory-hierarchy research
- [ ] Investigate layer/expert streaming rather than simply more aggressive quantization
- [ ] Evaluate SSD traffic vs resident-memory reduction
- [ ] Explore small resident controller + selectively invoked large/MoE component
- [ ] Identify 8 GB-compatible or modifiable candidates
- [ ] Determine whether larger useful capability can be obtained without full model residency

## Phase 8 — Synthesis
- [ ] Build capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental large-model/streamed profile
- [ ] Publish research findings when ready
