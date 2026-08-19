# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Direct MLX established a practical 8B runtime frontier on Apple M1 / 8 GB. Qwen3-8B-3bit is full-session stable but did not earn Pi promotion on frozen coding quality. Qwen3-8B-4bit passed smoke and standalone T01 narrowly, but both the original full benchmark and a host-state-controlled replication crossed the frozen free-memory guardrail. The exact 4-bit / 4096 / unquantized-KV continuous profile is now closed as RESOURCE FAIL; the active step is a read-only diagnostic of the controlled replication before deciding on at most one KV8 rescue.
Checkpoint: `DIRECT_MLX_8B_4BIT_HOSTSTATE_REPLICATION_001_DIAGNOSTIC`

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

Latest observed disk after controlled 4-bit full replication: **35.328 GiB free**. Verified 3-bit, 4-bit and GGUF artifacts remain retained.

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

Exact T01 `20260819-124952`: preflight 75% region, min free 19%, peak swap 1643.12 MB, delivery `written`, FULL_PASS.

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

Conclusion: Direct MLX solves resource stability for Qwen3-8B at 3-bit, but coding quality is not a clear upgrade. Pi remains blocked.

Records:
- `research/runtime/direct-mlx-coding-benchmark-001.md`
- `research/runtime/direct-mlx-coding-benchmark-001-diagnostic.md`.

## Qwen3-8B-4bit — exact unquantized-KV full-session profile CLOSED as RESOURCE FAIL

Artifact:
- `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64
- main weight 4.291 GiB.

Smoke `20260819-131009`:
- `max_kv_size=4096`, unquantized KV
- min free 10%
- peak swap 2403.31 MB
- generation 20.8411 t/s
- MLX peak 4.683327704 GB
- FULL_PASS.

Standalone exact T01 `20260819-132612`:
- preflight 74% free / 1395.25 MB swap
- generation 13.9275 t/s
- MLX peak 4.981664948 GB
- delivery `written`
- peak swap 2470.31 MB
- min free 6%
- FULL_PASS.

### Original full benchmark — PARTIAL_RESOURCE_FAIL

Run `20260819-133144`:
- frozen T01–T06 continuous-session condition
- preflight 56% free / 948.75 MB swap
- T01 started, no result persisted
- min free 4%
- peak swap 3028.25 MB
- child exit -15 after parent safety termination
- no valid quality result.

Resource diagnostic showed the 4% breach occurred while T01 was still running; max swap occurred earlier and swap was declining at the free-memory breach. Host state was a material uncontrolled difference versus successful references, so exactly one controlled replication was preregistered.

Records:
- `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001.md`
- `research/runtime/direct-mlx-8b-4bit-coding-benchmark-001-resource-diagnostic.md`.

### Host-State Controlled Replication 001 — PARTIAL_RESOURCE_FAIL

Host-state run `20260819-134010`; benchmark run `20260819-134012`.
Plan: `research/runtime/direct-mlx-8b-4bit-hoststate-replication-001-plan.md`
Result: `research/runtime/direct-mlx-8b-4bit-hoststate-replication-001.md`
Wrapper: `scripts/direct_mlx_8b_4bit_hoststate_replication_001.py`

Prospective host gate:
- 3 consecutive samples >=70% free
- no purge/process killing/swap manipulation.

Observed host samples:
- 72% / 1381.75 MB swap
- 74% / 1381.75 MB swap
- 74% / 1381.75 MB swap

Full-run safety preflight then observed 72% free / 1381.75 MB swap.

Same frozen runtime:
- 4-bit verified model
- Direct MLX
- exact Coding Benchmark 01 v1.0.1
- one loaded session
- `max_kv_size=4096`
- **unquantized KV**
- max 2048 tokens/task
- non-thinking, seed 0
- no retries/repair/salvage/test feedback
- free<5% / swap>5600 MB abort.

Observed progress:
- T01 running
- T02 running
- T03 running
- T04 running

Abort telemetry:
- peak sampled RSS 332.046875 MB
- peak swap 2879.38 MB
- min free **4%**
- disk 35.333 → 35.328 GiB
- classification `PARTIAL_RESOURCE_FAIL`.

Canonical conclusion:
> High-free-memory host state materially extended progress (T04 rather than T01), but did not rescue the profile. The exact Qwen3-8B-4bit + Direct MLX + `max_kv_size=4096` + unquantized-KV continuous coding condition is therefore closed as workload RESOURCE FAIL on the M1/8 GB reference machine.

No further identical replication is allowed. No aggregate 4-bit quality ordering is valid because neither full run completed. Pi remains blocked.

# Current checkpoint — controlled replication read-only diagnostic

Checkpoint: `DIRECT_MLX_8B_4BIT_HOSTSTATE_REPLICATION_001_DIAGNOSTIC`

Use existing inspector:
`scripts/inspect_direct_mlx_8b_4bit_coding_benchmark_001.py`

Target:
`results-local/mlx/8b-4bit-coding-benchmark-001/20260819-134012`

Required recovery:
- generated/persisted task count and task IDs
- child exit and wall time
- exact free-memory/swap timeline across T01–T04
- task transitions relative to pressure trend
- raw child stdout/stderr tails
- no scoring-based 4-bit quality conclusion from a partial run.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_direct_mlx_8b_4bit_coding_benchmark_001.py
python3 scripts/inspect_direct_mlx_8b_4bit_coding_benchmark_001.py \
  results-local/mlx/8b-4bit-coding-benchmark-001/20260819-134012
```

No model launch occurs.

## Decision after diagnostic

The failed unquantized-KV profile stays closed regardless of diagnostic details.

A single separately preregistered **KV8 rescue** may be justified only if the persisted timeline remains compatible with memory pressure accumulating across the continuous workload. MLX-LM supports `kv_bits` as a generation parameter; use 8-bit rather than a more aggressive KV precision to minimize the new quality confound. Preserve model, benchmark, `max_kv_size=4096`, prompts/parser/scorer, generation budget, host-state gate and 5%/5600 MB guardrails.

Do not begin an open-ended rescue ladder. If one KV8 rescue is run and resource-fails, close the 4-bit branch and advance to the next research frontier.

## Continuation rule

Before a new experiment, read this file. After every meaningful result/decision, update it before moving to the next checkpoint.
