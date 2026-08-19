# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM is now optimizing useful capability rather than resident model size on the Apple M1 / 8 GB reference system. Capability Amplifier 001 demonstrated the intended quality mechanism can solve T01 cleanly, but the warm-resident multi-call profile resource-failed during the T02 repair. The diagnostic is closed. A one-factor call-isolated replication is preregistered and ready.
Checkpoint: `CAPABILITY_AMPLIFIER_002_CALL_ISOLATED_READY`

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
- Runtime safety boundary where applicable: free memory <5% OR swap >5600 MB abort.
- Process RSS is diagnostic only; system-wide free memory and swap are decisive.
- Do not relabel harness/parser/capture defects as model failures.
- Do not assign aggregate quality scores to partial resource/runtime runs.
- Change one experimental factor at a time when testing a causal operational hypothesis.

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

This remains a later secondary Amplify control, not the primary subject.

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

Joint frontier metrics:
- quality / delivery
- free memory / swap
- wall time
- model calls
- prompt/generated tokens
- disk footprint where relevant.

# Phase 6 — Capability Amplification — ACTIVE

## Capability Amplifier 001 — frozen result

Plan: `research/amplify/capability-amplifier-001-plan.md`
Runner: `scripts/capability_amplifier_001.py`
Runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`
Partial result: `research/amplify/capability-amplifier-001-partial-20260819-142640.md`
Diagnostic: `research/amplify/capability-amplifier-001-resource-diagnostic.md`

Primary subject:
- `qwen3.5:4b-mlx`
- Ollama
- context 4096
- non-thinking
- temperature 0
- max 2048 tokens/call.

Frozen capability mechanism:
- exact baseline initial call;
- deterministic parser/test validation;
- all tests pass => no repair;
- otherwise maximum one repair with deterministic feedback;
- valid repair selected only if it passes more frozen tests; tie retains initial;
- no Pi, retrieval, planner, third call, human intervention or external model.

Run `20260819-142640`:
- initial host gate PASS: 74%, 74%, 74% free; swap 1206.12 MB
- classification `PARTIAL_RESOURCE_FAIL`
- exact reason: `memory free 4% < 5%`
- whole wall 42.789 s
- overall peak swap 2500.88 MB
- no aggregate quality score.

T01 initial:
- written
- 6/6 tests
- 15/15
- prompt 301
- gen 98
- 15.922 tok/s
- wall 12.391 s
- load duration ~3.668 s
- min free 5% during call.

T02 initial:
- written
- 3/7 tests
- 6.43/15
- prompt 406
- gen 118
- 16.026 tok/s
- wall 10.020 s
- load duration ~0.045 s
- min free 6%.

T02 repair:
- correctly authorized from frozen-test failure
- no completed model response
- telemetry free 7% -> 5% -> 5% -> 4%
- final swap 2500.88 MB
- guardrail abort.

Canonical interpretation:
> Amplifier 001 with continuous warm Ollama residency between sequential calls does not leave enough memory headroom for the validator + one-repair workflow on the M1/8 GB reference system.

This supports testing residency isolation, but does **not** prove a memory leak or any specific Ollama/MLX/KV mechanism.

## Capability Amplifier 002 — Call-Isolated — READY

Plan: `research/amplify/capability-amplifier-002-call-isolated-plan.md`
Runner: `scripts/capability_amplifier_002_call_isolated.py`
Runner blob: `df332568820e28c90baa5247df27e92cba43c0d6`
Frozen base runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`

One changed factor: model residency policy.

Preserved exactly:
- model/runtime/context/sampler/output budget
- benchmark/adaptor/scorer
- initial prompt/request/parser
- deterministic validation
- max one repair and feedback content
- candidate selection
- initial >=70% three-sample host gate
- free<5% / swap>5600 MB runtime guardrails
- quality gates.

Changed:
- before each model call, ensure target model is not resident;
- after every completed call, `ollama stop qwen3.5:4b-mlx`;
- poll `ollama ps` until model is absent (30 s timeout);
- record isolation memory/swap samples;
- no new >=70% threshold between calls.

If unload cannot be confirmed: `ISOLATION_FAIL`, no aggregate quality conclusion.

Frozen quality gates if COMPLETE:
- `QUALITY_IMPROVED`: delivery-adjusted >30.00
- `STRONG_AMPLIFICATION`: above + artifact >40.71 + delivery >3/6
- `PI_REFERENCE_REACHED`: descriptive if delivery-adjusted >=77.15.

Expected trade-off:
- higher cold-load/wall-time cost;
- potentially greater memory headroom.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/capability_amplifier_002_call_isolated.py
python3 scripts/capability_amplifier_002_call_isolated.py
```

No model download is expected.

Preserve output through `Summary:`.

## Decision after Amplifier 002

If `COMPLETE`:
- freeze quality/resource/efficiency result;
- compare directly with single-shot baseline and Amplifier 001 resource trajectory;
- only then select the next one-factor capability amplifier.

If `PARTIAL_RESOURCE_FAIL` despite confirmed isolation:
- call isolation alone is insufficient;
- do not weaken the 5% guardrail or simply rerun unchanged;
- next experiment needs a new architectural rationale.

If `ISOLATION_FAIL`:
- inspect/fix only the demonstrated isolation-harness defect before interpreting model/runtime behavior.

After the mechanism is established, port the same amplification logic to the faster llama.cpp 4B as an efficiency control.

## Continuation rule

After every meaningful result/decision, update this file and `ROADMAP.md` before moving to the next checkpoint.
