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
- [x] Investigate sustained warm memory trajectory 4.4 -> 7.2 GB
- [x] Invocation, context-pressure, multi-turn and cold-replay probes
- [x] Conclude cumulative retained warm high-water is a major contributor; internal mechanism unresolved
- [x] Qwen Code safe mode still 4363 > 4096; deprioritize Qwen Code
- [ ] Add daily-use validation/retry workflow later
- [ ] Test Aider/OpenCode only if later research value justifies it

## Phase 4 — llama.cpp — ACTIVE
- [x] Preregister Phase 4 and pin llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- [x] Install CMake 4.4.2
- [x] Resolve initial LOOM build-target defect
- [x] Setup Probe 003 canonical PASS: Release build, `llama-cli`, `llama-bench`, Metal ON
- [x] Preregister/run 4B GGUF Runtime Control 001
- [x] Record `research/runtime/llama-cpp-4b-control-001.md`
- [x] 4B control PASS: Qwen3 4B Q4_K_M, 2.326 GiB, Metal, pp512 230.85 t/s, tg128 22.33 t/s
- [x] 4B telemetry: peak process RSS 1914.91 MB, peak swap 1097.19 MB, minimum free memory 22%
- [x] Preregister `research/runtime/llama-cpp-8b-q4-001-plan.md`
- [ ] Perform explicit disk-capacity preflight before fresh 8B download
- [ ] Run Qwen3 8B Q4_K_M Capability 001 at context 4096 smoke, then throughput if stable
- [ ] Compare 4B -> 8B throughput/memory scaling
- [ ] Test 8B Q3 variant according to observed headroom
- [ ] Test ~9B Q3/Q2 where feasible
- [ ] Compare partial CPU/GPU offload where useful

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
