# CAPABILITY 000F — integrated Pi reproducibility / host recovery incomplete

Date: 2026-08-21
Status: COMPLETE AS DIAGNOSTIC / REPRODUCIBILITY STUDY INCOMPLETE

## Frozen intent

CAPABILITY 000F was designed to run three independent integrated Pi attempts with the canonical Qwen3-8B 3-bit model, BF16 KV, context 4096 and `prefill_step_size=512`, requiring a passive pre-load host gate of free memory >=60% and swap <=5600 MB before every scientific attempt.

## Observed admission

Attempt 1 pre-load:
- free memory: 65%
- swap: 1174.38 MB
- admitted: yes

Attempt 2 pre-load:
- free memory: 6%
- swap: 1848.25 MB
- admitted: no

Attempt 3 was not run because the host did not recover enough to admit attempt 2 during the invocation.

## Attempt 1 — valid science

Attempt 1 used the real Pi process and canonical local provider/model.

Observed:
- functional: FAIL
- strict: FAIL
- model turns: 2
- tool sequence: `read -> bash`
- largest input: 1576 tokens
- max KV: 1621 / 1792
- peak MLX: 4194.45 MB
- minimum free memory: 4%
- peak swap: 1860.94 MB
- elapsed: 53.144 s
- hard resource abort triggered
- `answer.txt` absent
- `numbers.txt` remained byte-identical
- telemetry errors: 0
- provider/model identity: canonical `loom-mlx-local` localhost bridge -> `results-local/mlx/models/Qwen3-8B-3bit/`

This is a valid scientific resource-abort attempt.

## Canonical interpretation

The reported run-level label `CAPABILITY_000F_HOST_NOT_READY` is operationally descriptive but must not be interpreted as `0/3` model reliability evidence.

Only one of three planned attempts was actually admitted. Therefore:

- attempt 1 = valid resource-abort science;
- attempt 2 = not admitted due host launch state;
- attempt 3 = not run;
- the planned three-attempt reproducibility measurement is incomplete.

CAPABILITY 000E already showed that exact R1->R2 direct replay can complete under controlled fresh-process conditions, including a sequential R2 peak of 4194.45 MB. Therefore the attempt-1 abort at the same approximate MLX peak further supports the conclusion that system-wide host state and recovery behavior materially affect the <5% free-memory gate.

## New unresolved question

Why did pre-load free memory fall from 65% before attempt 1 to 6% before attempt 2 even though each scientific attempt was intended to use a fresh server/model process?

Possible classes to distinguish without prematurely naming a leak:

1. prior scientific server/model process or child process did not fully terminate;
2. Metal/MLX/process resources remained live because process teardown was incomplete;
3. the process exited but macOS memory/compressor/page state recovered only after a delay;
4. host pressure from unrelated processes changed materially;
5. measurement timing captured a transient recovery phase;
6. unknown.

## Decision

Do not:
- classify CAPABILITY 000F as 0/3 model reliability;
- run CAPABILITY 001 yet;
- change chunk size from 512 yet;
- quantize KV;
- compress prompts/tools;
- change model precision;
- use purge or scripted host manipulation.

Next: CAPABILITY 000G — scientific-process teardown and natural host-recovery attribution.

The next study should prove process death, observe the process tree, and sample system memory/swap over time after model-server termination without purge or cleanup treatment. If host free memory naturally recovers to the >=60% launch gate after a bounded passive interval, a corrected 000F can wait for natural recovery between attempts. If the model/server process or resources remain alive, fix lifecycle first.
