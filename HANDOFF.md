# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Phase 4 llama.cpp main branch characterized. Qwen3 8B Q2 is runnable but inferior on the frozen structured workload; Qwen3 8B Q3_K_M is API-smoke viable with NP1 + Q8_0 KV but fails the frozen 5% free-memory guardrail during the first real coding task. Phase 5 Direct MLX setup has now passed and the first 8B/3-bit native-MLX model smoke is preregistered.
Checkpoint: `DIRECT_MLX_8B_3BIT_SMOKE_001_READY`

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
- canonical Ollama model `qwen3.5:4b-mlx`
- canonical experimental context/KV cap 4096 unless separately preregistered

## Production Pi constraint

Production Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration. No new runtime/model profile is exposed to Pi until technical, workload-safety and quality gates pass.

## Storage hygiene

Reuse verified artifacts and never silently delete models or canonical results. Free disk is a standard metric.

Latest confirmed after Direct MLX Setup Probe 001: **43.138 GiB free**.
Verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 GGUF artifacts are retained.
The validated MLX venv is also retained.

# Frozen baseline / prior agent results

## Coding Baseline 001 — Ollama/MLX qwen3.5:4b-mlx
Run `20260818-203156`, context 4096:
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s

## Pi Agentic Coding Benchmark 001
Run `20260818-214848`:
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6
- provider usage 20,209 tokens

# Phase 4 — llama.cpp — MAIN BRANCH CHARACTERIZED

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

4B Runtime Control 001:
- Qwen3-4B Q4_K_M, 2.326 GiB
- pp512 230.85 t/s ±0.12
- tg128 22.33 t/s ±0.02
- minimum free memory 22%

8B Q4 Capability 001:
- context 4096 / forced `-ngl -1`
- minimum free memory 1%
- VALID FAIL

## 8B Q2

Qwen3-8B Q2_K:
- Stage B FULL_PASS: pp512 103.00 t/s ±0.67; tg128 13.72 t/s ±0.34; minimum free 8%
- llama-server smoke FULL_PASS: API `OK`; minimum free 6%
- Coding Quality Compare 001: Q2 delivery 0/100 vs 4B Q4 34.29/100
- diagnostic: transport/API/JSON healthy but structured delivery degraded; repeated literal `filename` handling

Boundary:
> Q2 is technically runnable/API-servable but is not a practical upgrade for the frozen structured coding workload.

## 8B Q3

Q3 forced `-ngl -1` Capability 001:
- minimum free memory 1%
- VALID FAIL

Auto-Fit Server Smoke 001:
- auto server parallelism produced `n_slots=4`
- minimum free memory 4%
- VALID FAIL

Auto-Fit NP1 Server Smoke 001:
- `n_slots=1` verified
- minimum free memory still 4%
- VALID FAIL

Auto-Fit NP1 Q8 KV Server Smoke 001 — run `20260819-113658`:
- context 4096
- `-np 1`
- `-ctk q8_0 -ctv q8_0`
- auto-fit target 1024
- API `OK`
- minimum free memory 6%
- FULL_PASS smoke only

Coding Quality Compare 002 — run `20260819-114848`:
- Q3 server ready 7.360 s
- T01 entered real request processing
- free memory spent substantial time at 5%, then fell to 4% at ~20.3 s
- exact abort `memory free 4% < 5%`
- no HTTP response because safety shutdown terminated the server
- Q3 `PARTIAL_OR_RESOURCE_FAIL`
- 4B under common runtime COMPLETE, minimum free 15%
- printed `4B_HIGHER` is not a valid intrinsic quality ordering because Q3 did not complete

Canonical Phase-4 boundary:
> The exact Qwen3-8B Q3_K_M + llama.cpp + NP1 + Q8_0-KV profile is **API-smoke PASS / real-workload RESOURCE FAIL** at context 4096 under the frozen 5% free-memory boundary.

Records:
- `research/runtime/llama-cpp-coding-quality-compare-002.md`
- `research/runtime/llama-cpp-coding-quality-compare-002-diagnostic.md`

Do not expose the Q3 llama.cpp profile to Pi. Do not lower the guardrail or automatically stack another llama.cpp KV rescue.

# Phase 5 — Direct MLX — ACTIVE

## Setup Probe 001 — PASS

Run `20260819-120748`.
Plan: `research/runtime/direct-mlx-setup-probe-001-plan.md`
Result: `research/runtime/direct-mlx-setup-probe-001.md`
Runner: `scripts/direct_mlx_setup_probe.py`

Validated isolated environment:
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- Darwin arm64: PASS
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- tiny MLX local computation: PASS
- disk before 43.606 GiB
- disk after 43.138 GiB
- environment cost approximately 0.468 GiB
- classification PASS

No LLM weights were downloaded by Setup Probe 001.

## Current checkpoint — Direct MLX 8B 3-bit Smoke 001

Checkpoint: `DIRECT_MLX_8B_3BIT_SMOKE_001_READY`
Plan: `research/runtime/direct-mlx-8b-3bit-smoke-001-plan.md`
Runner: `scripts/direct_mlx_8b_3bit_smoke.py`

Candidate:
- repo `mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- native MLX 3-bit, group size 64
- main weight `model.safetensors`
- published main-weight size ~3.58 GB
- required SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- local destination `results-local/mlx/models/Qwen3-8B-3bit`

Frozen Direct MLX smoke:
- acquisition/reuse via isolated venv
- runtime uses local model with HF/Transformers offline mode
- `Reply only with OK.` through Qwen3 chat template
- `enable_thinking=False`
- max generation 16 tokens
- direct `stream_generate`
- `max_kv_size=4096`
- no KV quantization in this first Direct MLX condition
- one attempt / no same-run rescue
- system free memory <5% abort
- swap >5600 MB abort
- capture disk, model hash/size, process RSS, system memory/swap and MLX prompt/generation/peak-memory stats

Important runtime distinction:
> Direct MLX uses a rotating KV cap of 4096; this is an operational context/KV limit and is not assumed to allocate memory identically to llama.cpp server `-c 4096`.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/direct_mlx_8b_3bit_smoke.py
python3 scripts/direct_mlx_8b_3bit_smoke.py
```

The first run is expected to download the MLX model snapshot. No existing model is deleted or replaced.

Preserve output through `Summary:`.

## Decision after smoke

If `FULL_PASS`:
1. freeze acquisition/runtime telemetry;
2. preregister a real-workload T01 safety probe under the same Direct MLX policy;
3. only after workload-safety PASS proceed to full Coding Benchmark quality comparison and possible Pi integration.

If `RESOURCE_FAIL`:
- do not lower the 5% guardrail or change context inside the failed condition;
- consider KV quantization (`kv_bits=8`) only as a separately preregistered rescue.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
