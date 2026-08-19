# LOOM — Capability Amplifier 001 Partial Run

Date: 2026-08-19
Run: `20260819-142640`
Status: **PARTIAL_RESOURCE_FAIL — DIAGNOSTIC PENDING**

## Frozen condition

- model `qwen3.5:4b-mlx`
- Ollama
- context 4096
- Coding Benchmark 01 v1.0.1
- exact frozen initial single-shot adapter
- deterministic validation
- maximum one repair per task
- frozen test-based candidate selection
- host launch gate: 3 consecutive samples >=70% free
- runtime abort: free memory <5% OR swap >5600 MB

## Operator-reported execution

Preflight:
- disk free before: 36.360 GiB
- frozen adapter/scorer/manifest blobs: PASS
- model presence: PASS
- host samples: 74%, 74%, 74% free
- swap at host samples: 1206.12 MB
- host-state gate: PASS

Progress:
- T01 initial call completed
- T01 solved without repair
- T02 initial call completed
- T02 required a repair from `frozen_test_failure`
- run aborted during the T02 repair path

Terminal classification:
- `PARTIAL_RESOURCE_FAIL`
- completed model-call records printed: 2
- disk free after: 35.352 GiB

Run directory:
`results-local/amplify/capability-amplifier-001/20260819-142640`

Summary:
`results-local/amplify/capability-amplifier-001/20260819-142640/run-summary.json`

## Interpretation boundary

This is a valid safety/resource interruption of the frozen Amplify 001 run. It is **not** a coding-quality failure classification and no aggregate Amplify score exists.

The terminal excerpt does not expose the exact guardrail reason or resource timeline. Do not infer free-memory vs swap, retained warm state, or repair-specific memory growth until the saved summary/telemetry are inspected.

T01 solving without repair is positive task-level evidence only; it must not be used as an aggregate Amplify score.

## Required next step

Run the read-only inspector against the saved run directory. Recover:
- exact `failure_reason`;
- min free memory / max swap;
- task records and test counts for completed candidates;
- completed model-call records;
- telemetry evolution from T01 initial through T02 initial and repair;
- whether the T02 repair call produced a completed API response before the abort.

No new model run is authorized before this diagnostic is closed.
