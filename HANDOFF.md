# LOOM — Project Handoff

Last updated: 2026-08-19
Status: ACTIVE — Runtime-frontier work has established useful 8B boundaries on the Apple M1 / 8 GB reference machine. The project has now pivoted from primarily asking “what is the largest model that fits?” to asking **“what is the greatest useful capability an 8 GB local system can produce?”**. The active main branch is Capability Amplification on the canonical `qwen3.5:4b-mlx` model.
Checkpoint: `CAPABILITY_AMPLIFIER_001_READY`

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
- Do not reopen a rescue ladder without a new prospective scientific rationale.

Verified 3-bit, 4-bit and GGUF artifacts are retained. Latest known disk in the 4-bit branch was roughly 35 GiB free; re-measure before any future multi-GB acquisition.

# Frozen reference results

## Canonical Ollama/MLX 4B

Model: `qwen3.5:4b-mlx`
Context: 4096

Coding Baseline 001 (`20260818-203156`):
- artifact **40.71/100**
- strict/delivery-adjusted **30.00/100**
- delivery **3/6**
- recovered semantic-content diagnostic **82.86/100**
- weighted prompt throughput **186.46 tok/s**
- generation **16.01 tok/s**.

Pi Agentic Coding Benchmark 001 (`20260818-214848`):
- same `qwen3.5:4b-mlx` family through Pi file tools
- artifact/delivery-adjusted **77.15/100**
- strict protocol-adjusted **60.00/100**
- delivery **6/6**
- protocol **4/6**
- no hidden-test feedback
- whole run ~612 s
- severe but non-aborting warm memory/swap pressure.

Canonical agentic finding:
> Replacing fragile full-file JSON transport with direct filesystem tools materially improved end-to-end coding performance for the same local 4B model. This is key evidence motivating Capability Amplification.

Record: `research/agents/pi-agentic-benchmark-001.md`.

## llama.cpp reference

Pinned source commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`.

Qwen3-4B Q4 control:
- pp512 **230.85 tok/s**
- tg128 **22.33 tok/s**
- minimum free memory **22%**.

This faster 4B path remains a later **secondary Amplify control**, not the primary subject, because it is not the same model/runtime condition as `qwen3.5:4b-mlx`.

Qwen3-8B llama.cpp frontier:
- Q2 technically runnable/API-servable but frozen coding delivery poor;
- Q3 NP1 + Q8_0 KV API-smoke PASS at 6% free;
- exact Coding T01 reached 4% free and guardrail abort.

## Direct MLX 8B frontier — characterized / main branch closed

Environment:
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`.

Qwen3-8B 3-bit:
- smoke FULL_PASS
- exact T01 FULL_PASS
- full Coding Benchmark COMPLETE
- full-session min free **14%**, peak swap **1683.38 MB**
- artifact **38.57/100**
- delivery-adjusted **27.86/100**
- delivery **2/6**
- not promoted on quality.

Qwen3-8B 4-bit, `max_kv_size=4096`, unquantized KV:
- smoke PASS at 10% min free
- standalone T01 PASS at 6% min free
- original full benchmark resource-failed during T01
- >=70%-free controlled replication completed T01–T03, entered T04, then hit **4% free**
- exact continuous unquantized-KV profile closed as workload RESOURCE FAIL.

KV8 Rescue 001 was attempted and operator-reported as failed, but its detailed terminal output was not ingested before the research pivot. Do **not** assign a canonical KV8 failure type without the missing evidence.

Closure record:
`research/runtime/direct-mlx-8b-4bit-kv8-rescue-001-closure.md`

No further KV6/KV4/context rescue ladder is authorized in the old branch.

# Research pivot — ADOPTED

Record:
`research/notes/capability-amplification-pivot-2026-08-19.md`

New primary question:
> **What is the greatest useful capability that can be produced by an 8 GB local system?**

Two parallel long-term tracks:

