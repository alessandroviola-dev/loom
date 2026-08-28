# LOOM — Pi Agent Protocol

Version: 3.51
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. required gate instrumentation must persist before evidence is accepted;
8. failed frozen methods are not silently modified/rerun under the same checkpoint;
9. Integration Readiness Protocol v1 is mandatory before integration coding/model forward;
10. production code is canonical only after exact review and Git persistence;
11. production/user-facing Python must not depend on untracked research helper modules;
12. token streaming must use tokenizer-compatible stateful detokenization and stop/control tokens must not be emitted;
13. user-facing runtime claims require real end-to-end generation evidence.

## Local-root clarification

GitHub is canonical. The currently active local clone used for validated 30B and historical 8B `results-local` artifacts is:
`<repository-root>`.

A second archive/clone tree also exists at:
`<external-archive>`.

Do not mix relative paths/artifacts across the two roots inside one experiment. External archived model artifacts may be inspected explicitly by absolute path only.

## Mission

**Big models. Small machines.** Build a practical local AI system on Apple M1/8GB where multiple model sizes, tools, memory, skills/protocols and behavioral steering work as one adaptive system.

## Target LOOM architecture — THREE-TIER AUTO ROUTING

- **LOOM FAST / ~4B** — maximize speed, TTFT, low memory and effective capability through skills, protocols, tools and memory; default for easy tasks.
- **LOOM BALANCED / ~8B** — optimized middle tier for tasks where 4B is insufficient but 30B latency is not justified.
- **LOOM DEEP / 30B** — slow large-model tier for difficult tasks where measured capability gain justifies latency.
- **LOOM AUTO** — router chooses the cheapest tier likely to solve the task and may escalate 4B -> 8B -> 30B when confidence/verification is insufficient.

All tiers should eventually share compatible LOOM-level memory/retrieval, skills/protocols, tools, verification, context handling and provider/API layer.
Do not freeze router thresholds before matched evidence exists.

## LOOM Heretic — FUNDAMENTAL / NON-OPTIONAL TRACK

`LOOM_HERETIC_TECHNICAL_PAPER.md` is a fundamental design input to final LOOM, not an optional side experiment.
Execution remains after runtime-role selection so edits target the tiers that matter. Freeze refusal/steerability and capability-preservation gates before edits. Do not claim unmeasured absolute `guardrail-free` status.

## Frozen Qwen3-30B-A3B comparator

Canonical backend: `scripts/loom_30b_moe_expert_major_backend_001.py`.
Backend commit `96958de`; SHA `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`.
Exact-Q4/top-8 sustained 3x32 median `1.229233 tok/s`.

Closed current-verifier paths: routing sparsity no acceptable gain; Q2/Q3 from deployed Q4 fidelity fail; DFlash closed; exact K4 oracle verifier ceiling `1.792925 tok/s`, so real drafter is not justified.

## Qwen3.8 — parked

`QWEN38_BOTH_PORTABLE`; large downloads/execution remain parked until after practical tier comparison unless explicitly reactivated.

## LOOM 30B v1 — CANONICAL / FUNCTIONAL_SLOW

Canonical production commit:
`d3691b765004849abb01a7675e5a6e7c5d0edd4c`.

Files:
- `scripts/loom_30b_runtime_core_v1_001.py` SHA `75da01c85d3b0d4c1aae9c10cf5bb19723ef39ec6ef8b0149707a977afc4befc`;
- `scripts/loom_30b_interactive_v1_001.py` SHA `44b89ba34d597a3c9798c7ad1c081aa0eeff865cc5320e27213b3c6ebe4a5322`.

Historical long-form: TTFT `47.832 s`; decode `1.116 tok/s`; end-to-end `0.921 tok/s`; peak RSS `1,447,067,648 B`.
Manual LRUCache task: correct O(1) strategy and correct `get()->-1`, but 384-token output budget ended during `put()`, so requested complete executable solution was not delivered; subjective latency was minutes.

## Recovered LOOM 8B baseline

Historical REALGEN source:
`scripts/loom_real_generation_baseline_001.py`.

Model/runtime:
- `results-local/mlx/models/Qwen3-8B-3bit` exists in active local clone;
- upstream `mlx-community/Qwen3-8B-3bit`, revision `619ded3`;
- weight SHA `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit affine/group64;
- `results-local/mlx/venv-mlx-lm-0.31.3` exists;
- MLX/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- real M1 autoregressive built-in MLX `qmv_fast`, BF16 KV, greedy, thinking OFF;
- cleanup after each 10 committed tokens.

REALGEN 001 measured 722 real generated tokens:
- pooled generation `13.184615 tok/s`;
- pooled end-to-end output `12.046861 tok/s`;
- per-prompt TTFT ~`0.94 s`;
- peak MLX `3,826,575,836 B`;
- peak swap `1591.19 MB`.

Stretch-037 custom `S1_R8` achieved an M5 oracle-path improvement but is M5-only and MUST NOT be injected into real M1 chat generation.

## Current checkpoint — LOOM 8B matched practical bake-off runner

Preregistration:
`research/architecture/loom-8b-practical-bakeoff-runner-001-preregistration.md`.

Build one new bounded one-shot runner derived from REALGEN with NO runtime-semantic changes. Frozen task is the exact LRUCache prompt used on 30B, max generated tokens 384.

Required outputs: full text, completion reason/count, TTFT, prefill, generation/end-to-end tok/s, p50/p95, cleanup, memory/swap and provenance.

Do not build a full new CLI/UI yet. The purpose is a matched LOOM-vs-LOOM practical comparison.

After 8B evidence, recover/port the 4B LOOM tier under an analogous matched protocol, then choose initial FAST/BALANCED/DEEP roles. After tier selection/initial optimization, open mandatory LOOM Heretic integration.