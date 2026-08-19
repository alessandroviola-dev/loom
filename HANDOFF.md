# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains primary local agent harness; llama.cpp/Metal validated; 4B Q4 control PASS; 8B Q4/Q3 fail frozen memory guardrail; 8B Q2 now has a canonical TECHNICAL FULL PASS; next checkpoint is a localhost llama-server API smoke before objective quality comparison.
Checkpoint: `LLAMA_CPP_8B_Q2_SERVER_SMOKE_001_READY`

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

Latest confirmed observations:
- before 8B Q4: 56.285 GiB free
- after 8B Q4: 50.567 GiB free
- after 8B Q3: 46.763 GiB free
- Capability 003 before/after: 43.649 GiB free
- Q2 Stage B 001 after: **43.688 GiB free**
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts retained

## Frozen baseline / agent state

### Coding Baseline 001
- run `20260818-203156`
- Ollama/MLX `qwen3.5:4b-mlx`, context 4096
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s
- generation 16.01 tok/s

### Pi Agentic Coding Benchmark 001
- run `20260818-214848`
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6
- provider usage 20,209 total tokens

Pi is the current primary local agent harness. Qwen Code remains secondary/deprioritized because even safe mode estimates 4363 tokens against a 4096 hard limit before first tool use.

## Agentic memory investigation — practical conclusion

Historical warm Agentic 001 Ollama SIZE rose 4.4 -> 7.2 GB. Controlled invocation/context/depth/cold-replay work showed retained warm high-water across heterogeneous workloads is a major contributor. Exact internal mechanism remains unresolved; do not label it a leak/KV/allocator defect without evidence.

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
- official `Qwen/Qwen3-4B-GGUF`
- `Qwen3-4B-Q4_K_M.gguf`
- size 2.326 GiB

Observed:
- pp512 **230.85 t/s ± 0.12**
- tg128 **22.33 t/s ± 0.02**
- peak process RSS **1914.91 MB**
- peak swap **1097.19 MB**
- minimum free memory **22%**

Record: `research/runtime/llama-cpp-4b-control-001.md`.

## 8B Q4 Capability 001 — VALID FAIL

Run `20260819-091424`.

Frozen profile:
- Qwen3-8B Q4_K_M
- size 4.682 GiB
- context 4096
- `-ngl -1`
- abort below 5% free memory or above 5600 MB swap

Stage A:
- FAIL during load/init
- wall 21.558 s
- peak RSS 1940.5 MB
- peak swap 2108.38 MB
- minimum free memory 1%
- guardrail triggered; Stage B skipped

Record: `research/runtime/llama-cpp-8b-q4-001.md`.

## 8B Q3 Capability 001 — VALID FAIL

Run `20260819-093842`.

