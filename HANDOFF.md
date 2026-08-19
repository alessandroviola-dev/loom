# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Direct MLX established a practical 8B runtime frontier on Apple M1 / 8 GB. Qwen3-8B-3bit is full-session stable but did not earn Pi promotion on frozen coding quality. Qwen3-8B-4bit passed smoke and standalone T01 narrowly, then the original full benchmark hit the 5% free-memory guardrail during T01. Diagnostic evidence shows that failed run began from materially lower host free-memory state than the closest successful references, so exactly one host-state-controlled replication is preregistered before any runtime/KV rescue.
Checkpoint: `DIRECT_MLX_8B_4BIT_HOSTSTATE_REPLICATION_001_READY`

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

Latest measured disk after failed 4-bit full run: 35.338 GiB free. Verified 3-bit, 4-bit and GGUF artifacts remain retained.

# Frozen reference results

## Ollama/MLX 4B baseline

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6.

## llama.cpp boundary

Pinned commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`.

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
- repo `mlx-community/Qwen3-8B-3bit`
- revision `619ded3`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64
- observed main weight 3.338 GiB.

Safety-valid smoke `20260819-124440`: min free 23%, peak swap 1720.75 MB, FULL_PASS.

Exact T01 `20260819-124952`: min free 19%, peak swap 1643.12 MB, delivery `written`, FULL_PASS.

Full Coding Benchmark 001 `20260819-125647`:
- one loaded session T01–T06
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

Conclusion: resource stability solved, but 3-bit is not a clear coding-quality upgrade. Pi remains blocked.

Records:
- `research/runtime/direct-mlx-coding-benchmark-001.md`
- `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`.

## Qwen3-8B-4bit — smoke/T01 PASS, original full run RESOURCE FAIL

Artifact:
- repo `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- observed main weight 4.291 GiB.

Smoke `20260819-131009`:
- max_kv_size 4096, unquantized KV
- min free 10%
- peak swap 2403.31 MB
- generation 20.8411 t/s
- MLX peak memory 4.683327704 GB
- FULL_PASS.

Standalone exact T01 `20260819-132612`:
- preflight **74% free / 1395.25 MB swap**
- prompt 276 tok @ 35.2422 t/s
- generation 101 tok @ 13.9275 t/s
- MLX peak memory 4.981664948 GB
- delivery `written`
- peak swap 2470.31 MB
- min free **6%**
- FULL_PASS.

### Original full 4-bit Coding Benchmark 001 — PARTIAL_RESOURCE_FAIL

Run `20260819-133144`.
Frozen full condition:
- Coding Benchmark 01 v1.0.1 T01–T06
- exact adapter/scorer blobs
- one loaded Direct MLX model session
- local/offline, non-thinking
- `max_kv_size=4096`
- unquantized KV
- max 2048 tokens/task
- seed 0
- no retry/repair/salvage/test feedback
- free <5% / swap >5600 MB abort.

Observed:
- preflight **56% free / 948.75 MB swap**
- T01 started but no task result persisted
- child terminated by parent, exit -15
- wall 17.913 s
- peak child RSS 459.453125 MB
- peak swap 3028.25 MB
- min free **4%**
- classification `PARTIAL_RESOURCE_FAIL`
- no artifact or delivery-adjusted score.

Prospective Pi gate remains unevaluable because run was not COMPLETE.

### Resource diagnostic — CLOSED

Record:
`research/runtime/direct-mlx-8b-4bit-coding-benchmark-001-resource-diagnostic.md`

Memory timeline:
- 0–2 s: free 55–58%, child startup
- 3–5 s: free falls to 13%; model/session initialization region
- T01 marked running at ~5.9 s with free 18%, swap 2516 MB
- max swap 3028.25 MB at 6.881 s while free 22%
- free then declines steadily while swap generally declines
- 16.199 s: free 6%
- 17.403 s: free 4%, swap 1977.56 MB → guardrail abort
- no T01 response persisted and stdout/stderr remained empty.

Supported interpretation:
- the original frozen full run genuinely failed during T01 processing;
- failure was free-memory, not swap;
- no quality output completed;
- failed run began from materially lower host free-memory state than successful 4-bit T01 (56% vs 74%) and completed 3-bit full benchmark (56% vs 75%).

This does not prove host state caused the failure, but the 18–19 point preflight difference is a strong enough uncontrolled variable to justify one controlled replication before changing KV precision.

# Current checkpoint — host-state-controlled replication

Checkpoint: `DIRECT_MLX_8B_4BIT_HOSTSTATE_REPLICATION_001_READY`

Plan:
`research/runtime/direct-mlx-8b-4bit-hoststate-replication-001-plan.md`

Wrapper:
`scripts/direct_mlx_8b_4bit_hoststate_replication_001.py`

Frozen full runner required blob:
`541e23ef5a824a29f3f67e162e48228b2ccabb14`

The wrapper changes **no model/runtime/benchmark setting**. It only adds a prospective launch gate:
- sample `memory_pressure` once per second
- require 3 consecutive samples each >=70% free memory
- if not met: `HOST_STATE_NOT_READY`, MLX not launched
- if met: write preflight record, then `os.execv` replaces wrapper with exact frozen full benchmark runner so wrapper adds no resident process overhead.

No automated purge or process killing is allowed. Swap preflight is recorded but no new swap launch threshold is introduced. Runtime guardrails remain free<5% / swap>5600 MB.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_4bit_hoststate_replication_001.py
python3 scripts/direct_mlx_8b_4bit_hoststate_replication_001.py
```

If output is `HOST_STATE_NOT_READY`, no model was launched. Do not treat that as a failed model run. The user may naturally close heavy applications and retry the wrapper until the prelaunch gate is met; do not run memory/swap purge commands.

If the controlled replication launches and again hits the resource guardrail, close the 4-bit / 4096 / unquantized-KV full-session branch and do not repeat the same profile again.

If it completes, retain both the original failure and the controlled replication as evidence of host-state sensitivity, then apply the already-frozen quality gate: delivery-adjusted >27.86 and delivery >2/6 before any isolated Pi validation.

## Continuation rule

Before a new experiment, read this file. After every meaningful result/decision, update it before moving to the next checkpoint.
