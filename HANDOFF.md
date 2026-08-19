# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated; Q2 is technically runnable/API-servable but loses the frozen structured coding benchmark to 4B Q4; Q3 forced-offload and Q3 auto-fit both hit the memory guardrail. Diagnostic found pinned llama-server auto parallelism created four 4096-token slots; next checkpoint is an explicit single-slot (`-np 1`) Q3 auto-fit smoke.
Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_NP1_SERVER_SMOKE_001_READY`

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
- no new model download is required for the NP1 test

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

## 8B Q2 — technical/API PASS but quality inferior

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

Coding Quality Compare 001 run `20260819-110234`:
- 8B Q2 delivery-adjusted **0/100**
- 4B Q4 delivery-adjusted **34.29/100**
- delta -34.29
- relation `4B_HIGHER`
- diagnostic: all 8B requests HTTP 200 / EOS / valid JSON, but the 8B profile repeatedly treated `filename` as a literal schema key; T05 generated code under `filename/value`; 4B under identical transport delivered 4/6 tasks correctly.

Canonical boundary:
> The tested Qwen3-8B Q2_K profile is technically runnable and API-servable but is not a practical upgrade over Qwen3-4B Q4_K_M for this structured coding workload. The evidence establishes profile-level instruction/delivery degradation; it does not prove Q2 quantization alone is the cause.

Records:
- `research/runtime/llama-cpp-8b-q2-technical-pass.md`
- `research/runtime/llama-cpp-coding-quality-compare-001.md`
- `research/runtime/llama-cpp-coding-quality-compare-001-diagnostic.md`

# 8B Q3 Auto-Fit Server Smoke 001 — VALID FAIL

Run id: `20260819-111648`
Plan: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_server_smoke.py`

Frozen condition:
- same verified Q3_K_M artifact
- pinned llama.cpp / `llama-server` / Metal
- context 4096
- FA auto
- no forced `-ngl -1`
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- default KV-cache types
- server parallelism left at llama-server automatic default
- same 5% free-memory / 5600 MB swap guardrails

Observed:
- SHA PASS; size 3.841 GiB
- peak process RSS **2121.859375 MB**
- peak swap **2263.31 MB**
- minimum free memory **4%**
- guardrail `memory free 4% < 5%`
- runner classification FAIL
- disk after 43.658 GiB

## Closed diagnostic — default four-slot server behavior

Record: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-diagnostic.md`.

Saved health history:
- startup connection refused at ~0 s;
- HTTP 503 `Loading model` from ~1.0 through 6.2 s;
- guard sample at 7.228 s: free memory 4%, swap 2263.31 MB.

Critical stderr:
```text
0.07.342.019 ... initializing, n_slots = 4, n_ctx_slot = 4096, kv_unified = 'true'
0.07.414.811 ... model loaded
0.07.414.829 ... listening on http://127.0.0.1:18083
0.07.512.566 ... cleaning up before exit
```

Interpretation:
- the guardrail remained valid and fired before a subsequent healthy poll/API request;
- the server actually completed initialization just after the 4% sample;
- failure is in the load/context-initialization window, not generated-token workload;
- no saved fit/offload lines were emitted at the current verbosity;
- pinned `llama-server` defaults `n_parallel` to auto, then resolves auto to **4** with `kv_unified=true` in single-model mode;
- common context creation maps `n_parallel` into `n_seq_max`, and server context creates `n_parallel` slots;
- LOOM uses one request at a time, so four-way concurrency is unnecessary.

This does not prove that four slots alone cause the full memory gap, but it directly justifies testing explicit single-sequence server parallelism before altering KV precision.

# Current checkpoint — Q3 Auto-Fit NP1 Server Smoke 001

Checkpoint: `LLAMA_CPP_8B_Q3_AUTOFIT_NP1_SERVER_SMOKE_001_READY`
Plan: `research/runtime/llama-cpp-8b-q3-autofit-np1-server-smoke-001-plan.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_np1_server_smoke.py`

Research question:
> Can the existing Q3_K_M profile safely serve at context 4096 when server concurrency is explicitly reduced from the observed automatic four slots to one slot?

Frozen condition is identical to Auto-Fit Server Smoke 001 except:
- add `-np 1` / `--parallel 1`.

Unchanged:
- Q3_K_M exact artifact/SHA;
- pinned llama.cpp/Metal;
- context 4096;
- FA auto;
- no forced `-ngl -1`;
- `--fit on --fit-target 1024 --fit-ctx 4096`;
- default KV types;
- localhost/offline/no Web UI;
- one `Reply only with OK.` API smoke;
- same 5% free-memory / 5600 MB swap guardrails.

The runner reuses the exact exercised Q3 auto-fit runner only after verifying its Git blob `9dd7677107601132e57e7c84bd58d0710fb138f9`, adds `-np 1`, and requires stderr evidence `n_slots = 1` for `FULL_PASS`.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q3_autofit_np1_server_smoke.py
python3 scripts/llama_cpp_8b_q3_autofit_np1_server_smoke.py
```

No model download is expected.

Preserve output from `LOOM llama.cpp 8B Q3 Auto-Fit NP1 Server Smoke 001` through `Summary:` including `Slot evidence n_slots=1` and any auto-fit/offload evidence lines.

## Decision after NP1

- If `FULL_PASS`: freeze telemetry and slot evidence, then preregister Q3 vs 4B Q4 Coding Benchmark 01 with explicit `-np 1` for both profiles before any Pi test.
- If memory `VALID FAIL`: do not change context or safety threshold; next single-variable llama.cpp rescue is Q3 KV-cache compression Q8_0, or continue to Direct MLX.
- Do not test ~9B until the useful 8B frontier is resolved.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — Q2 technically passes but quality inferior; Q3 forced/auto-fit memory fail; Q3 NP1 rescue READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
