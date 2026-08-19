# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM is optimizing useful capability rather than resident model size on the Apple M1 / 8 GB reference system. Capability Amplifier 001 showed that a warm-resident validator + one-repair workflow lacks memory headroom. Amplifier 002 successfully isolated model residency between calls, but a cold T02 repair at context 4096 still crossed the 5% free-memory guardrail from a recovered 68%-free state. The next one-factor experiment reduces only repair-call context to 3072 while preserving initial calls at 4096.
Checkpoint: `CAPABILITY_AMPLIFIER_003_REPAIR_CONTEXT_3072_READY`

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
Latest observed free disk before Amplifier 002: ~35.346 GiB.

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
- valid repair selected only if it passes more frozen tests; ties retain initial;
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
> Warm continuous Ollama residency does not leave enough headroom for this validator + one-repair workflow. This does not prove a memory leak or specific low-level mechanism.

## Capability Amplifier 002 — call-isolated frozen result

Plan: `research/amplify/capability-amplifier-002-call-isolated-plan.md`
Runner: `scripts/capability_amplifier_002_call_isolated.py`
Runner blob: `df332568820e28c90baa5247df27e92cba43c0d6`
Partial result: `research/amplify/capability-amplifier-002-partial-20260819-144256.md`
Diagnostic: `research/amplify/capability-amplifier-002-resource-diagnostic.md`

One changed factor vs 001: unload and confirm the target absent from `ollama ps` before/after every model call. No inter-call >=70% recovery threshold.

Valid run `20260819-144256`:
- host gate PASS: 71%, 72%, 72% free; swap 1699.0 MB
- classification `PARTIAL_RESOURCE_FAIL`
- exact failure: memory free 4% <5%
- peak swap 2611.50 MB
- whole wall 55.4 s
- no aggregate quality score.

T01 initial:
- 6/6, 15/15
- prompt 301, gen 98
- 13.933 tok/s
- wall 14.256 s
- load ~4.153 s
- pre-isolation 71% free
- min during call 5%
- post-isolation 38% free.

T02 initial:
- 3/7, 6.43/15
- prompt 406, gen 118
- 14.395 tok/s
- wall 14.106 s
- load ~3.153 s
- pre-isolation 67% free
- min during call 5%
- post-isolation 39% free.

Isolation evidence before T02 repair:
- target model confirmed unloaded
- `ollama_stop_exit_code=0`
- repair pre-isolation sample **68% free / 2346.94 MB swap**.

T02 repair at context 4096:
- starts 68% free
- trajectory 68% -> 63% -> 23% -> 16% -> 4%
- peak/final swap 2611.50 MB
- no completed repair response
- post-abort unload returns 66% free / 1776.06 MB swap.

Canonical interpretation:
> Call isolation works operationally, but isolation alone is insufficient. A cold T02 repair at context 4096 independently crosses the free-memory guardrail from a materially recovered host state. This does not identify a specific allocator/KV/prompt-only cause.

A recovery gate alone is not the leading intervention because the failing repair started at 68% free while the successful T02 initial started at 67% free.

## Capability Amplifier 003 — Repair Context 3072 — READY

Plan: `research/amplify/capability-amplifier-003-repair-context-3072-plan.md`
Runner: `scripts/capability_amplifier_003_repair_context_3072.py`
Runner blob: `c2bcc8f126eb5b599645ba12d1fd08a348e2b443`

Provenance locks:
- Amplifier 001 base blob `9f472c60b523762276291232f6e8c6ffc1c5fcae`
- Amplifier 002 wrapper blob `df332568820e28c90baa5247df27e92cba43c0d6`.

Single changed factor vs 002:
- initial calls remain `num_ctx=4096`;
- repair calls use **`num_ctx=3072`**.

Preserved:
- same model/runtime
- initial prompt/request/parser
- repair prompt content and failure feedback
- deterministic validation
- max one repair
- candidate selection
- temperature 0 / non-thinking
- max-generation request 2048
- benchmark/scorer/task order
- call isolation before/after every model call
- initial >=70% three-sample host gate
- runtime free<5% / swap>5600 MB guardrails
- no Pi/retrieval/planner/third call/human intervention.

3072 is frozen as a single 25% repair-context reduction, not an automatic ladder. Changing repair context can affect both resource use and effective token budget; that is part of the tested profile.

Frozen quality gates if COMPLETE:
- `QUALITY_IMPROVED`: delivery-adjusted >30.00
- `STRONG_AMPLIFICATION`: above + artifact >40.71 + delivery >3/6
- `PI_REFERENCE_REACHED`: descriptive if delivery-adjusted >=77.15.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/capability_amplifier_003_repair_context_3072.py
python3 scripts/capability_amplifier_003_repair_context_3072.py
```

No model download is expected.

Expected preflight lines include:
- Amplifier 001 source blob PASS
- Amplifier 002 provenance blob PASS
- call-isolation transform PASS
- context policy initial=4096, repair=3072
- unchanged guardrails.

Decision rules:
- `HOST_STATE_NOT_READY`: no model result; naturally free host resources and retry launch wrapper only.
- harness/isolation/telemetry defect: fix only demonstrated defect.
- `PARTIAL_RESOURCE_FAIL` at repair context 3072: do not automatically descend to 2048; reassess repair architecture.
- `COMPLETE`: freeze full resource/quality result and apply prospective quality gates before adding another amplifier factor.

## Continuation rule

After every meaningful result/decision, update this file and `ROADMAP.md` before moving to the next checkpoint.
