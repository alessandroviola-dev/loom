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
- [x] Pin llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
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
- [x] Direct MLX 8B 3-bit Smoke 001 generated successfully (`20260819-121656`)
- [x] Output `OK.`; generation 24.62 t/s; MLX peak memory 3.668 GB
- [x] Minimum sampled free memory 25%
- [x] Identify swap telemetry defect: macOS emits decimal commas (`used = 1121,88M`)
- [x] Classify first smoke as generation PASS / swap safety channel unresolved
- [x] Record `research/runtime/direct-mlx-8b-3bit-smoke-001-swap-diagnostic.md`
- [x] Add locale-safe telemetry-only rerun wrapper `scripts/direct_mlx_8b_3bit_smoke_001_swapfix.py`
- [ ] Run identical Smoke 001 with corrected swap parser; reuse downloaded model
- [ ] If complete safety PASS, preregister real Coding Benchmark T01 workload-safety probe
- [ ] Only after T01 workload-safety PASS run full frozen Coding Benchmark quality comparison
- [ ] Only after technical + workload + quality gates consider Pi integration
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
