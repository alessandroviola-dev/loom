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
- [x] Preregister Capability Amplifier 001
- [x] Freeze mechanism: exact baseline initial call + deterministic validation + max one repair
- [x] Freeze deterministic candidate selection by frozen test pass count
- [x] Freeze initial host gate: 3 consecutive samples >=70% free
- [x] Freeze runtime guardrails: free<5% / swap>5600 MB
- [x] Freeze quality gates before result
- [x] Run Amplifier 001 (`20260819-142640`)
- [x] Host gate PASS at 74%, 74%, 74%; swap 1206.12 MB
- [x] T01 initial solves 6/6, 15/15, no repair
- [x] T02 initial completes 3/7 and correctly triggers repair
- [x] Amplifier 001 aborts during T02 repair as `PARTIAL_RESOURCE_FAIL`
- [x] Run read-only resource diagnostic
- [x] Recover exact failure: free memory 4% <5%; peak swap 2500.88 MB
- [x] Recover T01 min free 5%, T02 initial min free 6%, T02 repair 7% -> 5% -> 5% -> 4%
- [x] Confirm first call cold load ~3.668 s vs second warm load ~0.045 s
- [x] Freeze `research/amplify/capability-amplifier-001-resource-diagnostic.md`
- [x] Conclude warm-resident Amplifier 001 lacks sufficient headroom; do not claim memory leak
- [x] Preregister one-factor Capability Amplifier 002 — Call-Isolated
- [x] Preserve all quality logic/prompts/benchmark/scorer from Amplifier 001
- [x] Change only residency: unload and confirm model absent between every model call
- [x] Do not add an inter-call >=70% recovery threshold; keep single-factor design
- [x] Add `scripts/capability_amplifier_002_call_isolated.py`
- [x] Freeze base runner blob `9f472c60b523762276291232f6e8c6ffc1c5fcae`
- [x] Freeze Amplifier 002 wrapper blob `df332568820e28c90baa5247df27e92cba43c0d6`
- [ ] Run Capability Amplifier 002 — Call-Isolated
- [ ] If COMPLETE, freeze quality/resource/efficiency and compare with single-shot + Amplifier 001
- [ ] If PARTIAL_RESOURCE_FAIL despite isolation, do not rerun unchanged or weaken guardrail
- [ ] If ISOLATION_FAIL, fix only demonstrated isolation-harness defect
- [ ] After amplification mechanism is established, port same logic to llama.cpp 4B for capability/efficiency comparison
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
