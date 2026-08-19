# LOOM Roadmap

## Phase 0 — Project foundation
- [x] Choose project name: LOOM
- [x] Define research mission and handoff discipline
- [x] Create private repository `Ilcoach/loom`

## Phase 1 — Baseline
- [x] Validate canonical Ollama/MLX 4B baseline
- [x] Weighted prompt throughput 186.46 t/s; generation 16.01 t/s

## Phase 2 — Benchmark framework
- [x] Freeze Coding Benchmark 01 v1.0.1
- [x] Coding Baseline 001
- [ ] Define reasoning benchmark

## Phase 3 — Local agent investigation
- [x] Validate Pi 0.84.2 non-destructively
- [x] Pi Agentic Coding Benchmark 001
- [ ] Add daily-use validation/retry workflow later

## Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED
- [x] 4B Q4 control PASS
- [x] 8B Q4/Q3 max-offload memory frontier characterized
- [x] 8B Q2 technical/API PASS but structured coding quality inferior
- [x] Q3 NP1 + Q8_0 KV smoke PASS
- [x] Q3 real Coding T01 RESOURCE FAIL at 4% free
- [x] Freeze Q3 llama.cpp as API-smoke PASS / real-workload RESOURCE FAIL at context 4096
- [x] Move main branch to Direct MLX
- [ ] Optional future: separately motivate more aggressive llama.cpp KV if needed

## Phase 5 — Direct MLX — ACTIVE
- [x] Direct MLX Setup Probe 001 PASS (`20260819-120748`)
- [x] Freeze environment: `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- [x] Acquire/verify `mlx-community/Qwen3-8B-3bit`
- [x] 3-bit Smoke safety FULL_PASS (`20260819-124440`): minimum free 23%, peak swap 1720.75 MB
- [x] 3-bit exact T01 Workload Safety FULL_PASS (`20260819-124952`): minimum free 19%, peak swap 1643.12 MB, delivery written
- [x] 3-bit full Direct MLX Coding Benchmark 001 COMPLETE (`20260819-125647`)
- [x] 3-bit full-session resource stability PASS: minimum free 14%, peak swap 1683.38 MB
- [x] Freeze 3-bit quality: artifact 38.57/100, delivery-adjusted 27.86/100, structured delivery 2/6
- [x] Diagnose 3-bit quality from persisted outputs
- [x] T01 15/15, T02 12.86/15; T03–T06 delivery failures
- [x] Establish failures are not only formatting: T04/T06 also show content/instruction defects
- [x] Freeze `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`
- [x] Do not promote Qwen3-8B-3bit to Pi on current quality evidence
- [x] Select same-family profile `mlx-community/Qwen3-8B-4bit`
- [x] Verify 4-bit artifact: revision `545dc4251c05440727734bcd94334791f6ab0192`, 4-bit/group-size 64, SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- [x] Run Qwen3-8B-4bit Direct MLX Smoke 001 (`20260819-131009`)
- [x] 4-bit smoke FULL_PASS: output `OK.`, minimum free 10%, peak swap 2403.31 MB, MLX peak memory 4.6833 GB
- [x] Freeze `research/runtime/direct-mlx-8b-4bit-smoke-001.md`
- [x] Preregister exact 4-bit T01 workload-safety gate
- [x] Add `research/runtime/direct-mlx-8b-4bit-t01-workload-001-plan.md`
- [x] Add `scripts/direct_mlx_8b_4bit_t01_workload.py`
- [ ] Run 4-bit exact Coding Benchmark T01 workload safety at `max_kv_size=4096`, unquantized KV, unchanged 5%/5600 MB guardrails
- [ ] If 4-bit T01 FULL_PASS, freeze result and preregister full six-task 4-bit Coding Benchmark 01
- [ ] Only after COMPLETE 4-bit quality benchmark compare 4-bit vs 3-bit descriptively and decide whether Pi integration is justified
- [ ] If 4-bit T01 RESOURCE_FAIL, diagnose before any rescue; do not lower guardrails or change KV/context inside the failed condition
- [ ] Do not change prompts/parser/scorer or invent post-hoc thresholds

## Phase 6 — Colibrì / SSD streaming / MoE
- [ ] Install/evaluate Colibrì
- [ ] Identify 8 GB-compatible candidates
- [ ] Measure resident memory vs disk traffic
- [ ] Determine largest useful model

## Phase 7 — Extended runtime research
- [ ] Evaluate other Apple Silicon runtimes only when evidence suggests a material advantage

## Phase 8 — Synthesis
- [ ] Daily-use profile
- [ ] Maximum-capability profile
- [ ] Experimental large-model profile
- [ ] Publish research findings when ready
