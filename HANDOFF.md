# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM is optimizing useful capability rather than resident model size on the Apple M1 / 8 GB reference system. Amplifier 001 showed warm-resident multi-call memory pressure. Amplifier 002 proved call isolation works, but a cold T02 repair at context 4096 still crossed the 5% free-memory guardrail from 68% free. Amplifier 003 reduced only repair context to 3072; a valid launch again reached the T02 repair path and terminated `PARTIAL_RESOURCE_FAIL`. Exact 003 telemetry is not yet inspected.
Checkpoint: `CAPABILITY_AMPLIFIER_003_RESOURCE_DIAGNOSTIC`

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.

Tagline: **Big models. Small machines.**
Repository: `Ilcoach/loom`
Local path: `<repository-root>`

## Safety / production constraints

- Never reset, replace or destroy production Pi configuration.
- Controlled Pi experiments use run-local `PI_CODING_AGENT_DIR`.
- Never silently delete verified models or canonical results.
- Record disk around model acquisitions / large runtime work.
- Runtime safety boundary: free memory <5% OR swap >5600 MB abort.
- Process RSS is diagnostic only; system-wide free memory and swap are decisive.
- Do not relabel harness/parser/capture defects as model failures.
- Do not assign aggregate quality scores to partial resource/runtime runs.
- Change one experimental factor at a time when testing a causal operational hypothesis.
- Do not weaken guardrails post-hoc.
- Do not turn a single context rescue into an automatic reduction ladder.

Verified 3-bit, 4-bit and GGUF artifacts remain retained.

# Frozen reference results

## Canonical Ollama/MLX 4B

Model: `qwen3.5:4b-mlx`, context 4096.

Coding Baseline 001 (`20260818-203156`):
- artifact 40.71/100
- strict/delivery-adjusted 30.00/100
- delivery 3/6
- recovered semantic diagnostic 82.86/100
- weighted prompt throughput 186.46 tok/s
- generation 16.01 tok/s.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- artifact/delivery-adjusted 77.15/100
- strict protocol-adjusted 60.00/100
- delivery 6/6
- protocol 4/6
- no hidden-test feedback
- whole run ~612 s.

Canonical finding: the same local 4B became materially more useful when direct filesystem tools replaced fragile full-file JSON transport. This motivates Capability Amplification.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4 control:
- pp512 230.85 tok/s
- tg128 22.33 tok/s
- minimum free memory 22%.

This remains a later secondary Amplify control, not the same model/runtime condition as the canonical Ollama/MLX 4B.

## 8B runtime frontier — characterized / main branch closed

Direct MLX Qwen3-8B 3-bit:
- full six-task session COMPLETE
- min free 14%
- peak swap 1683.38 MB
- artifact 38.57
- delivery-adjusted 27.86
- delivery 2/6
- stable but not promoted on quality.

Direct MLX Qwen3-8B 4-bit, context 4096:
- smoke PASS
- standalone T01 PASS narrowly
- original full benchmark resource-failed
- >=70%-free controlled replication reached T04 then hit 4% free
- exact continuous unquantized-KV profile closed as RESOURCE FAIL.

KV8 Rescue 001 was operator-reported as failed but detailed output was not ingested before the project pivot; do not assign a canonical failure type.

# Research pivot — ADOPTED

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Long-term tracks:
1. **Amplify — small model, big capability**: validation/repair, planner/verifier/tool loops, retrieval, later specialization/distillation.
2. **Stretch — big model, small machine**: SSD/layer/expert streaming, MoE offload, hierarchical caching, small resident controller + selectively invoked larger component.

Joint frontier metrics: quality/delivery, free memory/swap, wall time, model calls, prompt/generated tokens, disk footprint where relevant.

# Phase 6 — Capability Amplification — ACTIVE

## Amplifier 001 — warm-resident frozen result