Frozen profile:
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q3_K_M.gguf`
- context 4096
- `-ngl -1`
- same guardrails

Stage A:
- FAIL
- wall 18.919 s
- peak RSS 1670.48 MB
- peak swap 2269.38 MB
- minimum free memory 1%
- guardrail triggered; Stage B skipped

Record: `research/runtime/llama-cpp-8b-q3-001.md`.

## 8B Q2 — harness chronology

### Capability 001 — INVALID
- Q2_K artifact loaded and began inference at requested context 4096
- invalid because inherited CLI smoke remained interactive without `-st`

### Capability 002 — INVALID
- `-st` corrected the interaction behavior
- single turn completed and exited
- min free memory 19%
- invalid because inherited parser required optional literal log strings

### Capability 003 — RECOVERED STAGE A PASS

Run `20260819-103347`.

Validated operational evidence:
- SHA256 PASS
- exact `-c 4096`
- exact `-ngl -1`
- `-st`
- Metal device preflight evidence
- exit code 0
- no timeout
- no guardrail abort
- wall 7.134 s
- peak RSS 2092.97 MB
- peak swap 1986.56 MB
- minimum free memory **10%**
- visible prompt ~42.7 t/s
- visible generation ~13.4 t/s

The only false validator field was `output_nonempty=False`; post-run inspection showed zero captured stdout/stderr bytes while the user visibly received CLI output. This is treated as a TTY/capture defect. Do not rerun llama-cli Stage A for this exact profile.

Record: `research/runtime/llama-cpp-8b-q2-003-recovered-stage-a.md`.

## 8B Q2 Stage B 001 — FULL PASS

Run id: `20260819-103952`
Plan: `research/runtime/llama-cpp-8b-q2-stage-b-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q2-stage-b-001.md`
Runner: `scripts/llama_cpp_8b_q2_stage_b.py`

Frozen benchmark:
- same verified Q2_K artifact, size 3.056 GiB
- `llama-bench`
- `-ngl -1`
- flash attention auto
- pp512 / tg128
- 3 repetitions
- same safety guardrails

Observed:
- pp512 **103.00 t/s ± 0.67**
- tg128 **13.72 t/s ± 0.34**
- backend `MTL,BLAS`
- reported `n_gpu_layers=-1`
- wall **53.536 s**
- peak process RSS **2461.17 MB**
- peak swap **1990.38 MB**
- minimum free memory **8%**
- no guardrail breach
- classification **FULL_PASS**
- disk free after **43.688 GiB**

## 8B Q2 — CANONICAL TECHNICAL CONCLUSION

Canonical combined record: `research/runtime/llama-cpp-8b-q2-technical-pass.md`.

> Qwen3 8B Q2_K is technically runnable on the reference Apple M1 8 GB machine under pinned llama.cpp/Metal at context 4096 and completes the frozen throughput workload without violating LOOM safety guardrails.

Descriptive scaling vs 4B Q4 under the same llama-bench shape:
- prompt throughput: 103.00 vs 230.85 t/s = **44.6%** of 4B, **55.4% lower**
- generation throughput: 13.72 vs 22.33 t/s = **61.4%** of 4B, **38.6% lower**
- process RSS: about **28.5% higher**
- peak swap: about **81.4% higher**
- minimum free memory: **8% vs 22%**

These are descriptive runtime comparisons only. Q2 is an aggressive quantization; parameter count alone does not establish better useful quality.

## 8B Q2 Server Smoke 001 — PREREGISTERED / READY

Plan: `research/runtime/llama-cpp-8b-q2-server-smoke-001-plan.md`
Runner: `scripts/llama_cpp_8b_q2_server_smoke.py`

Purpose:
- build only the `llama-server` target if it is not already present;
- verify the existing Q2 artifact and pinned source;
- launch localhost-only server at context 4096 / `-ngl -1` / Metal;
- poll official `GET /health` readiness;
- send one synchronous OpenAI-compatible `POST /v1/chat/completions` request;
- preserve the same 5% free-memory / 5600 MB swap guardrails;
- shut down immediately after the smoke.

No model download is expected.

Official pinned llama-server documentation confirms:
- OpenAI-compatible `/v1/chat/completions` exists;
- `GET /health` returns 503 while loading and 200 when healthy;
- localhost host/port flags are supported;
- Web UI can be disabled.

## Exact next step

Run:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q2_server_smoke.py
python3 scripts/llama_cpp_8b_q2_server_smoke.py
```

Preserve output from `LOOM llama.cpp 8B Q2 Server Smoke 001` through the final `Summary:` line.

## Decision after server smoke

If `FULL_PASS`:
1. use llama-server as a clean API transport;
2. reuse frozen Coding Benchmark 01 v1.0.1 in `single_shot` mode for a same-runtime comparison:
   - Qwen3 4B Q4_K_M;
   - Qwen3 8B Q2_K;
3. use the existing objective scorer and unchanged prompts;
4. only if Q2 quality/usefulness justifies it, evaluate Pi through the OpenAI-compatible llama-server API.

If server smoke fails due memory pressure, retain the raw Q2 TECHNICAL PASS and choose a separately preregistered direct-quality or memory/offload path. Do not call it a model-quality failure.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B Q4 PASS; 8B Q4/Q3 memory FAIL; 8B Q2 TECHNICAL FULL PASS; server smoke READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
