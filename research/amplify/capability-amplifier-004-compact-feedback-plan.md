# Capability Amplifier 004 — Compact Feedback — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can the frozen validator + maximum-one-repair amplifier complete safely on the Apple M1 / 8 GB reference host when the repair feedback is serialized under a strict deterministic byte budget, while preserving the original task prompt, current candidate, call isolation and repair context 3072?

## Motivation

Amplifier 003 T02 prompt anatomy:
- initial prompt: 1638 UTF-8 bytes
- repair prompt: 4573 UTF-8 bytes
- repair / initial: 2.792x
- validation feedback alone: 2762 bytes, about 60.4% of the repair prompt.

Record:
`research/amplify/capability-amplifier-003-prompt-anatomy-t02.md`

Amplifier 003 resource diagnostic established that the T02 repair, already reduced to context 3072 and starting from 70% free memory after confirmed model unload, still crossed the 5% free-memory guardrail.

## Frozen provenance

Primary model: `qwen3.5:4b-mlx`
Runtime: Ollama

Amplifier 001 base runner blob:
`9f472c60b523762276291232f6e8c6ffc1c5fcae`

Amplifier 002 wrapper blob:
`df332568820e28c90baa5247df27e92cba43c0d6`

Amplifier 003 wrapper blob:
`c2bcc8f126eb5b599645ba12d1fd08a348e2b443`

Benchmark:
LOOM Coding Benchmark 01 v1.0.1

Frozen benchmark artifacts:
- manifest blob `547050ecd0183b8d447dc3e21e724a8232f10297`
- single-shot adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`

## Single changed factor vs Amplifier 003

Only repair-feedback serialization changes.

Frozen feedback budget:
**768 UTF-8 bytes maximum for the variable failure-detail body.**

For frozen-test failure:
- always preserve the deterministic first line `Passed X/Y frozen tests.`;
- preserve a deterministic UTF-8-safe tail of the scorer stderr under the 768-byte body budget;
- label the body as a compact tail.

For structured-output parser failure:
- always preserve the parser-error line;
- preserve a deterministic UTF-8-safe tail of the raw model output under the 768-byte body budget.

No semantic summarizer, model-generated compression, regex-based interpretation of hidden tests, human editing or task-specific rule is allowed.

## Preserved exactly

- model and weights
- Ollama runtime
- initial call context 4096
- repair call context 3072
- initial prompt/request/parser
- repair preamble
- original task prompt in repair
- current editable candidate in repair
- permitted editable filenames
- deterministic validator
- exact frozen tests
- maximum one repair
- deterministic candidate selection
- temperature 0
- non-thinking
- max-generation request 2048
- task order T01–T06
- scorer
- call isolation before/after every model call
- initial host gate: 3 consecutive samples >=70% free
- guardrails: free memory <5% OR swap >5600 MB
- no Pi, retrieval, planner, third call, human intervention or external model.

## Required prompt telemetry

For every repair prompt save:
- full prompt file as before;
- total UTF-8 bytes;
- compact-feedback body bytes;
- original unbounded feedback bytes;
- truncation boolean.

## Interpretation boundary

If this profile uses less memory or completes, the result establishes only the system-level effect of bounded deterministic repair feedback. It does not prove that prompt length, KV cache, MLX or Ollama is the sole cause of previous failures.

If quality changes, that is part of this new system profile: less feedback may remove useful information.

## Safety and decision rules

1. `HOST_STATE_NOT_READY`: no model result; naturally free host resources and retry wrapper only.
2. Harness/provenance/isolation/telemetry defect: fix only demonstrated defect.
3. `PARTIAL_RESOURCE_FAIL`: do not reduce context further and do not create another feedback-budget ladder. Stop prompt-level rescue work on this Ollama/MLX profile and reassess the execution profile.
4. `COMPLETE`: freeze quality/resource/efficiency result and apply the existing prospective quality gates.

## Frozen quality gates if COMPLETE

Historical single-shot baseline:
- artifact 40.71/100
- delivery-adjusted 30.00/100
- delivery 3/6.

`QUALITY_IMPROVED`:
- COMPLETE
- delivery-adjusted >30.00.

`STRONG_AMPLIFICATION`:
- QUALITY_IMPROVED
- artifact >40.71
- delivery >3/6.

`PI_REFERENCE_REACHED` descriptive only:
- delivery-adjusted >=77.15.

## Planned execution

Runner:
`scripts/capability_amplifier_004_compact_feedback.py`

No model download is expected.
