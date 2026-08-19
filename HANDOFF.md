# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — llama.cpp/Metal validated; 4B Q4 control PASS; 8B Q4/Q3 fail the frozen memory guardrail; 8B Q2 has canonical technical FULL PASS and llama-server API FULL PASS; next checkpoint is the frozen same-runtime coding quality comparison against 4B Q4.
Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_001_READY`

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

Normal Pi contains real auth, sessions and customizations. LOOM must not reset or replace it. Controlled experiments use isolated/run-local Pi configuration where required.

## Storage hygiene

Free disk is a standard LOOM metric. Reuse verified artifacts and never silently delete models/results.

Latest confirmed disk observations:
- before 8B Q4: 56.285 GiB free
- after 8B Q4: 50.567 GiB free
- after 8B Q3: 46.763 GiB free
- Q2 Stage B 001 after: 43.688 GiB free
- 8B Q2 Server Smoke 001 before: 44.696 GiB free
- 8B Q2 Server Smoke 001 after: **43.611 GiB free**
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained

No new model download is required for the current quality comparison.

# Frozen baseline / agent state

## Coding Baseline 001
- run `20260818-203156`
- Ollama/MLX `qwen3.5:4b-mlx`, context 4096
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s

## Pi Agentic Coding Benchmark 001
- run `20260818-214848`
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6
- provider usage 20,209 total tokens

Pi remains the primary local agent harness. Qwen Code is secondary/deprioritized because even safe mode estimated 4363 prompt tokens against a 4096 hard limit before first tool use.

## Agentic memory investigation — practical conclusion

Historical warm Agentic 001 Ollama SIZE rose 4.4 -> 7.2 GB. Controlled probes and exact cold replays showed retained warm high-water across heterogeneous workloads is a major contributor. Exact internal mechanism remains unresolved; do not label it a leak/KV/allocator defect without further evidence.

# Phase 4 — llama.cpp

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

## Setup Probe 003 — CANONICAL PASS

Run `20260818-234628`:
- exact pinned commit
- Release build PASS
- `llama-cli` PASS
- `llama-bench` PASS
- Metal ON, embedded Metal library ON

Record: `research/runtime/llama-cpp-setup-probe-003.md`.

## 4B Runtime Control 001 — CANONICAL PASS

Run `20260818-235812`.

Artifact:
- Qwen3-4B Q4_K_M
- official `Qwen/Qwen3-4B-GGUF`
- size 2.326 GiB

Observed:
- pp512 **230.85 t/s ± 0.12**
- tg128 **22.33 t/s ± 0.02**
- peak process RSS **1914.91 MB**
- peak swap **1097.19 MB**
- minimum free memory **22%**

Record: `research/runtime/llama-cpp-4b-control-001.md`.

## 8B Q4 Capability 001 — VALID FAIL

Run `20260819-091424`:
- Qwen3-8B Q4_K_M, 4.682 GiB
- context 4096 / `-ngl -1`
- minimum free memory **1%**
- 5% guardrail triggered during Stage A
- Stage B skipped

Record: `research/runtime/llama-cpp-8b-q4-001.md`.

## 8B Q3 Capability 001 — VALID FAIL

Run `20260819-093842`:
- Qwen3-8B Q3_K_M
- context 4096 / `-ngl -1`
- minimum free memory **1%**
- peak RSS 1670.48 MB
- peak swap 2269.38 MB
- 5% guardrail triggered

Record: `research/runtime/llama-cpp-8b-q3-001.md`.

## 8B Q2 harness chronology

Capability 001 was INVALID because inherited `llama-cli` Stage A remained interactive. Capability 002 was INVALID because its parser required optional literal log strings. Capability 003 completed a real single turn and exited 0; post-run inspection proved the final false `output_nonempty` field was a TTY/capture defect.

Recovered Capability 003 Stage A evidence, run `20260819-103347`:
- exact `-c 4096`
- exact `-ngl -1`
- `-st`
- Metal preflight evidence
- exit 0
- no timeout
- no guardrail abort
- wall 7.134 s
- peak RSS 2092.97 MB
- peak swap 1986.56 MB
- minimum free memory **10%**
- visible prompt ~42.7 t/s
- visible generation ~13.4 t/s

Record: `research/runtime/llama-cpp-8b-q2-003-recovered-stage-a.md`.

## 8B Q2 Stage B 001 — FULL PASS

Run `20260819-103952`:
- Qwen3-8B Q2_K, 3.056 GiB
- `llama-bench`, `-ngl -1`, FA auto
- pp512 **103.00 t/s ± 0.67**
- tg128 **13.72 t/s ± 0.34**
- backend `MTL,BLAS`
- wall **53.536 s**
- peak RSS **2461.17 MB**
- peak swap **1990.38 MB**
- minimum free memory **8%**
- no guardrail breach
- classification **FULL_PASS**

Records:
- `research/runtime/llama-cpp-8b-q2-stage-b-001.md`
- `research/runtime/llama-cpp-8b-q2-technical-pass.md`

Canonical technical conclusion:
> Qwen3 8B Q2_K is technically runnable on the reference M1/8GB machine under pinned llama.cpp/Metal at context 4096 and can complete the frozen throughput workload without violating LOOM safety guardrails.

Descriptive scaling vs 4B Q4:
- prompt throughput: 103.00 vs 230.85 t/s
- generation throughput: 13.72 vs 22.33 t/s
- 8B generation retains ~61.4% of 4B speed
- minimum free memory: 8% vs 22%

Q2 is an aggressive quantization; this does not establish better useful quality.

## 8B Q2 Server Smoke 001 — CANONICAL FULL PASS

Run `20260819-104946`.
Plan: `research/runtime/llama-cpp-8b-q2-server-smoke-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q2-server-smoke-001.md`
Runner: `scripts/llama_cpp_8b_q2_server_smoke.py`

Frozen profile:
- same verified Q2_K artifact
- pinned llama.cpp
- `llama-server`
- context 4096
- `-ngl -1`
- Flash Attention auto
- localhost only
- Web UI disabled
- same 5% free-memory / 5600 MB swap guardrails

Observed:
- model SHA256 PASS
- `llama-server` build PASS
- readiness **PASS in 5.684 s**
- `/v1/chat/completions` **PASS**
- assistant content `OK`
- peak process RSS **1729.328125 MB**
- peak swap **1855.12 MB**
- minimum free memory **6%**
- classification **FULL_PASS**
- disk free after **43.611 GiB**

Interpretation:
> The 8B Q2 profile can serve a real local API request at context 4096, but its server headroom is narrow: 6% minimum free memory is only one point above the frozen 5% abort threshold.

# Current checkpoint — Coding Quality Compare 001

Plan: `research/runtime/llama-cpp-coding-quality-compare-001-plan.md`
Runner: `scripts/llama_cpp_coding_quality_compare.py`
Checkpoint: `LLAMA_CPP_CODING_QUALITY_COMPARE_001_READY`

Research question:
> Does Qwen3-8B Q2_K actually outperform Qwen3-4B Q4_K_M on the frozen coding suite when both use the same pinned llama.cpp/Metal runtime?

Frozen benchmark:
- LOOM Coding Benchmark 01 v1.0.1
- `single_shot`
- T01–T06 unchanged
- 100 total points
- exact existing adapter prompt construction
- one attempt/task
- no hidden test feedback
- no retry/salvage

Compared profiles:
1. Qwen3-8B Q2_K — run first
2. Qwen3-4B Q4_K_M — run second

Same runtime settings:
- pinned llama.cpp commit
- `llama-server`
- context 4096
- `-ngl -1`
- FA auto
- one model server at a time
- localhost only

Transport:
- raw `POST /completion`
- exact adapter-built prompt string
- `n_predict=2048`
- `temperature=0`
- `seed=0`
- `stream=false`
- `cache_prompt=false`
- `json_schema={}`

The runner verifies the frozen single-shot adapter Git blob `62abab57f6463c5813809b43d8f1e7bdfec5f304` before use. `cache_prompt=false` is frozen because the pinned server documentation warns prompt-cache reuse can change logits depending on batching.

Safety:
- abort active server below 5% free memory
- abort above 5600 MB swap
- preserve partial results; no rescue

Primary metric:
- delivery-adjusted score /100

Secondary:
- artifact score
- per-task scores/failure modes

Output relation is descriptive only: `8B_HIGHER`, `4B_HIGHER`, or `TIE`.

## Exact next step

Run:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_coding_quality_compare.py
python3 scripts/llama_cpp_coding_quality_compare.py
```

No model download is expected. The run executes 8B first, fully shuts it down, waits 5 seconds, then runs 4B.

Avoid starting unrelated memory-heavy applications during the run because the 8B server has only a small demonstrated margin above the safety guardrail.

Preserve output from `LOOM llama.cpp Coding Quality Compare 001` through the final `Summary:` line.

## Decision after quality comparison

- If `8B_HIGHER`: proceed to a controlled Pi/agent compatibility smoke through llama-server before any full agentic benchmark.
- If `4B_HIGHER` or `TIE`: do not call 8B Q2 a practical upgrade solely from parameter count; investigate a separately frozen higher-quality memory strategy (e.g. partial offload Q3/Q4) and/or Direct MLX.
- Do not test ~9B until the 8B quality/usefulness frontier is characterized.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B Q4 PASS; 8B Q4/Q3 memory FAIL; 8B Q2 TECHNICAL FULL PASS; llama-server FULL PASS; coding quality compare READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
