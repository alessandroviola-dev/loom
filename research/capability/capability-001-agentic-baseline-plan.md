# CAPABILITY 001 — Qwen3-8B 3-bit agentic usefulness baseline

Date: 2026-08-21
Status: PLANNED

## Goal

Measure the practical intelligence/usefulness of the current canonical LOOM Qwen3-8B 3-bit system, not only its memory use and token throughput.

The baseline should answer a concrete question:

> Can the current local model reliably perform real repository/software tasks through Pi with limited human intervention?

This baseline becomes the reference for future representation changes, especially stronger quantization. A future model/runtime that is faster or smaller but materially less capable should not be promoted blindly.

## Frozen subject

Canonical performance reference:

- Qwen3-8B, 3-bit affine/group64;
- Apple M1 8 GB;
- REALGEN 001 real autoregressive generation: 13.184615357 tok/s pooled;
- REALGEN 001 end-to-end output: 12.046861457 tok/s pooled;
- ordinary built-in MLX M1 qmv_fast;
- BF16 KV.

CAPABILITY 001 measures usefulness; it does not change model weights or optimize runtime.

## Benchmark philosophy

Prefer real, checkable tasks over subjective chat ratings.

Tasks should have deterministic or reviewable success criteria and should resemble work LOOM is expected to perform in this repository.

## Proposed task families

### A — Repository understanding

- inspect a supplied repository state and identify the active branch, dirty files and intended next action;
- locate the relevant experiment/report from a short problem description;
- summarize a result artifact without inventing metrics.

### B — Git operational reasoning

Use a disposable/local test repository or sandbox, never the canonical branch for destructive tests.

Examples:

- determine whether a branch is ahead/behind/diverged;
- choose fetch + fast-forward-safe actions;
- avoid force push, blind pull, unintended merge/rebase;
- stage only intended files;
- prepare a correct commit;
- recognize a dirty-tree condition and avoid overwriting work.

The benchmark is specifically interested in whether the local model can coordinate these operations through Pi correctly.

### C — Code modification

- fix a small Python defect with an existing test;
- add a bounded feature under explicit constraints;
- preserve unrelated behavior;
- run the correct tests and interpret failures.

### D — Experiment discipline

- implement a small benchmark from a frozen specification;
- preserve CONTROL/TREATMENT boundaries;
- stop correctly when a prerequisite fails;
- avoid silently changing the experiment to obtain a preferred result.

### E — Result interpretation

- read a compact JSON/CSV experiment result;
- compute or identify the correct primary metric;
- distinguish absolute throughput from causal balanced ratios;
- recommend GO/NO-GO according to a supplied threshold.

## Initial benchmark size

Target 10–15 tasks total, with multiple task families represented.

Do not make CAPABILITY 001 enormous. It is intended to be rerunnable after future quantization/model-representation changes.

## Primary metrics

Record at least:

- task success: pass/fail;
- percentage of tasks completed correctly;
- human interventions required;
- invalid/destructive command attempts;
- constraint violations;
- code/test correctness where applicable;
- number of correction turns;
- wall time per task if reliably measurable;
- model tokens/output volume if available.

Create a weighted aggregate only after task scoring is frozen. Preserve raw per-task outcomes.

## Critical failures

Flag separately from ordinary task failure:

- destructive Git action against instructions;
- fabricated test/result claim;
- silently changing frozen experiment conditions;
- deleting/overwriting unrelated work;
- claiming success without running required validation.

## Future quantization use

For any future lower-bit or mixed-precision candidate, compare against CAPABILITY 001 using the same tasks and scoring.

Report three dimensions together:

- memory delta;
- speed delta;
- capability delta.

Do not promote a representation solely because it fits or is faster.

## Execution boundary

Pi should be used to execute the actual agentic tasks and tests. ChatGPT owns benchmark design, scoring review, Git synchronization, HANDOFF and ROADMAP updates under `research/governance/chatgpt-pi-operating-protocol.md`.

## Next preparation step

Freeze the exact task set, disposable Git sandbox design, expected outcomes and scoring rubric before running CAPABILITY 001.
