# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Direct MLX has solved the 8B runtime/stability problem on the M1/8 GB reference machine. Qwen3-8B-3bit was safe but did not earn Pi promotion on frozen coding quality. Qwen3-8B-4bit has now passed the 4096-KV smoke with a narrower safety margin; the active gate is the exact frozen T01 workload-safety test.
Checkpoint: `DIRECT_MLX_8B_4BIT_T01_WORKLOAD_001_READY`

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
- Record free disk before/after model acquisitions and large runtime experiments.

Latest observed disk after Qwen3-8B-4bit Smoke 001: **35.329 GiB free**. The post-acquisition snapshot was 36.331 GiB; do not attribute the transient ~1 GiB difference to a specific mechanism without evidence. All verified 3-bit, 4-bit and GGUF artifacts are retained.

# Frozen baseline / prior agent results

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

# Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED

Pinned source commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`.

- 4B Q4 control: pp512 230.85 t/s, tg128 22.33 t/s, minimum free memory 22%.
- Qwen3-8B Q2_K: technically runnable/API-servable but coding delivery 0/100 vs 4B Q4 34.29/100 in Compare 001.
- Qwen3-8B Q3_K_M: NP1 + Q8_0 KV API smoke PASS at 6% free, but exact Coding T01 drove free memory to 4% and triggered the guardrail.

Canonical Q3 boundary:
> **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under llama.cpp.

Do not expose llama.cpp Q3 to Pi.

# Phase 5 — Direct MLX — ACTIVE

## Validated environment

Setup Probe 001 (`20260819-120748`):
- Darwin arm64
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- local MLX compute PASS.

## Qwen3-8B-3bit — runtime success, quality not promoted

Artifact:
- `mlx-community/Qwen3-8B-3bit`
- revision `619ded3`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64
- observed main weight 3.338 GiB.

Safety-valid smoke (`20260819-124440`):
- `max_kv_size=4096`, unquantized KV
- minimum free 23%
- peak swap 1720.75 MB
- generation 24.4160 t/s
- MLX peak memory 3.6676508 GB
- FULL_PASS.

Exact T01 workload (`20260819-124952`):
- delivery `written`
- 15/15 later confirmed by full benchmark
- minimum free 19%
- peak swap 1643.12 MB
- generation 16.52 t/s
- FULL_PASS.

Full Direct MLX Coding Benchmark 001 (`20260819-125647`):
- one loaded model session for T01–T06
- all six generations completed
- minimum free 14%
- peak swap 1683.38 MB
- artifact 38.57/100
- delivery-adjusted 27.86/100
- delivery 2/6
- COMPLETE.

Quality diagnostic:
- T01 clean success: 15/15, 6/6 tests.
- T02 clean delivery: 12.86/15, 6/7 tests.
- T03 protocol failure: valid-looking payload followed by extra fenced JSON.
- T04 protocol failure plus malformed/incorrect content; artifact fixture points are not model-earned delivery credit.
- T05 protocol failure; substantial candidate emitted but no post-hoc salvage permitted.
- T06 protocol failure plus tie-order semantic defect.

Canonical 3-bit interpretation:
> Direct MLX solves resource stability for Qwen3-8B, but the 3-bit profile is not a clear practical coding-quality upgrade. Failures are not only formatting; semantic/instruction defects are also present. Pi integration remains blocked.

Records:
- `research/runtime/direct-mlx-coding-benchmark-001.md`
- `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`

## Qwen3-8B-4bit — Smoke 001 FULL_PASS

Artifact:
- `mlx-community/Qwen3-8B-4bit`
- pinned revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- observed main weight **4.291 GiB**
- local path `results-local/mlx/models/Qwen3-8B-4bit`.

Smoke run `20260819-131009`:
- disk before 40.647 GiB
- snapshot acquisition PASS
- disk after acquisition 36.331 GiB
- SHA PASS
- quantization metadata PASS
- safety preflight 75% free / 1261.50 MB swap
- prompt `Reply only with OK.`
- `max_kv_size=4096`
- unquantized KV
- assistant `OK.`
- prompt 17 tok @ 3.2971 t/s
- generation 3 tok @ 20.8411 t/s
- MLX peak memory **4.683327704 GB**
- peak process RSS 560.484375 MB
- peak swap **2403.31 MB**
- minimum free memory **10%**
- classification **FULL_PASS**
- final observed disk 35.329 GiB.

Record:
`research/runtime/direct-mlx-8b-4bit-smoke-001.md`

Descriptive smoke comparison only:
- 3-bit min free 23% vs 4-bit 10%
- 3-bit peak swap 1720.75 MB vs 4-bit 2403.31 MB
- 3-bit generation 24.4160 t/s vs 4-bit 20.8411 t/s
- 3-bit MLX peak memory 3.6676508 GB vs 4-bit 4.683327704 GB.

Do not treat these deltas as causal estimates of one extra weight bit.

# Current checkpoint — 4-bit T01 workload safety

Checkpoint: `DIRECT_MLX_8B_4BIT_T01_WORKLOAD_001_READY`
Plan: `research/runtime/direct-mlx-8b-4bit-t01-workload-001-plan.md`
Runner: `scripts/direct_mlx_8b_4bit_t01_workload.py`

Frozen condition:
- exact verified Qwen3-8B-4bit artifact
- exact validated MLX environment
- exact Coding Benchmark 01 v1.0.1 T01
- frozen adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- exact adapter prompt envelope
- local/offline inference
- Qwen3 `enable_thinking=False`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- max 2048 generation tokens
- seed 0
- locale-safe swap telemetry
- free memory <5% / swap >5600 MB abort
- one attempt, no retries/repair/salvage/test feedback.

The 4-bit T01 runner is derived from the validated 3-bit T01 runner and refuses to execute if the frozen 3-bit template blob changes. Only model identity/result labels are transformed.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_4bit_t01_workload.py
python3 scripts/direct_mlx_8b_4bit_t01_workload.py
```

No model download is expected.

## Decision after T01

If `FULL_PASS`:
1. freeze 4-bit workload-safety telemetry and delivery evidence;
2. preregister full six-task 4-bit Coding Benchmark 01;
3. only after a COMPLETE full benchmark compare 4-bit vs 3-bit quality and decide on Pi.

If `RESOURCE_FAIL`:
- do not lower guardrails;
- do not reduce `max_kv_size` or quantize KV inside the failed condition;
- diagnose before any separately preregistered rescue.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
