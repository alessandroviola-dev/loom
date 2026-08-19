# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains primary local agent harness; llama.cpp/Metal validated; 4B control PASS; 8B Q4_K_M and Q3_K_M at context 4096 both hit the frozen memory guardrail; 8B Q2_K condition preregistered and ready
Checkpoint: `LLAMA_CPP_8B_Q2_001_READY`

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

Free disk is a standard LOOM metric. Reuse verified artifacts and never silently delete models/results.

Latest observed storage:
- before 8B Q4 download: 56.285 GiB free
- after 8B Q4: 50.567 GiB free
- after 8B Q3: **46.763 GiB free**
- verified 4B Q4, 8B Q4 and 8B Q3 artifacts retained

## Frozen baseline / agent state

### Coding Baseline 001
- run `20260818-203156`
- Ollama/MLX `qwen3.5:4b-mlx`, context 4096
- artifact 40.71/100; strict 30.00/100; delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt 186.46 tok/s; generation 16.01 tok/s

### Pi Agentic Coding Benchmark 001
- run `20260818-214848`
- artifact/delivery 77.15/100; strict 60.00/100
- delivery 6/6; protocol 4/6
- provider usage 20,209 total tokens

Pi is the current primary local agent harness. Qwen Code remains secondary/deprioritized because even safe mode estimates 4363 tokens against a 4096 hard limit before first tool use.

## Agentic memory investigation — practical conclusion

Historical warm Agentic 001 Ollama SIZE rose 4.4 -> 7.2 GB. Controlled invocation/context/depth/cold-replay work showed retained warm high-water across heterogeneous workloads is a major contributor. Exact internal mechanism remains unresolved; do not label it a leak/KV/allocator defect without further evidence.

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
- official Qwen3-8B Q4_K_M
- size 4.682 GiB
- context 4096
- `-ngl -1`
- abort below 5% memory free or above 5600 MB swap

Stage A:
- FAIL during load/init
- wall 21.558 s
- peak RSS 1940.5 MB
- peak swap 2108.38 MB
- minimum free memory **1%**
- guardrail triggered; Stage B skipped

Record: `research/runtime/llama-cpp-8b-q4-001.md`.

## 8B Q3 Capability 001 — VALID FAIL

Run `20260819-093842`.
Plan: `research/runtime/llama-cpp-8b-q3-001-plan.md`
Record: `research/runtime/llama-cpp-8b-q3-001.md`
Runner: `scripts/llama_cpp_8b_q3.py`

Frozen profile:
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q3_K_M.gguf`
- context 4096
- `-ngl -1`
- same 5% memory-free / 5600 MB swap guardrails

Stage A:
- **FAIL**
- wall **18.919 s**
- peak process RSS **1670.484375 MB**
- peak observed swap **2269.38 MB**
- minimum free memory **1%**
- guardrail: `memory free 1% < 5%`
- Stage B skipped
- disk free after: **46.763 GiB**

Interpretation:
> Q3 materially reduces the model representation and observed process RSS versus Q4, but does not recover enough system memory headroom at the frozen context-4096/full-offload profile. Q4 and Q3 both reach the same preregistered 1% memory-free failure signal.

Do not treat RSS as total unified-memory footprint. The decisive criterion is the frozen `memory_pressure` guardrail.

## 8B Q2 Capability 001 — PREREGISTERED / READY

Plan: `research/runtime/llama-cpp-8b-q2-001-plan.md`
Runner: `scripts/llama_cpp_8b_q2.py`

Artifact:
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q2_K.gguf`
- quantization `Q2_K`
- exact remote size **3,281,733,440 bytes (~3.06 GiB)**
- SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`

Frozen condition preserves:
- context 4096
- `-ngl -1`
- same deterministic Stage A smoke
- same 5% memory-free abort
- same 5600 MB swap abort
- Stage B pp512/tg128 x3 only after Stage A PASS
- no automatic rescue

Q2 is about 0.78 GiB smaller than Q3_K_M and about 1.63 GiB smaller than the failed Q4_K_M artifact. If Q2 passes, launchability alone is insufficient: quality/agent usefulness must be measured before calling it a practical upgrade.

Implementation reuses the frozen Q4 runner template after verifying Git blob `83e01eae5ed12d13396f003d5291ba786a668ffd`.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q2.py
python3 scripts/llama_cpp_8b_q2.py
```

The first Q2 run downloads approximately 3.06 GiB and verifies its SHA256 before inference.

Preserve complete output from `LOOM llama.cpp 8B Q2 Capability 001` through the final `Summary:` line.

## Decision after Q2

- If `FULL_PASS`: stop reducing quantization and test actual quality/usefulness and Pi compatibility before deciding whether Q2 8B is a practical upgrade.
- If Stage A `FAIL`: stop blindly descending quantizations; next test should be a separately preregistered partial-offload/context-memory strategy, then continue the broader runtime research.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B PASS; 8B Q4 FAIL; 8B Q3 FAIL; 8B Q2 READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
