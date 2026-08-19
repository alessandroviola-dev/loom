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
- [x] 8B Q3_K_M Capability 001 VALID FAIL at context 4096 / forced `-ngl -1`: memory free 1%; guardrail triggered
- [x] Resolve Q2 harness chronology: 001/002 invalid, 003 recovered Stage A PASS
- [x] 8B Q2 Stage B 001 FULL_PASS: pp512 103.00 t/s ±0.67; tg128 13.72 t/s ±0.34; peak RSS 2461.17 MB; peak swap 1990.38 MB; minimum free memory 8%
- [x] Freeze `research/runtime/llama-cpp-8b-q2-technical-pass.md`
- [x] Technical conclusion: Qwen3 8B Q2_K is runnable at context 4096 under LOOM safety guardrails
- [x] Server Smoke 001 FULL_PASS: readiness 5.684 s; `/v1/chat/completions` returned `OK`; peak RSS 1729.33 MB; peak swap 1855.12 MB; minimum free memory 6%
- [x] Run frozen Coding Benchmark 01 v1.0.1 same-runtime Qwen3 8B Q2 vs Qwen3 4B Q4
- [x] Quality Compare 001 primary result: 8B Q2 delivery 0/100 vs 4B Q4 34.29/100; delta -34.29; relation `4B_HIGHER`; both profiles COMPLETE
- [x] Inspect persisted per-task failure classes without rerunning inference
- [x] Freeze diagnostic: all 8B requests HTTP 200 / EOS / valid JSON, but Q2 repeatedly treated prompt placeholder `filename` as a literal key; T05 generated code under `filename/value`; no transport/resource defect identified
- [x] Record `research/runtime/llama-cpp-coding-quality-compare-001-diagnostic.md`
- [x] Conclusion: Q2 8B is technically runnable but not a practical upgrade for this structured coding workload
- [x] Preregister Q3 higher-quality rescue via llama.cpp automatic fit / partial-offload policy at context 4096
- [x] Add `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-plan.md`
- [x] Add `scripts/llama_cpp_8b_q3_autofit_server_smoke.py`
- [ ] Run Q3 Auto-Fit Server Smoke 001 with unchanged 5% free-memory / 5600 MB swap guardrails
- [ ] If Q3 auto-fit FULL_PASS, freeze actual fit/offload behavior then compare Q3 vs 4B Q4 on Coding Benchmark 01 before Pi
- [ ] If Q3 auto-fit FAIL, preregister one-variable Q3 KV-cache compression test (Q8_0 first) and/or continue Direct MLX
- [ ] Do not relax Q2 benchmark delivery rules post hoc
- [ ] Do not test ~9B until the 8B quality/usefulness frontier is characterized

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
