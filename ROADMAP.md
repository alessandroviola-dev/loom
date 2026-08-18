# LOOM Roadmap

## Phase 0 — Project foundation
- [x] Choose project name: LOOM
- [x] Define research mission
- [x] Define handoff discipline
- [x] Create private GitHub repository `Ilcoach/loom`
- [x] Push initial project structure

## Phase 1 — Baseline
- [x] Update Ollama
- [x] Install Qwen 3.5 4B MLX
- [x] Confirm MLX runner
- [x] Confirm 100% GPU execution
- [x] Measure initial generation throughput
- [x] Compare memory state with model ON/OFF
- [x] Re-evaluate prompt-processing throughput using real benchmark prompts — weighted 186.46 tok/s across T01–T06

## Phase 2 — Benchmark framework
- [x] Define Coding Benchmark 01
- [x] Validate/freeze prompts, fixtures and tests
- [x] Build/validate scoring and single-shot adapter
- [x] Fix scorer defect as Coding Benchmark 01 v1.0.1
- [x] Freeze Coding Baseline 001
- [x] Baseline canonical: artifact 40.71, strict 30.00, delivery 3/6
- [x] Recover malformed raw envelopes diagnostically — semantic-content 82.86
- [ ] Define reasoning benchmark

## Phase 3 — Local coding agent / runtime investigation
- [x] Install/configure Qwen Code 0.21.13 for Ollama
- [x] Qwen Code normal-config 4096 smoke — blocked before first tool call by 4474-token initial prompt
- [x] Add Ollama/Qwen to existing Pi non-destructively
- [x] Pi 4096 read-only smoke — PASS
- [x] Pi edit+test smoke — functional PASS / strict output FAIL
- [x] Build/preregister/run isolated Pi Coding Benchmark 01 agentic adapter
- [x] Freeze canonical Pi Agentic Coding Benchmark 001
- [x] Canonical Pi Agentic 001: artifact/delivery 77.15, strict 60.00, delivery 6/6, protocol 4/6
- [x] Validate raw tool paths — PASS
- [x] Ingest provider usage — 20,209 total tokens across six sessions
- [x] Identify Agentic 001 memory trajectory: Ollama SIZE 4.4 -> 7.2 GB; swap +3.279 GB
- [x] Pi Memory Retention Probe 001 — identical warm calls only 4.1 -> 4.5 GB; cold reset 4.1 GB
- [x] Ollama Context Retention Probe 001 — direct prompt pressure 4.1 -> 4.5 GB; retained warm high-water 4.6 GB
- [x] Determine invocation count and prompt pressure alone are insufficient to explain 7.2 GB
- [x] Pi Multi-turn Probe 001 — invalidate causal depth inference due speculative filename reads
- [x] Pi Multi-turn Probe 002 — valid depth 1/4 = 4.2/4.3 GB; depth 8 invalid due token protocol failures
- [x] Pi Multi-turn Probe 003 — valid depth 1/4 = 4.1/4.3 GB; depth 8 invalid because model terminated after first valid turn
- [x] Stop iterating artificial deep-turn protocols; valid 1->4 evidence shows only small SIZE effect
- [x] Run Pi Agentic Cold Replay 001 using exact frozen T01-T06 workloads
- [x] Validate T01-T05 cold replay; T06 timed out before tool use and is excluded from causal comparison
- [x] Classify cumulative retained warm high-water as a major contributor to Agentic 001 memory growth
- [x] Close synthetic memory investigation as sufficient for practical conclusion; exact internal runtime mechanism remains unknown
- [x] Run Qwen Code safe-mode 4096 diagnostic
- [x] Safe mode reduces initial estimate only ~4474 -> 4363 tokens; still 267 tokens above 4096 and fails before first tool call
- [x] Record `research/agents/qwen-code-safe-mode-4096.md`
- [x] Deprioritize Qwen Code as secondary harness comparator; no 8192 rescue required for main research path
- [ ] Add reproducible agent validation/retry workflow for daily-use profile later
- [ ] Test Aider/OpenCode later only if they add research value

## Phase 4 — llama.cpp — ACTIVE
- [x] Preregister first reproducible Apple Silicon/Metal setup in `research/runtime/llama-cpp-phase4-plan.md`
- [x] Pin initial llama.cpp source commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- [x] Add `scripts/llama_cpp_setup_probe.py`
- [ ] Run setup probe: prerequisites + Release Metal build + `llama-cli`/`llama-bench`
- [ ] Validate 4B GGUF runtime control (`Qwen/Qwen3-4B-GGUF`, Q4_K_M)
- [ ] Test 8B Q4_K_M as first main capability step
- [ ] Measure throughput, memory pressure, load time and Metal/GPU offload
- [ ] Test Q3 variants
- [ ] Test ~9B Q3/Q2 where feasible
- [ ] Compare CPU/GPU offload strategies

## Phase 5 — Direct MLX
- [ ] Set up MLX environment
- [ ] Run equivalent model directly
- [ ] Compare throughput
- [ ] Compare memory pressure
- [ ] Compare context scaling

## Phase 6 — Colibrì / SSD streaming / MoE
- [ ] Install Colibrì
- [ ] Identify 8 GB-compatible candidates
- [ ] Measure resident memory vs disk traffic
- [ ] Test practical throughput
- [ ] Determine largest useful model

## Phase 7 — Extended runtime research
- [ ] Evaluate new Apple Silicon runtimes
- [ ] Test only if evidence suggests material advantage

## Phase 8 — Synthesis
- [ ] Daily-use profile
- [ ] Maximum-capability profile
- [ ] Experimental large-model profile
- [ ] Publish research findings when ready
