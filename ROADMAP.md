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
- [x] Original full 4-bit benchmark (`20260819-133144`) resource-fails during T01: preflight 56%, min free 4%
- [x] Diagnose original failure and identify host-state mismatch
- [x] Preregister exactly one >=70%-free host-controlled replication
- [x] Controlled replication launches (`20260819-134012`) from 72–74% free
- [x] Controlled replication completes/persists T01–T03 and enters T04
- [x] Controlled replication still hits free-memory guardrail: min free 4%, peak swap 2879.38 MB
- [x] Close exact 4-bit / `max_kv_size=4096` / unquantized-KV continuous profile as workload RESOURCE FAIL
- [x] Prohibit further identical replications
- [x] Diagnose controlled replication read-only
- [x] Confirm T01–T03 complete with `written` delivery; T04 aborts at 4% free
- [x] Confirm pressure repeatedly approaches 5–7% during T02–T04; final breach is free-memory, not swap
- [x] Freeze `research/runtime/direct-mlx-8b-4bit-hoststate-replication-001-diagnostic.md`
- [x] Justify exactly one low-confound KV8 rescue
- [x] Preregister `research/runtime/direct-mlx-8b-4bit-kv8-rescue-001-plan.md`
- [x] Add `scripts/direct_mlx_8b_4bit_kv8_rescue_001.py`
- [x] Freeze KV rescue policy: `kv_bits=8`, `kv_group_size=64`, `quantized_kv_start=0`, `max_kv_size=4096` unchanged
- [x] Preserve >=70% host-state launch gate and 5%/5600 MB runtime guardrails
- [ ] Run Direct MLX 8B 4-bit KV8 Rescue 001
- [ ] If `HOST_STATE_NOT_READY`, do not count as model failure; retry launch only after naturally freeing host resources
- [ ] If KV8 rescue `PARTIAL_RESOURCE_FAIL`, close 4-bit branch with no KV6/KV4/context rescue ladder
- [ ] If KV8 rescue `COMPLETE`, apply frozen quality gate: delivery-adjusted >27.86 and delivery >2/6
- [ ] Only if both quality dimensions pass consider separately preregistered isolated Pi validation
- [ ] Pi remains blocked until technical + workload + prospective quality gates all pass
- [ ] Do not lower guardrails, change context, prompts/parser/scorer, or retry individual benchmark tasks

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
