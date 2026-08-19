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
- [x] Coding Quality Compare 001: 8B Q2 delivery 0/100 vs 4B Q4 34.29/100; relation `4B_HIGHER`
- [x] Diagnose Q2: transport healthy but structured delivery degraded; Q2 not a practical upgrade on the frozen workload
- [x] Q3 Auto-Fit Server Smoke 001 VALID FAIL: minimum free memory 4%
- [x] Diagnose auto server parallelism: `n_slots=4`, `n_ctx_slot=4096`, `kv_unified=true`
- [x] Q3 Auto-Fit NP1 Server Smoke 001: `n_slots=1` verified but still VALID FAIL at 4% free
- [x] Verify KV controls: `-ctk/--cache-type-k`, `-ctv/--cache-type-v`; Q8_0 supported; default K/V F16/F16
- [x] Q3 Auto-Fit NP1 Q8 KV Server Smoke 001 FULL_PASS, run `20260819-113658`
- [x] Q3 Q8 result: readiness 8.756 s; API `OK`; peak RSS 2246.75 MB; peak swap 2113.88 MB; minimum free memory 6%; `n_slots=1` and Q8 command evidence PASS
- [x] Freeze `research/runtime/llama-cpp-8b-q3-autofit-np1-q8-server-smoke-001.md`
- [x] Preregister Coding Quality Compare 002: Qwen3 8B Q3_K_M vs Qwen3 4B Q4_K_M
- [x] Freeze common runtime for both Compare 002 profiles: context 4096, `-np 1`, FA auto, auto-fit target 1024, Q8_0 K/V KV cache, no forced `-ngl -1`
- [x] Add `research/runtime/llama-cpp-coding-quality-compare-002-plan.md`
- [x] First Compare 002 invocation stopped before model launch: INVALID_HARNESS due fragile escaped-newline template needle
- [x] Record `research/runtime/llama-cpp-coding-quality-compare-002-invalid-harness-001.md`
- [x] Fix Compare 002 transformer using smaller unique replacements; preserve all preregistered runtime/benchmark invariants
- [ ] Run corrected Coding Quality Compare 002
- [ ] If Q3 quality is higher and both profiles COMPLETE, freeze result then preregister isolated Pi integration/agentic validation
- [ ] If 4B is higher/tied, close the current llama.cpp 8B frontier and move the main branch to Direct MLX
- [ ] If comparison is partial/resource-failed, diagnose persisted artifacts before changing any parameter
- [ ] Do not relax benchmark delivery rules post hoc
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
