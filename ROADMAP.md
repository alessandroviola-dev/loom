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
- [x] 3-bit Smoke FULL_PASS (`20260819-124440`): min free 23%, peak swap 1720.75 MB
- [x] 3-bit exact T01 FULL_PASS (`20260819-124952`): min free 19%, peak swap 1643.12 MB, delivery written
- [x] 3-bit full Coding Benchmark 001 COMPLETE (`20260819-125647`)
- [x] 3-bit full-session resource stability PASS: min free 14%, peak swap 1683.38 MB
- [x] Freeze 3-bit quality: artifact 38.57/100, delivery-adjusted 27.86/100, delivery 2/6
- [x] Diagnose 3-bit quality; failures are not only formatting
- [x] Do not promote Qwen3-8B-3bit to Pi on current quality evidence
- [x] Select/verify `mlx-community/Qwen3-8B-4bit`
- [x] 4-bit Smoke 001 FULL_PASS (`20260819-131009`): min free 10%, peak swap 2403.31 MB, MLX peak 4.6833 GB
- [x] 4-bit exact T01 Workload Safety 001 FULL_PASS (`20260819-132612`): preflight 74% free, min free 6%, peak swap 2470.31 MB
- [x] Preregister full 4-bit six-task Coding Benchmark 001
- [x] Freeze prospective 4-bit Pi gate before result: `COMPLETE` + delivery-adjusted >27.86 + delivery >2/6
- [x] Run original full Qwen3-8B-4bit Coding Benchmark 001 (`20260819-133144`)
- [x] Original 4-bit full run hits free-memory guardrail during T01: preflight 56%, min free 4%, peak swap 3028.25 MB
- [x] Classify original 4-bit full run `PARTIAL_RESOURCE_FAIL`; no valid aggregate quality ordering
- [x] Diagnose persisted 4-bit timeline/progress/child state; no model rerun
- [x] Confirm no T01 result persisted; child terminated at 17.913 s while T01 running
- [x] Confirm max swap occurred earlier than min-free sample and swap was decreasing at 4% breach
- [x] Identify material host-state difference: failed full preflight 56% free vs successful 4-bit T01 74% and completed 3-bit full 75%
- [x] Freeze `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001-resource-diagnostic.md`
- [x] Preregister exactly one host-state-controlled 4-bit full replication before any KV rescue
- [x] Add `research/runtime/direct-mlx-8b-4bit-hoststate-replication-001-plan.md`
- [x] Add `scripts/direct_mlx_8b_4bit_hoststate_replication_001.py`
- [ ] Run host-state wrapper; require 3 consecutive prelaunch samples >=70% free memory
- [ ] If `HOST_STATE_NOT_READY`, do not launch MLX and do not count as model failure; retry only after naturally freeing host resources
- [ ] If controlled replication launches and resource-fails again, close 4-bit / 4096 / unquantized-KV full-session branch with no further same-profile repeats
- [ ] If controlled replication completes, retain both original fail and replication; apply frozen quality gate (>27.86 delivery-adjusted and >2/6 delivery) before any Pi validation
- [ ] Do not automate memory/swap purge, lower guardrails, change KV/context, prompts/parser/scorer, or retry individual tasks
- [ ] Pi remains blocked until technical + workload + prospective quality gates all pass

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
