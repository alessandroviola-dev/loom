# Capability Amplifier 003 — Repair Context 3072 — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can the frozen validator + maximum-one-repair capability amplifier complete safely on the Apple M1 / 8 GB reference machine if only the **repair-call context allocation** is reduced, while initial calls remain identical to the canonical 4096-context baseline?

## Motivation

Amplifier 002 established:
- call isolation is operationally working;
- T02 initial starts at 67% free, context 4096, reaches minimum 5% and completes;
- T02 repair starts after confirmed unload at 68% free, context 4096, then reaches 4% and aborts;
- peak swap remains far below the 5600 MB swap guardrail.

Diagnostic:
`research/amplify/capability-amplifier-002-resource-diagnostic.md`

The next narrow factor is therefore repair-call context allocation, not residency timing.

## Frozen provenance

Primary model:
`qwen3.5:4b-mlx`

Runtime:
Ollama

Frozen base Amplifier 001 runner blob:
`9f472c60b523762276291232f6e8c6ffc1c5fcae`

Amplifier 002 call-isolation wrapper blob:
`df332568820e28c90baa5247df27e92cba43c0d6`

Benchmark:
LOOM Coding Benchmark 01 v1.0.1

Frozen benchmark artifacts:
- manifest blob `547050ecd0183b8d447dc3e21e724a8232f10297`
- single-shot adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`

## Single changed factor vs Amplifier 002

Initial calls:
- `num_ctx = 4096` unchanged.

Repair calls:
- **`num_ctx = 3072`** instead of 4096.

No other capability or safety factor changes.

3072 is frozen prospectively as a 25% reduction from 4096. This is a single planned test, not the first rung of an automatic context-reduction ladder.

## Preserved exactly

- model weights / model id
- Ollama runtime
- initial prompt/request/parser
- repair prompt content
- deterministic parser/test validation
- exact frozen-test feedback
- maximum one repair per task
- candidate selection: repair replaces initial only if more frozen tests pass; ties keep initial
- temperature 0
- non-thinking
- maximum generated-token request 2048
- benchmark task order T01-T06
- scorer
- initial three-sample host gate >=70% free
- free-memory guardrail <5%
- swap guardrail >5600 MB
- model unload + `ollama ps` absence confirmation before/after every model call
- no Pi
- no retrieval
- no planner
- no third call
- no human intervention
- no web/network model assistance.

## Important interpretation boundary

Changing repair `num_ctx` can affect both resource use and the effective token budget available within that repair request. That is part of the tested profile, not a harness defect.

The initial baseline call remains at 4096 so baseline comparability is preserved for Call 1.

Do not claim that a resource improvement proves KV cache is the sole cause. The test establishes only the effect of the repair context setting on this frozen profile.

## Host / residency policy

Before benchmark:
- stop target model;
- require 3 consecutive samples >=70% free memory;
- if not met: `HOST_STATE_NOT_READY`, no scientific model run.

Before and after every model call:
- `ollama stop qwen3.5:4b-mlx`;
- poll `ollama ps` until target model absent, timeout 30 s;
- record free-memory / swap sample.

No new inter-call recovery threshold is added.

## Runtime safety

During every model call:
- free memory <5% => stop model and `PARTIAL_RESOURCE_FAIL`;
- swap >5600 MB => stop model and `PARTIAL_RESOURCE_FAIL`;
- unavailable required telemetry => `TELEMETRY_FAIL`;
- unload confirmation failure => `ISOLATION_FAIL`.

Guardrails must not be weakened.

## Quality gates if and only if COMPLETE

Historical frozen baseline:
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

`PI_REFERENCE_REACHED` descriptive flag:
- delivery-adjusted >=77.15.

The Pi reference had no hidden-test repair feedback, so reaching this number is not an intrinsic model-superiority claim.

## Required result telemetry

Record:
- classification
- per-call context value
- per-task initial/repair status
- frozen-test results
- repair selections
- model calls
- prompt/generated tokens where returned
- model-call wall times
- load durations
- min free memory
- peak swap
- isolation samples
- disk before/after
- final artifact/delivery scores only if COMPLETE.

## Frozen decision rules

1. `HOST_STATE_NOT_READY`: no model result; naturally free host resources and retry launch wrapper only.
2. `ISOLATION_FAIL` / `TELEMETRY_FAIL` / harness defect: fix only demonstrated harness issue; do not score model.
3. `PARTIAL_RESOURCE_FAIL` at repair context 3072: do **not** automatically try 2048 or weaken guardrails. Reassess repair architecture.
4. `COMPLETE`: freeze result and apply quality gates before adding any new amplifier factor.
5. If COMPLETE and amplification is established, only then consider planner/verifier/tool/retrieval factors or the llama.cpp 4B efficiency control.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/capability_amplifier_003_repair_context_3072.py
python3 scripts/capability_amplifier_003_repair_context_3072.py
```

No model download is expected.
