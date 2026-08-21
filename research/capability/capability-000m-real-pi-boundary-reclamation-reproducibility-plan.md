# CAPABILITY 000M — Real Pi boundary-reclamation reproducibility plan

Date: 2026-08-21
Branch: `research/stretch-015-divergence-attribution`
Status: FROZEN PLAN

## Purpose

Promote the CAPABILITY 000L boundary mechanism into the actual Pi-integrated bridge and determine whether the frozen numbers.txt task completes reproducibly across three independent real Pi runs.

The treatment is exactly:

1. after each fully completed model HTTP response, identify the stale finished `GenerationBatch.Response` for that completed request;
2. detach only its stale `prompt_cache` with ownership verification;
3. call `mx.clear_cache()` exactly once;
4. then allow the next Pi/model request.

No other scientific factor changes.

## Frozen model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- max assistant output 2048
- thinking disabled
- `prefill_step_size=512`
- four Pi tools: read/write/edit/bash
- same localhost provider/bridge
- no Ollama/cloud fallback

## Frozen task

Fresh disposable workspace per attempt.

`numbers.txt` exact bytes:

```text
7
11
13
```

Pi instruction:

Read numbers.txt. Compute the sum. Create answer.txt containing exactly `31`. Verify it using an appropriate shell command. Do not modify numbers.txt. When finished reply exactly `DONE`.

## Host admission

Before each independent attempt:
- free memory >=60% for two consecutive passive samples;
- swap <=5600 MB.

After an attempt terminates, wait passively for natural host recovery. CAPABILITY 000G established that the host normally returns to >=60% within seconds.

No purge, scripted process kills, artificial allocation or swap manipulation.

## Attempt independence

Exactly three admitted attempts.

Each gets:
- fresh scientific server/model process;
- fresh Pi session;
- fresh workspace;
- no inference preflight in the scientific model process;
- empty conversation/request state.

No scientific retry, prompt rescue, manual tool injection or hidden file repair.

## Boundary treatment

After every completed model HTTP response in each attempt:

- verify exact completed-request ownership;
- detach only that finished response's stale `prompt_cache`;
- record active/cache/free/swap before and after detach;
- call `mx.clear_cache()` exactly once;
- record clear latency and post-clear state.

Forbidden:
- `gc.collect()`;
- model reload between turns;
- server restart within an attempt;
- queue-wide/global generator reset;
- context/KV/prompt/tool/prefill/model changes.

## Resource abort

After an attempt starts model execution, hard abort only if:
- system free <5%; or
- swap >5600 MB.

A resource abort is valid scientific evidence.

## Functional pass per attempt

Require all:
- model drives Pi successfully;
- reads numbers.txt;
- computes sum 31;
- creates `answer.txt` exactly `31`;
- executes actual shell verification;
- numbers.txt remains byte-identical;
- no destructive/out-of-workspace action;
- no fallback;
- no resource abort/core inference failure.

Strict pass additionally requires final assistant text exactly `DONE`.

## Measurements

Per model turn:
- input tokens;
- message count;
- action/tool;
- generated tokens where reliable;
- KV logical/capacity where safely observable;
- MLX peak;
- minimum free %;
- peak swap;
- boundary pre-detach active/cache;
- post-detach active/cache;
- post-clear active/cache;
- cache-clear latency;
- telemetry errors.

Persist exact request bodies and tool trace.

Actual prefill/generation timing is optional unless instrumentation is known-correct. Do not reuse the non-canonical ~0.01 s timing artifact from 000K.

## Classification

- `CAPABILITY_000M_REAL_PI_REPRODUCIBLE_PASS` — 3/3 functional pass.
- `CAPABILITY_000M_REAL_PI_MIXED_RELIABILITY` — 1/3 or 2/3 functional pass.
- `CAPABILITY_000M_REAL_PI_REPRODUCIBLE_RESOURCE_FAIL` — 0/3 due valid resource aborts.
- `CAPABILITY_000M_HOST_NOT_READY` — attempts cannot be admitted naturally.
- `CAPABILITY_000M_INFRASTRUCTURE_INCOMPLETE` — bridge/treatment instrumentation prevents valid science.

## Promotion rule

Only `3/3` functional pass admits the boundary-reclamation bridge into CAPABILITY 001.

Strict final-text formatting is secondary and must not erase functional capability.

## Evidence

Write under:
`results-local/capability/capability-000m/<run-id>/`

At minimum:
- summary.json
- host-admission.jsonl
- attempt-01/ ... attempt-03/
- requests/
- turn-metrics.jsonl
- boundary-metrics.jsonl
- tool-trace.json
- memory-samples.jsonl
- final-state.json

Do not proceed to CAPABILITY 001 automatically. ChatGPT reviews first.
