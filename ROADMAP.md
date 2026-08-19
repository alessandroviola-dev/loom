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

### Amplifier 001 — warm-resident
- [x] Preregister frozen initial + deterministic validation + max one repair
- [x] Run `20260819-142640`
- [x] T01 initial 6/6; T02 initial 3/7; repair triggered
- [x] `PARTIAL_RESOURCE_FAIL`: free 4% <5%, peak swap 2500.88 MB
- [x] Diagnose warm-resident profile as insufficient headroom
- [x] Do not claim memory leak

### Amplifier 002 — call-isolated
- [x] Preregister one-factor call-isolated profile
- [x] Preserve quality mechanism, context 4096 and guardrails
- [x] Valid run `20260819-144256`
- [x] T01 initial 6/6; T02 initial 3/7; repair triggered
- [x] Confirm model unload between calls
- [x] Confirm T02 repair starts at 68% free
- [x] Repair trajectory 68% -> 63% -> 23% -> 16% -> 4%
- [x] `PARTIAL_RESOURCE_FAIL`: free 4% <5%, peak swap 2611.50 MB
- [x] Conclude call isolation works but is insufficient
- [x] Do not add recovery gate as leading fix

### Amplifier 003 — repair context 3072
- [x] Preregister one-factor repair-context reduction
- [x] Initial calls remain 4096; repair calls frozen at 3072
- [x] Preserve call isolation, prompt content, validation, one repair, scorer and guardrails
- [x] Freeze runner blob `c2bcc8f126eb5b599645ba12d1fd08a348e2b443`
- [x] First attempt `20260819-150107`: `HOST_STATE_NOT_READY` at 69% free; 0 calls
- [x] Valid launch `20260819-150342`: host 71%, 74%, 74%; swap 1247.88 MB
- [x] T01 initial completes without repair
- [x] T02 initial completes and triggers repair
- [x] Terminal classification `PARTIAL_RESOURCE_FAIL`
- [x] Completed model-call records: 2
- [x] Freeze partial record `research/amplify/capability-amplifier-003-partial-20260819-150342.md`
- [ ] Run read-only diagnostic on `20260819-150342`
- [ ] Recover exact failure reason, repair context record, pre-state, telemetry and response completion
- [ ] Do not automatically lower repair context to 2048
- [ ] If 3072 still breaches from recovered state, redesign repair architecture/prompt budget
- [ ] If a harness/isolation/telemetry defect is found, fix only that defect

### Later amplification work
- [ ] Obtain first COMPLETE amplifier profile
- [ ] Compare against single-shot 30.00/3-of-6 and Pi 77.15/6-of-6
- [ ] Port established amplification logic to llama.cpp 4B for capability/efficiency comparison
- [ ] Later candidate capability factors: compact repair, planner/verifier, tool loop, retrieval
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
