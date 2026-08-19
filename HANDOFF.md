# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Direct MLX established a practical 8B runtime frontier on Apple M1 / 8 GB. Qwen3-8B-3bit is full-session stable but did not earn Pi promotion on frozen coding quality. Qwen3-8B-4bit passed smoke and standalone T01 only narrowly, then the preregistered continuous six-task benchmark hit the frozen free-memory guardrail during T01. No valid 4-bit aggregate quality result exists.
Checkpoint: `DIRECT_MLX_8B_4BIT_CODING_BENCHMARK_001_RESOURCE_DIAGNOSTIC`

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
- Record free disk before/after model acquisitions and large runtime experiments.
- Do not lower guardrails or alter a failed frozen condition post-hoc.

Latest observed disk after 4-bit full benchmark partial run: **35.338 GiB free**. Verified 3-bit, 4-bit and GGUF artifacts are retained.

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

## Phase 4 — llama.cpp boundary

Pinned commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`.

- 4B Q4 control: pp512 230.85 t/s, tg128 22.33 t/s, min free 22%.
- 8B Q2: technically runnable/API-servable but coding delivery 0/100 vs 4B Q4 34.29/100 in Compare 001.
- 8B Q3 NP1 + Q8_0 KV: API smoke PASS at 6% free; exact Coding T01 hit 4% free and guardrail abort.

Canonical Q3 boundary:
> **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under llama.cpp.

Do not expose llama.cpp Q3 to Pi.

# Phase 5 — Direct MLX

Validated environment:
- `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- Darwin arm64 / local MLX compute PASS.

## Qwen3-8B-3bit — full-session stable, quality not promoted

Artifact:
- `mlx-community/Qwen3-8B-3bit`
- revision `619ded3`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64
- observed main weight 3.338 GiB.

Safety-valid smoke (`20260819-124440`):
- `max_kv_size=4096`, unquantized KV
- min free 23%
- peak swap 1720.75 MB
- FULL_PASS.

Exact T01 (`20260819-124952`):
- min free 19%
- peak swap 1643.12 MB
- delivery `written`
- FULL_PASS.

Full Direct MLX Coding Benchmark 001 (`20260819-125647`):
- one loaded model session T01–T06
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57/100
- delivery-adjusted 27.86/100
- structured delivery 2/6
- COMPLETE.

Diagnostic:
- T01 15/15 clean success.
- T02 12.86/15, 6/7 tests.
- T03 protocol fail from extra fenced JSON.
- T04 protocol fail plus malformed/incorrect content.
- T05 protocol fail; substantial candidate emitted but no post-hoc salvage.
- T06 protocol fail plus tie-order semantic defect.

Conclusion:
> Direct MLX solves resource stability for Qwen3-8B, but the 3-bit profile is not a clear practical coding-quality upgrade. Pi remains blocked.

Records:
- `research/runtime/direct-mlx-coding-benchmark-001.md`
- `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`

## Qwen3-8B-4bit — smoke PASS, standalone T01 PASS, continuous benchmark RESOURCE FAIL

Artifact:
- `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- observed main weight 4.291 GiB.

Smoke `20260819-131009`:
- `max_kv_size=4096`, unquantized KV
- assistant `OK.`
- generation 20.8411 t/s
- MLX peak memory 4.683327704 GB
- peak swap 2403.31 MB
- min free 10%
- FULL_PASS.

Standalone exact T01 `20260819-132612`:
- prompt 276 tok @ 35.2422 t/s
- generation 101 tok @ 13.9275 t/s
- MLX peak memory 4.981664948 GB
- delivery `written`
- peak swap 2470.31 MB
- min free **6%**
- FULL_PASS.

### Full 4-bit Coding Benchmark 001 — PARTIAL_RESOURCE_FAIL

Run `20260819-133144`.
Plan: `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001-plan.md`
Result: `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001.md`
Runner: `scripts/direct_mlx_8b_4bit_coding_benchmark_001.py`

Frozen condition:
- exact Coding Benchmark 01 v1.0.1 T01–T06
- exact adapter/scorer blobs
- one loaded Direct MLX model session
- local/offline, non-thinking
- `max_kv_size=4096`
- unquantized KV
- max 2048 tokens/task
- seed 0
- no retry/repair/salvage/test feedback
- free <5% / swap >5600 MB abort.

Preflight:
- disk before 36.347 GiB
- environment/model/adapter/scorer/benchmark/prompts PASS
- 56% free / 948.75 MB swap.

Observed:
- session reached `[1/6] T01 running...`
- peak process RSS 459.453125 MB
- peak swap **3028.25 MB**
- minimum free memory **4%**
- guardrail abort
- classification **PARTIAL_RESOURCE_FAIL**
- disk after 35.338 GiB.

Canonical conclusion:
> Qwen3-8B-4bit Direct MLX passed smoke and a standalone exact T01, but the preregistered continuous benchmark condition crossed the frozen free-memory boundary during T01. Therefore this exact 4096-KV / unquantized-KV 4-bit profile is not established as full-session workload-stable on the reference M1/8 GB machine.

The prospectively frozen Pi-quality gate required `COMPLETE` + delivery-adjusted >27.86 + delivery >2/6. Because the run is partial, **no valid 4-bit aggregate quality comparison exists** and Pi remains blocked.

Do not compare any partial score/output against the completed 3-bit benchmark.

# Current checkpoint — 4-bit resource diagnostic

Checkpoint: `DIRECT_MLX_8B_4BIT_CODING_BENCHMARK_001_RESOURCE_DIAGNOSTIC`
Inspector: `scripts/inspect_direct_mlx_8b_4bit_coding_benchmark_001.py`
Local run:
`results-local/mlx/8b-4bit-coding-benchmark-001/20260819-133144`

Diagnostic must recover without rerunning the model:
- exact `guardrail_abort_reason`;
- child exit/wall state;
- progress state and whether T01 completed/persisted;
- free-memory/swap timeline around the 4% breach;
- raw child stdout/stderr tails;
- whether evidence places the breach during model load, prompt processing, generation, or after response completion.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_direct_mlx_8b_4bit_coding_benchmark_001.py
python3 scripts/inspect_direct_mlx_8b_4bit_coding_benchmark_001.py \
  results-local/mlx/8b-4bit-coding-benchmark-001/20260819-133144
```

Paste the full output.

## Decision after diagnostic

- If the 4% breach occurred during genuine T01 processing/generation, freeze the exact 4-bit condition as workload RESOURCE FAIL. Do not rerun the same condition.
- Do not lower the guardrail or reduce `max_kv_size` inside the failed experiment.
- A new rescue is allowed only as a separately preregistered one-factor experiment with a clear mechanistic rationale; avoid an endless rescue ladder.
- If no single low-confound rescue is strongly justified, close the 4-bit branch and move to the next Phase 5/6 frontier.
- Pi remains blocked regardless until a profile passes technical, workload and prospective quality gates.

## Continuation rule

Before a new experiment, read this file. After every meaningful result/decision, update this file before moving to the next checkpoint.
