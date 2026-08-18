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
- [x] Validate and freeze task prompts/fixtures/tests
- [x] Define coding measurement runner
- [x] Define coding scoring rubric
- [x] Define machine-readable coding result format
- [x] Build Ollama single-shot benchmark adapter
- [x] Run Qwen 3.5 4B MLX on Coding Benchmark 01
- [x] Detect v1.0.0 subtest-counting scoring defect
- [x] Patch scorer as Coding Benchmark 01 v1.0.1
- [x] Add deterministic rescoring utility
- [x] Rescore existing Qwen run — artifact score 40.71/100
- [x] Ingest `run-summary.json` timing/token/memory and adapter-status data
- [x] Define delivery-adjusted strict single-shot scoring — first run 30.00/100
- [x] Harden Ollama adapter telemetry, progress and delivery accounting
- [x] Inspect preserved raw T04–T06 Ollama responses
- [x] Recover malformed envelopes without editing model code and test semantic content — recovered diagnostic score 82.86/100
- [x] Freeze Coding Baseline 001 official full result
- [ ] Define reasoning benchmark

## Phase 3 — Local coding agent
- [x] Research/select first agent layer — **Qwen Code**
- [x] Verify Node/npm prerequisites
- [x] Install Qwen Code — `0.21.13`
- [x] Add reproducible project configuration for Ollama / `qwen3.5:4b-mlx` at context 4096
- [x] Pull project config onto reference Mac and verify config contents
- [x] Correct local provider placeholder auth and set first smoke run to `approvalMode: plan`
- [x] Add reproducible read-only smoke-test runner with memory/swap and working-tree checks
- [ ] Run sandboxed read-only tool smoke test
- [ ] Run targeted edit + test smoke test
- [ ] Measure agent-layer memory/swap overhead
- [ ] Add reproducible validation/retry workflow
- [ ] Run Coding Benchmark 01 in `agentic` mode
- [ ] Compare agentic score, protocol reliability, latency and memory against Baseline 001
- [ ] Test Aider as second agentic comparator
- [ ] Evaluate OpenCode if context requirements are practical on 8 GB

## Phase 4 — llama.cpp
- [ ] Install/build optimized Apple Silicon version
- [ ] Test 7B/8B Q4
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
