# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp main branch characterized. Direct MLX setup passed and Qwen3-8B-3bit successfully generated at max_kv_size 4096, but Smoke 001 did not capture swap telemetry, so workload testing is paused until the safety sampler is diagnosed.
Checkpoint: `DIRECT_MLX_8B_3BIT_SMOKE_001_SWAP_DIAGNOSTIC`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.
Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

Reference stack:
- Apple M1, 8 GB unified memory
- Ollama 0.32.14
- Pi 0.84.2
- Qwen Code 0.21.13
- canonical experimental context/KV cap 4096 unless separately preregistered

## Safety / production constraints

- Production Pi contains real auth, sessions and customizations; never reset or replace it.
- Controlled experiments use isolated/run-local configuration.
- No new runtime/model profile reaches Pi until technical, workload-safety and quality gates pass.
- Frozen safety boundary: free memory <5% OR swap >5600 MB abort.
- Process RSS is diagnostic only; system-wide free memory and swap are decisive.
- Never silently delete verified models or canonical results.

## Storage

Latest confirmed after Direct MLX 8B 3-bit Smoke 001: **39.668 GiB free**.
The verified GGUF artifacts, validated MLX venv and downloaded MLX 8B/3-bit model are retained.

# Frozen prior results

## Ollama/MLX 4B baseline

Coding Baseline 001, run `20260818-203156`:
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s

Pi Agentic Coding Benchmark 001, run `20260818-214848`:
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6

# Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED

Pinned commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`

4B Q4 control:
- pp512 230.85 t/s
- tg128 22.33 t/s
- minimum free memory 22%

8B Q2:
- technically runnable and API-servable
- Stage B pp512 103.00 t/s / tg128 13.72 t/s
- Coding Quality Compare 001: delivery 0/100 vs 4B 34.29/100
- structured delivery degraded; not a practical upgrade

8B Q3 llama.cpp:
- forced max offload: VALID FAIL, 1% free
- auto-fit: VALID FAIL, 4% free
- auto-fit + `-np 1`: VALID FAIL, 4% free
- auto-fit + NP1 + Q8_0 KV smoke: FULL_PASS, 6% free
- real Coding T01 under same profile: resource abort at 4% free

Canonical boundary:
> Qwen3-8B Q3_K_M under llama.cpp with NP1 + Q8_0 KV is API-smoke PASS but real-workload RESOURCE FAIL at context 4096 under the frozen 5% boundary.

Do not expose this llama.cpp profile to Pi. Compare 002 does not establish intrinsic 4B>Q3 quality because Q3 did not complete.

# Phase 5 — Direct MLX — ACTIVE

## Setup Probe 001 — PASS

Run `20260819-120748`.
Validated isolated environment:
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- Darwin arm64
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- local MLX compute PASS
- disk 43.606 -> 43.138 GiB

Record: `research/runtime/direct-mlx-setup-probe-001.md`

## Direct MLX 8B 3-bit Smoke 001 — GENERATION PASS / SAFETY TELEMETRY INCOMPLETE

Run `20260819-121656`.
Plan: `research/runtime/direct-mlx-8b-3bit-smoke-001-plan.md`
Result: `research/runtime/direct-mlx-8b-3bit-smoke-001.md`
Runner: `scripts/direct_mlx_8b_3bit_smoke.py`

Model:
- `mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- local `model.safetensors` SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`: PASS
- observed main weight 3.338 GiB
- config metadata: 3-bit / group size 64 PASS

Frozen runtime:
- local/offline inference
- Qwen3 `enable_thinking=False`
- `Reply only with OK.`
- max 16 generation tokens
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV

Observed:
- snapshot acquisition PASS
- disk before 43.032 GiB
- disk after acquisition 40.668 GiB
- child exit 0
- assistant `OK.`
- prompt 17 tok @ 6.3733 t/s
- generation 3 tok @ 24.6243 t/s
- MLX-reported peak memory 3.6676508 GB
- sampled peak process RSS 443.875 MB
- minimum observed free memory **25%**
- **peak observed swap: None**
- final disk 39.668 GiB

Canonical interpretation:
> The verified Direct MLX 8B/3-bit profile successfully loaded and generated at max_kv_size 4096 with large free-memory headroom, but the swap channel of the frozen safety gate was not observable. Therefore the run is not yet accepted as a complete safety FULL_PASS.

The ~1.000 GiB disk delta between post-acquisition and final snapshots remains unattributed; do not assume it is swap without evidence.

# Current checkpoint — swap telemetry diagnostic

Checkpoint: `DIRECT_MLX_8B_3BIT_SMOKE_001_SWAP_DIAGNOSTIC`
Diagnostic: `scripts/diagnose_macos_swap_telemetry.py`

Purpose:
- read raw `sysctl -n vm.swapusage` and `sysctl vm.swapusage` output;
- show whether the current runner regex can parse the machine's format;
- test a more robust parser;
- report current `memory_pressure` free percentage and disk free;
- launch no model and mutate nothing.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/diagnose_macos_swap_telemetry.py
python3 scripts/diagnose_macos_swap_telemetry.py
```

Paste the full output.

## Decision after diagnostic

If swap is readable and this is only a parser defect:
1. fix only telemetry collection;
2. preregister/re-run the identical Direct MLX smoke using the already-downloaded model;
3. do not alter model, max_kv_size, KV precision or prompt.

Only after both safety channels pass may LOOM proceed to real Coding Benchmark T01 under Direct MLX.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
