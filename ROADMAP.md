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
- [x] Qwen Code 0.21.13 normal-config 4096 blocked before first request (~4474 tokens)
- [x] Pi 0.84.2 configured non-destructively for Ollama
- [x] Pi 4096 read-only and edit/test smoke tests
- [x] Freeze Pi Agentic Coding Benchmark 001
- [x] Pi Agentic 001: artifact/delivery 77.15, strict 60.00, delivery 6/6, protocol 4/6
- [x] Conclude cumulative retained warm high-water is a major contributor to prior memory growth; internal mechanism unresolved
- [x] Qwen Code safe mode still 4363 > 4096; deprioritize Qwen Code
- [ ] Add daily-use validation/retry workflow later

## Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED
- [x] Pin llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- [x] Install CMake 4.4.2 and validate Release/Metal build
- [x] Setup Probe 003 canonical PASS: `llama-cli`, `llama-bench`, Metal ON
- [x] 4B Q4_K_M Runtime Control 001 PASS: pp512 230.85 t/s; tg128 22.33 t/s; minimum free memory 22%
- [x] 8B Q4_K_M Capability 001 VALID FAIL at context 4096: memory free 1%
- [x] 8B Q3_K_M Capability 001 VALID FAIL at context 4096 / forced `-ngl -1`: memory free 1%
- [x] 8B Q2 Stage B FULL_PASS: pp512 103.00 t/s; tg128 13.72 t/s; minimum free 8%
- [x] Q2 llama-server smoke FULL_PASS: API `OK`; minimum free 6%
- [x] Coding Quality Compare 001: Q2 delivery 0/100 vs 4B Q4 34.29/100; Q2 profile not a practical upgrade
- [x] Q3 auto-fit default server VALID FAIL at 4% free
- [x] Q3 explicit `-np 1` VALID FAIL at 4% free
- [x] Q3 NP1 + Q8_0 KV API smoke FULL_PASS: minimum free 6%
- [x] Run Coding Quality Compare 002 under common NP1/Q8_0 runtime
- [x] Compare 002 Q3 server ready, then T01 resource abort: `memory free 4% < 5%`
- [x] Diagnose Q3 T01 timeline: repeatedly at 5% free, then 4% at ~20.3 s; no HTTP response because safety shutdown terminated server
- [x] Freeze `research/runtime/llama-cpp-coding-quality-compare-002-diagnostic.md`
- [x] Classify exact Q3 NP1/Q8 profile as **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096
- [x] Keep Compare 002 quality relation unresolved because Q3 did not complete
- [x] Do not expose Q3 llama.cpp profile to Pi
- [x] Move main research branch to Direct MLX instead of stacking another automatic llama.cpp KV rescue
- [ ] Optional future: revisit more aggressive llama.cpp KV only as a separately motivated branch, not the main path
- [ ] Do not lower the 5% guardrail or retroactively alter failed conditions
- [ ] Do not test ~9B until the useful 8B frontier is better characterized

## Phase 5 — Direct MLX — ACTIVE
- [x] Research current direct-MLX runtime/candidate path
- [x] Select isolated setup condition: `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- [x] Preregister `research/runtime/direct-mlx-setup-probe-001-plan.md`
- [x] Add `scripts/direct_mlx_setup_probe.py`
- [ ] Run Direct MLX Setup Probe 001; no model weights downloaded
- [ ] If setup PASS, freeze environment/package lock
- [ ] Separately preregister acquisition/runtime smoke for `mlx-community/Qwen3-8B-3bit` with disk accounting
- [ ] Test 8B/3-bit direct MLX at context 4096 under the same 5% free-memory safety boundary
- [ ] If workload-safe, compare throughput/memory against llama.cpp profiles
- [ ] Only after workload-safety PASS run frozen Coding Benchmark 01 and consider Pi integration

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
