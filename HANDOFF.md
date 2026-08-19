# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated. Qwen3 8B Q2 is technically runnable/API-servable but loses the frozen structured coding benchmark to 4B Q4. Qwen3 8B Q3_K_M now has its first technical/API FULL_PASS at context 4096 using explicit single-slot server configuration plus Q8_0 K/V KV cache. The active checkpoint is the frozen Q3-vs-4B coding quality comparison before any Pi integration.
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

Free disk is a standard LOOM metric. Reuse verified artifacts; never silently delete verified models or canonical results.

Latest confirmed:
- Coding Quality Compare 001 after: 43.591 GiB free
- Q3 Auto-Fit NP1 Server Smoke 001 after: 43.632 GiB free
- Q3 Auto-Fit NP1 Q8 KV Server Smoke 001 before: 43.599 GiB free
- Q3 Auto-Fit NP1 Q8 KV Server Smoke 001 after: **43.597 GiB free**
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained
- no new model download is required for Compare 002

# Frozen baseline / agent state

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

Pi remains the primary local-agent harness. Qwen Code remains secondary/deprioritized because its safe prompt exceeded the 4096 hard budget before first tool use.

# Phase 4 — llama.cpp

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

## Setup / 4B control

Setup Probe 003 run `20260818-234628`: canonical PASS; exact pinned commit; Release build; `llama-cli`, `llama-bench`; Metal ON.

4B Runtime Control 001 run `20260818-235812`:
- Qwen3-4B Q4_K_M, 2.326 GiB
- pp512 230.85 t/s ±0.12
- tg128 22.33 t/s ±0.02
- peak process RSS 1914.91 MB
- peak swap 1097.19 MB
- minimum free memory 22%

## 8B Q4 / Q3 maximum-offload frontier

8B Q4 Capability 001 run `20260819-091424`:
- Qwen3-8B Q4_K_M, 4.682 GiB
- context 4096 / forced `-ngl -1`
- minimum free memory 1%
- frozen 5% guardrail triggered during Stage A
- VALID FAIL

8B Q3 Capability 001 run `20260819-093842`:
- Qwen3-8B Q3_K_M
- context 4096 / forced `-ngl -1`
- peak RSS 1670.48 MB
- peak swap 2269.38 MB
- minimum free memory 1%
- frozen guardrail triggered
- VALID FAIL

Q3 artifact:
- repository `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q3_K_M.gguf`
- SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size 3.841 GiB
- already present locally

# 8B Q2 — technical/API PASS, quality inferior

Recovered Stage A run `20260819-103347`:
- context 4096 / `-ngl -1`
- exit 0, no guardrail
- peak RSS 2092.97 MB
- peak swap 1986.56 MB
- minimum free memory 10%

Stage B run `20260819-103952`: FULL_PASS
- pp512 103.00 t/s ±0.67
- tg128 13.72 t/s ±0.34
- peak RSS 2461.17 MB
- peak swap 1990.38 MB
- minimum free memory 8%

Server Smoke run `20260819-104946`: FULL_PASS
- readiness 5.684 s
- `/v1/chat/completions` returned `OK`
- peak RSS 1729.33 MB
- peak swap 1855.12 MB
- minimum free memory 6%

Coding Quality Compare 001 run `20260819-110234`:
- 8B Q2 delivery-adjusted 0/100
- 4B Q4 delivery-adjusted 34.29/100
- delta -34.29
- relation `4B_HIGHER`

Closed diagnostic:
- all 8B Q2 requests returned HTTP 200 / EOS / non-empty syntactically valid JSON;
- T01/T02/T03/T04/T06 treated prompt placeholder `filename` as a literal schema key and omitted file content;
- T05 generated code but returned `filename/value` rather than filename->content map;
- 4B Q4 under identical transport delivered T01/T02/T05/T06 correctly.

Canonical boundary:
> Qwen3-8B Q2_K is technically runnable and API-servable on the reference machine but is not established as a practical upgrade over Qwen3-4B Q4_K_M for this structured coding workload. Evidence is profile-level; it does not prove Q2 quantization alone is the cause.

# Q3 automatic-fit rescue sequence

## Auto-Fit Server Smoke 001 — VALID FAIL

Run `20260819-111648`:
- Q3_K_M / context 4096
- no forced `-ngl -1`
- `--fit on --fit-target 1024 --fit-ctx 4096`
- default KV precision
- server parallelism auto
- peak RSS 2121.86 MB
- peak swap 2263.31 MB
- minimum free memory 4%
- guardrail triggered

Diagnostic showed:
```text
initializing, n_slots = 4, n_ctx_slot = 4096, kv_unified = 'true'
model loaded
```

Pinned llama-server resolves auto `n_parallel` to 4 in single-model mode, motivating a controlled `-np 1` test.

## Auto-Fit NP1 Server Smoke 001 — VALID FAIL

