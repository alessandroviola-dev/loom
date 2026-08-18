# LOOM — llama.cpp Setup Probe 002

Date: 2026-08-18
Status: **INVALID AS RUNTIME BUILD RESULT — PROBE CONFIGURATION DEFECT IDENTIFIED**
Run id: `20260818-234152`
Pinned llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`

## Observed

- CMake 4.4.2 installed successfully via Homebrew.
- Prerequisites: PASS.
- Pinned commit matched actual checkout exactly.
- CMake configure: PASS.
- `GGML_METAL=ON`.
- `GGML_METAL_EMBED_LIBRARY=ON`.
- Build command failed with:

```text
make: *** No rule to make target `llama-cli'. Stop.
```

- `llama-cli`: FAIL / absent.
- `llama-bench`: not produced because the multi-target build stopped on the missing `llama-cli` target.

## Root cause

This was a LOOM probe configuration defect, not evidence that llama.cpp cannot build on the reference M1.

At the pinned llama.cpp commit, `tools/CMakeLists.txt` adds `tools/cli` only inside:

```cmake
if (LLAMA_BUILD_SERVER)
    add_subdirectory(ui)
    add_subdirectory(cli)
    add_subdirectory(server)
endif()
```

The original LOOM setup probe explicitly configured `-DLLAMA_BUILD_SERVER=OFF`, so CMake correctly omitted the `llama-cli` target.

## Correction

`script/llama_cpp_setup_probe.py` was revised to:

- keep the same pinned llama.cpp commit;
- keep Release + Metal settings unchanged;
- set `LLAMA_BUILD_SERVER=ON` so `llama-cli` exists;
- set `LLAMA_BUILD_UI=OFF` so the embedded Web UI is not needed;
- explicitly set `LLAMA_BUILD_COMMON=ON` and `LLAMA_BUILD_TOOLS=ON`;
- record those CMake cache values in the result.

No model download or benchmark parameter changed.

## Interpretation

Do not classify this run as a llama.cpp build failure. It validates the Apple/Metal configure stage and exposes a harness defect before compilation of the intended binaries.

Next action: rerun the corrected setup probe unchanged at the same pinned source commit.
