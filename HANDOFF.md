# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi validated as primary local agent harness; Agentic 001 frozen; memory-retention question practically resolved; Qwen Code deprioritized; llama.cpp Phase 4 setup probe corrected after identifying a LOOM target-configuration defect
Checkpoint: LLAMA_CPP_SETUP_002_PROBE_FIXED_RERUN_READY

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.

Tagline: **Big models. Small machines.**

Reference repo: `Ilcoach/loom`
Local path: `<repository-root>`

Reference stack before Phase 4:
- Apple M1, 8 GB unified memory
- Ollama 0.32.14
- Pi 0.84.2
- Qwen Code 0.21.13
- canonical Ollama model `qwen3.5:4b-mlx`
- canonical context 4096 unless an experiment explicitly changes it

## Production Pi constraint

The user's normal Pi installation contains real OpenAI API/Codex auth, sessions and customizations. LOOM added Ollama only as an additional provider.

Do not reset/overwrite normal Pi state. Controlled experiments use run-local `PI_CODING_AGENT_DIR` and explicit per-run resources.

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Benchmark: Coding Benchmark 01 v1.0.1
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical:
- artifact **40.71/100**
- strict delivery-adjusted **30.00/100**
- structured delivery **3/6**
- recovered semantic diagnostic **82.86/100**
- weighted prompt throughput **186.46 tok/s**
- weighted generation **16.01 tok/s**

Record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

Key finding:
> Full-file JSON delivery was a major bottleneck; recovered code quality was much stronger than strict end-to-end delivery.

## Pi Agentic Coding Benchmark 001 — FROZEN / CANONICAL

Run id: `20260818-214848`
Record:
- `research/agents/pi-agentic-benchmark-001.md`

Canonical scores:
- artifact **77.15/100**
- delivery-adjusted **77.15/100**
- strict protocol-adjusted **60.00/100**
- delivery **6/6**
- protocol **4/6**

Versus single-shot:
- artifact **40.71 -> 77.15** (+36.44)
- strict **30.00 -> 60.00** (+30.00)
- delivery **3/6 -> 6/6**

Correctness deficit from 100 artifact: **22.85 points**.
Additional strict-only protocol loss: **17.15 points**, entirely T02/T03 final-output noncompliance.

Workspace/tool-path safety: PASS.
Provider usage across task sessions: **19,556 input + 653 output = 20,209 total**.

Primary agent conclusion:
> Pi is the current primary local agent harness for LOOM. At context 4096 it completes real read/edit/test loops and delivers all six benchmark tasks, while Qwen Code cannot form its first 4096-token request even in safe mode.

## Agentic memory investigation — practical conclusion

Historical Agentic 001 post-task Ollama SIZE:
- T01 4.4 GB
- T02 5.2 GB
- T03 5.6 GB
- T04 6.4 GB
- T05 6.8 GB
- T06 7.2 GB

Historical swap delta: **+3279 MB**.

Controlled findings:
1. Four identical small warm Pi calls only produced **4.1 -> 4.5 GB**; cold controls reset to 4.1 GB.
2. Direct Ollama prompt pressure without Pi produced **4.1 -> 4.5 GB** and retained a 4.6 GB warm high-water.
3. Valid synthetic true-depth evidence from 1 to 4 model/tool turns produced only about **+0.1 to +0.2 GB**.
4. Exact-workload cold replay T01-T05 kept individual tasks at **4.3-4.9 GB**, while historical warm sequence reached 6.8 GB by T05.
5. T03-T05 cold replay used equal/more tool activity or provider usage than historical runs yet remained **1.1-2.3 GB** below historical warm SIZE.
6. T06 cold replay timed out before tool use and is excluded from workload comparison.

Canonical practical conclusion:
> Cross-task retained warm runtime high-water is a **major contributor** to sustained memory growth in Agentic 001. Individual cold workloads T01-T05 do not independently require the later 6-7 GB reported state.

Internal mechanism remains unidentified. Do not label it a leak, KV-cache effect, allocator bug or fragmentation without lower-level evidence.

## Qwen Code — SECONDARY / DEPRIORITIZED

