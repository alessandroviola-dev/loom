# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM is optimizing useful capability rather than resident model size on the Apple M1 / 8 GB reference system. Capability Amplifier 001 warm-resident resource-failed during T02 repair. Capability Amplifier 002 changed only residency policy by unloading and confirming the model absent between calls; a valid >=70%-free run still resource-failed during the T02 repair path. Exact 002 telemetry is not yet inspected, so no further architectural change is authorized.
Checkpoint: `CAPABILITY_AMPLIFIER_002_RESOURCE_DIAGNOSTIC`

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
- Do not weaken guardrails or add recovery thresholds post-hoc to an already-failed frozen condition.

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

Direct MLX Qwen3-8B 4-bit, 4096, unquantized KV:
- smoke PASS
- standalone T01 PASS narrowly
- original full benchmark resource-failed
- >=70%-free controlled replication completed T01–T03, entered T04, then hit 4% free
- exact continuous profile closed as RESOURCE FAIL.

KV8 Rescue 001 was operator-reported as failed but detailed output was not ingested before the project pivot; do not assign a canonical failure type.

# Research pivot — ADOPTED

Record: `research/notes/capability-amplification-pivot-2026-08-19.md`

Primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Long-term tracks:
1. **Amplify — small model, big capability**: validation/repair, planner/verifier/tool loops, retrieval, later specialization/distillation.
2. **Stretch — big model, small machine**: SSD/layer/expert streaming, MoE offload, hierarchical caching, small resident controller + selectively invoked larger component.

Joint frontier metrics: quality/delivery, free memory/swap, wall time, model calls, prompt/generated tokens, disk footprint where relevant.

# Phase 6 — Capability Amplification — ACTIVE

## Capability Amplifier 001 — warm-resident frozen result

Plan: `research/amplify/capability-amplifier-001-plan.md`
Runner: `scripts/capability_amplifier_001.py`
Runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`
Partial result: `research/amplify/capability-amplifier-001-partial-20260819-142640.md`
Diagnostic: `research/amplify/capability-amplifier-001-resource-diagnostic.md`

Frozen capability mechanism:
- exact baseline initial call;
- deterministic parser/test validation;
- all tests pass => no repair;
- otherwise maximum one repair with deterministic feedback;
- valid repair selected only if it passes more frozen tests; tie retains initial;
- no Pi, retrieval, planner, third call, human intervention or external model.

Run `20260819-142640`:
- host gate PASS: 74%, 74%, 74% free; swap 1206.12 MB
- `PARTIAL_RESOURCE_FAIL`: memory free 4% <5%
- peak swap 2500.88 MB
- no aggregate quality score.

T01 initial:
- written, 6/6, 15/15
- prompt 301, gen 98
- 15.922 tok/s, wall 12.391 s
- load ~3.668 s
- min free 5%.

T02 initial:
- written, 3/7, 6.43/15
- prompt 406, gen 118
- 16.026 tok/s, wall 10.020 s
- load ~0.045 s
- min free 6%.

T02 repair:
- correctly authorized
- no completed response
- free 7% -> 5% -> 5% -> 4%
- guardrail abort.

Canonical interpretation:
> Warm continuous Ollama residency does not leave enough headroom for this validator + one-repair workflow on the M1/8 GB reference system. This does not prove a memory leak or specific Ollama/MLX/KV mechanism.

## Capability Amplifier 002 — Call-Isolated

Plan: `research/amplify/capability-amplifier-002-call-isolated-plan.md`
Runner: `scripts/capability_amplifier_002_call_isolated.py`
Runner blob: `df332568820e28c90baa5247df27e92cba43c0d6`
Frozen base runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`
Partial result: `research/amplify/capability-amplifier-002-partial-20260819-144256.md`

One changed factor vs Amplifier 001: model residency policy.

Preserved:
- model/runtime/context/sampler/output budget
- benchmark/adapter/scorer
- initial prompt/request/parser
- deterministic validation
- max one repair and feedback
- candidate selection
- initial >=70% three-sample host gate
- free<5% / swap>5600 MB runtime guardrails
- quality gates.

Changed:
- ensure target model absent before each model call;
- after every completed call, `ollama stop qwen3.5:4b-mlx`;
- poll `ollama ps` until target absent (30 s timeout);
- record isolation memory/swap samples;
- intentionally no inter-call >=70% recovery threshold, to keep a one-factor design.

First launch `20260819-143838`:
- host free 67% <70%
- `HOST_STATE_NOT_READY`
- model calls 0
- not a scientific model run.

Valid launch `20260819-144256`:
- source blob PASS
- call-isolation transform PASS
- disk before 35.346 GiB
- host gate PASS: 71%, 72%, 72% free; swap 1699.0 MB
- T01 initial completed and solved without repair
- T02 initial completed
- T02 repair authorized from `frozen_test_failure`
- terminal classification `PARTIAL_RESOURCE_FAIL`
- completed model-call records printed: 2
- disk after 35.345 GiB
- no aggregate quality score.

Current interpretation boundary:
> Call isolation alone did not allow the full benchmark to complete, but the terminal output does not establish whether the model was successfully unloaded around each call, what free/swap level existed after isolation, or whether the T02 repair itself independently drove the breach. Do not yet add an inter-call recovery gate or change prompt/context/model.

# Current checkpoint — Amplifier 002 resource diagnostic

Checkpoint: `CAPABILITY_AMPLIFIER_002_RESOURCE_DIAGNOSTIC`

Use the existing read-only inspector:
`scripts/inspect_capability_amplifier_001.py`

Target:
`results-local/amplify/capability-amplifier-002-call-isolated/20260819-144256`

Required recovery:
- exact `failure_reason`
- min free and peak swap
- T01/T02 initial test results
- all `*_isolation` telemetry samples
- free/swap immediately after confirmed unloads
- free/swap immediately before T02 repair generation
- whether model absence was actually confirmed around each call
- final samples leading into abort.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_capability_amplifier_001.py
python3 scripts/inspect_capability_amplifier_001.py \
  results-local/amplify/capability-amplifier-002-call-isolated/20260819-144256
```

This is read-only and does not launch the model.

## Decision after diagnostic

If unload is confirmed but free memory remains low before the next call, a separately preregistered **unload + recovery-gated** profile may be justified. That would be a new factor and must not be retrofitted into Amplifier 002.

If free memory recovers materially after unload and the cold T02 repair alone drives the 4% breach, the next architecture must address repair-call footprint rather than residency timing.

If isolation was not actually completed, classify/fix the isolation harness before drawing runtime conclusions.

After a complete amplification mechanism is established, port the same logic to the faster llama.cpp 4B as an efficiency control.

## Continuation rule

After every meaningful result/decision, update this file and `ROADMAP.md` before moving to the next checkpoint.
