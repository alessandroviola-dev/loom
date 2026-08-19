# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Direct MLX established a practical 8B runtime frontier on Apple M1 / 8 GB. Qwen3-8B-3bit is full-session stable but did not earn Pi promotion on frozen coding quality. Qwen3-8B-4bit with `max_kv_size=4096` and unquantized KV is now closed as continuous-workload RESOURCE FAIL after both the original full run and a >=70%-free host-controlled replication crossed the 5% free-memory guardrail. The controlled replication diagnostic supports exactly one final low-confound rescue: 8-bit KV cache active from token 0.
Checkpoint: `DIRECT_MLX_8B_4BIT_KV8_RESCUE_001_READY`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.
Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Frozen safety / production constraints

- Never reset or replace production Pi configuration.
- Controlled experiments use isolated/run-local configuration.
- No new profile reaches Pi until technical, workload-safety and quality gates pass.
- Frozen runtime abort: free memory <5% OR swap >5600 MB.
- Process RSS is diagnostic only; system-wide free memory and swap drive safety decisions.
- Never silently delete verified models or canonical results.
- Record free disk before/after model acquisitions and large runtime experiments.
- Do not lower guardrails or alter a failed frozen condition post-hoc.
- Do not repeat a frozen profile once a controlled replication confirms its resource failure.
- The KV8 rescue below is the only remaining rescue authorized for the 4-bit branch; no rescue ladder.

Latest observed disk after controlled 4-bit replication: **35.328 GiB free**. Verified 3-bit, 4-bit and GGUF artifacts remain retained.

# Frozen reference results

## Ollama/MLX 4B baseline

Coding Baseline 001 (`20260818-203156`): artifact 40.71/100, strict 30.00/100, delivery 3/6, recovered semantic diagnostic 82.86/100, generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`): artifact/delivery 77.15/100, strict 60.00/100, delivery 6/6, protocol 4/6.

## llama.cpp boundary

Pinned commit `60addddf3c567c43ec3caf70fc953fba3572d96f`.
- 4B Q4 control: pp512 230.85 t/s, tg128 22.33 t/s, min free 22%.
- 8B Q2: technically runnable/API-servable but coding delivery 0/100 vs 4B Q4 34.29/100 in Compare 001.
- 8B Q3 NP1 + Q8_0 KV: API smoke PASS at 6% free; exact Coding T01 hit 4% free and guardrail abort.

Canonical Q3 boundary: **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under llama.cpp.

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
- main weight 3.338 GiB.

Safety-valid smoke `20260819-124440`: min free 23%, peak swap 1720.75 MB, FULL_PASS.

Exact T01 `20260819-124952`: min free 19%, peak swap 1643.12 MB, delivery `written`, FULL_PASS.

Full Coding Benchmark 001 `20260819-125647`:
- one loaded T01–T06 session
- preflight 75% free / 1339.00 MB swap
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57/100
- delivery-adjusted 27.86/100
- delivery 2/6
- COMPLETE.

Quality diagnostic:
- T01 15/15 clean success
- T02 12.86/15, 6/7 tests
- T03 protocol fail from extra fenced JSON
- T04 protocol fail plus malformed/incorrect content
- T05 protocol fail; no post-hoc salvage
- T06 protocol fail plus tie-order semantic defect.

Conclusion: resource stability solved at 3-bit, but coding quality is not a clear practical upgrade. Pi remains blocked.

Records:
- `research/runtime/direct-mlx-coding-benchmark-001.md`
- `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`.

## Qwen3-8B-4bit — unquantized-KV profile CLOSED as RESOURCE FAIL

Artifact:
- `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- main weight 4.291 GiB.

Smoke `20260819-131009`: `max_kv_size=4096`, unquantized KV, min free 10%, peak swap 2403.31 MB, generation 20.8411 t/s, FULL_PASS.

Standalone exact T01 `20260819-132612`: preflight 74% free, min free 6%, peak swap 2470.31 MB, delivery `written`, FULL_PASS.

### Original full benchmark `20260819-133144`

- preflight 56% free / 948.75 MB swap
- T01 started, no result persisted
- min free 4%
- peak swap 3028.25 MB
- child exit -15
- `PARTIAL_RESOURCE_FAIL`.

