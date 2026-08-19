# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Pi remains the primary local agent harness; memory-retention investigation practically resolved; Qwen Code deprioritized; llama.cpp Metal setup and 4B control validated; 8B Q4 disk preflight passed and staged capability runner ready
Checkpoint: `LLAMA_CPP_8B_Q4_001_READY`

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

Free disk is a standard LOOM operational metric for Phase 4-6.

Rules:
- record free disk before/after new multi-GB models where practical;
- periodically inspect `results-local/models/`, llama.cpp source/build trees and related caches;
- reuse verified artifacts rather than redownloading;
- never silently delete models/results;
- before cleanup, separate reproducible caches/builds from canonical research records.

### 8B disk preflight — PASS

Observed 2026-08-19 before Capability 001:

```text
Filesystem        Size    Used   Avail Capacity  Mounted on
/dev/disk3s1s1   228Gi    12Gi    56Gi    18%   /

2.3G  results-local/models
415M  results-local/llama-cpp
```

Frozen fresh-download minimum: **12 GiB**.
Observed free: **56 GiB**.
Conclusion: no cleanup required before the 8B Q4 run.

## Frozen baseline / agent results

### Coding Baseline 001

Run `20260818-203156`, Coding Benchmark 01 v1.0.1, Ollama/MLX `qwen3.5:4b-mlx`, context 4096.

Canonical:
- artifact 40.71/100
- strict 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- weighted generation 16.01 tok/s

### Pi Agentic Coding Benchmark 001

Run `20260818-214848`.

Canonical:
- artifact/delivery 77.15/100
- strict 60.00/100
- delivery 6/6
- protocol 4/6
- provider usage 20,209 total tokens

Conclusion:
> Pi is the current primary local agent harness for LOOM at context 4096. Qwen Code remains secondary because its core request does not fit 4096 even in safe mode.

## Memory investigation — practical conclusion

Historical warm Agentic 001 Ollama SIZE rose 4.4 -> 7.2 GB and swap increased by about 3.279 GB.

Controlled work showed:
- identical warm calls only 4.1 -> 4.5 GB;
- direct prompt pressure only 4.1 -> 4.5 GB, with warm high-water retention;
- valid synthetic 1 -> 4 true turns added only ~0.1-0.2 GB;
- exact-workload cold T01-T05 stayed 4.3-4.9 GB, while historical warm sequence reached 6.8 GB by T05;
- T03-T05 cold replays were equal/heavier by tool or token activity yet 1.1-2.3 GB below warm historical SIZE.

Canonical conclusion:
> Cross-task retained warm runtime high-water is a major contributor to sustained memory growth. The lower-level internal mechanism is unresolved; do not call it a leak, KV effect, allocator bug or fragmentation without further evidence.

## Qwen Code — deprioritized

Normal-config initial estimate: ~4474 tokens at hard limit 4096.
Safe-mode run `qwen-safe-20260818-233219`: 4363 tokens, still 267 over, no first tool call.

No 8192 rescue is required for the main research path while Pi works.

# Phase 4 — llama.cpp

Pinned official llama.cpp source commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

## Setup Probe 003 — CANONICAL PASS

Run `20260818-234628`.

- exact pinned commit
- prerequisites PASS
- configure PASS
- build PASS
- `llama-cli` PASS
- `llama-bench` PASS
- `GGML_METAL=ON`
- `GGML_METAL_EMBED_LIBRARY=ON`
- `LLAMA_BUILD_COMMON=ON`
- `LLAMA_BUILD_TOOLS=ON`
- `LLAMA_BUILD_SERVER=ON`
- `LLAMA_BUILD_UI=OFF`

Record: `research/runtime/llama-cpp-setup-probe-003.md`.

## 4B Runtime Control 001 — CANONICAL PASS

Run id: `20260818-235812`
Record: `research/runtime/llama-cpp-4b-control-001.md`
Plan: `research/runtime/llama-cpp-4b-control-001-plan.md`
Runner: `scripts/llama_cpp_4b_control.py`

Frozen artifact:
- `Qwen/Qwen3-4B-GGUF`
- `Qwen3-4B-Q4_K_M.gguf`
- SHA256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- observed size 2.326 GiB

Device evidence:
- `MTL0: Apple M1 (5461 MiB, 5460 MiB free)`
- BLAS Accelerate
- unified memory true
- embedded Metal library loaded
- recommended Metal max working set 5726.63 MB

Benchmark, `-ngl -1`, flash-attn auto, 3 repetitions:
- pp512: **230.85 t/s ± 0.12**
- tg128: **22.33 t/s ± 0.02**
- backend `MTL,BLAS`
- Metal evidence true
- peak process RSS **1914.91 MB**
- peak observed swap **1097.19 MB**
- minimum observed free memory **22%**
- success true

Interpretation:
> GGUF download/hash verification, pinned llama.cpp, Metal execution and telemetry are validated. This is not an apples-to-apples performance claim versus the different `qwen3.5:4b-mlx` model.

## 8B Q4 Capability 001 — READY

Plan: `research/runtime/llama-cpp-8b-q4-001-plan.md`
Runner: `scripts/llama_cpp_8b_q4.py`

Frozen artifact:
- official repo `Qwen/Qwen3-8B-GGUF`
- `Qwen3-8B-Q4_K_M.gguf`
- remote size `5,027,783,488` bytes (~4.68 GiB)
- SHA256 `d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785`

Disk preflight passed with 56 GiB free, well above the frozen 12 GiB minimum.

Frozen staged sequence:
1. download/resume the 8B GGUF and verify exact SHA256;
2. stop the canonical Ollama model if present;
3. Stage A: `llama-cli`, maximum Metal offload (`-ngl -1`), context **4096**, tiny deterministic prompt, 8 generated tokens;
4. monitor RSS, swap and memory pressure;
5. abort if observed free memory <5% or swap >5600 MB;
6. Stage B runs only if Stage A passes;
7. Stage B: same pp512/tg128, 3-repetition `llama-bench` shape as the 4B control;
8. record disk free after the run;
9. no same-run reduction of context, quantization or GPU layers.

Classification:
- `FULL_PASS`: smoke + benchmark pass without guardrail breach;
- `LAUNCH_PASS_BENCH_FAIL`: context-4096 smoke passes but benchmark fails/aborts;
- `FAIL`: hash or Stage A failure/guardrail.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_8b_q4.py
python3 scripts/llama_cpp_8b_q4.py
```

The first run downloads approximately 4.68 GiB and is resumable. Preserve the complete output from `LOOM llama.cpp 8B Q4 Capability 001` through the final `Summary:` line.

If the runner reports `FAIL` or `LAUNCH_PASS_BENCH_FAIL`, do not manually rerun with altered parameters before updating the canonical result and deciding the next preregistered condition.

## Roadmap state

- Phase 0: DONE
- Phase 1: DONE
- Phase 2: DONE / FROZEN
- Phase 3: materially complete for current needs
- **Phase 4: ACTIVE — 4B control PASS; 8B Q4 Capability 001 READY**
- Phase 5 Direct MLX: queued
- Phase 6 Colibrì / SSD / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
