# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated; 8B Q2 is technically runnable/API-servable but loses the frozen structured coding benchmark to 4B Q4; 8B Q3 automatic-fit server rescue also hit the frozen memory guardrail. The active checkpoint is inspection of the saved Q3 fit/offload evidence before changing any parameter.
Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_SERVER_SMOKE_001_DIAGNOSTIC`

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

Normal Pi contains real auth, sessions and customizations. LOOM must never reset/replace production Pi configuration. Controlled experiments use isolated/run-local configuration where needed. Do not expose a new llama.cpp profile to Pi until it passes technical/API and quality gates.

## Storage hygiene

Free disk is a standard LOOM metric. Reuse verified artifacts and never silently delete models/results.

Latest confirmed:
- Coding Quality Compare 001 after: 43.591 GiB free
- Q3 Auto-Fit Server Smoke 001 before: 43.659 GiB free
- Q3 Auto-Fit Server Smoke 001 after: **43.658 GiB free**
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained
- no new model download is currently required

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

8B Q3 Capability 001 run `20260819-093842`: VALID FAIL; context 4096 / forced `-ngl -1`; peak RSS 1670.48 MB; peak swap 2269.38 MB; minimum free memory 1%; guardrail triggered.

Q3 artifact:
- repository `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q3_K_M.gguf`
- SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size 3.841 GiB
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

Primary result:
- 8B Q2 delivery-adjusted **0/100**
- 4B Q4 delivery-adjusted **34.29/100**
- delta 8B-4B **-34.29**
- relation **`4B_HIGHER`**
- both profiles `COMPLETE`

Closed diagnostic:
- every 8B task returned HTTP 200, EOS, non-empty syntactically valid JSON;
- T01/T02/T03/T04/T06 used literal `filename` as the file key and omitted actual file contents;
- T05 generated code but encoded it under `filename/value` instead of the exact required filename-to-content map;
- 4B Q4 under the identical transport delivered T01/T02/T05/T06 correctly.

Canonical boundary:
> The tested Qwen3-8B Q2_K profile is technically runnable and API-servable but is not a practical upgrade over Qwen3-4B Q4_K_M for this structured coding workload. The evidence establishes profile-level instruction/delivery degradation; it does not by itself prove that Q2 quantization alone is the cause.

Do not relax the benchmark envelope post hoc and do not proceed to Pi or ~9B from the Q2 profile.

# 8B Q3 Auto-Fit Server Smoke 001 — VALID FAIL

Run id: `20260819-111648`
Plan: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_server_smoke.py`

Frozen condition:
- same verified Q3_K_M artifact
- pinned llama.cpp / `llama-server` / Metal
- explicit context 4096
- FA auto
- no forced `-ngl -1`
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- default KV-cache types
- localhost only / offline / no Web UI
- same 5% free-memory and 5600 MB swap guardrails

Observed:
- disk before 43.659 GiB
- model SHA256 PASS
- model size 3.841 GiB
- server target present
- automatic-fit launch started
- API smoke FAIL
- peak process RSS **2121.859375 MB**
- peak swap **2263.31 MB**
- minimum free memory **4%**
- guardrail `memory free 4% < 5%`
- classification **FAIL**
- disk after **43.658 GiB**

Interpretation:
> This exact Q3 auto-fit condition is not safe enough under the frozen LOOM margin. The console output does not establish the exact fit/offload decision; inspect the persisted summary/logs before choosing the next memory intervention.

Descriptively, 4% minimum free is less severe than the 1% observed in the earlier forced-Q3 run, but the execution shapes differ and this is not an apples-to-apples performance comparison.

# Current checkpoint — Q3 auto-fit diagnostic

Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_SERVER_SMOKE_001_DIAGNOSTIC`

Existing local run directory:
`results-local/llama-cpp/8b-q3-autofit-server-smoke/20260819-111648`

Need to inspect, without rerunning inference:
- `server_ready`
- `request_pass`
- `failure_reason`
- final `/health` states
- `fit_offload_log_lines`
- final memory samples
- relevant `llama-server-stderr.txt` lines around fit/offload/layer placement

## Decision after diagnostic

- If fit logs show auto-fit still retained essentially maximum Metal placement and the failure occurred during load/readiness, preregister one-variable Q3 KV-cache compression starting with Q8_0 only if the expected memory source can plausibly affect the failing phase.
- If the guardrail fires before KV allocation or logs show a weights/device-placement bottleneck, KV compression is unlikely to solve the load failure; prefer an explicit partial-offload experiment or move to Direct MLX.
- Do not lower the safety guardrail, context, and quantization simultaneously.
- Do not test ~9B yet.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — Q2 technical/API PASS but quality inferior; Q3 forced offload FAIL; Q3 auto-fit FAIL at 4% free; fit/offload diagnostic active**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
