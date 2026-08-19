# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp frontier characterized. Phase 5 Direct MLX Qwen3-8B-3bit is technically and workload-safety viable at `max_kv_size=4096`; the full frozen Coding Benchmark 01 has now completed in one continuous MLX session. Resource stability is strong, but structured coding quality is not yet a clear upgrade, so Pi integration remains blocked pending per-task quality diagnosis.
Checkpoint: `DIRECT_MLX_CODING_BENCHMARK_001_QUALITY_DIAGNOSTIC`

## Mission

Study practical local LLM/agent execution on constrained Apple M1 / 8 GB hardware.
Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / production constraints

- Never reset or replace production Pi configuration.
- Controlled experiments use isolated/run-local configuration.
- No new profile reaches Pi until technical, workload-safety and quality gates pass.
- Frozen safety boundary: free memory <5% OR swap >5600 MB abort.
- Process RSS is diagnostic only; system-wide free memory and swap are decisive.
- Never silently delete verified models or canonical results.

# Frozen baseline / prior agent results

## Ollama/MLX 4B baseline

Coding Baseline 001, run `20260818-203156`:
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- generation 16.01 tok/s

Pi Agentic Coding Benchmark 001, run `20260818-214848`:
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6

# Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

4B Q4 control:
- pp512 230.85 t/s
- tg128 22.33 t/s
- minimum free memory 22%

Qwen3-8B Q2_K:
- technically runnable/API-servable;
- coding delivery 0/100 vs 4B Q4 34.29/100 under Compare 001;
- structured delivery degraded;
- not established as a practical upgrade.

Qwen3-8B Q3_K_M:
- NP1 + Q8_0 KV API smoke PASS at 6% free;
- first real Coding T01 drove free memory to 4% and triggered guardrail;
- canonical classification: **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096.

Compare 002 does not establish intrinsic 4B>Q3 quality because Q3 did not complete. Do not expose this llama.cpp profile to Pi.

# Phase 5 — Direct MLX — ACTIVE

## Setup / verified model

Setup Probe 001 run `20260819-120748`:
- Darwin arm64
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- tiny MLX compute PASS.

Verified model:
- `mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- local `model.safetensors`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`: PASS
- observed weight 3.338 GiB
- quantization metadata 3-bit / group size 64 PASS.

## Smoke / T01 workload safety

Safety-valid smoke rerun `20260819-124440`:
- `max_kv_size=4096`, unquantized KV
- output `OK.`
- peak swap 1720.75 MB
- minimum free memory 23%
- FULL_PASS.

T01 Workload Safety 001 run `20260819-124952`:
- exact frozen Coding Benchmark T01 prompt/envelope
- prompt 276 tok @ 57.1148 tok/s
- generation 86 tok @ 16.5166 tok/s
- MLX peak memory 3.959549116 GB
- structured delivery `written`
- peak swap 1643.12 MB
- minimum free memory 19%
- FULL_PASS.

This cleared the exact real-workload gate where llama.cpp Q3 failed.

## Direct MLX Coding Benchmark 001 — COMPLETE

Run `20260819-125647`.
Plan: `research/runtime/direct-mlx-coding-benchmark-001-plan.md`
Result: `research/runtime/direct-mlx-coding-benchmark-001.md`
Runner: `scripts/direct_mlx_coding_benchmark_001.py`

Frozen invariants:
- Coding Benchmark 01 v1.0.1, T01–T06
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`
- exact adapter `build_prompt()` / `extract_files()`
- isolated benchmark working tree
- one attempt per task
- no retries, repair, salvage, re-prompt or test feedback
- one loaded MLX model session for all six tasks
- local/offline Direct MLX
- Qwen3 `enable_thinking=False`
- `max_kv_size=4096`
- unquantized KV
- max 2048 generated tokens per task
- free memory <5% / swap >5600 MB abort.

Observed runtime/safety:
- disk before 40.638 GiB
- safety preflight 75% free / 1339.00 MB swap
- all six generations completed sequentially
- peak process RSS 594.546875 MB
- peak swap **1683.38 MB**
- minimum free memory **14%**
- disk after 40.637 GiB
- classification **COMPLETE**.

Per-task delivery / generation:
- T01 `written`, prompt 276, gen 86, 16.2289 t/s
- T02 `written`, prompt 374, gen 125, 16.4403 t/s
- T03 `failed`, prompt 359, gen 117, 16.4839 t/s
- T04 `failed`, prompt 486, gen 237, 16.2571 t/s
- T05 `failed`, prompt 501, gen 244, 16.2318 t/s
- T06 `failed`, prompt 331, gen 255, 16.3910 t/s

Frozen quality result:
- artifact score **38.57/100**
- delivery-adjusted score **27.86/100**
- structured delivery **2/6**
- primary preregistered metric: delivery-adjusted score.

Canonical conclusion:
> Direct MLX solves the resource/stability problem for this 8B/3-bit profile: six heterogeneous coding tasks complete in one loaded session with substantial safety headroom. However, the full frozen quality result is not yet evidence of a clear practical upgrade because delivery-adjusted quality is 27.86/100 and only 2/6 outputs satisfy the frozen structured-delivery contract.

Historical 4B/Q2 results may be compared descriptively only; runtimes/model formats differ and raw score gaps are not causal evidence.

# Current checkpoint — quality diagnostic before Pi

Checkpoint: `DIRECT_MLX_CODING_BENCHMARK_001_QUALITY_DIAGNOSTIC`
Inspector: `scripts/inspect_direct_mlx_coding_benchmark_001.py`
Local run:
`results-local/mlx/coding-benchmark-001/20260819-125647`

Required diagnostic:
- exact adapter error for T03–T06;
- raw output prefix and JSON/top-level/file-key structure;
- frozen scorer points and tests passed per task;
- delivery-adjusted contribution per task;
- distinguish protocol/delivery failures from semantic/code failures and untouched-fixture artifact points.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_direct_mlx_coding_benchmark_001.py
python3 scripts/inspect_direct_mlx_coding_benchmark_001.py \
  results-local/mlx/coding-benchmark-001/20260819-125647
```

No model is launched by this inspector.

## Decision after diagnostic

- If failures are predominantly structured-output/protocol failures, preserve them as genuine quality evidence; do not alter prompt/parser post-hoc. Decide whether an isolated Pi agentic test is still scientifically useful as a separate question, not as an assumed upgrade.
- If semantic/code quality is also weak, do not promote the 8B profile to Pi as the main candidate; proceed to the next Phase 5/6 research branch.
- Do not invent a post-hoc threshold or rescue score.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
