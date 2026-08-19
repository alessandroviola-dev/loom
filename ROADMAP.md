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

## Phase 4 — llama.cpp — ACTIVE
- [x] Pin llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- [x] Install CMake 4.4.2 and validate Release/Metal build
- [x] Setup Probe 003 canonical PASS: `llama-cli`, `llama-bench`, Metal ON
- [x] 4B Q4_K_M Runtime Control 001 PASS
- [x] 4B: 2.326 GiB; pp512 230.85 t/s; tg128 22.33 t/s; peak RSS 1914.91 MB; peak swap 1097.19 MB; minimum free memory 22%
- [x] 8B Q4_K_M Capability 001 VALID FAIL at context 4096: memory free 1%; guardrail triggered
- [x] 8B Q3_K_M Capability 001 VALID FAIL at context 4096: memory free 1%; guardrail triggered
- [x] Q2 Capability 001: model loaded/began inference but INVALID because CLI stayed interactive
- [x] Q2 Capability 002: single-turn completed with 19% minimum free memory, but INVALID because Stage A parser required optional literal log strings
- [x] Record `research/runtime/llama-cpp-8b-q2-002-invalid.md`
- [x] Preregister `research/runtime/llama-cpp-8b-q2-003-plan.md`
- [x] Add `scripts/llama_cpp_8b_q2_003.py` with corrected deterministic Stage A evidence validation
- [ ] Run Q2 Capability 003 using the existing SHA256-verified model
- [ ] If Q2 FULL_PASS, test actual quality/usefulness before calling it a practical 8B upgrade
- [ ] If Q2 Stage A genuinely FAILs, stop descending quantizations and test a separately frozen partial-offload/context-memory strategy
- [ ] Test ~9B only if the 8B frontier provides sufficient evidence/headroom

## Phase 5 — Direct MLX
- [ ] Set up direct MLX environment
- [ ] Run equivalent model directly
- [ ] Compare throughput, memory pressure and context scaling

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
