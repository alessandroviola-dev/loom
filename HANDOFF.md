# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp main branch characterized. Direct MLX setup passed and Qwen3-8B-3bit successfully generated at max_kv_size 4096 with 25% minimum free memory. Smoke 001 safety qualification was blocked only by a macOS swap-telemetry parser defect caused by locale decimal commas. The defect is now diagnosed and a telemetry-only identical rerun is ready.
Checkpoint: `DIRECT_MLX_8B_3BIT_SMOKE_001_SWAPFIX_RERUN_READY`

## Mission

Study practical local LLM/agent execution on constrained Apple M1 / 8 GB hardware.
Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / production constraints

- Never reset/replace production Pi configuration.
- Controlled experiments use isolated/run-local configuration.
- No new profile reaches Pi until technical, workload-safety and quality gates pass.
- Frozen safety boundary: free memory <5% OR swap >5600 MB abort.
- Process RSS is diagnostic only; system-wide free memory and swap are decisive.
- Never silently delete verified models or canonical results.

## Phase 4 — llama.cpp boundary

Qwen3-8B Q2_K:
- technically runnable/API-servable;
- coding delivery 0/100 vs 4B 34.29/100;
- not established as a practical upgrade.

Qwen3-8B Q3_K_M:
- NP1 + Q8_0 KV API smoke PASS at 6% free;
- first real Coding T01 drove free memory to 4% and triggered guardrail;
- canonical classification: **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096.

Main branch moved to Direct MLX.

# Phase 5 — Direct MLX — ACTIVE

## Setup Probe 001 — PASS

Run `20260819-120748`:
- Darwin arm64
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- tiny MLX compute PASS.

## Direct MLX 8B 3-bit Smoke 001 — generation PASS / swap telemetry incomplete

Run `20260819-121656`.
Model:
- `mlx-community/Qwen3-8B-3bit`
- revision `619ded3`
- SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`: PASS
- 3-bit / group size 64: PASS
- main weight 3.338 GiB

Frozen runtime:
- local/offline
- `enable_thinking=False`
- prompt `Reply only with OK.`
- max 16 tokens
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV

Observed:
- child exit 0
- output `OK.`
- prompt 17 tok @ 6.3733 t/s
- generation 3 tok @ 24.6243 t/s
- MLX peak memory 3.6676508 GB
- min system free memory 25%
- swap telemetry `None`

Record:
`research/runtime/direct-mlx-8b-3bit-smoke-001.md`

## Swap diagnostic — CLOSED

Read-only host output:
```text
total = 2048,00M  used = 1121,88M  free = 926,12M  (encrypted)
```

Observed diagnostic state:
- current swap used by inspection: 1121.88 MB
- current free memory: 72%
- current disk free: 40.647 GiB

Root cause:
- original parser accepted decimal points only;
- this Mac emits locale decimal commas;
- both original and first "robust" diagnostic regex therefore returned `None`.

This is a **telemetry parser defect**, not an MLX/model failure. Current swap is far below the 5600 MB threshold, but it cannot retroactively validate the missing samples from run `20260819-121656`.

Diagnostic record:
`research/runtime/direct-mlx-8b-3bit-smoke-001-swap-diagnostic.md`

## Current checkpoint — identical smoke rerun with telemetry-only fix

Checkpoint: `DIRECT_MLX_8B_3BIT_SMOKE_001_SWAPFIX_RERUN_READY`
Wrapper:
`scripts/direct_mlx_8b_3bit_smoke_001_swapfix.py`

The wrapper:
- imports the existing frozen Smoke 001 runner;
- changes only `swap_used_mb()`;
- accepts `.` or `,` decimal separators and Unicode whitespace;
- normalizes comma to point before numeric conversion;
- leaves all model/runtime/generation/safety settings unchanged.

The already-downloaded verified model is reused. No model change, KV change, context change, prompt change or quality rescue is authorized.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_3bit_smoke_001_swapfix.py
python3 scripts/direct_mlx_8b_3bit_smoke_001_swapfix.py
```

Preserve output through `Summary:`.

## Decision after rerun

If the rerun:
- captures numeric swap samples;
- stays <=5600 MB swap;
- stays >=5% free memory;
- and satisfies all original Smoke 001 generation criteria,

then freeze it as the canonical Direct MLX 8B/3-bit safety-valid smoke and preregister a real Coding Benchmark T01 workload-safety probe.

If it fails a real memory/swap guardrail, classify that profile as RESOURCE_FAIL. Do not lower thresholds or alter context inside the failed condition.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
