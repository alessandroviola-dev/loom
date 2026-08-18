# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi validated as primary local agent harness; Agentic 001 frozen; practical memory-retention question resolved; Qwen Code deprioritized; llama.cpp Phase 4 Metal setup fully validated; 4B GGUF runtime control preregistered and ready
Checkpoint: LLAMA_CPP_4B_CONTROL_001_READY

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
> Pi is the current primary local agent harness for LOOM. At context 4096 it completes real agentic file work and delivers all six benchmark tasks, while Qwen Code cannot form its first 4096-token request even in safe mode.

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
1. identical small warm Pi calls only produced **4.1 -> 4.5 GB**; cold controls reset to 4.1 GB;
2. direct Ollama prompt pressure without Pi produced **4.1 -> 4.5 GB** and retained a 4.6 GB warm high-water;
3. valid synthetic depth 1 -> 4 changed reported SIZE only about **+0.1 to +0.2 GB**;
4. exact-workload cold replay T01-T05 kept individual tasks at **4.3-4.9 GB**, while the historical warm sequence reached 6.8 GB by T05;
5. T03-T05 cold replay used equal/more tool activity or provider usage yet remained **1.1-2.3 GB** below historical warm SIZE;
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
- no tool call

Record:
- `research/agents/qwen-code-safe-mode-4096.md`

Decision:
> No further Qwen Code minimization/8192 rescue is required for the main research path while Pi already provides a viable local agent harness.

## Phase 4 — llama.cpp — ACTIVE

Official source:
- `ggml-org/llama.cpp`

Pinned source commit:
- `60addddf3c567c43ec3caf70fc953fba3572d96f`

Phase plan:
- `research/runtime/llama-cpp-phase4-plan.md`

### Setup Probe 001 — BLOCKED_MISSING_CMAKE

Run id `20260818-233856`.
- stopped at prerequisite gate because CMake was absent;
- no build inference.

Record:
- `research/runtime/llama-cpp-setup-probe-001.md`

CMake subsequently installed through Homebrew:
- CMake **4.4.2**.

### Setup Probe 002 — INVALID BUILD RESULT / LOOM DEFECT

Run id `20260818-234152`.
- prerequisites PASS;
- exact pinned checkout;
- configure PASS;
- Metal ON;
- target build failed because the LOOM probe set `LLAMA_BUILD_SERVER=OFF`, which at the pinned source commit omits `llama-cli`.

Record:
- `research/runtime/llama-cpp-setup-probe-002.md`

Correction:
- `LLAMA_BUILD_SERVER=ON`
- `LLAMA_BUILD_UI=OFF`
- `LLAMA_BUILD_COMMON=ON`
- `LLAMA_BUILD_TOOLS=ON`
- Metal settings and pinned commit unchanged.

### Setup Probe 003 — PASS / CANONICAL SETUP RESULT

Run id: `20260818-234628`.

Observed:
- pinned commit exact match
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
- overall success `True`

Local build:
- source: `results-local/llama-cpp/source-60addddf3c56`
- build: `results-local/llama-cpp/source-60addddf3c56/build-loom-metal`

Record:
- `research/runtime/llama-cpp-setup-probe-003.md`

Conclusion:
> The reference Apple M1 / 8 GB machine can build the pinned llama.cpp Release binaries with Metal enabled. Phase 4 runtime/model testing is authorized.

## llama.cpp 4B Runtime Control 001 — PREREGISTERED / READY

Plan:
- `research/runtime/llama-cpp-4b-control-001-plan.md`

Runner:
- `scripts/llama_cpp_4b_control.py`

Frozen model artifact:
- official repo `Qwen/Qwen3-4B-GGUF`
- file `Qwen3-4B-Q4_K_M.gguf`
- quantization `Q4_K_M`
- expected SHA256 `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- published size about 2.5 GB

Runner behavior:
- uses the exact pinned llama.cpp build;
- unloads the canonical Ollama model first if Ollama is available;
- downloads/resumes the model into ignored `results-local/models/`;
- verifies SHA256 before execution;
- records `llama-bench --list-devices`;
- runs `llama-bench` at `-ngl -1`, flash-attn auto, pp512, tg128, 3 repetitions;
- records JSON throughput output, backend/device evidence and offload log lines;
- samples process RSS, swap and memory-pressure free percentage while the benchmark runs.

This control is **not** an apples-to-apples model quality comparison with `qwen3.5:4b-mlx`. It validates the llama.cpp/GGUF/Metal measurement path.

Success authorizes the next main experiment:
- Qwen3 8B Q4_K_M
- initial context 4096
- maximum practical Metal/GPU offload first.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/llama_cpp_4b_control.py
python3 scripts/llama_cpp_4b_control.py
```

The first run will download approximately 2.5 GB if the verified GGUF is not already present. The download is resumable.

Preserve complete output from `LOOM llama.cpp 4B Runtime Control 001` through the final `Summary:` line, including device and benchmark sections.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 baseline: DONE
- Phase 2 Coding Benchmark/Baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: materially complete; Pi primary, Qwen Code secondary
- **Phase 4 llama.cpp: ACTIVE — Metal setup validated, 4B runtime control ready**
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD/MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
