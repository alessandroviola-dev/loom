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
- [x] 4B Q4_K_M Runtime Control 001 PASS: pp512 230.85 t/s; tg128 22.33 t/s; minimum free memory 22%
- [x] 8B Q4_K_M Capability 001 VALID FAIL at context 4096: memory free 1%; guardrail triggered
- [x] 8B Q3_K_M Capability 001 VALID FAIL at context 4096: memory free 1%; guardrail triggered
- [x] Resolve Q2 harness chronology: 001/002 invalid, 003 recovered Stage A PASS
- [x] 8B Q2 Stage B 001 FULL_PASS: pp512 103.00 t/s ±0.67; tg128 13.72 t/s ±0.34; peak RSS 2461.17 MB; peak swap 1990.38 MB; minimum free memory 8%
- [x] Freeze `research/runtime/llama-cpp-8b-q2-technical-pass.md`
- [x] Technical conclusion: Qwen3 8B Q2_K is runnable at context 4096 under LOOM safety guardrails
- [x] Run 8B Q2 llama-server smoke
- [x] Server Smoke 001 FULL_PASS: readiness 5.684 s; `/v1/chat/completions` returned `OK`; peak RSS 1729.33 MB; peak swap 1855.12 MB; minimum free memory 6%
- [x] Record `research/runtime/llama-cpp-8b-q2-server-smoke-001.md`
- [x] Preregister `research/runtime/llama-cpp-coding-quality-compare-001-plan.md`
- [x] Add `scripts/llama_cpp_coding_quality_compare.py`
- [ ] Run frozen Coding Benchmark 01 v1.0.1: same-runtime Qwen3 8B Q2 vs Qwen3 4B Q4
- [ ] If 8B Q2 scores higher, run controlled Pi/agent compatibility smoke through llama-server
- [ ] If 8B Q2 is equal/lower, do not call it a practical upgrade; investigate higher-quality memory strategy (e.g. partial offload Q3/Q4) and/or Direct MLX
- [ ] Test ~9B only after the 8B quality/usefulness frontier is characterized

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
