# LOOM — llama.cpp Setup Probe 003

Date: 2026-08-18
Status: **PASS / VALID**
Run id: `20260818-234628`
Pinned llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`

## Result

The corrected Phase 4 setup probe passed all required checks on the reference Apple M1 / 8 GB machine.

Observed terminal result:

- pinned commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- actual commit: exact match
- prerequisites: PASS
- configure: PASS
- build: PASS
- `llama-cli`: PASS
- `llama-bench`: PASS
- `GGML_METAL=ON`
- `GGML_METAL_EMBED_LIBRARY=ON`
- `LLAMA_BUILD_COMMON=ON`
- `LLAMA_BUILD_TOOLS=ON`
- `LLAMA_BUILD_SERVER=ON`
- `LLAMA_BUILD_UI=OFF`
- overall success: `True`

Local source/build:

- source: `results-local/llama-cpp/source-60addddf3c56`
- build: `results-local/llama-cpp/source-60addddf3c56/build-loom-metal`
- summary: `results-local/llama-cpp/setup/20260818-234628/setup-summary.json`

## Interpretation

The Phase 4 toolchain/build gate is complete. At the pinned llama.cpp source commit, the reference Mac can build the intended Release binaries with the Metal backend enabled.

Setup Probe 001 remains a prerequisite-gate record (`cmake` missing). Setup Probe 002 remains an invalid runtime-build result caused by a LOOM CMake target-selection defect. Probe 003 is the first valid full setup result.

This result does not yet measure model performance or prove that larger GGUF models are useful on 8 GB. It authorizes the preregistered Stage A 4B GGUF runtime control.

## Next action

Run the dedicated Qwen3 4B Q4_K_M llama.cpp control before the 8B capability experiment.
