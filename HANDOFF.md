# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated; 8B Q2 is technically runnable/API-servable but failed the frozen structured coding delivery benchmark; diagnostic confirms Q2 instruction/delivery degradation rather than a transport/resource defect. Next checkpoint: higher-quality 8B Q3 under llama.cpp automatic fit / partial offload.
Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_SERVER_SMOKE_001_READY`

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

Normal Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration where needed.

## Storage hygiene

Free disk is a standard LOOM metric. Reuse verified artifacts and never silently delete models/results.

Latest confirmed:
- Coding Quality Compare 001 before: 44.594 GiB free
- Coding Quality Compare 001 after: 43.591 GiB free
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained
- no new model download is required for the current Q3 auto-fit test

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

Pi remains the primary local agent harness. Do not test a new llama.cpp profile through Pi until it first passes the technical/API and frozen quality gates.

# Phase 4 — llama.cpp

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

## Setup / 4B control

Setup Probe 003 run `20260818-234628`: canonical PASS, Release build, `llama-cli`, `llama-bench`, Metal ON.

4B Runtime Control 001 run `20260818-235812`:
- Qwen3-4B Q4_K_M, 2.326 GiB
- pp512 230.85 t/s ±0.12
- tg128 22.33 t/s ±0.02
- peak RSS 1914.91 MB
- peak swap 1097.19 MB
- minimum free memory 22%

## 8B quantization frontier

8B Q4 Capability 001 run `20260819-091424`: VALID FAIL; context 4096 / forced `-ngl -1`; minimum free memory 1%; 5% guardrail triggered during Stage A.

8B Q3 Capability 001 run `20260819-093842`: VALID FAIL; Qwen3-8B Q3_K_M; context 4096 / forced `-ngl -1`; peak RSS 1670.48 MB; peak swap 2269.38 MB; minimum free memory 1%; 5% guardrail triggered.

Q3 artifact:
- repository `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q3_K_M.gguf`
- expected SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- already present locally

## 8B Q2 — technical/API PASS

Capability 003 recovered Stage A run `20260819-103347`:
- exact `-c 4096`, `-ngl -1`, `-st`
- Metal preflight
- exit 0, no timeout/guardrail
- peak RSS 2092.97 MB
- peak swap 1986.56 MB
- minimum free memory 10%

Stage B 001 run `20260819-103952`: FULL_PASS
- Qwen3-8B Q2_K, 3.056 GiB
- pp512 103.00 t/s ±0.67
- tg128 13.72 t/s ±0.34
- peak RSS 2461.17 MB
- peak swap 1990.38 MB
- minimum free memory 8%

Server Smoke 001 run `20260819-104946`: FULL_PASS
- context 4096 / `-ngl -1`
- readiness 5.684 s
- `/v1/chat/completions` returned `OK`
- peak RSS 1729.33 MB
- peak swap 1855.12 MB
- minimum free memory 6%

Canonical technical record: `research/runtime/llama-cpp-8b-q2-technical-pass.md`.

# Coding Quality Compare 001 — COMPLETE / 4B_HIGHER

Run `20260819-110234`.
Records:
- `research/runtime/llama-cpp-coding-quality-compare-001-plan.md`
- `research/runtime/llama-cpp-coding-quality-compare-001.md`
- `research/runtime/llama-cpp-coding-quality-compare-001-diagnostic.md`

Frozen comparison:
- LOOM Coding Benchmark 01 v1.0.1, single-shot
- same pinned llama.cpp/Metal/llama-server runtime
- context 4096 / `-ngl -1` / FA auto
- raw `POST /completion`
- exact frozen adapter-built prompts
- one request/task, no retry/salvage/test feedback
- `n_predict=2048`, temperature 0, seed 0, cache_prompt false, `json_schema={}`

Primary result:
- 8B Q2 delivery-adjusted **0/100**
- 4B Q4 delivery-adjusted **34.29/100**
- delta 8B-4B **-34.29**
- relation **`4B_HIGHER`**
- both profiles `COMPLETE`

8B resource state during quality run:
- server ready
- no guardrail abort
- no execution failure
- peak RSS 1953.02 MB
- peak swap 2026.44 MB
- minimum free memory 7%

## Closed failure-mode diagnostic

All six 8B requests returned HTTP 200, `stop_type=eos`, non-empty content and syntactically valid JSON. Therefore the 0/100 delivery result is not a server, HTTP, timeout, memory or JSON-syntax failure.

Observed Q2 pattern:
- T01/T02/T03/T04/T06 returned `{"files":{"filename":"<actual expected name>"}}` or equivalent, treating the illustrative placeholder word `filename` as a literal schema key and omitting file contents;
- T05 generated a substantial code body but returned it as `{"files":{"filename":"order.py","value":"..."}}` instead of `{ "files": { "order.py": "..." } }`.

The 4B control used the same transport/settings and correctly delivered T01, T02, T05 and T06 in the exact required file envelope. Its T03/T04 failures remain valid strict delivery failures.

Canonical conclusion:
> Qwen3-8B Q2_K is technically runnable and API-servable, but its aggressive Q2 quantization does not preserve reliable structured instruction following on the frozen coding workload. It is **not a practical upgrade** over Qwen3-4B Q4_K_M for this use case.

Do not create a post-hoc easier Q2 benchmark, do not salvage T05 into the primary score, and do not proceed to Pi or ~9B from this Q2 profile.

# Current checkpoint — 8B Q3 Auto-Fit Server Smoke 001

Plan: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-plan.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_server_smoke.py`
Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_SERVER_SMOKE_001_READY`

Research question:
> Can the higher-quality Q3_K_M weights fit and serve at context 4096 if llama.cpp may choose automatic device fit / partial offload instead of forced `-ngl -1`?

Frozen condition:
- same local Q3_K_M artifact / exact SHA256
- pinned llama.cpp / Metal / llama-server
- explicit `-c 4096`
- FA auto
- do not force `-ngl -1`
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- default KV-cache types; no KV quantization in this experiment
- localhost only / Web UI disabled / offline
- same 5% free-memory and 5600 MB swap guardrails
- one `Reply only with OK.` chat completion if server reaches healthy state

The runner records server logs and extracts fit/offload/GPU-layer-related lines where available.

## Exact next step

Run:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q3_autofit_server_smoke.py
python3 scripts/llama_cpp_8b_q3_autofit_server_smoke.py
```

No model download is expected.

Preserve output from `LOOM llama.cpp 8B Q3 Auto-Fit Server Smoke 001` through the final `Summary:` line, including any `Auto-fit/offload evidence:` lines.

## Decision after Q3 auto-fit

- If `FULL_PASS`: freeze the actual observed fit/offload behavior, then preregister Q3 vs 4B Q4 on the frozen Coding Benchmark 01 before any Pi test.
- If `FAIL`: do not alter several parameters at once. Next candidate is a separately preregistered Q3 KV-cache compression condition, starting Q8_0, or Direct MLX.
- Do not test ~9B until the 8B quality/usefulness frontier is characterized.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — Q2 technical/API PASS but quality inferior; Q3 auto-fit rescue READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
