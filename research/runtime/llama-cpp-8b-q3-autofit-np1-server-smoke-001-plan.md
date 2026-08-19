# LOOM — llama.cpp 8B Q3 Auto-Fit NP1 Server Smoke 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY AFTER RUNNER COMMIT**

## Research question

Can Qwen3-8B Q3_K_M serve safely at context 4096 when the pinned `llama-server` is restricted to one parallel sequence instead of its automatic four-slot default, while all other settings from Auto-Fit Server Smoke 001 remain unchanged?

## Motivation

Auto-Fit Server Smoke 001 was a valid memory-guardrail failure at 4% free memory. Post-run diagnostics showed the server initialized:

```text
n_slots = 4
n_ctx_slot = 4096
kv_unified = true
```

At the pinned llama.cpp commit, server `n_parallel` defaults to auto and single-model server mode resolves auto to `n_parallel = 4`, `kv_unified = true`. LOOM currently sends one request at a time, so four parallel server slots are unnecessary for this experiment.

This experiment changes only the server parallelism to `-np 1`. It does not change quantization, context, KV precision, fit target, safety threshold or request shape.

## Frozen artifact

- repository: `unsloth/Qwen3-8B-GGUF`
- file: `Qwen3-8B-Q3_K_M.gguf`
- quantization: `Q3_K_M`
- SHA256: `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size: ~3.841 GiB
- local verified artifact must be reused; no download

## Runtime condition

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- existing Release/Metal build
- `llama-server`
- Metal
- explicit context `-c 4096`
- explicit parallelism `-np 1`
- Flash Attention `-fa auto`
- no forced `-ngl -1`
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- default K/V KV-cache types
- localhost only
- Web UI disabled
- offline
- stop canonical Ollama model before launch when Ollama is available

## Single changed variable

Compared with Q3 Auto-Fit Server Smoke 001:

```text
previous: server automatic parallelism -> observed n_slots = 4
new:      -np 1                    -> required n_slots = 1
```

No other memory strategy is changed.

## Safety guardrails

Unchanged LOOM thresholds:
- abort if system-wide free memory falls below **5%**;
- abort if swap exceeds **5600 MB**.

The guardrail remains authoritative even if the server reaches `model loaded` or begins listening.

## Procedure

1. Record free disk and memory baseline.
2. Verify pinned llama.cpp source commit/build.
3. Verify Q3 model exact SHA256 and size.
4. Verify localhost port availability.
5. Stop `qwen3.5:4b-mlx` if Ollama is present.
6. Launch `llama-server` with the frozen runtime condition and explicit `-np 1`.
7. Poll `GET /health` while sampling process RSS, system memory pressure and swap.
8. Abort immediately on a frozen guardrail breach.
9. Require server stderr evidence of `n_slots = 1`.
10. If healthy and safe, send one synchronous `/v1/chat/completions` request: `Reply only with OK.` with temperature 0, max 8 tokens, reasoning disabled.
11. Continue telemetry through the request and final sample.
12. Terminate server and save all logs/artifacts.

## Success criteria

`FULL_PASS` requires all of:
- model SHA256 PASS;
- exact pinned runtime preflight PASS;
- server reaches HTTP 200 health;
- stderr contains `n_slots = 1`;
- no memory/swap guardrail breach;
- API request returns HTTP 200 with non-empty assistant content;
- controlled shutdown succeeds.

## Failure classification

A guardrail breach is a **VALID FAIL** for this NP1 condition.

A missing `n_slots = 1` log is a harness/configuration validation failure, not a model failure.

If the server process exits, API fails or model hash/preflight fails, classify by the exact mechanism; do not reinterpret it as a Q3 quality result.

## Decision after result

### If FULL_PASS
Freeze actual telemetry and slot evidence. Then preregister Q3 vs 4B Q4 on Coding Benchmark 01 using explicit `-np 1` for both profiles so server concurrency is controlled before any Pi test.

### If memory VALID FAIL
Do not reduce context or lower the guardrail. The next single-variable llama.cpp rescue may be Q3 KV-cache compression, starting with Q8_0, but only as a separately preregistered condition. Direct MLX remains a parallel next-phase option.

### Regardless
Do not proceed to ~9B until the useful 8B frontier is resolved.