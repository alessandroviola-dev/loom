# LOOM — llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY AFTER RUNNER COMMIT**

## Research question

Can the existing Qwen3-8B Q3_K_M profile safely serve at context 4096 when the already-controlled single-slot server condition (`-np 1`) is retained and only the main-model KV-cache precision is reduced from the pinned default F16/F16 to Q8_0/Q8_0?

## Motivation

Q3 Auto-Fit NP1 Server Smoke 001 successfully produced `n_slots = 1` but still hit the frozen memory guardrail at 4% free memory. Therefore reducing server parallelism from four slots to one was insufficient.

At the pinned llama.cpp commit, main-model K and V cache types default to F16. The CLI exposes `-ctk/--cache-type-k` and `-ctv/--cache-type-v`, and Q8_0 is an allowed KV-cache type. This experiment changes only those two representations from F16 to Q8_0 while preserving the entire NP1 condition.

## Frozen artifact

- repository: `unsloth/Qwen3-8B-GGUF`
- file: `Qwen3-8B-Q3_K_M.gguf`
- quantization: `Q3_K_M`
- SHA256: `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size: ~3.841 GiB
- reuse local verified artifact; no download

## Runtime condition

Unchanged from Q3 Auto-Fit NP1 Server Smoke 001:
- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- existing Release/Metal build
- `llama-server`
- Metal
- context `-c 4096`
- parallelism `-np 1`
- Flash Attention `-fa auto`
- no forced `-ngl -1`
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- localhost only
- Web UI disabled
- offline
- stop canonical Ollama model before launch if available
- one synchronous `Reply only with OK.` chat-completion smoke

Changed variable only:
- previous main-model K cache: F16 -> new `-ctk q8_0`
- previous main-model V cache: F16 -> new `-ctv q8_0`

No weight quantization, context, fit target, server parallelism, request or safety threshold changes are permitted.

## Safety guardrails

Unchanged:
- abort if system-wide free memory falls below **5%**;
- abort if swap exceeds **5600 MB**.

A 4% sample remains a FAIL even if the server subsequently reports `model loaded` or begins listening.

## Validation requirements

The runner must:
1. verify the exact model SHA256;
2. verify the frozen Q3 auto-fit base runner blob before transformation;
3. issue explicit `-np 1 -ctk q8_0 -ctv q8_0`;
4. require stderr evidence `n_slots = 1`;
5. record the exact server command and a boolean proving both Q8_0 cache flags were requested;
6. sample process RSS, swap and system memory pressure through readiness and the API request;
7. preserve stderr/stdout, health history, samples, request response and summary.

## Success criteria

`FULL_PASS` requires all of:
- model SHA256 PASS;
- pinned runtime preflight PASS;
- command evidence for both Q8_0 cache flags;
- stderr evidence `n_slots = 1`;
- server reaches HTTP 200 health;
- no guardrail breach;
- chat-completion request returns HTTP 200 with non-empty assistant content;
- controlled shutdown.

## Failure classification

A memory/swap guardrail breach is a **VALID FAIL** for this Q8_0 condition.

Argument rejection, missing slot evidence, model hash mismatch or harness/preflight failure must be classified by mechanism and not interpreted as a model-quality result.

## Decision after result

### If FULL_PASS
Freeze telemetry and the exact cache/slot condition. Before Pi, preregister the frozen Coding Benchmark 01 comparing Q3 Q8-KV against 4B Q4 under controlled single-slot llama-server settings. Because KV quantization is a runtime-state compression rather than weight quantization, the quality benchmark is still required; do not assume semantic neutrality.

### If memory VALID FAIL
Do not stack further post-hoc llama.cpp changes immediately. Treat Q3 at context 4096 as not yet viable under the current llama.cpp safety target and move the main research branch to Direct MLX. A more aggressive KV type such as Q4 may remain an explicit later experiment only if justified separately.

### Regardless
Do not lower the guardrail or test ~9B yet.
