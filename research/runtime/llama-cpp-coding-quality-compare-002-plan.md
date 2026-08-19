# LOOM — llama.cpp Coding Quality Compare 002 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY AFTER RUNNER COMMIT**

## Research question

Does the technically viable Qwen3-8B Q3_K_M profile deliver higher structured coding quality than Qwen3-4B Q4_K_M when both are run through the same pinned llama-server configuration, with the same context, parallelism, KV-cache precision, benchmark, request envelope, parser, scorer and safety guardrails?

## Why this comparison is needed

Qwen3-8B Q2_K was technically runnable but lost Coding Quality Compare 001 to the 4B Q4 control, 0/100 versus 34.29/100 delivery-adjusted. Q3 is the first higher-precision 8B profile to pass the technical/API gate at context 4096 on the reference M1 8 GB machine, using explicit single-sequence server parallelism and Q8_0 K/V KV cache.

A quality comparison is required before exposing Q3 to Pi.

## Frozen benchmark

- LOOM Coding Benchmark 01
- version: `1.0.1`
- tasks: T01–T06
- frozen prompts and fixture tree
- same single-shot adapter and scorer used by Coding Quality Compare 001
- no task retries
- no test feedback
- no salvage
- no prompt rewriting
- no post-hoc relaxation of the file-delivery envelope

## Profiles

### Profile A — Qwen3 8B Q3_K_M

- repository: `unsloth/Qwen3-8B-GGUF`
- file: `Qwen3-8B-Q3_K_M.gguf`
- SHA256: `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size: ~3.841 GiB

### Profile B — Qwen3 4B Q4_K_M

- repository: `Qwen/Qwen3-4B-GGUF`
- file: `Qwen3-4B-Q4_K_M.gguf`
- SHA256: `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`
- observed size: ~2.326 GiB

## Identical runtime condition for both profiles

- Apple M1, 8 GB unified memory
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- existing Release/Metal build
- `llama-server`
- raw `POST /completion`
- context `-c 4096`
- parallelism `-np 1`
- Flash Attention `-fa auto`
- **no forced `-ngl -1`**
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- `-ctk q8_0`
- `-ctv q8_0`
- localhost only
- offline
- Web UI disabled
- one profile server at a time
- stop the canonical Ollama model before each profile when available

Using Q8_0 KV for both profiles avoids comparing Q3/Q8-KV against a 4B/F16-KV control. This is a practical same-runtime comparison; it still does not isolate parameter count and weight quantization as independent causal variables.

## Frozen request envelope

For every task:

```text
endpoint = /completion
n_predict = 2048
temperature = 0
seed = 0
stream = false
cache_prompt = false
json_schema = {}
```

The benchmark prompt is passed directly as the raw completion prompt. No chat template is added.

## Primary metric

Primary metric: **delivery-adjusted benchmark score**.

For each profile, only benchmark points from tasks whose model output successfully passes the frozen adapter and is written to the expected files contribute to the primary score.

Primary relation:

```text
8B_HIGHER  if score_Q3 > score_4B
4B_HIGHER  if score_Q3 < score_4B
TIE        if equal
```

## Secondary observations

Record without changing the primary decision rule:
- artifact score;
- written task count;
- per-task adapter status/error;
- HTTP status;
- stop type;
- evaluated/predicted tokens;
- server readiness;
- process RSS;
- swap;
- minimum system-wide free-memory percentage;
- disk before/after.

## Safety guardrails

Unchanged LOOM thresholds for both profiles:
- abort if system-wide free memory falls below **5%**;
- abort if swap exceeds **5600 MB**.

If either profile hits a guardrail or otherwise cannot complete all six attempts, the overall comparison classification is `PARTIAL`; do not infer a clean quality ordering from a resource-failed profile.

## Order

Run Qwen3 8B Q3_K_M first, terminate it fully, cooldown, then run Qwen3 4B Q4_K_M. This preserves the large-profile-first convention from Compare 001. No simultaneous servers.

## Success / classification

`COMPLETE` requires both profiles to:
- pass model SHA preflight;
- reach server health under the common runtime condition;
- remain above/below the frozen memory/swap guardrails;
- attempt all six frozen tasks;
- complete benchmark scoring.

If both are `COMPLETE`, report the primary quality relation and score delta Q3-minus-4B.

## Decision after result

### If Q3 is higher

Q3 becomes the leading llama.cpp candidate. Freeze the quality result, then preregister a Pi integration/agentic validation using isolated LOOM configuration; do not alter production Pi configuration.

### If 4B is higher or tied

Do not expose Q3 to Pi as an assumed upgrade. Close the current llama.cpp 8B frontier and proceed to Direct MLX unless diagnostics identify a preregistered, non-post-hoc reason to test one further runtime condition.

### If comparison is partial/resource-failed

Diagnose the exact resource or harness mechanism from saved artifacts before changing any parameter.

Do not test ~9B before resolving this gate.
