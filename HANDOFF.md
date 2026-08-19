# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains primary local agent harness; llama.cpp/Metal validated; 4B control PASS; 8B Q4 and Q3 hit frozen memory guardrails; first Q2 attempt proved load/inference but was invalidated by interactive CLI behavior; corrected Q2 Capability 002 is ready.
Checkpoint: `LLAMA_CPP_8B_Q2_002_READY`

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

Latest confirmed storage observations:
- before 8B Q4: 56.285 GiB free
- after 8B Q4: 50.567 GiB free
- after 8B Q3: 46.763 GiB free
- before first Q2 attempt: 46.746 GiB free
- verified 4B Q4, 8B Q4, 8B Q3 and 8B Q2 artifacts are retained

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

Frozen profile:
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q3_K_M.gguf`
- context 4096
- `-ngl -1`
- same guardrails

Stage A:
- FAIL
- wall 18.919 s
- peak RSS 1670.484375 MB
- peak swap 2269.38 MB
- minimum free memory **1%**
- guardrail triggered; Stage B skipped

Record: `research/runtime/llama-cpp-8b-q3-001.md`.

## 8B Q2 Capability 001 — INVALID / DIAGNOSTIC ONLY

Plan: `research/runtime/llama-cpp-8b-q2-001-plan.md`
Invalid record: `research/runtime/llama-cpp-8b-q2-001-invalid.md`
Original runner: `scripts/llama_cpp_8b_q2.py`

Artifact:
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q2_K.gguf`
- observed size **3.056 GiB**
- SHA256 PASS
- context 4096
- `-ngl -1`

Observed diagnostic behavior:
- model loaded successfully
- `llama-cli` entered actual inference on the frozen prompt
- on-screen preliminary timing approximately **32.8 prompt t/s / 14.3 generation t/s**
- after first response, CLI remained at an interactive prompt instead of exiting

Root cause:
- at the pinned llama.cpp commit, conversation mode is auto-enabled when a chat template is available;
- `-st` / `--single-turn` is documented to run one conversation turn and exit, and with a predefined prompt it does not remain interactive;
- the inherited Q4 Stage A command omitted `-st`.

Classification:
> Capability 001 is **INVALID**, not PASS/FAIL. It proves only that Q2 can load and begin inference at context 4096; it cannot provide a final automated Stage A or Stage B result.

## 8B Q2 Capability 002 — PREREGISTERED / READY

Plan: `research/runtime/llama-cpp-8b-q2-002-plan.md`
Runner: `scripts/llama_cpp_8b_q2_002.py`

Frozen model/runtime condition remains unchanged from Capability 001:
- same Q2_K artifact and expected SHA256
- context 4096
- `-ngl -1`
- same 8-token Stage A prompt
- same 5% memory-free abort
- same 5600 MB swap abort
- Stage B pp512/tg128 x3 only after Stage A PASS
- no automatic rescue

Only harness correction:
- add `-st` (`--single-turn`) to Stage A so `llama-cli` exits after the predefined first turn.

Implementation preserves prior reproducibility by leaving the Q4/Q3 runners unchanged. The new Q2 Capability 002 wrapper still verifies the exact frozen Q4 template blob `83e01eae5ed12d13396f003d5291ba786a668ffd`, then adds only the Q2 constants plus `-st` during deterministic transformation.

The verified local Q2 model must be reused; no new ~3 GB download is expected.

## Exact next step

First terminate the still-interactive Capability 001 process with `Ctrl+C` if it is still open.

Then run:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q2_002.py
python3 scripts/llama_cpp_8b_q2_002.py
```

Preserve complete output from `LOOM llama.cpp 8B Q2 Capability 002` through the final `Summary:` line.

## Decision after Q2 Capability 002

- If `FULL_PASS`: stop reducing quantization and test actual quality/usefulness and Pi compatibility before calling Q2 8B a practical upgrade.
- If Stage A `FAIL`: stop blindly descending quantizations; next test is a separately preregistered partial-offload/context-memory strategy, then continue broader runtime research.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B PASS; 8B Q4 FAIL; 8B Q3 FAIL; Q2 Capability 001 INVALID; Q2 Capability 002 READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
