# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains primary local agent harness; llama.cpp/Metal validated; 4B control PASS; 8B Q4 and Q3 hit frozen memory guardrails; Q2 demonstrably loads/completes a turn with usable headroom; Capability 003 Stage A is recovered PASS evidence after confirming a TTY/capture defect; Stage B-only benchmark continuation is preregistered and ready.
Checkpoint: `LLAMA_CPP_8B_Q2_STAGE_B_001_READY`

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
- Capability 002 before: 43.686 GiB free
- Capability 002 after: 43.674 GiB free
- Capability 003 before/after: **43.649 GiB free**
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
- peak RSS 1670.484375 MB
- peak swap 2269.38 MB
- minimum free memory 1%
- guardrail triggered; Stage B skipped

Record: `research/runtime/llama-cpp-8b-q3-001.md`.

## 8B Q2 Capability 001 — INVALID / DIAGNOSTIC ONLY

Plan: `research/runtime/llama-cpp-8b-q2-001-plan.md`
Invalid record: `research/runtime/llama-cpp-8b-q2-001-invalid.md`
Runner: `scripts/llama_cpp_8b_q2.py`

Artifact:
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q2_K.gguf`
- observed size 3.056 GiB
- SHA256 PASS

Diagnostic:
- model loaded and began inference at requested context 4096;
- on-screen timing about 32.8 prompt t/s / 14.3 generation t/s;
- invalidated because CLI remained interactive without `-st`.

## 8B Q2 Capability 002 — INVALID / VALIDATION DEFECT

Run `20260819-102747`.

Observed:
- same verified Q2 artifact;
- single turn completed and CLI exited automatically with `-st`;
- on-screen prompt 43.2 t/s;
- on-screen generation 11.4 t/s;
- wall 7.229 s;
- peak RSS 2215.203125 MB;
- peak swap 2181.12 MB;
- minimum free memory 19%;
- no guardrail breach.

Invalidated because the inherited parser required optional literal Stage A log strings.

Record: `research/runtime/llama-cpp-8b-q2-002-invalid.md`.

## 8B Q2 Capability 003 — STAGE A RECOVERED PASS / CAPTURE DEFECT

Run id: `20260819-103347`
Plan: `research/runtime/llama-cpp-8b-q2-003-plan.md`
Runner: `scripts/llama_cpp_8b_q2_003.py`
Recovered Stage A record: `research/runtime/llama-cpp-8b-q2-003-recovered-stage-a.md`

Frozen runtime/model condition:
- same Q2_K artifact, SHA256 PASS;
- context command evidence: exact `-c 4096`;
- requested offload evidence: exact `-ngl -1`;
- single-turn evidence: `-st`;
- same-run Metal device preflight evidence;
- unchanged 5% memory-free / 5600 MB swap guardrails.

Observed terminal behavior:
- model loaded successfully;
- one inference turn executed;
- on-screen prompt about **42.7 t/s**;
- on-screen generation about **13.4 t/s**;
- CLI printed `Exiting...` and returned cleanly.

Runner telemetry:
- exit code **0**;
- timeout **False**;
- guardrail abort **False**;
- wall **7.134 s**;
- peak RSS **2092.96875 MB**;
- peak swap **1986.56 MB**;
- minimum free memory **10%**.

Post-run inspection of saved validator fields:
- `metal_evidence=True`;
- `context_4096_evidence=True`;
- `requested_offload_evidence=True`;
- `single_turn_evidence=True`;
- `stage_a_metal_preflight_evidence=True`;
- only `output_nonempty=False` caused `pass=False`;
- captured stdout bytes `0`;
- captured stderr bytes `0`.

Canonical interpretation:
> The remaining false criterion is a TTY/capture defect: the user visibly received llama-cli output while the runner pipes contained zero bytes. Capability 003 is not called a full capability PASS because Stage B never ran, but its Stage A launch/memory evidence is accepted as recovered PASS. Do not rerun llama-cli Stage A again for this exact Q2 condition.

## 8B Q2 Stage B 001 — PREREGISTERED / READY

Plan: `research/runtime/llama-cpp-8b-q2-stage-b-001-plan.md`
Runner: `scripts/llama_cpp_8b_q2_stage_b.py`

Purpose:
- complete the throughput portion only;
- inherit Stage A launch/memory evidence from run `20260819-103347`;
- avoid all further llama-cli capture/parser issues.

Frozen Stage B:
- same Q2_K artifact and exact SHA256;
- pinned llama.cpp build;
- `llama-bench`;
- `-ngl -1`;
- flash attention auto;
- pp512;
- tg128;
- 3 repetitions;
- JSON output;
- unchanged abort below 5% free memory or above 5600 MB swap.

Classification:
- `FULL_PASS`: benchmark exits 0, JSON parses, positive pp512/tg128 rows exist, Metal evidence exists, no timeout/guardrail;
- `BENCH_FAIL`: Stage A remains recovered-valid but Stage B fails/times out/breaches guardrail.

## Exact next step

Run only the Stage B continuation:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q2_stage_b.py
python3 scripts/llama_cpp_8b_q2_stage_b.py
```

No model download and no llama-cli Stage A rerun are expected.

Preserve complete output from `LOOM llama.cpp 8B Q2 Stage B 001` through the final `Summary:` line.

## Decision after Stage B

- If `FULL_PASS`: freeze Q2 8B as technically runnable, compare 4B/Q2-8B throughput/memory, then test quality/usefulness/Pi compatibility before calling it a practical upgrade.
- If `BENCH_FAIL`: stop repairing the Q2 harness and move to a separately preregistered memory/offload strategy or broader runtime comparison.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B PASS; 8B Q4 FAIL; 8B Q3 FAIL; Q2 Stage A recovered PASS; Q2 Stage B READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
