# Capability Amplifier 002 — Call-Isolated — Partial Run

Date: 2026-08-19
Run id: `20260819-144256`
Status: **PARTIAL_RESOURCE_FAIL — diagnostic pending**

## Frozen condition

- Primary model: `qwen3.5:4b-mlx`
- Runtime: Ollama / MLX
- Context: 4096
- Capability mechanism inherited from Amplifier 001
- Exact baseline initial call
- Deterministic parser/test validation
- Maximum one repair
- Deterministic candidate selection
- Same Coding Benchmark 01 v1.0.1 / adapter / scorer / quality gates
- Runtime guardrails unchanged: free memory <5% OR swap >5600 MB
- Initial host-state gate unchanged: three consecutive samples >=70% free
- One changed factor: unload target model and confirm absent from `ollama ps` between every model call
- No inter-call >=70% recovery threshold

Runner:
`scripts/capability_amplifier_002_call_isolated.py`

Wrapper blob:
`df332568820e28c90baa5247df27e92cba43c0d6`

Frozen Amplifier 001 source blob:
`9f472c60b523762276291232f6e8c6ffc1c5fcae`

## Operator terminal evidence

Run directory:
`results-local/amplify/capability-amplifier-002-call-isolated/20260819-144256`

Summary:
`results-local/amplify/capability-amplifier-002-call-isolated/20260819-144256/run-summary.json`

Observed:
- source blob preflight PASS
- call-isolation transform PASS
- residency policy reported as unload + confirm absent from `ollama ps` between every model call
- disk before 35.346 GiB
- frozen adapter/scorer/manifest PASS
- model presence PASS
- host samples: 71%, 72%, 72% free
- initial swap: 1699.0 MB
- host-state gate PASS
- T01 initial call completed and solved without repair
- T02 initial call completed
- T02 repair authorized from `frozen_test_failure`
- terminal classification: `PARTIAL_RESOURCE_FAIL`
- completed model-call records printed: 2
- disk after 35.345 GiB

## Current interpretation boundary

The terminal excerpt proves that call isolation did not by itself allow the full benchmark to complete. It does **not** yet establish the exact guardrail reason, inter-call recovery levels, or whether the model was successfully unloaded/reloaded before each call in the persisted telemetry.

Do not yet conclude that unload is ineffective, that a recovery gate would solve the issue, or that the T02 repair prompt is independently too large.

No aggregate quality score is valid from this partial run.

## Required next diagnostic

Use the existing read-only inspector against this run to recover:
- exact `failure_reason`
- min free memory / peak swap
- T01/T02 initial test results
- isolation samples before/after calls
- whether `ollama ps` absence was confirmed around each call
- free/swap state immediately before the T02 repair
- final samples leading into the abort.
