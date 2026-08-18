# llama.cpp Phase 4 — Setup and Capability Plan

Date: 2026-08-18
Status: PREREGISTERED / SETUP READY

## Research goal

Return LOOM to the main runtime/model-capability path after validating Pi as the primary local agent harness.

Question:
> Can llama.cpp on the reference Apple M1 / 8 GB machine provide a better practical frontier for quantized models, GPU offload and larger useful local models than the current Ollama/MLX baseline?

## Reference machine

- Apple M1
- 8 GB unified memory
- macOS

## Pinned llama.cpp source

Official repository: `ggml-org/llama.cpp`

Pinned source commit for the first Phase 4 setup:
- `60addddf3c567c43ec3caf70fc953fba3572d96f`
- observed current `master` on 2026-08-18

Pinning the commit makes the first measurements reproducible even if llama.cpp changes rapidly afterward.

## Setup build

The initial setup probe will:

1. verify `git`, `cmake`, `xcrun` and C/C++ toolchain availability;
2. clone/fetch the pinned llama.cpp commit into `results-local/llama-cpp/`;
3. configure a Release build with Metal explicitly enabled;
4. build `llama-cli` and `llama-bench`;
5. verify the built binaries and `GGML_METAL=ON` in CMake cache;
6. record machine/toolchain/source metadata;
7. avoid downloading any model during setup.

The source/build tree is local experimental state and is not committed into LOOM.

## Initial model sequence after setup

### Stage A — 4B GGUF runtime control

Use the official Qwen GGUF family as a runtime control:
- `Qwen/Qwen3-4B-GGUF`
- `Q4_K_M`

Purpose:
- validate GGUF download/inference;
- validate Metal offload;
- establish llama.cpp telemetry and throughput methodology before stressing the 8 GB machine.

This is **not** an apples-to-apples quality comparison with the existing `qwen3.5:4b-mlx`, because the model family/version and quantization differ.

### Stage B — 8B Q4 main capability test

Then test:
- `Qwen/Qwen3-8B-GGUF`
- `Q4_K_M`
- context 4096 initially
- maximum practical Metal/GPU offload first

This is the first Phase 4 test directly aligned with LOOM's "Big models. Small machines." objective.

## Metrics

For each inference condition capture where available:

- exact llama.cpp commit/build
- model repo/file/quantization
- model file size
- context
- GPU-offloaded layers / backend information
- model load time
- prompt-eval tokens and tok/s
- generation tokens and tok/s
- wall time
- PhysMem
- system memory free percentage
- swap before/after/peak sampling where implemented
- process success/failure

Later controlled conditions may compare partial GPU/CPU offload and more aggressive Q3/Q2 quantizations.

## Safety / machine guardrails

- Do not intentionally change macOS memory settings.
- Do not disable swap.
- Stop/escalate cautiously if the machine becomes unresponsive or sustained memory pressure becomes critical.
- Large-model launchability is not sufficient: LOOM cares about **useful** throughput and stability.

## Qwen Code decision

Qwen Code remains a secondary harness comparator. Its safe-mode 4096 diagnostic still exceeded the context budget (4363 estimated tokens vs hard limit 4096). Further Qwen Code minimization/8192 testing is deferred and does not block Phase 4.

## Immediate checkpoint

Run `scripts/llama_cpp_setup_probe.py`.

A successful setup requires:
- pinned source checkout matches exactly;
- CMake configure/build succeeds;
- `llama-cli` exists;
- `llama-bench` exists;
- CMake cache confirms Metal enabled.

Only after setup PASS should model downloads begin.
