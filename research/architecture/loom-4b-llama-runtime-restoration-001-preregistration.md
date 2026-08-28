# LOOM 4B llama.cpp Runtime Restoration 001 — Preregistration

Date: 2026-08-28
Status: PREREGISTERED / NOT YET RUN

## Question

Can the historical pinned llama.cpp/Metal runtime required by the LOOM 4B practical bake-off be reconstructed exactly, without changing the model artifact or scientific bake-off condition?

This checkpoint is **mechanical runtime restoration only**. No model inference is authorized.

## Historical target

Pinned upstream repo:
`https://github.com/ggml-org/llama.cpp.git`

Pinned commit:
`60addddf3c567c43ec3caf70fc953fba3572d96f`

Canonical local source path:
`results-local/llama-cpp/source-60addddf3c56`

Canonical build path:
`results-local/llama-cpp/source-60addddf3c56/build-loom-metal`

Required CMake state:
- `CMAKE_BUILD_TYPE=Release`;
- `GGML_METAL=ON`;
- `GGML_METAL_EMBED_LIBRARY=ON`;
- `LLAMA_BUILD_TESTS=OFF`;
- `LLAMA_BUILD_SERVER=ON`;
- `LLAMA_BUILD_UI=OFF`;
- `LLAMA_BUILD_COMMON=ON`;
- `LLAMA_BUILD_TOOLS=ON`.

Historical setup source:
`scripts/llama_cpp_setup_probe.py`.

Current tracked setup probe SHA:
`f7a49cc9e31a3754fcb7d5b0a912f93e2eadbd22`.

Important: the existing probe configures server support but its explicit build target list is only `llama-cli` and `llama-bench`. Therefore, after a successful exact setup-probe run, this restoration checkpoint explicitly authorizes **one additional build command for the already-configured pinned source/build** targeting only `llama-server`.

## Authorized operations

1. Read-only preflight of active Git root, tracked setup-probe SHA, prerequisites, disk and host telemetry.
2. Execute the existing `scripts/llama_cpp_setup_probe.py` exactly as tracked.
   - Network access is authorized only to clone/fetch the official `ggml-org/llama.cpp` source if the pinned local source is absent/incomplete.
   - No model network access is authorized.
3. If and only if setup probe reports exact pinned source/configuration PASS, execute:
   `cmake --build results-local/llama-cpp/source-60addddf3c56/build-loom-metal --config Release --target llama-server`
   using a normal bounded local parallel build.
4. Verify exact source HEAD, CMake cache values, executable existence and basic read-only diagnostics.

No tracked source modifications are authorized in this checkpoint.

## Required verification

PASS requires all of:
- exact llama.cpp source HEAD equals `60addddf3c567c43ec3caf70fc953fba3572d96f`;
- `llama-cli` exists and executes `--version`;
- `llama-bench` exists and executes/help is valid;
- `llama-server` exists and executes `--version` or `--help` successfully without loading a model;
- CMake cache confirms Metal ON and embedded library ON;
- server ON, UI OFF, tools/common ON;
- `llama-bench --list-devices` exposes Apple M1 Metal device/backend;
- no model file was downloaded, copied, modified, converted or requantized;
- no inference/model load occurred;
- active LOOM tracked-file diff remains unchanged by restoration.

## Artifact preservation

The verified 4B model remains external/archive-only for now:
`<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`

Expected SHA:
`7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`.

Do not copy or mutate it during runtime restoration.

## Forbidden

No:
- model inference;
- model download/copy;
- Ollama;
- llama.cpp version update beyond the pinned commit;
- patching llama.cpp source;
- patching tracked LOOM source;
- different CMake flags;
- benchmarks involving model weights;
- skills/tools/RAG/memory;
- Heretic;
- speculative decoding;
- 4B bake-off execution in this same checkpoint.

## Evidence

Persist under:
`results-local/research/4b-llama-runtime-restoration-001/<timestamp>/`

Record:
- active LOOM root/HEAD/status;
- setup-probe SHA;
- prerequisite/toolchain versions;
- exact commands and exit codes;
- pinned llama.cpp source HEAD;
- complete CMake target flags;
- executable paths and hashes;
- `llama-cli`/`llama-bench`/`llama-server` diagnostic outputs;
- Metal device list;
- host memory/swap before/after;
- proof no model inference/acquisition occurred;
- final classification.

## Classification

`LOOM_4B_LLAMA_RUNTIME_RESTORATION_GO` only if all exact runtime/Metal/server checks pass.

Otherwise fail closed with `LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO` and preserve evidence. Do not automatically repair beyond the explicitly authorized setup probe + server-target build.

After GO, stop. The unchanged 4B practical bake-off runner is a separate next checkpoint.