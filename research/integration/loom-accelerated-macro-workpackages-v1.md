# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: ACTIVE — user-approved structure

## Purpose

Replace user-facing micro-checkpoints with four substantial Pi work packages.

Scientific gates remain internal. Pi records failures, reverts regressions and continues inside the active work package instead of returning after every GO/NO_GO.

A work package ends only when its substantial deliverable is complete or a genuine blocker requires user action, credentials, destructive/security-sensitive host changes, unavailable storage/hardware, or a project-direction choice not resolvable from existing goals/evidence.

## WP1 — Runtime + Product Serving — COMPLETE / GO

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Authoritative contract:
`research/integration/loom-runtime-productization-wp1.md`

Canonical result:
`research/integration/loom-runtime-productization-wp1-result.md`

Outcome:
- canonical S32 runtime at 5.596 tok/s median matched decode;
- S24 retained as rollback;
- persistent localhost `llama-server`;
- existing embedded WebUI;
- OpenAI-compatible local API;
- Pi connected/tested;
- serving-path prompt/KV reuse verified;
- operational start/status/health/stop workflow.

## WP2 — Context Intelligence — ACTIVE

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Authoritative contract:
`research/integration/loom-context-intelligence-wp2.md`

Goal:
improve effective local-model/Pi context efficiency and continuity with only the two highest-priority mechanisms selected by the user.

Primary engineering inputs only:

### 1. Caveman
Use for:
- deterministic type-aware compression;
- token-budget context selection/packing;
- lexical/BM25-style relevance + recency + priority + error/pin preservation;
- recovery handles for omitted evidence;
- restoring chronology after relevance-based selection;
- bypassing compression on small/no-op inputs when overhead would be negative.

Primary expected benefit:
less provider-facing input context, lower prefill cost/memory pressure, and more targeted use of the 30B model.

### 2. Cavemem
Use for:
- project-scoped progressive local memory;
- SQLite/FTS5-first compact searchable observations;
- retrieving only relevant prior facts/decisions/evidence;
- exact body/evidence retrieval on demand;
- privacy/redaction before durable writes;
- no mandatory embeddings in v0.

Cavemem decides what prior information should be recovered; Caveman decides what should actually enter the prompt and how compactly.

Do **not** integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems in WP2. Small implementation ideas may be borrowed only when they are necessary to support Caveman/Cavemem and have negligible overhead.

WP2 final comparison:
- A: WP1 baseline;
- B: Caveman only;
- C: Caveman + Cavemem.

WP2 completion requires measured net benefit in token use/task utility, exact recovery/provenance, safe memory/privacy behavior and easy rollback.

## WP3 — Behavioral Transform — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Goal:
produce and validate an actual model/adapter-level behavioral-freedom transform for the final LOOM profile. Prompt-only behavior does not satisfy WP3.

Current technical search priority:
1. **Abliterix-derived methodology**, especially MoE-aware behavioral editing concepts, adapted to LOOM rather than assuming the full upstream CUDA stack can run on M1 8 GiB;
2. **Heretic** as the established project baseline and technical reference;
3. **Senbonzakura-style multi-direction methods** if they offer a better feasible route for the canonical Qwen MoE configuration;
4. a clean LOOM-native equivalent when upstream implementations are physically/toolchain-incompatible.

The criterion is not project popularity. Select the method that gives the strongest technically valid transform for the actual canonical GGUF/llama.cpp/Apple-Silicon stack.

Preferred final artifact:
a small reversible/runtime-loadable adapter or equivalent artifact usable by the final llama.cpp serving path, rather than a second full model copy, when technically valid.

Require provenance, frozen behavioral evaluation, capability preservation, resource/throughput delta and exact artifact hashes.

## WP4 — Final Integration + Acceptance — PLANNED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Goal:
assemble the best validated outputs of WP1–WP3 into the final practical LOOM system.

Required acceptance:
- reliable clean startup;
- localhost serving/API healthy;
- selected existing browser WebUI works;
- Pi works against local LOOM;
- selected runtime acceleration active;
- validated serving-path prompt/prefix caching active where applicable;
- Caveman + Cavemem enabled only in their validated net-positive form;
- behavioral-transform profile loaded and validated, or exact evidenced physical/toolchain blocker documented;
- representative capability smoke tests pass;
- final decode/prefill/E2E/RAM/swap recorded;
- simple documented start/stop/health flow;
- exact artifact/config/source hashes and evidence roots retained.

## Global execution rules

1. Do not return after routine internal NO_GO results.
2. Record and revert regressions, then continue.
3. Never relax a frozen scientific gate after seeing its result.
4. Keep a known-good runnable baseline throughout.
5. Prefer small LOOM-native adaptations over installing large upstream stacks.
6. No public internet exposure by default.
7. No SIP/security disabling, destructive system actions, unrelated user-data deletion, or paid-cloud/credential requirements without returning to the user.
8. Pi does not commit/push; ChatGPT persists canonical Git state at macro-work-package boundaries.
9. Intermediate evidence remains under `results-local/`.
10. A macro work package returns one bounded end report with deliverables, measurements, failed/reverted attempts, changed files, commands and evidence roots.

## Current work package

`LOOM_CONTEXT_INTELLIGENCE_WP2`
