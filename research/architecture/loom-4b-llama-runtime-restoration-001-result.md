# LOOM 4B llama.cpp Runtime Restoration 001 — Result

Date: 2026-08-28
Status: **LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO**

## Result

The mechanical restoration rebuilt the historically pinned llama.cpp runtime successfully, including `llama-cli`, `llama-bench`, and `llama-server`, at exact source commit:

`60addddf3c567c43ec3caf70fc953fba3572d96f`

The setup probe and exact `llama-server` target build both exited 0. Frozen configuration was preserved: Release, Metal ON, embedded Metal ON, tests OFF, server ON, UI OFF, common ON, tools ON. Apple M1 Metal was visible through `llama-bench --list-devices`.

However, during the authorized server-target build, the llama.cpp build system unexpectedly downloaded a UI asset from Hugging Face. That network operation was outside the preregistered authorization. Per fail-closed policy the checkpoint classification is therefore `LOOM_4B_LLAMA_RUNTIME_RESTORATION_NO_GO` even though the resulting binaries are mechanically present and diagnostic checks pass.

## Important interpretation

This is a provenance/protocol failure of the restoration checkpoint, not a model/runtime-functional failure.

No model was downloaded, copied, converted, loaded, or used for inference. No model-like file under `results-local` was modified. Tracked LOOM files remained unchanged. The unexpected artifact was a UI asset, not a model artifact.

The resulting pinned runtime now exists locally:
- `build-loom-metal/bin/llama-cli` — diagnostic PASS;
- `build-loom-metal/bin/llama-bench` — diagnostic PASS;
- `build-loom-metal/bin/llama-server` — diagnostic PASS;
- exact source HEAD — PASS;
- Metal backend/device — PASS.

Because the restoration checkpoint violated its frozen network boundary, it cannot be retroactively reclassified GO. A separate preregistered checkpoint is required to decide whether the already-built binaries may be used without rebuilding.

## Host / provenance

- Active LOOM root: `<repository-root>`
- LOOM HEAD at run: `041ae309709a85cf396f080b3c3f9dd5c5aa45f8`
- setup probe SHA: `f7a49cc9e31a3754fcb7d5b0a912f93e2eadbd22`
- Python `3.13.0`
- CMake `4.4.2`
- Xcode `26.6`
- Apple Clang `21.0.0`
- arm64
- free memory `68% -> 67%`
- swap `1843.06 MiB -> 1827.06 MiB`

## Evidence

`results-local/research/4b-llama-runtime-restoration-001/20260828T150632Z/`
