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
- [x] Preregister Capability Amplifier 001
- [x] Freeze exact baseline initial call + deterministic validation + max one repair
- [x] Freeze deterministic candidate selection by test pass count
- [x] Freeze initial host gate: 3 consecutive samples >=70% free
- [x] Freeze runtime guardrails: free<5% / swap>5600 MB
- [x] Freeze quality gates before result
- [x] Run Amplifier 001 (`20260819-142640`)
- [x] T01 initial solves 6/6, 15/15, no repair
- [x] T02 initial completes 3/7 and triggers repair
- [x] Abort during T02 repair as `PARTIAL_RESOURCE_FAIL`
- [x] Read-only diagnostic recovers exact free-memory breach: 4% <5%; peak swap 2500.88 MB
- [x] Confirm T01 min free 5%, T02 initial min free 6%, repair 7% -> 5% -> 5% -> 4%
- [x] Confirm first call cold load ~3.668 s vs second warm load ~0.045 s
- [x] Freeze warm-resident profile as insufficient headroom; do not claim memory leak

### Amplifier 002 — call-isolated
- [x] Preregister one-factor call-isolated profile
- [x] Preserve model, prompts, validation, repair, scorer, context, sampler and guardrails
- [x] Change only residency: unload and confirm target absent between every model call
- [x] Do not add inter-call >=70% recovery threshold in 002
- [x] Freeze Amplifier 002 wrapper blob `df332568820e28c90baa5247df27e92cba43c0d6`
- [x] First launch (`20260819-143838`) returns `HOST_STATE_NOT_READY` at 67% free; 0 model calls
- [x] Valid launch (`20260819-144256`) passes host gate at 71%, 72%, 72%; swap 1699.0 MB
- [x] T01 initial completes and solves without repair
- [x] T02 initial completes and triggers repair
- [x] Call-isolated run still terminates `PARTIAL_RESOURCE_FAIL` during T02 repair path
- [x] Freeze partial record `research/amplify/capability-amplifier-002-partial-20260819-144256.md`
- [x] Do not assign aggregate quality score to partial 002 run
- [ ] Run read-only diagnostic on Amplifier 002 persisted telemetry
- [ ] Recover exact failure reason, min free, peak swap and all isolation samples
- [ ] Verify actual unload confirmation before/after each completed call
- [ ] Determine free/swap state immediately before T02 repair
- [ ] If unload succeeded but memory did not recover enough, preregister unload + recovery-gated profile as a new factor
- [ ] If memory recovered materially and cold repair alone drives breach, redesign repair footprint rather than residency timing
- [ ] If isolation itself failed, fix only demonstrated isolation harness issue
- [ ] Do not rerun unchanged Amplifier 002 or weaken guardrail

### Later amplification work
- [ ] Once a COMPLETE amplification mechanism exists, compare quality/resource/efficiency against single-shot 30.00/3-of-6 and Pi 77.15/6-of-6
- [ ] Port established amplification logic to llama.cpp 4B as capability/efficiency control
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