Run `20260819-112818`:
- exact same Q3 artifact/runtime policy except explicit `-np 1`
- `n_slots = 1`, `n_ctx_slot = 4096`, `kv_unified = false`: PASS
- peak RSS 2100.44 MB
- peak swap 2295.94 MB
- minimum free memory 4%
- guardrail `memory free 4% < 5%`
- API smoke not authorized to complete
- VALID FAIL

Interpretation:
> Reducing server parallelism from four slots to one did not recover the frozen safety margin. Four-way concurrency was not the dominant cause.

Record:
`research/runtime/llama-cpp-8b-q3-autofit-np1-server-smoke-001.md`

## Auto-Fit NP1 Q8 KV Server Smoke 001 — FULL_PASS

Run `20260819-113658`.
Plan: `research/runtime/llama-cpp-8b-q3-autofit-np1-q8-server-smoke-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q3-autofit-np1-q8-server-smoke-001.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_np1_q8_server_smoke.py`

Frozen condition relative to NP1:
- keep exact Q3 artifact/SHA;
- keep context 4096;
- keep `-np 1`;
- keep FA auto;
- keep `--fit on --fit-target 1024 --fit-ctx 4096`;
- keep no forced `-ngl -1`;
- change only target K/V KV cache from F16/F16 to Q8_0/Q8_0;
- same 5% free-memory / 5600 MB swap guardrails.

Observed:
- disk before 43.599 GiB
- model SHA PASS
- model size 3.841 GiB
- llama-server target present
- readiness **PASS (8.756 s)**
- slot evidence `n_slots=1`: **PASS**
- Q8_0 KV command evidence: **PASS**
- API smoke: **PASS**
- assistant content: `OK`
- peak process RSS **2246.75 MB**
- peak swap **2113.88 MB**
- minimum free memory **6%**
- classification **FULL_PASS**
- disk after **43.597 GiB**

Server evidence:
```text
initializing, n_slots = 1, n_ctx_slot = 4096, kv_unified = 'false'
```

Canonical interpretation:
> This exact Qwen3-8B Q3_K_M + NP1 + Q8_0-KV profile is technically API-servable at context 4096 under the frozen LOOM safety criterion. The safety margin is narrow (6% minimum free, one point above the 5% guardrail), so full-workload testing must keep the same guardrails.

Do not expose Q3 to Pi yet.

# Current checkpoint — Coding Quality Compare 002

Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_002_READY`
Plan: `research/runtime/llama-cpp-coding-quality-compare-002-plan.md`
Runner: `scripts/llama_cpp_coding_quality_compare_002.py`

Research question:
> Does the technically viable Qwen3-8B Q3_K_M profile deliver higher structured coding quality than Qwen3-4B Q4_K_M when both use the same pinned llama-server runtime and the same frozen Coding Benchmark 01 v1.0.1?

Profiles:
1. Qwen3-8B Q3_K_M
2. Qwen3-4B Q4_K_M

Common server policy for **both** profiles:
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

Common request envelope:
```text
POST /completion
n_predict = 2048
temperature = 0
seed = 0
stream = false
cache_prompt = false
json_schema = {}
```

Benchmark discipline:
- Coding Benchmark 01 v1.0.1, T01–T06;
- same frozen prompts/fixtures;
- same adapter/parser/scorer as Compare 001;
- one attempt per task;
- no retries;
- no test feedback;
- no salvage;
- no prompt changes;
- delivery-adjusted score is primary.

The Compare 002 runner verifies the exact Compare 001 template blob `c8aeac7a56830abca633f0a6629be2c640d115f9`, then transforms only the preregistered profile/runtime fields. It refuses execution if the generated implementation lacks NP1/Q8/auto-fit settings or still contains forced `-ngl -1`.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_coding_quality_compare_002.py
python3 scripts/llama_cpp_coding_quality_compare_002.py
```

No model download is expected.

Preserve output from `LOOM llama.cpp Coding Quality Compare 002` through `Summary:`.

## Decision after Compare 002

If both profiles are `COMPLETE` and Q3 delivery-adjusted score is higher:
1. freeze quality result;
2. Q3 becomes the leading llama.cpp candidate;
3. preregister an isolated Pi integration / Pi Agentic validation;
4. production Pi config remains untouched.

If both are `COMPLETE` and 4B is higher or tied:
1. do not expose Q3 to Pi as an assumed upgrade;
2. close the current llama.cpp 8B frontier;
3. move the main research branch to Phase 5 Direct MLX.

If comparison is `PARTIAL` because of resource/harness failure:
1. inspect persisted artifacts;
2. identify exact mechanism before changing any parameter;
3. do not infer a clean quality ordering from a resource-failed profile.

Do not relax benchmark delivery rules post hoc, lower the safety guardrail, or test ~9B before this gate is resolved.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — Q2 technical pass but quality inferior; Q3 NP1/Q8 technical/API FULL_PASS; Coding Quality Compare 002 READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
