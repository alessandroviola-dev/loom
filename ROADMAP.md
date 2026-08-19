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
- [x] Q2 llama-server smoke FULL_PASS: readiness 5.684 s; API returned `OK`; minimum free memory 6%
- [x] Run frozen Coding Benchmark 01 same-runtime Qwen3 8B Q2 vs Qwen3 4B Q4
- [x] Quality Compare 001: 8B Q2 delivery 0/100 vs 4B Q4 34.29/100; relation `4B_HIGHER`
- [x] Diagnose Q2 failures: HTTP/API/JSON healthy, repeated structured-instruction/delivery failure; Q2 profile not a practical upgrade
- [x] Q3 Auto-Fit Server Smoke 001 VALID FAIL: minimum free memory 4%
- [x] Diagnose default server: auto parallelism resolved to `n_slots=4`, `n_ctx_slot=4096`, `kv_unified=true`
- [x] Preregister and run Q3 Auto-Fit NP1 Server Smoke 001
- [x] Q3 NP1 evidence PASS: `n_slots=1`, `n_ctx_slot=4096`, `kv_unified=false`
- [x] Q3 NP1 still VALID FAIL: peak RSS 2100.44 MB; peak swap 2295.94 MB; minimum free memory 4%; parallelism reduction insufficient
- [x] Record `research/runtime/llama-cpp-8b-q3-autofit-np1-server-smoke-001.md`
- [x] Verify pinned llama.cpp KV flags: `-ctk/--cache-type-k`, `-ctv/--cache-type-v`; Q8_0 supported; default main K/V cache F16/F16
- [x] Preregister next one-variable rescue: keep NP1/context/fit fixed, change only KV F16/F16 -> Q8_0/Q8_0
- [x] Add `research/runtime/llama-cpp-8b-q3-autofit-np1-q8-server-smoke-001-plan.md`
- [x] Add `scripts/llama_cpp_8b_q3_autofit_np1_q8_server_smoke.py`
- [ ] Run Q3 Auto-Fit NP1 Q8 KV Server Smoke 001
- [ ] If Q8 KV FULL_PASS, freeze telemetry then compare Q3 vs 4B Q4 on Coding Benchmark 01 under controlled single-slot settings before Pi
- [ ] If Q8 KV still memory FAIL, move main branch to Direct MLX rather than stacking multiple llama.cpp rescue changes; consider more aggressive KV only as a separately justified later experiment
- [ ] Do not relax Q2 benchmark delivery rules post hoc
- [ ] Do not lower the 5% guardrail or reduce context inside an already-failed condition
- [ ] Do not test ~9B until the useful 8B frontier is characterized

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
