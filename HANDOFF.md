# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — LOOM has pivoted from maximizing resident model size to maximizing useful capability on an Apple M1 / 8 GB system. Capability Amplifier 001 was launched on the canonical `qwen3.5:4b-mlx`; T01 solved on the initial call, T02 required a repair, and the frozen run hit the runtime safety boundary during the T02 repair path. No aggregate quality result exists yet.
Checkpoint: `CAPABILITY_AMPLIFIER_001_RESOURCE_DIAGNOSTIC`

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
- Do not assign a quality score to a partial resource/runtime run.
- Do not change an amplifier design before diagnosing a frozen failure.

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

Canonical finding: the same local 4B became materially more useful when fragile full-file JSON transport was replaced by direct filesystem tools. This is the main motivation for Capability Amplification.

## llama.cpp 4B efficiency reference

Qwen3-4B Q4 control:
- pp512 230.85 tok/s
- tg128 22.33 tok/s
- minimum free memory 22%.

This remains a later secondary Amplify control; it is not treated as the same model/runtime condition as `qwen3.5:4b-mlx`.

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

Two long-term tracks:

1. **Amplify — small model, big capability**
   - validation / repair
   - planner / verifier / tool loops
   - retrieval
   - later specialization / LoRA / SFT / distillation when justified.

2. **Stretch — big model, small machine**
   - SSD/layer/expert streaming
   - MoE offload
   - hierarchical caching
   - small resident controller + selectively invoked larger component.

Joint frontier metrics:
- quality / delivery
- free memory / swap
- wall time
- model calls
- prompt/generated tokens
- disk footprint where relevant.

# Phase 6 — Capability Amplification — ACTIVE

## Capability Amplifier 001 — frozen design

Plan: `research/amplify/capability-amplifier-001-plan.md`
Runner: `scripts/capability_amplifier_001.py`
Runner blob: `9f472c60b523762276291232f6e8c6ffc1c5fcae`

Primary subject:
- `qwen3.5:4b-mlx`
- Ollama
- context 4096
- non-thinking
- temperature 0
- max 2048 tokens/call.

Frozen provenance:
- Coding Benchmark 01 v1.0.1
- manifest blob `547050ecd0183b8d447dc3e21e724a8232f10297`
- single-shot adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`.

Mechanism:
- exact baseline initial call;
- deterministic parser/test validation;
- all tests pass => no repair;
- otherwise maximum one repair with deterministic feedback;
- valid repair selected only if it passes more frozen tests; tie retains initial;
- no Pi, retrieval, third call, human intervention or external model.

Host/safety:
- stop model before launch;
- 3 consecutive host samples >=70% free;
- during model calls free<5% or swap>5600 MB => `PARTIAL_RESOURCE_FAIL`.

Frozen success gates if COMPLETE:
- `QUALITY_IMPROVED`: delivery-adjusted >30.00
- `STRONG_AMPLIFICATION`: above + artifact >40.71 + delivery >3/6
- `PI_REFERENCE_REACHED`: descriptive flag if delivery-adjusted >=77.15.

## Capability Amplifier 001 — partial run `20260819-142640`

Record: `research/amplify/capability-amplifier-001-partial-20260819-142640.md`

Observed terminal evidence:
- disk before 36.360 GiB
- frozen adapter/scorer/manifest PASS
- model presence PASS
- host samples 74%, 74%, 74% free
- host swap 1206.12 MB
- T01 initial call completed and solved without repair
- T02 initial call completed
- T02 repair authorized from `frozen_test_failure`
- run aborted during T02 repair path
- terminal classification `PARTIAL_RESOURCE_FAIL`
- completed model-call records printed: 2
- disk after 35.352 GiB
- no final scorer result / no valid aggregate quality score.

Important boundary:
The terminal excerpt does not reveal the exact guardrail reason or telemetry trajectory. Do not yet claim free-memory failure, swap failure, warm-retention causality, or repair-specific causality.

Run directory:
`results-local/amplify/capability-amplifier-001/20260819-142640`

Summary:
`results-local/amplify/capability-amplifier-001/20260819-142640/run-summary.json`

# Current checkpoint — read-only resource diagnostic

Checkpoint: `CAPABILITY_AMPLIFIER_001_RESOURCE_DIAGNOSTIC`

Inspector:
`scripts/inspect_capability_amplifier_001.py`

Target run:
`results-local/amplify/capability-amplifier-001/20260819-142640`

Required recovery:
- exact `failure_reason`
- min free memory and peak swap
- T01/T02 initial test results
- whether T02 repair produced a completed API response
- telemetry grouped by task/phase
- last samples leading into the guardrail
- completed model-call records.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/inspect_capability_amplifier_001.py
python3 scripts/inspect_capability_amplifier_001.py \
  results-local/amplify/capability-amplifier-001/20260819-142640
```

This inspector is read-only and does not launch Ollama/MLX.

## Decision after diagnostic

Do not rerun frozen Amplify 001 yet.

If telemetry supports retained warm-state accumulation across completed calls, the leading next design is a separately preregistered **call-isolated amplifier** that preserves model/prompts/feedback/scoring but unloads/re-establishes the model between amplification units. That would be a new operational profile, not a rescue rewrite.

If the resource breach instead appears specific to one unusually large repair prompt or another localized factor, design the next experiment around that demonstrated cause.

The broader Amplify research question remains active regardless of this resource interruption: the system around a small model must itself be memory-aware on an 8 GB machine.

## Continuation rule

After every meaningful result/decision, update this file and `ROADMAP.md` before moving to the next checkpoint.
