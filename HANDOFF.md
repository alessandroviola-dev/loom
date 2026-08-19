# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated. Qwen3 8B Q2 is technically runnable/API-servable but loses the frozen structured coding benchmark to 4B Q4. Qwen3 8B Q3_K_M has a technical/API FULL_PASS at context 4096 using NP1 + Q8_0 K/V KV cache. Coding Quality Compare 002 remains the active quality gate; its first invocation was INVALID_HARNESS before any model launch and the runner has been corrected without changing the preregistered experiment.
Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_002_READY`

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

Production Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration where required. Do not expose a new llama.cpp profile to Pi until it passes technical/API and frozen quality gates.

## Storage hygiene

Reuse verified artifacts and never silently delete models or canonical results. Free disk is a standard metric.
Latest confirmed after Q3 NP1 Q8 smoke: **43.597 GiB free**. Verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts are retained. No new model download is required for Compare 002.

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

The safety margin is narrow: 6% minimum free, one point above the 5% guardrail. Full workloads must retain the same guardrails.

# Current checkpoint — Coding Quality Compare 002

Plan: `research/runtime/llama-cpp-coding-quality-compare-002-plan.md`
Runner: `scripts/llama_cpp_coding_quality_compare_002.py`

Research question:
> Does Qwen3-8B Q3_K_M deliver higher structured coding quality than Qwen3-4B Q4_K_M when both run under the same pinned llama-server policy and the frozen Coding Benchmark 01 v1.0.1?

Profiles:
1. Qwen3-8B Q3_K_M
2. Qwen3-4B Q4_K_M

Common server policy for both:
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

Common benchmark/request policy:
- Coding Benchmark 01 v1.0.1, T01–T06
- `POST /completion`
- `n_predict=2048`
- `temperature=0`
- `seed=0`
- `cache_prompt=false`
- `json_schema={}`
- one attempt per task
- no retries, test feedback, salvage or prompt changes
- delivery-adjusted score is primary

## Invalid harness attempt 001

First invocation of Compare 002 stopped immediately with:
```text
Template transform: FAIL — expected one occurrence, found 0
```

Classification: **INVALID_HARNESS**.

No llama-server was launched, no Q3/4B model was loaded and no benchmark task ran. Therefore this attempt produced no scientific data and does not consume the comparison.

Root cause: the wrapper used a template needle with literal escaped newline sequences (`\\n`) rather than actual template newlines; another later needle had the same fragility.

Record:
`research/runtime/llama-cpp-coding-quality-compare-002-invalid-harness-001.md`

Correction commit: Compare 002 transformer now uses smaller unique replacements plus exact profile/server blocks. Pre-execution invariants still require Q3, NP1, Q8_0 K/V, auto-fit and absence of forced `-ngl -1`. No scientific condition changed.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_coding_quality_compare_002.py
python3 scripts/llama_cpp_coding_quality_compare_002.py
```

Preserve output from `LOOM llama.cpp Coding Quality Compare 002` through `Summary:`.

## Decision after Compare 002

If both profiles are `COMPLETE` and Q3 delivery-adjusted score is higher:
1. freeze quality result;
2. Q3 becomes the leading llama.cpp candidate;
3. preregister isolated Pi integration / Pi Agentic validation;
4. production Pi config remains untouched.

If both are `COMPLETE` and 4B is higher or tied:
1. do not expose Q3 to Pi as an assumed upgrade;
2. close the current llama.cpp 8B frontier;
3. move the main branch to Phase 5 Direct MLX.

If comparison is `PARTIAL` because of resource or harness failure:
1. inspect persisted artifacts;
2. identify the exact mechanism before changing any parameter;
3. do not infer a clean quality ordering.

Do not relax benchmark delivery rules, lower the 5% guardrail, reduce context inside a failed condition, or test ~9B before this gate is resolved.
