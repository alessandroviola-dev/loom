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
- [x] Research/select first controlled agent layer — Qwen Code
- [x] Verify Node/npm prerequisites
- [x] Install Qwen Code — `0.21.13`
- [x] Add reproducible project configuration for Ollama / `qwen3.5:4b-mlx` at context 4096
- [x] Run Qwen Code normal-config read-only smoke at 4096 — failed before first tool call because initial prompt estimated 4474 tokens
- [x] Elevate existing Pi installation as immediate matched comparator
- [x] Add Ollama/Qwen to Pi non-destructively while preserving OpenAI/Codex setup
- [x] Run Pi read-only smoke at 4096 with only `read` exposed — PASS, returned `# LOOM`, working tree unchanged
- [x] Establish first measured harness-overhead result: Pi minimal harness fits 4096 where Qwen Code normal config does not
- [ ] Ingest Qwen Code + Pi smoke summaries and compare memory/swap/runtime/tool metadata
- [ ] Diagnose Qwen Code smoke working-tree status delta
- [ ] Run Pi targeted edit + test smoke at context 4096
- [ ] Run Qwen Code safe-mode 4096 diagnostic
- [ ] Measure Qwen Code context scaling to 8192 only as a separate experiment if still useful
- [ ] Add reproducible agent validation/retry workflow
- [ ] Run Coding Benchmark 01 in Pi `agentic` mode
- [ ] Compare agentic score, protocol reliability, latency and memory against Baseline 001
- [ ] Decide whether Qwen Code remains a primary comparator after safe-mode/context tests
- [ ] Test Aider as later comparator if it adds research value
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