1. **Amplify — small model, big capability**
   - deterministic validation / repair
   - planner / verifier / tool loops
   - retrieval
   - later specialization, LoRA/SFT/distillation when justified.

2. **Stretch — big model, small machine**
   - SSD/layer/expert streaming
   - MoE offload
   - hierarchical caching
   - selective routing from a small resident controller
   - Colibrì / related memory-hierarchy ideas later.

The project optimizes a joint capability frontier, not tokens/second alone:
- quality
- delivery/reliability
- RAM/free-memory/swap
- total wall time
- model calls
- prompt/generated tokens
- disk footprint when relevant.

# Phase 6 — Capability Amplification — ACTIVE

## Capability Amplifier 001 — READY

Plan:
`research/amplify/capability-amplifier-001-plan.md`

Runner:
`scripts/capability_amplifier_001.py`

Primary subject:
- `qwen3.5:4b-mlx`
- Ollama
- context 4096
- non-thinking
- temperature 0
- max 2048 tokens/call.

Frozen benchmark provenance:
- Coding Benchmark 01 v1.0.1
- manifest blob `547050ecd0183b8d447dc3e21e724a8232f10297`
- single-shot adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`.

### Mechanism

Each task gets at most two calls.

Call 1:
- exact frozen single-shot prompt/request/parser
- no test feedback.

Validation:
- parser failure => deterministic parser feedback;
- valid delivery => exact frozen task tests;
- all tests pass => no repair allowed;
- otherwise exactly one repair allowed.

Call 2, only when needed:
- same model/runtime/sampler/context
- original task/context
- current candidate
- exact parser error or frozen test-failure summary
- same JSON delivery contract.

Candidate selection is deterministic:
- valid repair beats initial only if it passes more frozen tests;
- ties retain initial;
- invalid repair never replaces valid initial;
- if only repair is valid, repair is selected;
- if neither is valid, fixture remains and final delivery is failed.

No Pi, retrieval, third call, human intervention, web access, external model or fine-tuning in Amplify 001.

### Host / safety

Before benchmark:
- stop `qwen3.5:4b-mlx` once for cold-model policy;
- require 3 consecutive samples >=70% free memory.

If host gate is not met:
- `HOST_STATE_NOT_READY`
- no model benchmark launch.

During each model call:
- continuous free-memory/swap telemetry
- free <5% or swap >5600 MB => stop model + `PARTIAL_RESOURCE_FAIL`
- missing telemetry => `TELEMETRY_FAIL`.

### Frozen success gates

Historical single-shot reference:
- artifact 40.71
- delivery-adjusted 30.00
- delivery 3/6.

`QUALITY_IMPROVED`:
- COMPLETE
- delivery-adjusted **>30.00**.

`STRONG_AMPLIFICATION`:
- QUALITY_IMPROVED
- artifact **>40.71**
- delivery **>3/6**.

`PI_REFERENCE_REACHED` descriptive flag:
- delivery-adjusted **>=77.15**.

Because Amplify 001 intentionally exposes one deterministic hidden-test feedback round, reaching the Pi number does not imply intrinsic superiority over Pi Agentic 001.

## Exact next step

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/capability_amplifier_001.py
python3 scripts/capability_amplifier_001.py
```

No model download is expected.

Preserve output through `Summary:`.

## Decision after Amplify 001

If `COMPLETE`:
- freeze full per-task repair trajectory, quality and efficiency metrics;
- compare against the frozen 4B single-shot baseline;
- only then decide the next one-factor amplifier.

If `HOST_STATE_NOT_READY`:
- no scientific model run occurred; naturally free host resources and retry the launch.

If `PARTIAL_RESOURCE_FAIL` / `RUNTIME_FAIL` / `TELEMETRY_FAIL`:
- diagnose before changing the amplifier design.

If the mechanism establishes clear amplification, the next major comparison should eventually apply the same amplification logic to the faster llama.cpp 4B as a secondary efficiency control.

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file and `ROADMAP.md` before moving to the next checkpoint.
