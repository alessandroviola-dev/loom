# LOOM — llama.cpp 4B Runtime Control 001 Plan

Date: 2026-08-18
Status: **PREREGISTERED / READY**

## Purpose

Validate the Phase 4 llama.cpp measurement path on the reference Apple M1 / 8 GB machine before stressing the machine with an 8B model.

This is a runtime/instrumentation control, not a quality comparison with the existing Ollama/MLX `qwen3.5:4b-mlx` baseline.

## Frozen runtime

- llama.cpp source: `ggml-org/llama.cpp`
- pinned commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- build: Release
- backend: Metal
- `GGML_METAL=ON`
- `GGML_METAL_EMBED_LIBRARY=ON`
- binaries from the validated Setup Probe 003 build tree

## Frozen model artifact

Official model repository:
- `Qwen/Qwen3-4B-GGUF`

Artifact:
- file: `Qwen3-4B-Q4_K_M.gguf`
- quantization: `Q4_K_M`
- expected SHA256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- published file size: approximately 2.5 GB

The runner downloads the exact named artifact from the repository's `main` resolve endpoint and then verifies the SHA256. A hash mismatch invalidates the run instead of silently accepting changed bytes.

## Pre-run controls

- require validated `llama-bench` and `llama-cli` binaries from the pinned build;
- require `curl`, `sysctl`, `ps`, and macOS `memory_pressure`;
- require enough local free disk for the GGUF plus result data;
- unload the canonical Ollama model before benchmarking so Ollama does not occupy unified memory during the llama.cpp control;
- preserve existing downloaded model bytes when their SHA256 already matches.

## Benchmark condition

Primary `llama-bench` condition:

- model: local verified `Qwen3-4B-Q4_K_M.gguf`
- maximum GPU/Metal layer offload: `-ngl -1`
- flash attention: `auto`
- prompt-processing test: 512 tokens
- generation test: 128 tokens
- repetitions: 3
- normal llama-bench warmup retained
- JSON result output

`llama-bench` measurements are used for raw prompt-processing and text-generation throughput. They do not include tokenization/sampling time and must not be presented as end-to-end agent latency.

## Device/runtime verification

Before the benchmark, run `llama-bench --list-devices` and preserve the exact output. The benchmark result/logs must show the actual backend/device and GPU-layer configuration; do not infer full Metal offload from the build flag alone.

## Memory telemetry

Capture:

- macOS memory state before download/benchmark;
- swap before benchmark;
- process RSS samples while `llama-bench` is alive;
- swap samples during the benchmark;
- periodic memory-pressure free percentage;
- peak process RSS;
- peak observed swap;
- minimum observed free-memory percentage;
- final memory state after the process exits.

These metrics are observational. Process RSS is not assumed to equal total Metal/unified-memory allocation.

## Success criteria

The control is valid/successful only if:

1. pinned llama.cpp binaries exist;
2. model download/cache completes;
3. model SHA256 exactly matches the preregistered value;
4. `llama-bench` exits cleanly;
5. stdout parses as JSON;
6. at least one prompt-processing row and one generation row are present;
7. benchmark rows report positive throughput;
8. Metal/device evidence is preserved in device output and benchmark/log metadata.

A benchmark failure or hash mismatch is recorded as a result; do not change quantization, model, llama.cpp commit, or benchmark token counts as an in-run rescue.

## Interpretation

If the 4B control passes, Phase 4 measurement infrastructure is considered validated and the next experiment is the Qwen3 8B Q4_K_M capability test at context 4096.

If the 4B control fails, diagnose the exact download/runtime/backend issue before moving to 8B.
