# CAPABILITY 000F — Integrated Pi Reproducibility

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Question

Can the canonical Qwen3-8B 3-bit + Pi stack complete the frozen multi-turn `numbers.txt` task reproducibly with `prefill_step_size=512` when each attempt starts from a fresh scientific server process and an admitted passive host state?

CAPABILITY 000E showed that exact R2 (1576 tokens) succeeds both fresh and sequentially after R1 without cleanup. Therefore CAPABILITY 000D Fix2's resource abort is not established as an intrinsic prompt-length limit.

## Frozen model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- max output 2048
- `enable_thinking=false`
- `prefill_step_size=512`
- localhost bridge only
- Pi isolated configuration
- tools: read/write/edit/bash

## Frozen task

Disposable workspace contains `numbers.txt` with exact bytes:

```text
7
11
13
```

Pi is instructed to:

1. read `numbers.txt`;
2. compute the sum;
3. create `answer.txt` containing exactly `31`;
4. verify it with an appropriate shell command;
5. leave `numbers.txt` byte-identical;
6. finish exactly `DONE`.

One Pi session per attempt. No prompt rescue, manual tool injection, human correction or scientific retry within an attempt.

## Host admission

Before model load for every attempt:

- system free memory >=60%;
- swap <=5600 MB.

If the gate is not met, classify that launch sample `HOST_NOT_READY`; it does not consume one of the three scientific attempts.

No scripted process kills, `purge`, artificial allocation, swap manipulation or automated cleanup is allowed. Normal manual closure of unrelated user applications before a later launch sample is permitted as passive host preparation.

## Fresh-process requirement

Each scientific attempt uses a new server/model process.

No model preflight inference may run in that scientific process before the Pi task. Syntax/configuration checks and non-inference harness validation may occur separately.

Between attempts, terminate the completed scientific server normally; do not rely on request-level cleanup treatments.

## Attempts

Run exactly three admitted independent attempts unless a core infrastructure defect prevents further valid execution.

Each attempt is scored independently.

## Resource policy

During an admitted scientific attempt, hard abort if:

- system free memory <5%; or
- swap >5600 MB.

A resource abort after actual model execution is a valid scientific outcome.

## Metrics

For every model turn record:

- input token count;
- message count;
- M segments;
- prefill wall/tok/s;
- generated tokens and generation tok/s;
- tool/action and result size;
- KV logical/capacity;
- MLX active/peak/cache when safely observable;
- Pi RSS;
- minimum system free memory;
- peak swap;
- telemetry errors.

Persist exact request bodies and ordered tool trace.

## Success

Functional PASS for an attempt requires:

- actual canonical local model drives the Pi tool loop;
- `answer.txt` exists with exact content `31`;
- shell verification was actually executed;
- `numbers.txt` remains byte-identical;
- no destructive/out-of-workspace action;
- no provider fallback;
- no core inference failure;
- no resource abort.

Strict PASS additionally requires final assistant text exactly `DONE`.

## Aggregate classification

- `CAPABILITY_000F_REPRODUCIBLE_PASS`: 3/3 functional PASS.
- `CAPABILITY_000F_MIXED_RELIABILITY`: 1/3 or 2/3 functional PASS, with valid scientific failures in the remainder.
- `CAPABILITY_000F_REPRODUCIBLE_RESOURCE_FAIL`: 0/3 functional PASS because admitted attempts resource-abort after model execution.
- `CAPABILITY_000F_INFRASTRUCTURE_INCOMPLETE`: core harness/infrastructure defect prevents three valid scientific attempts.
- `CAPABILITY_000F_HOST_NOT_READY`: no admitted attempt can start because launch state never satisfies the frozen host gate during the run invocation.

Strict-protocol failures are reported separately from functional reliability.

## Decision rule

- 3/3 functional PASS: admit the 512 integrated bridge for CAPABILITY 001.
- 1/3 or 2/3: do not run CAPABILITY 001; first address reliability/headroom.
- 0/3 resource PASS: select the next isolated memory treatment from existing evidence.

No new treatment is tested inside CAPABILITY 000F.

## Pi boundary

Pi codes/tests only. No Git, HANDOFF or ROADMAP updates.
