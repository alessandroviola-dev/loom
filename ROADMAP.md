# LOOM Roadmap

## Phase 0 — Project foundation
- [x] Choose project name: LOOM
- [x] Define research mission and handoff discipline
- [x] Create private repository `Ilcoach/loom`

## Phase 1 — Baseline
- [x] Update Ollama
- [x] Install/validate Qwen 3.5 4B MLX
- [x] Confirm MLX runner and 100% GPU execution
- [x] Measure baseline throughput and memory
- [x] Weighted prompt throughput: 186.46 tok/s; generation: 16.01 tok/s

## Phase 2 — Benchmark framework
- [x] Define/freeze Coding Benchmark 01 v1.0.1
- [x] Freeze single-shot Coding Baseline 001
- [x] Canonical baseline: artifact 40.71, strict 30.00, delivery 3/6
- [x] Recovered semantic diagnostic: 82.86
- [ ] Define reasoning benchmark

## Phase 3 — Local coding agent / runtime investigation
- [x] Qwen Code 0.21.13 normal-config 4096 blocked before first request
- [x] Pi 0.84.2 configured non-destructively for Ollama
- [x] Pi 4096 smoke / Agentic Coding Benchmark 001
- [x] Pi Agentic 001: artifact/delivery 77.15, strict 60.00, delivery 6/6
- [ ] Add daily-use validation/retry workflow later

## Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED
- [x] Pin llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- [x] Setup Probe 003 PASS; Metal build validated
- [x] 4B Q4 control PASS: pp512 230.85 t/s; tg128 22.33 t/s; min free 22%
- [x] 8B Q4 max-offload VALID FAIL at 1% free
- [x] 8B Q3 max-offload VALID FAIL at 1% free
- [x] 8B Q2 technical/API PASS but frozen coding delivery 0/100 vs 4B 34.29/100
- [x] Q3 auto-fit default FAIL at 4% free
- [x] Q3 `-np 1` FAIL at 4% free
- [x] Q3 NP1 + Q8_0 KV API smoke PASS at 6% free
- [x] Q3 real Coding T01 then resource abort at 4% free
- [x] Freeze Q3 llama.cpp as **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096
- [x] Move main research branch to Direct MLX
- [ ] Optional future: separately motivate more aggressive llama.cpp KV if needed

## Phase 5 — Direct MLX — ACTIVE
- [x] Select isolated environment `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- [x] Direct MLX Setup Probe 001 PASS (`20260819-120748`)
- [x] Validate Darwin arm64 and tiny MLX computation
- [x] Acquire/verify `mlx-community/Qwen3-8B-3bit`, 3-bit/group-size 64
- [x] Main weight SHA256 PASS; observed weight 3.338 GiB
- [x] Direct MLX 8B 3-bit Smoke 001 generated successfully (`20260819-121656`)
- [x] Smoke output `OK.`; prompt 6.37 t/s; generation 24.62 t/s; MLX peak memory 3.668 GB
- [x] Minimum sampled free memory 25%
- [!] Swap telemetry unavailable (`None`), so frozen two-channel safety gate is incomplete
- [x] Freeze result as generation PASS / safety telemetry incomplete
- [x] Add `scripts/diagnose_macos_swap_telemetry.py`
- [ ] Run read-only swap telemetry diagnostic
- [ ] If parser defect, fix telemetry only and rerun identical smoke with already-downloaded model
- [ ] Only after complete safety PASS preregister real Coding Benchmark T01 workload probe
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
