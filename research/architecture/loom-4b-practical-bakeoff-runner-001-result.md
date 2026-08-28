# LOOM 4B Practical Bake-off Runner 001 — Result

Date: 2026-08-28
Status: **`LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`**

## Frozen checkpoint

Preregistration:
`research/architecture/loom-4b-practical-bakeoff-runner-001-preregistration.md`.

Local experimental runner created:
`scripts/loom_4b_practical_bakeoff_runner_001.py`.

The checkpoint required the historical pinned llama.cpp/Metal runtime to exist before inference and explicitly forbade rebuild/update or Ollama substitution. Therefore the correct action on missing runtime was to stop before model execution.

## Model artifact

The exact historical model artifact was found only in the archive tree:
`<external-archive>/models/Qwen3-4B-GGUF/Qwen3-4B-Q4_K_M.gguf`.

Verified identity:
- repo identity: `Qwen/Qwen3-4B-GGUF`;
- file: `Qwen3-4B-Q4_K_M.gguf`;
- quantization: `Q4_K_M`;
- SHA-256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` — PASS.

No model acquisition, conversion, requantization or copy was performed.

## Runtime readiness failure

Required historical llama.cpp identity:
`60addddf3c567c43ec3caf70fc953fba3572d96f`.

Observed at the active LOOM clone:
- historical pinned source/build not available at the expected runtime path;
- `build-loom-metal/bin/llama-server` absent;
- therefore Metal serving backend could not be validated;
- no server startup and no inference occurred.

The reported active Git repository HEAD (`e9a20c29...` at the time of the run) is not a substitute for the required external llama.cpp source commit and is not evidence of a model/runtime mismatch; the decisive readiness fact is that the pinned source/build/server was unavailable.

## Execution result

- classification: `LOOM_4B_BAKEOFF_RUNTIME_NOT_READY`;
- generated text: none;
- output tokens: `0`;
- task completion: `NOT_ASSESSED`;
- inference: **NOT EXECUTED**;
- preflight-only full runner wall: `24.284 s`;
- host telemetry readable;
- swap observed: `1874.38 MB` used of `3072 MB`;
- Metal/model performance: not measured.

Evidence:
`results-local/research/4b-practical-bakeoff-runner-001/20260828T145853Z/`.

## Scientific interpretation

This is a **mechanical runtime-availability result**, not a 4B capability or performance result. It supports no comparison claim against the matched 8B or 30B conditions.

The exact 4B model artifact is preserved and verified. The only blocker is reconstructing the already-canonical pinned llama.cpp/Metal toolchain before rerunning the unchanged frozen bake-off condition.

## Historical reproducibility target

Canonical historical setup probe 003 previously proved on the same machine:
- llama.cpp commit `60addddf...` exact;
- Release build;
- `GGML_METAL=ON`;
- `GGML_METAL_EMBED_LIBRARY=ON`;
- `LLAMA_BUILD_SERVER=ON`;
- `LLAMA_BUILD_UI=OFF`;
- `llama-cli` and `llama-bench` valid.

Historical 4B runtime control then measured `22.33 tok/s ± 0.02` text generation with the same verified Q4_K_M artifact.

Next checkpoint: reconstruct the pinned runtime only. Do not rerun the model until runtime restoration is separately accepted.