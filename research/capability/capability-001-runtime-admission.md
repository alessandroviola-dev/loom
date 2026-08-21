# CAPABILITY 001 — admitted runtime profile

Date: 2026-08-21
Status: FROZEN BEFORE RUN

This document complements `capability-001-frozen-spec.md` and `capability-001-context-amendment.md`.

## Admitted bridge/runtime

CAPABILITY 000M established 3/3 functional and 3/3 strict real-Pi reproducibility for the canonical local bridge.

Freeze the CAPABILITY 001 runtime to:

- Qwen3-8B full parameter count;
- affine 3-bit/group64;
- BF16 KV;
- MLX/mlx-metal 0.31.2;
- mlx-lm 0.31.3;
- context 4096;
- max assistant output 2048;
- `enable_thinking=false`;
- `prefill_step_size=512`;
- built-in M1 `qmv_fast`;
- localhost-only `loom-mlx-local` provider;
- Pi tools `read`, `write`, `edit`, `bash`;
- no Ollama/cloud fallback.

## Request-boundary policy

After every fully completed model HTTP response:

1. verify ownership of the finished `GenerationBatch.Response`;
2. detach only that completed response's stale `prompt_cache`;
3. call `mx.clear_cache()` exactly once.

This policy is part of the admitted runtime for CAPABILITY 001 because CAPABILITY 000I–000M showed that it removes stale completed-request KV ownership, returns allocator cache to system headroom, preserves semantics, and gives reproducible real-Pi execution.

Do not change or disable this boundary policy inside CAPABILITY 001.

## Host admission

Before each fresh CAPABILITY 001 task process/session:

- require system free memory >=60% on two consecutive passive samples;
- require swap <=5600 MB;
- wait passively for natural recovery when necessary;
- no purge, unrelated process kills, artificial allocations or swap manipulation.

Each task uses a fresh isolated Pi session and disposable workspace.

## Resource abort

After admitted model execution begins, abort only if:

- system free <5%; or
- swap >5600 MB.

A resource abort is task evidence; do not rescue or retry the task.

## Scientific boundary

CAPABILITY 001 measures capability, not runtime optimization.

Do not change:

- model weights/quantization;
- KV representation;
- context/output limits;
- prefill step;
- prompt/tool schemas outside each frozen task;
- boundary reclamation policy.

Any future representation/runtime candidate must later be compared against this same capability baseline on memory, speed and capability together.
