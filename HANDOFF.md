# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains primary local agent harness; llama.cpp/Metal validated; 4B control PASS; 8B Q4_K_M context-4096 profile hit frozen memory guardrail; 8B Q3_K_M condition preregistered and ready
Checkpoint: `LLAMA_CPP_8B_Q3_001_READY`

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
- canonical context 4096 unless a separately preregistered experiment changes it

## Production Pi constraint

Normal Pi contains real auth, sessions and customizations. LOOM must not reset or replace it. Controlled experiments use isolated/run-local Pi configuration where required.

## Storage hygiene

Free disk is a standard LOOM operational metric. Reuse verified artifacts and never silently delete models/results.

Latest observed storage:
- before 8B Q4 download: **56.285 GiB free**
- after 8B Q4 run: **50.567 GiB free**
- verified 4B GGUF retained
- verified 8B Q4 GGUF retained

## Frozen baseline / agent state

### Coding Baseline 001
- run `20260818-203156`
- model/runtime: Ollama/MLX `qwen3.5:4b-mlx`, context 4096
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s
- weighted generation 16.01 tok/s

### Pi Agentic Coding Benchmark 001
- run `20260818-214848`
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6
- provider usage 20,209 total tokens

Pi is the current primary local agent harness. Qwen Code is secondary/deprioritized because even safe mode estimates 4363 tokens against a 4096 hard limit before first tool use.

## Agentic memory investigation — practical conclusion

Historical warm Agentic 001 Ollama SIZE rose 4.4 -> 7.2 GB. Controlled invocation/context/depth/cold-replay work showed that retained warm high-water across heterogeneous workloads is a major contributor. Exact internal mechanism remains unresolved; do not label it a leak/KV/allocator defect without further evidence.

# Phase 4 — llama.cpp

Pinned source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

## Setup Probe 003 — CANONICAL PASS

Run `20260818-234628`:
- exact pinned commit
- Release build PASS
- `llama-cli` PASS
- `llama-bench` PASS
- `GGML_METAL=ON`
- embedded Metal library ON

Record: `research/runtime/llama-cpp-setup-probe-003.md`.

## 4B Runtime Control 001 — CANONICAL PASS

Run `20260818-235812`.

Artifact:
- official `Qwen/Qwen3-4B-GGUF`
- `Qwen3-4B-Q4_K_M.gguf`
- size 2.326 GiB
- SHA256 verified

Observed:
- Metal device `MTL0: Apple M1`
- recommended Metal max working set 5726.63 MB
- pp512 **230.85 t/s ± 0.12**
- tg128 **22.33 t/s ± 0.02**
- peak process RSS **1914.91 MB**
- peak swap **1097.19 MB**
- minimum free memory **22%**

Record: `research/runtime/llama-cpp-4b-control-001.md`.

## 8B Q4 Capability 001 — VALID FAIL

Run id: `20260819-091424`
Record: `research/runtime/llama-cpp-8b-q4-001.md`
Plan: `research/runtime/llama-cpp-8b-q4-001-plan.md`
Runner: `scripts/llama_cpp_8b_q4.py`

Frozen profile:
- official `Qwen/Qwen3-8B-GGUF`
- `Qwen3-8B-Q4_K_M.gguf`
- observed size **4.682 GiB**
- SHA256 PASS
- context **4096**
- `-ngl -1`
- abort below 5% memory free or above 5600 MB swap
- no same-run rescue

Stage A result:
- **FAIL** while loading/initializing
- wall **21.558 s**
- peak process RSS **1940.5 MB**
- peak observed swap **2108.38 MB**
- minimum observed free memory **1%**
- guardrail: `memory free 1% < 5%`
- Stage B skipped
- classification **FAIL**

Interpretation:
> The exact 8B Q4_K_M / context-4096 / maximum-requested-Metal-offload profile is not acceptable under LOOM's frozen safety criterion on the reference M1 8 GB machine. This is not a claim that every altered 8B Q4 configuration is impossible.

RSS is not treated as total unified-memory footprint; the decisive signal is the preregistered `memory_pressure` guardrail.

## 8B Q3 Capability 001 — PREREGISTERED / READY

Plan: `research/runtime/llama-cpp-8b-q3-001-plan.md`
Runner: `scripts/llama_cpp_8b_q3.py`

Artifact:
- community quant repository `unsloth/Qwen3-8B-GGUF`
- base model class: Qwen3-8B
- file `Qwen3-8B-Q3_K_M.gguf`
- quantization `Q3_K_M`
- remote pointer size **4,124,161,856 bytes (~3.84 GiB)**
- expected SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`

Source caveat:
> Official Qwen's current GGUF file set used for the Q4 test does not include Q3_K_M, so this lower-quantization condition uses an Unsloth community artifact. Interpret it as capability evidence, not a perfectly controlled quantizer-source comparison.

Frozen Q3 condition preserves:
- context 4096
- `-ngl -1`
- same tiny Stage A smoke
- same 5% memory-free abort
- same 5600 MB swap abort
- Stage B pp512/tg128 x3 only if Stage A passes
- no automatic rescue

Implementation note:
`scripts/llama_cpp_8b_q3.py` reuses the exercised Q4 runner logic through a deterministic source transform and verifies the exact Q4 runner Git blob `83e01eae5ed12d13396f003d5291ba786a668ffd` before execution. This prevents later Q4-runner edits from silently changing the Q3 experiment.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q3.py
python3 scripts/llama_cpp_8b_q3.py
```

The first Q3 run downloads approximately 3.84 GiB and verifies its SHA256 before inference.

Preserve complete output from `LOOM llama.cpp 8B Q3 Capability 001` through the final `Summary:` line.

## Open decisions after Q3

- If `FULL_PASS`: measure 4B -> 8B scaling and then test actual quality/agent usefulness before calling Q3 8B a practical upgrade.
- If `LAUNCH_PASS_BENCH_FAIL`: separately preregister partial offload or Q2.
- If Stage A `FAIL`: move to a separately preregistered 8B Q2-class condition rather than repeatedly tuning Q3.
- Only attempt ~9B after the 8B frontier is characterized.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B PASS, 8B Q4 guardrail FAIL, 8B Q3 READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
