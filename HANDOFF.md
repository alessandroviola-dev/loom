# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains primary local agent harness; llama.cpp/Metal validated; 4B control PASS; 8B Q4 and Q3 hit frozen memory guardrails; Q2 now demonstrably loads/completes a turn with healthy headroom, but Capability 002 was invalidated by an evidence-parser defect; Capability 003 is preregistered and ready.
Checkpoint: `LLAMA_CPP_8B_Q2_003_READY`

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
- Capability 002 before: **43.686 GiB free**
- Capability 002 after: **43.674 GiB free**
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

Diagnostic result:
- model loaded successfully
- actual inference began at requested context 4096
- preliminary on-screen timing ~32.8 prompt t/s / 14.3 generation t/s
- CLI then remained interactive because Stage A omitted `-st`

Classification: **INVALID**, not PASS/FAIL.

## 8B Q2 Capability 002 — INVALID / VALIDATION DEFECT

Run id: `20260819-102747`
Plan: `research/runtime/llama-cpp-8b-q2-002-plan.md`
Invalid record: `research/runtime/llama-cpp-8b-q2-002-invalid.md`
Runner: `scripts/llama_cpp_8b_q2_002.py`

Frozen runtime/model condition:
- same verified Q2_K artifact
- context 4096 via `-c 4096`
- `-ngl -1`
- `-st`
- 8 generated tokens
- same 5% memory-free / 5600 MB swap guardrails

Observed:
- SHA256 PASS
- model size 3.056 GiB
- single turn completed and CLI exited automatically
- on-screen prompt **43.2 t/s**
- on-screen generation **11.4 t/s**
- wall **7.229 s**
- peak RSS **2215.203125 MB**
- peak swap **2181.12 MB**
- minimum free memory **19%**
- no guardrail breach
- Stage B skipped because Stage A validator printed FAIL

Validation defect:
- inherited validator required literal `metal`/`mtl` and `4096` strings inside Stage A child stdout/stderr;
- the completed child did not print those optional strings;
- therefore the parser could label a healthy completed run FAIL despite the requested command and same-run device preflight being correct.

Canonical treatment:
> Capability 002 remains **INVALID**, not promoted post hoc. It is strong diagnostic evidence that Q2 has materially more headroom than Q4/Q3, but a corrected preregistered validator must authorize Stage B.

## 8B Q2 Capability 003 — PREREGISTERED / READY

Plan: `research/runtime/llama-cpp-8b-q2-003-plan.md`
Runner: `scripts/llama_cpp_8b_q2_003.py`

Runtime/model condition is unchanged from Capability 002.

Only validation correction:
- exact `-c 4096` pair must be present in the executed command;
- exact `-ngl -1` pair must be present;
- `-st`/`--single-turn` must be present;
- same-run device preflight must show `MTL0` and Metal evidence;
- child must exit 0, produce output, avoid timeout and avoid guardrail breach.

Stage B remains unchanged pp512/tg128 x3 and independently records backend/effective GPU-layer evidence.

The runner leaves frozen Q4/Q3 code untouched and still verifies the original Q4 runner blob `83e01eae5ed12d13396f003d5291ba786a668ffd` before deterministic transformation.

## Exact next step

Run:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q2_003.py
python3 scripts/llama_cpp_8b_q2_003.py
```

The verified Q2 artifact is already local; no new multi-GB download is expected.

Preserve complete output from `LOOM llama.cpp 8B Q2 Capability 003` through the final `Summary:` line.

## Decision after Capability 003

- If `FULL_PASS`: stop reducing quantization; compare 4B/Q2-8B throughput and test actual quality/usefulness/Pi compatibility before calling Q2 8B a practical upgrade.
- If `LAUNCH_PASS_BENCH_FAIL`: separately preregister a memory/offload strategy.
- If Stage A genuinely `FAIL`: stop descending quantizations and move to a separately frozen partial-offload/context-memory condition.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B PASS; 8B Q4 FAIL; 8B Q3 FAIL; Q2 001/002 INVALID; Q2 Capability 003 READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
