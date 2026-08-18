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

## Phase 3 — Local coding agent / runtime investigation
- [x] Research/select first controlled agent layer — Qwen Code
- [x] Verify Node/npm prerequisites
- [x] Install Qwen Code — `0.21.13`
- [x] Add reproducible project configuration for Ollama / `qwen3.5:4b-mlx` at context 4096
- [x] Run Qwen Code normal-config read-only smoke at 4096 — failed before first tool call because initial prompt estimated 4474 tokens
- [x] Elevate existing Pi installation as immediate matched comparator
- [x] Add Ollama/Qwen to Pi non-destructively while preserving OpenAI/Codex setup
- [x] Run Pi read-only smoke at 4096 — PASS
- [x] Establish first harness-overhead result: Pi minimal harness fits 4096 where Qwen Code normal config does not
- [x] Run Pi targeted edit + test smoke at 4096 — functional PASS / strict output FAIL
- [x] Build, preregister and run isolated Pi Coding Benchmark 01 agentic adapter with hidden tests excluded
- [x] Validate raw Pi tool paths stay inside temporary workspaces — PASS
- [x] Freeze canonical `research/agents/pi-agentic-benchmark-001.md`
- [x] Canonical Pi Agentic 001: artifact/delivery **77.15**, strict **60.00**, delivery **6/6**, protocol **4/6**
- [x] Classify 22.85 artifact points as genuine frozen-test deficits and 17.15 additional strict points as final-output protocol-only loss
- [x] Identify sustained memory-pressure finding in Agentic 001: swap +3.279 GB and Ollama reported allocation 4.4 -> 7.2 GB at context 4096
- [x] Preregister/run Pi Memory Retention Probe 001 with identical warm/cold calls
- [x] Determine invocation count alone is insufficient: identical warm calls only 4.1 -> 4.5 GB; cold calls reset to 4.1 GB
- [x] Preregister/run direct Ollama Context Retention Probe 001
- [x] Record `research/runtime/ollama-context-retention-probe-001.md`
- [x] Confirm runtime-level prompt-pressure allocation: direct warm 418 -> 1618 -> 3018 prompt tokens produced 4.1 -> 4.3 -> 4.5 GB at fixed context 4096
- [x] Confirm retained warm high-water: low-after-high remained 4.6 GB while cold-low reset to 4.1 GB
- [x] Determine prompt pressure alone is still insufficient to explain Agentic 001 7.2 GB; cold-high was only 4.2 GB
- [x] Preregister Pi Multi-turn Memory Probe 001 with forced sequential file-chain round trips
- [x] Add `scripts/pi_multiturn_memory_probe.py`
- [ ] Run Pi Multi-turn Memory Probe 001: cold 1/4/8 sequential reads + warm 1-read after 8
- [ ] Determine whether within-session tool/turn depth materially raises Ollama high-water allocation
- [ ] If multi-turn remains insufficient, design lower-level/runtime probe closer to benchmark task shape
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
