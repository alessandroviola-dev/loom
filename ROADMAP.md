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
- [x] Direct MLX Smoke 001 generated successfully
- [x] Diagnose locale swap parser defect (`used = 1121,88M`)
- [x] Rerun identical smoke with telemetry-only locale-safe parser
- [x] Smoke safety rerun FULL_PASS (`20260819-124440`): minimum free memory 23%, peak swap 1720.75 MB
- [x] Freeze `research/runtime/direct-mlx-8b-3bit-smoke-001-swapfix-rerun.md`
- [x] Run real Coding Benchmark T01 Workload Safety 001 (`20260819-124952`)
- [x] T01 workload FULL_PASS: minimum free memory 19%, peak swap 1643.12 MB
- [x] T01 structured delivery `written`; prompt 57.11 t/s; generation 16.52 t/s; MLX peak memory 3.960 GB
- [x] Freeze `research/runtime/direct-mlx-8b-3bit-t01-workload-001.md`
- [x] Preregister full Direct MLX Coding Benchmark 001
- [x] Freeze exact adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- [x] Freeze exact scorer blob `754e9a6506968d2b191bff57997710591efe8133`
- [x] Add `research/runtime/direct-mlx-coding-benchmark-001-plan.md`
- [x] Add `scripts/direct_mlx_coding_benchmark_001.py`
- [ ] Run full T01–T06 Direct MLX benchmark in one loaded model session
- [ ] If COMPLETE, freeze artifact/delivery-adjusted/per-task quality and compare with established baselines
- [ ] After COMPLETE quality review, decide whether isolated Pi integration/agentic validation is justified
- [ ] If partial resource/telemetry/runtime fail, diagnose before changing runtime
- [ ] Do not lower 5% free-memory / 5600 MB swap guardrails
- [ ] Do not change KV cap/precision, prompts, parser, scorer or retry policy inside the frozen benchmark

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
