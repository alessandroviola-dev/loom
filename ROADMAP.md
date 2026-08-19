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
- [x] Preserve call isolation, prompts, validation, one repair, scorer and guardrails
- [x] First attempt `20260819-150107`: `HOST_STATE_NOT_READY`, 0 calls
- [x] Valid run `20260819-150342`
- [x] Confirm repair `call_context=3072`
- [x] Confirm repair starts at 70% free / 2069.12 MB swap
- [x] Confirm trajectory 70 -> 65 -> 31 -> 7 -> 6 -> 4% free
- [x] `PARTIAL_RESOURCE_FAIL`: exact reason free 4% <5%
- [x] Peak swap 2318.12 MB
- [x] Freeze `research/amplify/capability-amplifier-003-resource-diagnostic.md`
- [x] Conclude 3072 changes pressure but is insufficient
- [x] Do not automatically descend to 2048
- [x] Note successful initial calls still reach only 6% free

### Repair-prompt anatomy — CURRENT
- [x] Add read-only `scripts/inspect_amplifier_prompt_anatomy.py`
- [ ] Measure T02 initial vs repair prompt bytes/chars/lines/words
- [ ] Decompose repair into original task / validation feedback / candidate / non-editable context
- [ ] If repair is materially inflated, preregister Compact Repair as one-factor architecture
- [ ] If repair is already compact, stop prompt-rescue work and reassess primary execution profile
- [ ] Treat llama.cpp 4B as strongest alternate due to larger observed memory headroom and higher throughput

### Later amplification work
- [ ] Obtain first COMPLETE amplifier profile
- [ ] Compare capability/resource/efficiency against single-shot and Pi references
- [ ] Port established amplification logic across the selected 4B profiles where scientifically useful
- [ ] Later candidate factors: compact repair, planner/verifier, tool loop, retrieval
- [ ] Only later consider specialization / LoRA / SFT / distillation

## Phase 7 — Stretch / Memory Hierarchy
- [ ] Reframe Colibrì / SSD streaming / MoE as explicit memory-hierarchy research
- [ ] Investigate layer/expert streaming rather than only aggressive quantization
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
