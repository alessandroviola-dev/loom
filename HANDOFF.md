# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated. Qwen3 8B Q2 is technically runnable/API-servable but loses the frozen structured coding benchmark to 4B Q4. Qwen3 8B Q3_K_M has an API-smoke FULL_PASS at context 4096 using NP1 + Q8_0 K/V KV cache, but Coding Quality Compare 002 hit the frozen resource guardrail during T01. The comparison is PARTIAL and does not establish a valid quality ordering.
Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_002_RESOURCE_DIAGNOSTIC`

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
- canonical context 4096 unless separately preregistered

## Production Pi constraint

Production Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration where required. Do not expose a new llama.cpp profile to Pi until it passes technical/API, workload-safety and frozen quality gates.

## Storage hygiene

Reuse verified artifacts and never silently delete models or canonical results. Free disk is a standard metric.
Latest confirmed after Coding Quality Compare 002: **43.643 GiB free**. Verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts are retained.

# Frozen baseline / prior results

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

# Phase 4 — llama.cpp

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

4B Runtime Control 001:
- Qwen3-4B Q4_K_M, 2.326 GiB
- pp512 230.85 t/s ±0.12
- tg128 22.33 t/s ±0.02
- peak RSS 1914.91 MB
- peak swap 1097.19 MB
- minimum free memory 22%

8B Q4 Capability 001: VALID FAIL at context 4096 / forced `-ngl -1`; minimum free memory 1%.

8B Q3 Capability 001: VALID FAIL at context 4096 / forced `-ngl -1`; minimum free memory 1%.

Q3 artifact:
- repository `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q3_K_M.gguf`
- SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size 3.841 GiB

## Q2 technical/API PASS, quality inferior

Qwen3-8B Q2_K:
- Stage B FULL_PASS: pp512 103.00 t/s ±0.67; tg128 13.72 t/s ±0.34; minimum free 8%
- llama-server smoke FULL_PASS: API `OK`; minimum free 6%
- Coding Quality Compare 001: Q2 delivery 0/100 vs 4B Q4 34.29/100; relation `4B_HIGHER`
- diagnostic: requests/API/JSON healthy, but Q2 repeatedly treated `filename` as a literal structured-output key; 4B delivered 4/6 tasks under identical transport.

Boundary: Q2 is runnable but not established as a practical upgrade for the frozen structured coding workload.

## Q3 rescue sequence

Auto-Fit Server Smoke 001:
- default server auto parallelism resolved to `n_slots=4`, `n_ctx_slot=4096`, `kv_unified=true`
- minimum free memory 4%
- VALID FAIL

Auto-Fit NP1 Server Smoke 001:
- explicit `-np 1`
- `n_slots=1`, `n_ctx_slot=4096`, `kv_unified=false` verified
- minimum free memory still 4%
- VALID FAIL

Auto-Fit NP1 Q8 KV Server Smoke 001 — FULL_PASS, run `20260819-113658`:
- Q3_K_M, context 4096
- `-np 1`
- FA auto
- `--fit on --fit-target 1024 --fit-ctx 4096`
- `-ctk q8_0 -ctv q8_0`
- no forced `-ngl -1`
- readiness 8.756 s
- API `OK`
- peak RSS 2246.75 MB
- peak swap 2113.88 MB
- minimum free memory 6%
- FULL_PASS

Canonical record:
`research/runtime/llama-cpp-8b-q3-autofit-np1-q8-server-smoke-001.md`

Important boundary: this established API-smoke viability only. Its one-point margin above the 5% guardrail required full-workload validation before Pi.

# Coding Quality Compare 002 — PARTIAL / RESOURCE FAIL

Plan: `research/runtime/llama-cpp-coding-quality-compare-002-plan.md`
Result: `research/runtime/llama-cpp-coding-quality-compare-002.md`
Runner: `scripts/llama_cpp_coding_quality_compare_002.py`
Run: `20260819-114848`

Common runtime for both profiles:
```text
-c 4096
-np 1
-fa auto
--fit on
--fit-target 1024
--fit-ctx 4096
-ctk q8_0
-ctv q8_0
no forced -ngl -1
```

Common benchmark discipline:
- Coding Benchmark 01 v1.0.1, T01–T06
- `POST /completion`
- `n_predict=2048`
- `temperature=0`
- `seed=0`
- `cache_prompt=false`
- `json_schema={}`
- one attempt per task
- no retries, feedback, salvage or prompt changes
- delivery-adjusted score primary

Observed:

### Qwen3 8B Q3_K_M
- server ready in 7.360 s
- T01 started
- T01 `guardrail abort`
- profile artifact 15.0/100
- delivery-adjusted 0/100
- classification `PARTIAL_OR_RESOURCE_FAIL`

### Qwen3 4B Q4_K_M
- server ready in 1.060 s
- T01 written
- T02 written
- T03 failed delivery
- T04 failed delivery
- T05 written
- T06 failed delivery
- artifact 36.43/100
- delivery-adjusted 25.72/100
- classification `COMPLETE`

Top-level runner printed `4B_HIGHER`, delta -25.72, but overall classification is `PARTIAL`.

Canonical interpretation:
> **Do not use the printed `4B_HIGHER` as a quality conclusion.** The preregistered decision rule requires both profiles to complete. Q3 suffered a resource abort during the first real coding request. This demonstrates that the current NP1 + Q8_0 KV Q3 profile is API-smoke viable but has not demonstrated workload stability at context 4096 under the frozen LOOM memory guardrail.

Do not expose Q3 to Pi from this result.

# Current checkpoint — Compare 002 resource diagnostic

Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_002_RESOURCE_DIAGNOSTIC`
Inspector: `scripts/inspect_llama_cpp_quality_compare_002.py`
Existing local run:
`results-local/llama-cpp/coding-quality-compare-002/20260819-114848`

The inspector is read-only and must recover:
- exact Q3 `guardrail_abort_reason`;
- Q3 peak RSS / peak swap / minimum free-memory percentage;
- final memory samples around T01;
- whether T01 produced an HTTP/API response before the abort;
- relevant server/KV/context/request log lines.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_llama_cpp_quality_compare_002.py
python3 scripts/inspect_llama_cpp_quality_compare_002.py \
  results-local/llama-cpp/coding-quality-compare-002/20260819-114848
```

No model is launched by this inspector.

## Decision after diagnostic

- If the abort is a real free-memory/swap breach caused during T01 generation, freeze Q3 as **smoke-pass / workload-fail** for this exact context/runtime. Do not infer coding quality from Compare 002.
- Only after identifying the mechanism decide whether one separately preregistered memory intervention is scientifically justified or whether the main branch should move to Phase 5 Direct MLX.
- Do not lower the 5% guardrail, reduce context inside this failed condition, relax delivery rules, or test ~9B before the 8B frontier is resolved.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
