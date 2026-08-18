# LOOM Roadmap

## Phase 0 — Project foundation
- [x] Choose project name: LOOM
- [x] Define research mission
- [x] Define handoff discipline
- [x] Create private GitHub repository `Ilcoach/loom`
- [x] Push initial project structure

## Phase 1 — Baseline
- [x] Update Ollama
- [x] Install Qwen 3.5 4B MLX
- [x] Confirm MLX runner
- [x] Confirm 100% GPU execution
- [x] Measure initial generation throughput
- [x] Compare memory state with model ON/OFF
- [ ] Repeat throughput test to validate prompt-processing measurement

## Phase 2 — Benchmark framework
- [x] Define Coding Benchmark 01 v1.0.0
- [x] Validate and freeze Coding Benchmark 01
- [ ] Define reasoning benchmark
- [x] Define coding measurement runner
- [x] Define coding scoring rubric
- [x] Define machine-readable coding result format
- [x] Build Ollama single-shot benchmark adapter
- [ ] Run Qwen 3.5 4B MLX on Coding Benchmark 01

## Phase 3 — Local coding agent
- [ ] Select agent layer
- [ ] Connect to Ollama
- [ ] Read repository files
- [ ] Modify code
- [ ] Execute commands/tests safely
- [ ] Benchmark end-to-end agent tasks

## Phase 4 — llama.cpp
- [ ] Install/build optimized Apple Silicon version
- [ ] Test 7B/8B Q4
- [ ] Test Q3 variants
- [ ] Test ~9B Q3/Q2 where feasible
- [ ] Compare CPU/GPU offload strategies

## Phase 5 — Direct MLX
- [ ] Set up MLX environment
- [ ] Run equivalent model directly
- [ ] Compare throughput
- [ ] Compare memory pressure
- [ ] Compare context scaling

## Phase 6 — Colibrì / SSD streaming / MoE
- [ ] Install Colibrì
- [ ] Identify 8 GB-compatible candidates
- [ ] Measure resident memory vs disk traffic
- [ ] Test practical throughput
- [ ] Determine largest useful model

## Phase 7 — Extended runtime research
- [ ] Evaluate new Apple Silicon runtimes
- [ ] Test only if evidence suggests material advantage

## Phase 8 — Synthesis
- [ ] Daily-use profile
- [ ] Maximum-capability profile
- [ ] Experimental large-model profile
- [ ] Publish research findings when ready
