# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp frontier characterized. Phase 5 Direct MLX proves Qwen3-8B can run safely on the M1/8 GB reference machine, but the 3-bit profile did not earn Pi promotion on frozen coding quality. The main branch now tests the same Qwen3-8B family at native MLX 4-bit precision.
Checkpoint: `DIRECT_MLX_8B_4BIT_SMOKE_001_READY`

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
- Record free disk before/after every model acquisition or large runtime experiment.

Latest confirmed disk after Direct MLX Coding Benchmark 001: **40.637 GiB free**.

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

Pinned source commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`.

- 4B Q4 control: pp512 230.85 t/s, tg128 22.33 t/s, minimum free memory 22%.
- Qwen3-8B Q2_K: technically runnable/API-servable but structured coding delivery 0/100 vs 4B Q4 34.29/100 in Compare 001.
- Qwen3-8B Q3_K_M: NP1 + Q8_0 KV smoke PASS at 6% free, but exact Coding T01 drove free memory to 4% and triggered the frozen guardrail.

Canonical Q3 boundary:
> **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under llama.cpp.

Do not expose the llama.cpp Q3 profile to Pi.

# Phase 5 — Direct MLX — ACTIVE

## Validated environment

Setup Probe 001 run `20260819-120748`:
- Darwin arm64
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- tiny local MLX computation PASS.

## Qwen3-8B-3bit — resource success, quality not promoted

Verified model:
- `mlx-community/Qwen3-8B-3bit`
- revision `619ded3`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64
- observed main weight 3.338 GiB.

Safety-valid smoke rerun `20260819-124440`:
- `max_kv_size=4096`, unquantized KV
- output `OK.`
- minimum free memory 23%
- peak swap 1720.75 MB
- FULL_PASS.

Exact T01 Workload Safety 001 run `20260819-124952`:
- exact frozen Coding Benchmark T01 prompt/envelope
- structured delivery `written`
- generation 16.52 t/s
- minimum free memory 19%
- peak swap 1643.12 MB
- FULL_PASS.

Full Direct MLX Coding Benchmark 001 run `20260819-125647`:
- one loaded model session for T01–T06
- all six generations completed
- minimum free memory **14%**
- peak swap **1683.38 MB**
- artifact score **38.57/100**
- delivery-adjusted score **27.86/100**
- structured delivery **2/6**
- classification **COMPLETE**.

## Coding Benchmark 001 quality diagnostic — CLOSED

Record: `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`.

Per-task:
- T01: `written`, **15/15**, 6/6 tests — clean protocol + semantic success.
- T02: `written`, **12.86/15**, 6/7 tests — clean protocol, one semantic edge-case miss.
- T03: delivery FAIL because a valid-looking outer payload was followed by an extra fenced JSON block; no frozen salvage, so 0/15.
- T04: delivery FAIL plus visible malformed generated content; artifact 8.57/15 came from untouched fixture/base state and is not model-earned delivery credit.
- T05: delivery FAIL; substantial candidate emitted but semantic quality is not validated because post-hoc salvage is forbidden.
- T06: delivery FAIL plus visible tie-ordering semantic defect; artifact 2.14/15 from untouched fixture/base state is not model-earned delivery credit.

Canonical interpretation:
> Direct MLX solves the memory/stability problem for Qwen3-8B on this machine, but the 3-bit profile is not a clear practical coding-quality upgrade. Protocol failure dominates delivery, while semantic/instruction defects are also present. Do not reduce this result to "just JSON formatting."

Historical references are descriptive only:
- Ollama/MLX 4B baseline: artifact 40.71, strict 30.00, delivery 3/6.
- llama.cpp 4B Q4 Compare 001: delivery-adjusted 34.29, delivery 4/6.
- Direct MLX 8B 3-bit: delivery-adjusted 27.86, delivery 2/6.

Different runtime/model/quantization conditions prevent causal inference, but the 8B/3-bit result does **not** earn Pi promotion.

Pi integration for 8B/3-bit remains blocked.

# Current checkpoint — Qwen3-8B-4bit Direct MLX smoke

Checkpoint: `DIRECT_MLX_8B_4BIT_SMOKE_001_READY`
Plan: `research/runtime/direct-mlx-8b-4bit-smoke-001-plan.md`
Runner: `scripts/direct_mlx_8b_4bit_smoke.py`

Prospectively selected candidate:
- repo `mlx-community/Qwen3-8B-4bit`
- pinned revision `545dc4251c05440727734bcd94334791f6ab0192`
- MLX quantization 4-bit / group size 64
- published `model.safetensors` ~4.61 GB
- required SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- local destination `results-local/mlx/models/Qwen3-8B-4bit`.

Research motivation:
> Test whether less aggressive weight quantization improves the useful-quality frontier while preserving Direct MLX's strong memory behavior. This is a new same-family profile, not a post-hoc rewrite of the completed 3-bit benchmark.

Frozen smoke condition:
- same validated MLX environment
- local/offline inference after acquisition
- `enable_thinking=False`
- prompt `Reply only with OK.`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- max 16 generated tokens
- seed 0
- locale-safe swap telemetry
- free memory <5% / swap >5600 MB abort
- no retry/rescue.

Storage:
- require >=10 GiB free before first acquisition
- retain all existing verified 3-bit and GGUF artifacts
- verify model SHA + 4-bit/group-size-64 metadata
- record disk before/acquisition-after/final.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_4bit_smoke.py
python3 scripts/direct_mlx_8b_4bit_smoke.py
```

The first run will download the 4-bit model snapshot. Preserve output through `Summary:`.

## Decision after 4-bit smoke

If `FULL_PASS`:
1. freeze the technical/safety result;
2. preregister exact T01 workload-safety under the same 4-bit runtime;
3. only after T01 PASS run the full frozen coding benchmark;
4. compare 4-bit vs 3-bit descriptively before any Pi decision.

If `RESOURCE_FAIL`:
- do not lower guardrails;
- do not reduce `max_kv_size` or quantize KV inside the failed condition;
- diagnose before any separately preregistered rescue.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
