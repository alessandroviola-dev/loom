# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp frontier characterized. Phase 5 Direct MLX Qwen3-8B-3bit has now passed both the safety-valid 4096-KV smoke and the exact frozen Coding Benchmark T01 real-workload safety gate. The active checkpoint is the full frozen Coding Benchmark 01 quality run before any Pi integration.
Checkpoint: `DIRECT_MLX_CODING_BENCHMARK_001_READY`

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

Compare 002 therefore does not establish intrinsic 4B>Q3 quality because Q3 did not complete. Do not expose this llama.cpp profile to Pi.

# Phase 5 — Direct MLX — ACTIVE

## Setup Probe 001 — PASS

Run `20260819-120748`:
- Darwin arm64
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- tiny MLX compute PASS.

## Verified model

`mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- local `model.safetensors`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`: PASS
- observed weight 3.338 GiB
- quantization metadata: 3-bit / group size 64 PASS
- local path `results-local/mlx/models/Qwen3-8B-3bit`

## Direct MLX Smoke 001 — safety-valid FULL_PASS

Initial run `20260819-121656` generated successfully but swap parsing failed because macOS emitted locale decimal commas. Root cause was telemetry-only.

Safety-valid telemetry-fix rerun `20260819-124440`:
- local/offline Direct MLX
- `enable_thinking=False`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- output `OK.`
- prompt 17 tok @ 11.0758 t/s
- generation 3 tok @ 24.4160 t/s
- MLX peak memory 3.6676508 GB
- peak swap **1720.75 MB**
- minimum free memory **23%**
- FULL_PASS

Record:
`research/runtime/direct-mlx-8b-3bit-smoke-001-swapfix-rerun.md`

## Direct MLX T01 Workload Safety 001 — FULL_PASS

Run `20260819-124952`.
Plan: `research/runtime/direct-mlx-8b-3bit-t01-workload-001-plan.md`
Result: `research/runtime/direct-mlx-8b-3bit-t01-workload-001.md`
Runner: `scripts/direct_mlx_8b_3bit_t01_workload.py`

Frozen workload:
- exact Coding Benchmark 01 v1.0.1 T01
- exact frozen adapter `build_prompt()` envelope
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- no retry, repair, salvage or test feedback
- max generation 2048
- `max_kv_size=4096`
- unquantized KV
- same 5% / 5600 MB guardrails

Observed:
- disk before 40.634 GiB
- environment/model/adapter preflights PASS
- safety preflight 75% free / 1266.38 MB swap
- T01 child exit 0
- T01 output 372 chars
- prompt 276 tok @ **57.1148 tok/s**
- generation 86 tok @ **16.5166 tok/s**
- MLX peak memory **3.959549116 GB**
- finish `stop`
- structured delivery **written**
- peak process RSS 403.25 MB
- peak swap **1643.12 MB**
- minimum free memory **19%**
- classification **FULL_PASS**
- disk after 40.633 GiB

Canonical conclusion:
> The verified Direct MLX Qwen3-8B 3-bit profile completed the exact frozen T01 coding workload at `max_kv_size=4096` with unquantized KV while remaining comfortably inside both LOOM safety guardrails. It also satisfied the frozen structured-output envelope. This clears the exact real-workload gate where the Q3/llama.cpp profile failed.

T01 correctness was intentionally not scored by the safety probe; aggregate quality is the next gate.

# Current checkpoint — Direct MLX Coding Benchmark 001

Checkpoint: `DIRECT_MLX_CODING_BENCHMARK_001_READY`
Plan: `research/runtime/direct-mlx-coding-benchmark-001-plan.md`
Runner: `scripts/direct_mlx_coding_benchmark_001.py`

Research question:
> Can the workload-safe Direct MLX 8B/3-bit profile complete all six frozen Coding Benchmark 01 tasks under the frozen safety boundary, and what delivery-adjusted coding quality does it achieve?

Frozen benchmark invariants:
- Coding Benchmark 01 v1.0.1, T01–T06
- adapter `scripts/ollama_single_shot.py`
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer `benchmarks/coding/v1/runner.py`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`
- exact adapter `build_prompt()` and `extract_files()`
- isolated copy of benchmark tree
- one attempt per task
- no retry, repair, salvage, re-prompt or test feedback

Direct MLX runtime remains:
- verified local 8B/3-bit model
- pinned isolated environment
- local/offline inference
- Qwen3 `enable_thinking=False`
- direct `stream_generate`
- one model load for the full six-task session
- `max_kv_size=4096`
- unquantized KV
- max 2048 generated tokens per task
- seed 0 at session start
- locale-safe swap telemetry
- free memory <5% / swap >5600 MB abort

The single loaded model session is deliberate: it exposes retained-memory behavior across heterogeneous tasks instead of hiding it with six cold restarts.

Each task result is persisted before moving to the next task, so a later resource abort retains diagnostic evidence from earlier completed tasks.

Primary quality metric: delivery-adjusted score.
Secondary: artifact score, written tasks / 6, per-task score/protocol behavior, throughput and telemetry.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_coding_benchmark_001.py
python3 scripts/direct_mlx_coding_benchmark_001.py
```

No model download is expected.

Preserve output from `LOOM Direct MLX Coding Benchmark 001` through `Summary:`.

## Decision after full benchmark

If `COMPLETE`:
1. freeze full quality/delivery result;
2. compare descriptively with the established 4B and llama.cpp evidence without claiming bit-identical equivalence;
3. decide whether Direct MLX 8B has earned isolated Pi integration/agentic validation.

If partial due resource/telemetry/runtime failure:
- do not infer a clean aggregate quality ordering;
- diagnose exact mechanism before changing runtime parameters.

Do not lower guardrails, change KV cap/precision, alter prompts/parsers/scorer, or retry individual tasks inside this frozen condition.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
