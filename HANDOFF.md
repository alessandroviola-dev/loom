# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated; 8B Q2 is technically runnable/API-servable but loses the frozen structured coding benchmark to 4B Q4. Q3 forced offload, auto-fit, and explicit single-slot auto-fit all fail the frozen 5% memory guardrail at context 4096. Next checkpoint is a one-variable Q3 KV-cache Q8_0 rescue while retaining single-slot server configuration.
Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_NP1_Q8_SERVER_SMOKE_001_READY`

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

Production Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration where required. Do not expose a new llama.cpp profile to Pi until it first passes technical/API and frozen quality gates.

## Storage hygiene

Free disk is a standard LOOM metric. Reuse verified artifacts; never silently delete models or canonical results.

Latest confirmed:
- Coding Quality Compare 001 after: 43.591 GiB free
- Q3 Auto-Fit Server Smoke 001 after: 43.658 GiB free
- Q3 Auto-Fit NP1 Server Smoke 001 before: 43.628 GiB free
- Q3 Auto-Fit NP1 Server Smoke 001 after: **43.632 GiB free**
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained
- no new model download is required for the Q8 KV test

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

Pi remains the primary local-agent harness. Qwen Code remains secondary/deprioritized because its safe prompt still exceeded the 4096 hard budget before first tool use.

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
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q3_K_M.gguf`
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
> The tested Qwen3-8B Q2_K profile is technically runnable and API-servable but is not established as a practical upgrade over Qwen3-4B Q4_K_M for this structured coding workload. Evidence is profile-level; it does not prove Q2 quantization alone is the cause.

# Q3 automatic-fit branch

## Auto-Fit Server Smoke 001 — VALID FAIL

Run `20260819-111648`:
- Q3_K_M / context 4096
- no forced `-ngl -1`
- `--fit on --fit-target 1024 --fit-ctx 4096`
- default KV precision
- server parallelism left auto
- peak RSS 2121.86 MB
- peak swap 2263.31 MB
- minimum free memory 4%
- guardrail triggered

Diagnostic of saved logs:
```text
initializing, n_slots = 4, n_ctx_slot = 4096, kv_unified = 'true'
model loaded
listening on http://127.0.0.1:18083
```

Pinned llama-server resolves auto `n_parallel` to 4 in single-model mode. This directly motivated a controlled `-np 1` test.

Records:
- `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001.md`
- `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-diagnostic.md`

## Auto-Fit NP1 Server Smoke 001 — VALID FAIL

Run `20260819-112818`.
Plan: `research/runtime/llama-cpp-8b-q3-autofit-np1-server-smoke-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q3-autofit-np1-server-smoke-001.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_np1_server_smoke.py`

Frozen change relative to prior auto-fit run:
- explicit `-np 1` only.

Observed:
- model SHA PASS
- size 3.841 GiB
- slot evidence **PASS**
- stderr: `n_slots = 1, n_ctx_slot = 4096, kv_unified = 'false'`
- peak process RSS **2100.4375 MB**
- peak swap **2295.94 MB**
- minimum free memory **4%**
- guardrail `memory free 4% < 5%`
- API smoke not authorized to complete after guardrail breach
- classification **VALID FAIL**
- disk after **43.632 GiB**

Interpretation:
> Reducing llama-server from four slots to one did not restore the frozen memory margin. Four-way server parallelism is therefore not the dominant cause of this Q3 failure. Do not infer exact system-memory savings from process RSS alone.

# Current checkpoint — Q3 NP1 + Q8_0 KV Server Smoke 001

Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_NP1_Q8_SERVER_SMOKE_001_READY`
Plan: `research/runtime/llama-cpp-8b-q3-autofit-np1-q8-server-smoke-001-plan.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_np1_q8_server_smoke.py`

Pinned llama.cpp facts verified before preregistration:
- `-ctk` / `--cache-type-k` sets main-model K KV-cache type;
- `-ctv` / `--cache-type-v` sets main-model V KV-cache type;
- `q8_0` is supported;
- default main-model K/V cache types are F16/F16.

Research question:
> Can Q3_K_M at context 4096 become safe when the already-controlled NP1 condition is retained and only main-model KV precision changes from F16/F16 to Q8_0/Q8_0?

Frozen condition:
- exact existing Q3 artifact/SHA
- pinned llama.cpp / Metal / llama-server
- context `-c 4096`
- `-np 1`
- `-ctk q8_0`
- `-ctv q8_0`
- FA auto
- no forced `-ngl -1`
- `--fit on --fit-target 1024 --fit-ctx 4096`
- localhost only / offline / no Web UI
- one `Reply only with OK.` chat request only if readiness remains safe
- unchanged guardrails: free memory <5% or swap >5600 MB abort

Only changed variable relative to NP1 is KV precision F16/F16 -> Q8_0/Q8_0.

The runner verifies frozen Q3 auto-fit base blob `9dd7677107601132e57e7c84bd58d0710fb138f9`, requires `n_slots = 1`, records exact Q8 cache command evidence and preserves full telemetry/logs.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q3_autofit_np1_q8_server_smoke.py
python3 scripts/llama_cpp_8b_q3_autofit_np1_q8_server_smoke.py
```

No model download is expected.

Preserve output through `Summary:`, especially:
- `Slot evidence n_slots=1`
- `Q8_0 KV command evidence`
- API smoke
- peak RSS / swap / minimum free memory
- guardrail/classification
- any auto-fit/offload evidence

## Decision after Q8 KV

If `FULL_PASS`:
1. freeze technical/API result;
2. preregister Q3 vs 4B Q4 on frozen Coding Benchmark 01 under explicit single-slot server settings;
3. do not proceed to Pi until Q3 passes the quality gate.

If memory `VALID FAIL`:
1. do not stack more rescue variables immediately;
2. move the main research branch to Phase 5 Direct MLX;
3. a more aggressive llama.cpp KV type can remain a separately justified later experiment, not an automatic rescue.

Do not lower the 5% safety guardrail, alter context inside a failed condition, or test ~9B yet.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — Q2 technical/API pass but quality inferior; Q3 maximum offload fail; Q3 auto-fit fail; Q3 NP1 fail; Q3 NP1 Q8 KV READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
