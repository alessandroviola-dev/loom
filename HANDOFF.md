# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Direct MLX has established a safe 8B frontier on the Apple M1 / 8 GB reference machine. Qwen3-8B-3bit is full-session stable but did not earn Pi promotion on frozen coding quality. Qwen3-8B-4bit has passed both smoke and exact T01 workload safety at `max_kv_size=4096`, but T01 reached only 6% free memory. The active gate is the full six-task 4-bit coding benchmark in one continuous model session.
Checkpoint: `DIRECT_MLX_8B_4BIT_CODING_BENCHMARK_001_READY`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.
Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Frozen safety / production constraints

- Never reset or replace production Pi configuration.
- Controlled experiments use isolated/run-local configuration.
- No new profile reaches Pi until technical, workload-safety and quality gates pass.
- Frozen safety abort: free memory <5% OR swap >5600 MB.
- Process RSS is diagnostic only; system-wide free memory and swap drive safety decisions.
- Never silently delete verified models or canonical results.
- Record free disk before/after model acquisition and large runtime experiments.

Latest observed disk after 4-bit T01: **35.354 GiB free**. Verified 3-bit, 4-bit and GGUF artifacts are retained.

# Frozen prior results

## Ollama/MLX 4B baseline

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- generation 16.01 tok/s

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6

## Phase 4 llama.cpp boundary

Pinned llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`.

- 4B Q4 control: pp512 230.85 t/s, tg128 22.33 t/s, min free 22%.
- 8B Q2: technically runnable/API-servable but frozen coding delivery 0/100 vs 4B Q4 34.29/100.
- 8B Q3 NP1 + Q8_0 KV: API smoke PASS at 6% free, but exact Coding T01 hit 4% free and guardrail abort.

Canonical Q3 boundary:
> **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under llama.cpp.

Do not expose llama.cpp Q3 to Pi.

# Phase 5 — Direct MLX — ACTIVE

Validated environment:
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- Darwin arm64 / local MLX compute PASS.

## Qwen3-8B-3bit — resource success, quality not promoted

Artifact:
- `mlx-community/Qwen3-8B-3bit`
- revision `619ded3`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64
- observed main weight 3.338 GiB.

Safety-valid smoke (`20260819-124440`): min free 23%, peak swap 1720.75 MB, FULL_PASS.

Exact T01 (`20260819-124952`): min free 19%, peak swap 1643.12 MB, structured delivery `written`, FULL_PASS.

Full Coding Benchmark 001 (`20260819-125647`):
- one loaded model session T01–T06
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57/100
- delivery-adjusted 27.86/100
- delivery 2/6
- COMPLETE.

Diagnostic:
- T01 15/15 clean success.
- T02 12.86/15, 6/7 tests.
- T03 protocol fail from extra fenced JSON.
- T04 protocol fail plus malformed/incorrect content.
- T05 protocol fail; candidate emitted but no post-hoc salvage.
- T06 protocol fail plus tie-order semantic defect.

Conclusion:
> Direct MLX solves resource stability for Qwen3-8B, but the 3-bit profile is not a clear practical coding-quality upgrade. Pi remains blocked.

Records:
- `research/runtime/direct-mlx-coding-benchmark-001.md`
- `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`

## Qwen3-8B-4bit — smoke PASS

Artifact:
- `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- observed main weight 4.291 GiB
- local path `results-local/mlx/models/Qwen3-8B-4bit`.

Smoke `20260819-131009`:
- `max_kv_size=4096`, unquantized KV
- assistant `OK.`
- generation 20.8411 t/s
- MLX peak memory 4.683327704 GB
- peak swap 2403.31 MB
- minimum free memory 10%
- FULL_PASS.

Record: `research/runtime/direct-mlx-8b-4bit-smoke-001.md`.

## Qwen3-8B-4bit — exact T01 FULL_PASS

Run `20260819-132612`.
Plan: `research/runtime/direct-mlx-8b-4bit-t01-workload-001-plan.md`
Result: `research/runtime/direct-mlx-8b-4bit-t01-workload-001.md`
Runner: `scripts/direct_mlx_8b_4bit_t01_workload.py`

Frozen condition:
- exact Coding Benchmark 01 v1.0.1 T01 / frozen adapter
- local/offline Direct MLX
- `enable_thinking=False`
- `max_kv_size=4096`
- unquantized KV
- max generation 2048
- seed 0
- one attempt, no retry/repair/salvage/test feedback
- unchanged 5% / 5600 MB guardrails.

Observed:
- disk before/after 35.354 GiB
- safety preflight 74% free / 1395.25 MB swap
- generation exit 0
- output 421 chars
- prompt 276 tok @ 35.2422 t/s
- generation 101 tok @ 13.9275 t/s
- MLX peak memory 4.981664948 GB
- structured delivery `written`
- peak process RSS 558.921875 MB
- peak swap **2470.31 MB**
- minimum free memory **6%**
- classification **FULL_PASS**.

Canonical interpretation:
> The 4-bit profile clears the exact real T01 gate but only narrowly on free memory: 6% minimum, one percentage point above the frozen 5% threshold. This authorizes the full benchmark without authorizing any runtime relaxation.

Descriptive T01 comparison, 3-bit vs 4-bit:
- min free 19% vs 6%
- peak swap 1643.12 vs 2470.31 MB
- MLX peak memory 3.9595 vs 4.9817 GB
- generation 16.5166 vs 13.9275 t/s
- delivery `written` for both.

Do not interpret these as a causal estimate of weight precision.

# Current checkpoint — 4-bit full Coding Benchmark 001

Checkpoint: `DIRECT_MLX_8B_4BIT_CODING_BENCHMARK_001_READY`
Plan: `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001-plan.md`
Runner: `scripts/direct_mlx_8b_4bit_coding_benchmark_001.py`

The runner is a frozen transform of validated 3-bit full benchmark blob `01b00d604026affff4bad0d599a3159faaf786ae` and changes only model identity and result labels/directories.

Frozen full-run condition:
- exact 4-bit artifact and pinned MLX environment
- exact Coding Benchmark 01 v1.0.1 T01–T06
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`
- exact prompts/parser/scorer
- one loaded model session for all six tasks
- local/offline, non-thinking
- `max_kv_size=4096`, unquantized KV
- max 2048 generation tokens/task
- seed 0
- no retry/repair/salvage/test feedback
- free <5% / swap >5600 MB abort.

Prospectively frozen quality gate versus same-runtime 3-bit:
- 3-bit reference delivery-adjusted: 27.86/100
- 3-bit structured delivery: 2/6
- 4-bit becomes eligible for later isolated Pi validation only if `COMPLETE`, delivery-adjusted **>27.86**, and delivery count **>2/6**.
- This gate does not by itself establish a daily-use upgrade.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_4bit_coding_benchmark_001.py
python3 scripts/direct_mlx_8b_4bit_coding_benchmark_001.py
```

No model download is expected. Preserve output through `Summary:`.

## Decision after full 4-bit run

If `COMPLETE`, freeze quality/safety and apply the prospectively frozen gate above before any Pi experiment.

If resource/telemetry/runtime partial, do not infer a clean quality ordering. Diagnose before changing any runtime parameter. Do not lower guardrails, reduce `max_kv_size`, quantize KV, alter prompts/parser/scorer or retry tasks inside this condition.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
