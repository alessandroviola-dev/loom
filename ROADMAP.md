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
- [x] Preregister real Coding Benchmark T01 workload-safety probe
- [x] Add `research/runtime/direct-mlx-8b-3bit-t01-workload-001-plan.md`
- [x] Add `scripts/direct_mlx_8b_3bit_t01_workload.py`
- [ ] Run Direct MLX 8B 3-bit T01 Workload Safety 001
- [ ] If T01 workload safety FULL_PASS, freeze result and preregister full Direct MLX Coding Benchmark 01
- [ ] Only after full quality/delivery gate consider Pi integration
- [ ] If T01 RESOURCE_FAIL, do not lower 5%/5600 MB guardrails or reduce the 4096 KV cap inside the failed condition
- [ ] Consider Direct MLX KV quantization only as a separately preregistered rescue if needed

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