Read-only diagnostic established that the breach occurred during T01 processing and that max swap occurred earlier; the materially lower host free-memory state justified exactly one controlled replication.

### Host-State Controlled Replication 001

Host gate `20260819-134010`: 72%, 74%, 74% free; swap 1381.75 MB. Launch eligible.

Full run `20260819-134012`, unchanged model/runtime/benchmark:
- preflight 72% free / 1381.75 MB swap
- completed and persisted T01, T02, T03
- entered T04
- min free 4%
- peak swap 2879.38 MB
- child exit -15 at 49.353 s
- `PARTIAL_RESOURCE_FAIL`.

Controlled replication diagnostic:
- T01: 101 gen tok, 13.1458 t/s, MLX peak 4.981664948 GB, `written`
- T02: 119 gen tok, 13.3513 t/s, MLX peak 5.037748316 GB, `written`
- T03: 60 gen tok, 12.7644 t/s, MLX peak 5.037748316 GB, `written`
- T03 reaches exactly 5% free without breaching the `<5%` rule, then temporarily recovers
- T04 begins at 6% free and reaches 4% at 49.198 s
- final 4% sample has swap 2099.94 MB; peak swap occurred much earlier during T01.

Canonical conclusion:
> Host state affects how far the 4-bit run progresses, but does not rescue the exact 4-bit + Direct MLX + `max_kv_size=4096` + unquantized-KV continuous profile. That profile is closed as workload RESOURCE FAIL. No aggregate 4-bit quality score is valid from either partial full run.

Records:
- `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001.md`
- `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001-resource-diagnostic.md`
- `research/runtime/direct-mlx-8b-4bit-hoststate-replication-001.md`
- `research/runtime/direct-mlx-8b-4bit-hoststate-replication-001-diagnostic.md`.

# Current checkpoint — single KV8 rescue

Checkpoint: `DIRECT_MLX_8B_4BIT_KV8_RESCUE_001_READY`

Plan:
`research/runtime/direct-mlx-8b-4bit-kv8-rescue-001-plan.md`

Runner:
`scripts/direct_mlx_8b_4bit_kv8_rescue_001.py`

Scientific rationale:
- continuous 4-bit session repeatedly approaches the free-memory floor while completing multiple tasks;
- MLX-LM Direct generation exposes KV-cache quantization independently from weight quantization and `max_kv_size`;
- KV precision is therefore the narrowest remaining directly supported memory-control factor.

One-factor rescue policy:
- model weights unchanged
- environment unchanged
- exact Coding Benchmark 01 v1.0.1 unchanged
- prompts/parser/scorer unchanged
- one loaded T01–T06 session unchanged
- `enable_thinking=False` unchanged
- max 2048 generated tokens/task unchanged
- seed 0 unchanged
- **`max_kv_size=4096` unchanged**
- KV policy changes from unquantized to:
  - `kv_bits=8`
  - `kv_group_size=64`
  - `quantized_kv_start=0`.

`quantized_kv_start=0` is explicit so KV8 actually engages on these sub-5000-token tasks; the CLI deferred default of 5000 would not test the intended rescue.

Controlled launch gate remains:
- 3 consecutive samples >=70% free memory
- no purge/process killing/swap manipulation
- if not met: `HOST_STATE_NOT_READY`, MLX launch skipped, not a model result.

Runtime safety remains:
- free <5% abort
- swap >5600 MB abort.

Prospective quality gate if and only if run reaches COMPLETE:
- delivery-adjusted >27.86/100
- structured delivery >2/6.

Both are required before any isolated Pi validation may be considered.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_4bit_kv8_rescue_001.py
python3 scripts/direct_mlx_8b_4bit_kv8_rescue_001.py
```

No model download is expected.

If `HOST_STATE_NOT_READY`, no MLX run occurred; naturally close heavy applications and retry only the launch wrapper.

If the KV8 run resource-fails after launch, close the entire 4-bit branch and move to the next frontier. Do not test KV6/KV4, lower context or lower guardrails.

If it reaches COMPLETE, freeze full safety/quality evidence and apply the already-frozen quality gate before any Pi experiment.

## Continuation rule

Before a new experiment, read this file. After every meaningful result/decision, update it before moving to the next checkpoint.
