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
- [x] Qwen3-8B-3bit full six-task session stable
- [x] Freeze 3-bit quality: artifact 38.57, delivery-adjusted 27.86, delivery 2/6
- [x] Qwen3-8B-4bit smoke + standalone T01 PASS
- [x] Full 4-bit unquantized-KV profile fails frozen memory guardrail
- [x] Controlled >=70%-free replication reaches T04 then fails at 4% free
- [x] Close exact 4-bit / 4096 / unquantized-KV continuous profile
- [x] Attempt one final KV8 rescue; operator reports failure
- [x] Do not assign KV8 canonical failure type without missing detailed log
- [x] Close 8B 4-bit rescue ladder
- [x] Preserve verified models/results

## Phase 6 — Capability Amplification — ACTIVE

Research question:
**What is the greatest useful capability that can be produced by an 8 GB local system?**

Primary subject: `qwen3.5:4b-mlx` via Ollama.

- [x] Adopt Amplify / Stretch research pivot
- [x] Select canonical Ollama/MLX 4B as primary Amplify subject
- [x] Keep faster llama.cpp 4B as later secondary control
- [x] Preregister `research/amplify/capability-amplifier-001-plan.md`
- [x] Add `scripts/capability_amplifier_001.py`
- [x] Freeze Amplify 001 mechanism: exact baseline initial call + deterministic validation + max one repair
- [x] Freeze deterministic candidate selection by frozen test pass count
- [x] Freeze host gate: 3 consecutive samples >=70% free
- [x] Freeze runtime guardrails: free<5% / swap>5600 MB
- [x] Freeze quality gates before result
- [x] Run Capability Amplifier 001 (`20260819-142640`)
- [x] Host-state gate PASS at 74%, 74%, 74% free; swap 1206.12 MB
- [x] T01 solved on initial call with no repair
- [x] T02 initial call completes and triggers one repair from frozen-test failure
- [x] Frozen run aborts during T02 repair path as `PARTIAL_RESOURCE_FAIL`
- [x] Do not assign aggregate quality score to partial run
- [x] Freeze partial result record `research/amplify/capability-amplifier-001-partial-20260819-142640.md`
- [x] Add read-only inspector `scripts/inspect_capability_amplifier_001.py`
- [ ] Inspect exact failure reason and telemetry for run `20260819-142640`
- [ ] Determine whether pressure reflects warm-state accumulation, repair-specific prompt load, or another demonstrated factor
- [ ] Do not rerun unchanged Amplify 001 before diagnostic
- [ ] If evidence supports warm-state accumulation, preregister a call-isolated amplification profile rather than changing the model
- [ ] Preserve quality mechanism: validator + max one repair remains the scientific capability factor unless evidence requires otherwise
- [ ] If a future Amplify run reaches COMPLETE, compare against single-shot 30.00/3-of-6 and Pi reference 77.15/6-of-6
- [ ] After mechanism is established, port same amplification logic to llama.cpp 4B for capability/efficiency comparison
- [ ] Later candidate capability factors: planner/verifier, tool loop, retrieval
- [ ] Only later consider specialization / LoRA / SFT / distillation

## Phase 7 — Stretch / Memory Hierarchy
- [ ] Reframe Colibrì / SSD streaming / MoE as explicit memory-hierarchy research
- [ ] Investigate layer/expert streaming rather than only more aggressive quantization
- [ ] Evaluate SSD traffic vs resident-memory reduction
- [ ] Explore small resident controller + selectively invoked large/MoE component
- [ ] Identify 8 GB-compatible or modifiable candidates

## Phase 8 — Synthesis
- [ ] Build capability-vs-memory-vs-time frontier
- [ ] Daily-use profile
- [ ] Fast/efficient profile
- [ ] Maximum-capability profile
- [ ] Experimental large-model/streamed profile
- [ ] Publish research findings when ready