Normal-config 4096 smoke:
- estimated prompt ~4474 tokens
- no tool call

Safe-mode diagnostic run `qwen-safe-20260818-233219`:
- estimated prompt **4363 tokens**
- hard limit **4096**
- **267 tokens over limit**
- safe mode recovers only **111 tokens**
- compression `NOOP`
- no tool call
- working tree unchanged

Record:
- `research/agents/qwen-code-safe-mode-4096.md`

Decision:
> Qwen Code remains a secondary comparator. No 8192 rescue/minimization work is blocking the main LOOM path because Pi already provides the primary agent harness.

## Phase 4 — llama.cpp — ACTIVE

Plan:
- `research/runtime/llama-cpp-phase4-plan.md`

Setup runner:
- `scripts/llama_cpp_setup_probe.py`

Official source:
- `ggml-org/llama.cpp`

Pinned source commit:
- `60addddf3c567c43ec3caf70fc953fba3572d96f`

### Setup Probe 001 — BLOCKED_MISSING_CMAKE

Run id: `20260818-233856`.

- `cmake` missing on PATH.
- Probe stopped before clone/configure/build.
- Record: `research/runtime/llama-cpp-setup-probe-001.md`.

CMake was subsequently installed through Homebrew:
- CMake **4.4.2**
- `/opt/homebrew/Cellar/cmake/4.4.2`

### Setup Probe 002 — PROBE CONFIGURATION DEFECT

Run id: `20260818-234152`.

Observed:
- pinned commit matched actual checkout exactly
- prerequisites PASS
- configure PASS
- `GGML_METAL=ON`
- `GGML_METAL_EMBED_LIBRARY=ON`
- build failed: `make: *** No rule to make target 'llama-cli'. Stop.`

Root cause verified against the exact pinned llama.cpp source:
- `tools/CMakeLists.txt` adds `tools/cli` only inside `if (LLAMA_BUILD_SERVER)`;
- original LOOM runner set `-DLLAMA_BUILD_SERVER=OFF`;
- therefore CMake correctly omitted the `llama-cli` target.

This is a **LOOM probe defect**, not a llama.cpp/Metal/M1 build failure.

Record:
- `research/runtime/llama-cpp-setup-probe-002.md`

### Setup Probe revision 2 — READY

Runner patched without changing pinned source commit or Metal configuration:
- `LLAMA_BUILD_SERVER=ON`
- `LLAMA_BUILD_UI=OFF`
- `LLAMA_BUILD_COMMON=ON`
- `LLAMA_BUILD_TOOLS=ON`
- `GGML_METAL=ON`
- `GGML_METAL_EMBED_LIBRARY=ON`
- tests OFF

Rationale:
> At the pinned source commit `llama-cli` depends on the server/tool subtree being enabled. The embedded Web UI is not needed for LOOM and remains disabled.

### Planned sequence after setup PASS

1. **4B runtime control**
   - `Qwen/Qwen3-4B-GGUF`
   - `Q4_K_M`
   - instrumentation/runtime validation

2. **8B Q4 main capability test**
   - `Qwen/Qwen3-8B-GGUF`
   - `Q4_K_M`
   - context 4096
   - maximum practical Metal/GPU offload first
   - capture load time, prompt/gen throughput, memory/swap and stability

3. Later:
   - Q3 variants
   - ~9B Q3/Q2 where feasible
   - partial CPU/GPU offload comparisons

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_setup_probe.py
python3 scripts/llama_cpp_setup_probe.py
```

No model download should occur in this setup step.

Preserve complete output, especially:
- Configure / Build
- `llama-cli` / `llama-bench`
- `GGML_METAL`
- `GGML_METAL_EMBED_LIBRARY`
- `LLAMA_BUILD_COMMON`
- `LLAMA_BUILD_TOOLS`
- `LLAMA_BUILD_SERVER`
- `LLAMA_BUILD_UI`
- any build stderr

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 baseline: DONE
- Phase 2 Coding Benchmark/Baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: materially complete; Pi primary, Qwen Code secondary
- **Phase 4 llama.cpp: ACTIVE — corrected setup probe ready**
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD/MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
