# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi validated as primary local agent harness; Agentic 001 frozen; practical memory-retention question resolved; Qwen Code deprioritized; llama.cpp Phase 4 setup preregistered and ready
Checkpoint: LLAMA_CPP_PHASE4_SETUP_READY

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

Configuration:
- Coding Benchmark 01 v1.0.1
- Pi 0.84.2
- Ollama / `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- tools `read,write,edit`
- no bash/test feedback
- hidden tests excluded
- isolated run-local Pi directory
- no retries/rescue/manual repair

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

### Primary agent conclusion

> Pi is the current primary local agent harness for LOOM. At context 4096 it can complete real read/edit/test loops and deliver all six benchmark tasks, while Qwen Code cannot form its first 4096-token request even in safe mode.

This does not mean Pi is globally superior; it means Pi is the practical harness for the current constrained-machine research path.

## Agentic memory investigation — practical conclusion

Historical sustained Agentic 001 post-task Ollama SIZE:
- T01 4.4 GB
- T02 5.2 GB
- T03 5.6 GB
- T04 6.4 GB
- T05 6.8 GB
- T06 7.2 GB

Historical swap:
- start 1544.12 MB
- final 4823.12 MB
- delta +3279.00 MB

Controlled findings:

1. Repeating identical small Pi calls warm only produced **4.1 -> 4.5 GB**; cold controls reset to 4.1 GB.
2. Direct Ollama prompt pressure without Pi produced **4.1 -> 4.5 GB** and retained a 4.6 GB warm high-water after returning to a small prompt.
3. Valid synthetic true-depth evidence from 1 to 4 tool/model turns produced only about **+0.1 to +0.2 GB**.
4. Exact-workload cold replay T01-T05 kept individual tasks at **4.3-4.9 GB**, while historical warm sequence reached 6.8 GB by T05.
5. T03-T05 cold replay used equal/more tool activity or provider usage than historical runs yet remained **1.1-2.3 GB** below the historical warm SIZE.
6. T06 cold replay timed out before tool use and is excluded from workload comparison.

Canonical practical conclusion:
> Cross-task retained warm runtime high-water is a **major contributor** to the sustained memory growth seen in Agentic 001. Individual cold workloads T01-T05 do not independently require the later 6-7 GB reported state.

Do not infer the internal mechanism. It is not currently identified as leak, KV cache, MLX allocator behavior or fragmentation.

Practical implication:
> Periodic model unload/reload is a plausible long-session memory mitigation on 8 GB, with reload-latency tradeoff to measure later in the daily-use profile.

Records:
- `research/agents/pi-memory-retention-probe-001.md`
- `research/runtime/ollama-context-retention-probe-001.md`
- `research/agents/pi-multiturn-memory-probe-001.md`
- `research/agents/pi-multiturn-memory-probe-002.md`
- `research/agents/pi-multiturn-memory-probe-003.md`
- `research/agents/pi-agentic-cold-replay-001.md`

## Qwen Code — SECONDARY / DEPRIORITIZED

Historical normal-config 4096 smoke:
- estimated prompt ~4474 tokens
- hard limit 4096
- no tool call
- model not loaded

Safe-mode diagnostic:
- run id `qwen-safe-20260818-233219`
- Qwen Code 0.21.13
- customizations disabled
- estimated prompt **4363 tokens**
- hard limit **4096**
- still **267 tokens over limit**
- safe mode recovers only **111 tokens** versus normal config
- compression `NOOP`
- no tool call
- working tree unchanged

Record:
- `research/agents/qwen-code-safe-mode-4096.md`

Decision:
> Optional project/custom context is not the main 4096 bottleneck. Qwen Code's core safe-mode request is still too large. Further Qwen Code minimization and 8192 rescue are deferred because Pi already serves the primary agent role.

## Phase 4 — llama.cpp — ACTIVE

Plan:
- `research/runtime/llama-cpp-phase4-plan.md`

Setup runner:
- `scripts/llama_cpp_setup_probe.py`

Official source:
- `ggml-org/llama.cpp`

Pinned initial source commit:
- `60addddf3c567c43ec3caf70fc953fba3572d96f`

Why llama.cpp now:
- this returns LOOM to the primary runtime/model-capability mission;
- Apple Silicon/Metal is a first-class llama.cpp target;
- GGUF quantizations and CPU/GPU offload let LOOM explore larger useful models and more aggressive memory tradeoffs than the current Ollama/MLX baseline.

### Phase 4 sequence

1. **Setup / build verification**
   - check git/cmake/xcrun/clang
   - clone/fetch pinned source under `results-local/llama-cpp/`
   - Release build with `GGML_METAL=ON`
   - build/verify `llama-cli` and `llama-bench`

2. **4B runtime control**
   - official `Qwen/Qwen3-4B-GGUF`
   - `Q4_K_M`
   - purpose is instrumentation/runtime validation, not apples-to-apples quality comparison with Qwen3.5 MLX

3. **8B Q4 main capability test**
   - official `Qwen/Qwen3-8B-GGUF`
   - `Q4_K_M`
   - initial context 4096
   - maximum practical Metal/GPU offload first
   - capture load time, prompt/gen throughput, memory/swap and stability

4. Later:
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

Preserve the complete output, especially:
- prerequisites
- configure/build result
- actual pinned commit
- `GGML_METAL`
- `llama-cli` / `llama-bench` checks
- any configure/build stderr

No model download should happen in this setup step.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 baseline: DONE
- Phase 2 Coding Benchmark/Baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: materially complete for current needs; Pi primary, Qwen Code secondary
- **Phase 4 llama.cpp: ACTIVE — setup ready**
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD/MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
