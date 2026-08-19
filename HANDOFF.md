# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp frontier characterized. Phase 5 Direct MLX is now technically/safety validated at smoke level: Qwen3-8B-3bit completed the frozen 4096-KV smoke with both free-memory and swap telemetry valid. The active gate is the real frozen Coding Benchmark T01 workload-safety probe before any full quality benchmark or Pi integration.
Checkpoint: `DIRECT_MLX_8B_3BIT_T01_WORKLOAD_001_READY`

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
- frozen coding delivery 0/100 vs 4B 34.29/100;
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
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- tiny MLX compute PASS.

## Model

`mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- main weight SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`: PASS
- observed weight size 3.338 GiB
- quantization metadata: 3-bit / group size 64 PASS
- local path `results-local/mlx/models/Qwen3-8B-3bit`

## Direct MLX 8B 3-bit Smoke 001

Initial run `20260819-121656` generated successfully but swap telemetry was `None` because this Mac emits locale decimal commas in `vm.swapusage`.

Diagnostic raw format:
`used = 1121,88M`

Root cause was telemetry-only. The parser accepted decimal points but not commas.

### Safety-valid telemetry-fix rerun — FULL_PASS

Run `20260819-124440`.
Wrapper: `scripts/direct_mlx_8b_3bit_smoke_001_swapfix.py`.
Record: `research/runtime/direct-mlx-8b-3bit-smoke-001-swapfix-rerun.md`.

Frozen runtime unchanged from Smoke 001:
- local/offline Direct MLX
- Qwen3 `enable_thinking=False`
- `Reply only with OK.`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- max generation 16 tokens
- free-memory <5% / swap >5600 MB abort

Observed:
- locale-safe swap preflight 1113.88 MB: PASS
- existing model SHA: PASS
- no model re-download
- assistant `OK.`
- prompt 17 tok @ 11.0758 t/s
- generation 3 tok @ 24.4160 t/s
- MLX peak memory 3.6676508 GB
- peak process RSS 494.8125 MB
- peak observed swap **1720.75 MB**
- minimum observed free memory **23%**
- classification **FULL_PASS**
- disk after 40.639 GiB

Canonical conclusion:
> The verified Direct MLX Qwen3-8B 3-bit profile is smoke-level technically and safety viable with `max_kv_size=4096` and unquantized KV on the reference M1/8 GB machine. This does not yet establish real-workload stability or coding quality.

# Current checkpoint — T01 workload safety

Checkpoint: `DIRECT_MLX_8B_3BIT_T01_WORKLOAD_001_READY`
Plan: `research/runtime/direct-mlx-8b-3bit-t01-workload-001-plan.md`
Runner: `scripts/direct_mlx_8b_3bit_t01_workload.py`

Research question:
> Can the same safety-valid Direct MLX profile complete the real frozen Coding Benchmark T01 request without crossing the 5% free-memory or 5600 MB swap guardrails?

Frozen benchmark provenance:
- Coding Benchmark 01 v1.0.1
- T01 only
- frozen adapter `scripts/ollama_single_shot.py`
- required adapter Git blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- exact adapter `build_prompt()` envelope
- no test feedback
- one attempt
- no retry/repair/salvage

Direct MLX condition retained:
- exact verified 8B/3-bit model
- isolated pinned MLX environment
- local/offline
- Qwen3 non-thinking chat template
- `max_kv_size=4096`
- unquantized KV
- seed 0
- locale-safe swap telemetry

Workload changes relative to smoke only:
- prompt becomes exact frozen T01 single-shot prompt;
- generation budget becomes 2048 tokens, matching Coding Benchmark 01.

Structured delivery is recorded but does not determine this workload-safety classification. No benchmark test runner is executed in this probe.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_3bit_t01_workload.py
python3 scripts/direct_mlx_8b_3bit_t01_workload.py
```

No model download is expected.

Preserve output through `Summary:` including:
- safety preflight;
- T01 generation exit;
- MLX stats;
- structured delivery status;
- peak swap;
- minimum free memory;
- classification.

## Decision after T01

If `FULL_PASS`:
1. freeze workload-safety result;
2. preregister full Direct MLX Coding Benchmark 01;
3. use quality/delivery as next gate before Pi.

If `RESOURCE_FAIL`:
- do not lower guardrails or reduce the 4096 KV cap inside the failed condition;
- consider KV quantization only as a separately preregistered rescue.

If delivery fails while resource safety passes, preserve that protocol evidence and do not alter the prompt/parser post-hoc.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
