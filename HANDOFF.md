# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated; 8B Q2 has technical FULL PASS and llama-server FULL PASS, but frozen Coding Quality Compare 001 strongly favored 4B Q4 on delivery. Exact 8B failure classes are now the active diagnostic.
Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_001_DIAGNOSTIC`

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
- quality compare before: 44.594 GiB free
- quality compare after: 43.591 GiB free
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained

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

Pi remains the primary local agent harness. Qwen Code remains secondary/deprioritized because its safe mode still exceeded a 4096 hard prompt budget before first tool use.

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

8B Q4 Capability 001 run `20260819-091424`: VALID FAIL; context 4096 / `-ngl -1`; minimum free memory 1%; 5% guardrail triggered during Stage A.

8B Q3 Capability 001 run `20260819-093842`: VALID FAIL; context 4096 / `-ngl -1`; minimum free memory 1%; guardrail triggered.

8B Q2 harness 001/002 were invalidated by CLI/parser defects. Capability 003 run `20260819-103347` provides recovered Stage A PASS evidence:
- exact `-c 4096`, `-ngl -1`, `-st`
- Metal preflight
- exit 0, no timeout, no guardrail
- peak RSS 2092.97 MB
- peak swap 1986.56 MB
- minimum free memory 10%

8B Q2 Stage B 001 run `20260819-103952`: FULL_PASS
- Qwen3-8B Q2_K, 3.056 GiB
- pp512 103.00 t/s ±0.67
- tg128 13.72 t/s ±0.34
- peak RSS 2461.17 MB
- peak swap 1990.38 MB
- minimum free memory 8%

Canonical technical record: `research/runtime/llama-cpp-8b-q2-technical-pass.md`.

## 8B Q2 llama-server smoke — FULL PASS

Run `20260819-104946`:
- localhost llama-server
- context 4096 / `-ngl -1` / FA auto
- readiness PASS in 5.684 s
- `/v1/chat/completions` PASS, assistant content `OK`
- peak RSS 1729.33 MB
- peak swap 1855.12 MB
- minimum free memory 6%

Record: `research/runtime/llama-cpp-8b-q2-server-smoke-001.md`.

Interpretation: API serving works, but server memory headroom is narrow: 6% minimum free vs 5% abort threshold.

# Coding Quality Compare 001 — COMPLETE

Run id: `20260819-110234`
Plan: `research/runtime/llama-cpp-coding-quality-compare-001-plan.md`
Result: `research/runtime/llama-cpp-coding-quality-compare-001.md`
Runner: `scripts/llama_cpp_coding_quality_compare.py`

Frozen comparison:
- LOOM Coding Benchmark 01 v1.0.1, `single_shot`
- same pinned llama.cpp/Metal/llama-server runtime
- context 4096, `-ngl -1`, FA auto
- raw `POST /completion`
- exact existing adapter-built prompts
- one request/task, no retry/salvage/test feedback
- `n_predict=2048`, temperature 0, seed 0, stream false, cache_prompt false, `json_schema={}`
- 8B Q2 first, then 4B Q4

Observed:

### 8B Q2
- server ready 6.294 s
- T01–T06 all adapter `failed`
- artifact 15.0/100
- delivery-adjusted **0/100**
- profile `COMPLETE`

### 4B Q4
- server ready 1.043 s
- T01 written
- T02 written
- T03 failed
- T04 failed
- T05 written
- T06 written
- artifact 42.86/100
- delivery-adjusted **34.29/100**
- profile `COMPLETE`

Primary frozen comparison:
- delta 8B-4B = **-34.29**
- relation = **`4B_HIGHER`**
- overall classification = `COMPLETE`

Canonical boundary:
> Under the frozen end-to-end delivery metric, 4B Q4 clearly beats 8B Q2. Therefore Q2 8B is **not established as a practical upgrade** despite technical runtime PASS.

Do not yet claim the 8B has zero semantic coding ability: all six 8B outputs failed at the adapter/delivery layer. The persisted raw responses must be inspected before deciding whether this is primarily Q2 semantic/instruction degradation, malformed JSON/file-envelope behavior, or a transport-specific defect.

Also do not treat the 8B artifact 15/100 as 15 model-earned points: failed adapter outputs are not written into the working tree, so some artifact score can come from the benchmark's starting fixture state.

# Current checkpoint — failure-mode diagnostic

Inspector: `scripts/inspect_llama_cpp_quality_compare.py`

The inspector reads the existing run only. It does **not** start llama-server or rerun any model.

Exact next step:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_llama_cpp_quality_compare.py
python3 scripts/inspect_llama_cpp_quality_compare.py \
  results-local/llama-cpp/coding-quality-compare-001/20260819-110234
```

Preserve the complete inspector output. Required fields include, per task:
- adapter status/error
- HTTP status
- stop type
- token counts
- content presence/length
- JSON shape
- short response prefix
- profile telemetry/guardrail state

## Decision after diagnostic

- If 8B failures are genuine malformed/instruction-following outputs under otherwise healthy API requests, freeze Q2 as technically runnable but qualitatively/protocol-wise inferior for this workload. Next research branch: separately preregister higher-quality Q3/Q4 memory strategies (e.g. partial offload) and/or Direct MLX.
- If failures expose a transport/harness defect specific to the frozen comparison, keep Compare 001 primary result unchanged but preregister a corrected Compare 002; never silently reinterpret or overwrite Compare 001.
- Do not proceed to Pi or ~9B until this diagnostic closes the 8B usefulness frontier.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 8B Q2 TECHNICAL FULL PASS + server PASS, but Coding Quality Compare 001 = 4B_HIGHER; diagnostic active**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
