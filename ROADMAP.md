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
- [x] Ingest Qwen Code + Pi smoke summaries and compare memory/swap/runtime/tool metadata
- [x] Record `research/agents/harness-comparison-001.md`
- [x] Harden Qwen Code smoke runner to detect semantic API errors and capture `.qwen/settings.json` diffs
- [x] Inspect Qwen Code settings delta — only automatic schema marker `"$version": 4`
- [x] Adopt Qwen Code settings schema version 4 in the versioned LOOM config
- [x] Add isolated reproducible Pi edit+test smoke runner at context 4096
- [x] Run Pi targeted edit + test smoke at context 4096 — **functional PASS**: read/edit/bash used, solution fixed, independent tests pass, tests unchanged, tracked LOOM tree unchanged
- [x] Detect Pi edit-smoke validator defect: exact final-output compliance was computed but omitted from aggregate success
- [x] Patch Pi edit-smoke runner to separate `functional_success` and `strict_success`
- [x] Record `research/agents/pi-edit-test-smoke-001.md` — functional PASS / strict output FAIL
- [x] Ingest Pi edit+test smoke memory/swap/runtime metrics — ~114 s, +655.31 MB swap, Ollama 4.8 GB / 100% GPU / context 4096 after run
- [x] Build isolated Pi Coding Benchmark 01 agentic adapter with hidden tests excluded from agent workspaces
- [x] Preregister Pi agentic benchmark protocol and scoring in `research/agents/pi-agentic-benchmark-001-plan.md`
- [x] Run Coding Benchmark 01 in Pi file-agentic mode at context 4096 — preliminary artifact/delivery **77.15**, strict **60.00**, delivery **6/6**, protocol **4/6**
- [x] Record preliminary result in `research/agents/pi-agentic-benchmark-001-preliminary.md`
- [ ] Ingest full Pi agentic `run-summary.json`: task scores, protocol failures, tool/final-text events, runtime and memory/swap
- [ ] Validate adapter/isolation and freeze canonical Pi Agentic Coding Benchmark 001 result
- [ ] Compare canonical agentic artifact/delivery/strict scores, protocol reliability, latency and memory against Baseline 001
- [ ] Run Qwen Code safe-mode 4096 diagnostic as secondary harness-overhead experiment
- [ ] Measure Qwen Code context scaling to 8192 only if it still adds research value
- [ ] Add reproducible agent validation/retry workflow for real-world daily-use profile
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
