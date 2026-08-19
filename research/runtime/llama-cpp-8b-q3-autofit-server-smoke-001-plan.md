# LOOM — llama.cpp 8B Q3 Auto-Fit Server Smoke 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY AFTER RUNNER COMMIT**

## Research question

Can the already-downloaded higher-quality Qwen3-8B Q3_K_M model run as a useful llama-server profile at context 4096 on the reference M1/8GB machine if llama.cpp is allowed to automatically choose a device-fit / partial-offload configuration instead of forcing `-ngl -1`?

This follows the Q2 quality diagnostic, which showed Q2 is technically runnable but loses reliable structured instruction following.

## Prior evidence

Q3 Capability 001, run `20260819-093842`, forced `-ngl -1` and failed the frozen 5% memory-free guardrail during Stage A:
- minimum free memory `1%`;
- peak RSS `1670.484375 MB`;
- peak swap `2269.38 MB`.

The failure was a valid memory failure, not a model-quality result.

## Model

- repository: `unsloth/Qwen3-8B-GGUF`
- file: `Qwen3-8B-Q3_K_M.gguf`
- expected SHA256: `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- existing verified local artifact only; no download

## Frozen runtime

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- existing Metal build / `llama-server`
- context exactly `4096`
- Flash Attention `auto`
- localhost only
- Web UI disabled
- offline mode
- one model server only

## Changed variable: device fit policy

Unlike Q3 Capability 001, **do not force `-ngl -1`**.

Use llama.cpp automatic fit policy explicitly:
- omit an exact numeric/all GPU-layer override;
- `--fit on`;
- `--fit-target 1024` MiB;
- `--fit-ctx 4096`;
- keep explicit `-c 4096`.

The intention is to preserve the Q3 weights and context while allowing llama.cpp to reduce device residency / GPU-layer placement if necessary.

No KV-cache quantization is introduced in this experiment. K/V cache types remain the runtime defaults, so the only intended memory-strategy change is device-fit/offload policy.

## Workload

1. Verify pinned source/build and exact model SHA256.
2. Stop the canonical Ollama model if loaded.
3. Start `llama-server` on localhost with the frozen auto-fit profile.
4. Poll `GET /health` until ready or failure.
5. If healthy, send one synchronous `/v1/chat/completions` request: `Reply only with OK.`
6. Request `reasoning_effort=none`, temperature 0, max 8 tokens.
7. Shut the server down immediately after the request.

## Safety guardrails

Unchanged from previous 8B work:
- abort below **5%** observed free memory;
- abort above **5600 MB** swap;
- no retry with altered parameters in the same run.

## Required telemetry

Record:
- exact model SHA256 and size;
- server command;
- readiness time;
- HTTP result / assistant content;
- process RSS samples;
- swap samples;
- memory-pressure samples;
- peak RSS;
- peak swap;
- minimum free-memory percentage;
- server stderr/stdout;
- log lines containing fit/offload/GPU-layer information where available;
- disk free before/after.

## Classification

### FULL_PASS
- model hash PASS;
- server reaches healthy state;
- API request returns HTTP 200 with non-empty assistant content;
- no timeout;
- no guardrail breach.

### FAIL
- model cannot load/serve under auto-fit, server exits, request fails, timeout occurs or a frozen guardrail is breached.

A FULL_PASS establishes only technical/API viability for Q3 under automatic fit. It does not establish quality superiority.

## Decision after run

If FULL_PASS:
- freeze the actual observed fit/offload behavior;
- then preregister a Coding Benchmark comparison of Q3 vs 4B Q4 under the same server transport before any Pi test.

If FAIL:
- do not change multiple variables post hoc;
- next candidate is a separately preregistered Q3 KV-cache compression condition (Q8_0 first) or Direct MLX.

Do not proceed to Q4 rescue or ~9B until the Q3 branch is characterized.