Plan: `research/amplify/capability-amplifier-001-plan.md`
Runner: `scripts/capability_amplifier_001.py`
Runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`
Diagnostic: `research/amplify/capability-amplifier-001-resource-diagnostic.md`

Run `20260819-142640`:
- host gate 74%, 74%, 74% free; swap 1206.12 MB
- `PARTIAL_RESOURCE_FAIL`: memory free 4% <5%
- peak swap 2500.88 MB
- no aggregate quality score
- T01 initial: 6/6, 15/15, prompt 301, gen 98, 15.922 tok/s, wall 12.391 s, min free 5%
- T02 initial: 3/7, 6.43/15, prompt 406, gen 118, 16.026 tok/s, wall 10.020 s, min free 6%
- T02 repair: free 7% -> 5% -> 5% -> 4%, no completed response.

Interpretation: warm continuous Ollama residency lacks sufficient headroom. Do not call this a leak.

## Amplifier 002 — call-isolated frozen result

Plan: `research/amplify/capability-amplifier-002-call-isolated-plan.md`
Runner: `scripts/capability_amplifier_002_call_isolated.py`
Runner blob: `df332568820e28c90baa5247df27e92cba43c0d6`
Diagnostic: `research/amplify/capability-amplifier-002-resource-diagnostic.md`

One changed factor vs 001: unload and confirm target absent from `ollama ps` before/after every model call.

Valid run `20260819-144256`:
- host gate 71%, 72%, 72% free; swap 1699.0 MB
- `PARTIAL_RESOURCE_FAIL`: memory free 4% <5%
- peak swap 2611.50 MB
- T01 initial: 6/6, cold load ~4.153 s
- T02 initial: 3/7, cold load ~3.153 s
- model unload confirmed
- T02 repair starts from 68% free / 2346.94 MB swap
- repair trajectory 68% -> 63% -> 23% -> 16% -> 4%
- post-abort unload returns 66% free / 1776.06 MB swap.

Interpretation: call isolation works operationally but is insufficient. Recovery gating alone is not the leading fix because the failing repair starts at 68% free while successful T02 initial starts at 67% free.

## Amplifier 003 — repair context 3072 — PARTIAL / DIAGNOSTIC PENDING

Plan: `research/amplify/capability-amplifier-003-repair-context-3072-plan.md`
Runner: `scripts/capability_amplifier_003_repair_context_3072.py`
Runner blob: `c2bcc8f126eb5b599645ba12d1fd08a348e2b443`
Partial record: `research/amplify/capability-amplifier-003-partial-20260819-150342.md`

Single changed factor vs 002:
- initial calls remain `num_ctx=4096`
- repair calls use `num_ctx=3072`.

Preserved:
- same model/runtime
- same initial and repair prompt content
- deterministic validation and frozen-test feedback
- max one repair
- candidate selection
- temperature 0 / non-thinking
- max-generation request 2048
- call isolation
- initial >=70% three-sample host gate
- free<5% / swap>5600 MB guardrails
- no Pi/retrieval/planner/third call/human intervention.

Attempt `20260819-150107`:
- host free 69%
- `HOST_STATE_NOT_READY`
- 0 model calls
- not a scientific model result.

Valid run `20260819-150342`:
- disk before 36.344 GiB
- frozen provenance checks PASS
- host gate PASS: 71%, 74%, 74% free
- swap 1247.88 MB
- T01 initial completes and solves without repair
- T02 initial completes
- T02 repair authorized from `frozen_test_failure`
- terminal classification `PARTIAL_RESOURCE_FAIL`
- completed model-call records: 2
- disk after 35.342 GiB
- no aggregate quality score.

Important boundary: terminal output alone does not expose exact 003 failure reason, repair context record, pre-repair free/swap, or telemetry trajectory. Do not yet claim that 3072 had no resource effect.

# Current checkpoint — Amplifier 003 read-only diagnostic

Checkpoint: `CAPABILITY_AMPLIFIER_003_RESOURCE_DIAGNOSTIC`

Use existing inspector:
`scripts/inspect_capability_amplifier_001.py`

Target:
`results-local/amplify/capability-amplifier-003-repair-context-3072/20260819-150342`

Required recovery:
- exact failure reason
- min free / peak swap
- T01/T02 task results
- model-call context records
- isolation samples
- T02 repair pre-state and telemetry trajectory
- whether a repair API response completed.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 scripts/inspect_capability_amplifier_001.py \
  results-local/amplify/capability-amplifier-003-repair-context-3072/20260819-150342
```

This inspector is read-only and does not launch the model.

## Decision after diagnostic

- If the 3072 repair still crosses the same guardrail from a recovered pre-state, do not automatically try 2048. Redesign repair architecture/prompt budget.
- If telemetry shows a materially different failure mechanism, design the next one-factor experiment around that demonstrated mechanism.
- If a harness/isolation/telemetry defect is found, fix only that defect before interpretation.

## Continuation rule

After every meaningful result/decision, update this file and `ROADMAP.md` before moving to the next checkpoint.
