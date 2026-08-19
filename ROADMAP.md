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
- [x] Main weight SHA PASS; 3-bit/group-size 64 PASS
- [x] Direct MLX Smoke safety FULL_PASS (`20260819-124440`): minimum free 23%, peak swap 1720.75 MB
- [x] Direct MLX T01 Workload Safety FULL_PASS (`20260819-124952`): minimum free 19%, peak swap 1643.12 MB, delivery written
- [x] Run full Direct MLX Coding Benchmark 001 (`20260819-125647`) in one loaded model session
- [x] Full benchmark resource stability PASS: minimum free 14%, peak swap 1683.38 MB
- [x] Full benchmark classification COMPLETE
- [x] Freeze quality result: artifact 38.57/100, delivery-adjusted 27.86/100, structured delivery 2/6
- [x] Freeze `research/runtime/direct-mlx-coding-benchmark-001.md`
- [x] Add read-only `scripts/inspect_direct_mlx_coding_benchmark_001.py`
- [ ] Diagnose T03–T06 adapter failures and scorer points from persisted run; no model rerun
- [ ] After diagnostic, decide whether isolated Pi agentic validation is scientifically justified
- [ ] Do not promote the 8B profile as a practical upgrade solely because runtime stability is strong
- [ ] Do not alter prompts/parser/scorer or invent a post-hoc quality threshold
- [ ] If quality is not competitive, move to next Direct MLX quantization/model branch or Phase 6 rather than forcing Pi integration
- [ ] Do not lower 5% free-memory / 5600 MB swap guardrails

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
