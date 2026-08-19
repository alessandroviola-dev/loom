# Capability Amplifier 003 — Partial Result

Date: 2026-08-19
Run id: `20260819-150342`
Status: **PARTIAL_RESOURCE_FAIL / DIAGNOSTIC REQUIRED**

## Frozen profile

Plan: `research/amplify/capability-amplifier-003-repair-context-3072-plan.md`
Runner: `scripts/capability_amplifier_003_repair_context_3072.py`
Runner blob: `c2bcc8f126eb5b599645ba12d1fd08a348e2b443`

Primary model: `qwen3.5:4b-mlx` via Ollama.

Frozen behavior:
- initial calls `num_ctx=4096`
- repair calls `num_ctx=3072`
- call isolation before/after every model call
- exact frozen initial prompt/request/parser
- exact frozen repair prompt content and validation feedback
- max one repair
- deterministic candidate selection
- free-memory guardrail `<5%`
- swap guardrail `>5600 MB`
- initial host gate: 3 consecutive samples >=70% free.

## Launch evidence

A prior attempt `20260819-150107` returned `HOST_STATE_NOT_READY` at 69% free with zero model calls. It is not a scientific model result.

Valid run `20260819-150342`:
- disk before: 36.344 GiB free
- frozen adapter/scorer/manifest: PASS
- model presence: PASS
- host samples: 71%, 74%, 74% free
- host swap: 1247.88 MB
- host-state gate: PASS.

## Task progression

Observed terminal progression:
- T01 initial call completed and solved without repair
- T02 initial call completed
- T02 repair was authorized from `frozen_test_failure`
- run terminated during the T02 repair path.

Terminal classification:
`PARTIAL_RESOURCE_FAIL`

Completed model-call records reported by the runner:
`2`

No final scorer result exists, so no aggregate artifact/delivery quality score is valid.

## Disk

- before: 36.344 GiB
- after: 35.342 GiB

## Interpretation boundary

The terminal excerpt confirms that repair context 3072 did not allow the run to complete, but it does **not** expose:
- the exact failure reason;
- whether the T02 repair actually launched with recorded context 3072;
- repair pre-isolation free memory / swap;
- repair telemetry trajectory;
- whether the failure was free-memory, swap, telemetry, isolation, runtime, or another classified cause.

Therefore do not yet conclude that reducing repair context from 4096 to 3072 had no resource effect or that the repair architecture itself is definitively the sole issue.

## Required next step

Run the existing read-only inspector against:

`results-local/amplify/capability-amplifier-003-repair-context-3072/20260819-150342`

Recover exact failure reason, context records and telemetry before designing Amplifier 004.
