# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: ACTIVE — user-approved structure

## Purpose

Replace user-facing micro-checkpoints with four substantial Pi work packages.

Scientific gates remain internal. Pi records failures, reverts regressions and continues inside the active work package instead of returning after every GO/NO_GO.

A work package ends only when its substantial deliverable is complete or a genuine blocker requires user action, credentials, destructive/security-sensitive host changes, unavailable storage/hardware, or a project-direction choice not resolvable from existing goals/evidence.

## WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Contract:
`research/integration/loom-runtime-productization-wp1.md`

Result:
`research/integration/loom-runtime-productization-wp1-result.md`

Outcome:
- canonical S32 runtime at `5.596 tok/s` median matched decode;
- S24 retained as rollback;
- persistent localhost `llama-server`;
- embedded existing WebUI;
- OpenAI-compatible local API;
- Pi connected/tested;
- serving-path prompt/KV reuse verified;
- `scripts/loom-deep-server` lifecycle workflow persisted.

## WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Contract:
`research/integration/loom-context-intelligence-wp2.md`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Outcome:
- Caveman-derived deterministic context packing/compression/recovery;
- Cavemem-derived SQLite/FTS5 progressive project memory;
- Pi host-side `before_provider_request` integration;
- no extra LLM/embedding daemon/model-visible tool schema;
- `23.24%` median heavy-context provider-input reduction;
- `0%` no-op input overhead;
- `6/6` SHA-verified exact recovery;
- objective success non-inferior to baseline;
- easy disable/rollback.

Do not integrate LoopX, Observal or pi-dynamic-workflows as separate permanent systems.

## WP3 — Behavioral Transform — COMPLETE LOCALLY / NO_GO — PERSISTENCE PENDING

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Contract:
`research/integration/loom-behavioral-transform-wp3.md`

Local result:
`research/integration/loom-behavioral-transform-wp3-result.md`

Evidence:
`results-local/behavioral-transform-wp3/20260830T144523Z/`

Classification:
`LOOM_BEHAVIORAL_TRANSFORM_WP3_NO_GO`.

Validated bounded outcome:
- actual GGUF LoRA adapters were constructed and loaded through canonical `llama-server`;
- rank-1 directional candidate tested;
- MoE-router candidate tested;
- rank-4 subspace/multi-direction candidate tested;
- frozen held-out refusal remained `6/6` for all tested transformed candidates;
- target-behavior reduction remained `0%`;
- frozen behavior promotion gate therefore failed;
- no behavioral adapter is promoted;
- base S32 + WP2 was restored, hash-verified, health-checked and rollback-tested.

Interpretation:
WP3 is scientific NO_GO rather than physical block: the host/toolchain can produce and serve the transforms, but the bounded validated methods did not produce a useful behavior improvement.

Do not weaken the frozen gate, relabel prompt-only behavior, or retry the same method families merely under different names.

Before WP4, persist the bounded WP3 reproducibility package: result, frozen evaluation specs and reusable small source/scripts/configs. Exclude generated adapter/model artifacts and `results-local/`.

## WP4 — Final Integration + Acceptance — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Goal:
assemble the strongest validated outputs into the final practical LOOM system.

Final candidate should use:
- S32 runtime/server/WebUI/API;
- validated serving-path prompt/prefix cache reuse;
- Caveman + Cavemem;
- **no behavioral adapter enabled**, because WP3 completed valid NO_GO.

Required acceptance:
- reliable clean startup;
- localhost serving/API healthy;
- selected existing browser WebUI works;
- Pi works against local LOOM;
- S32 or later better validated runtime active;
- validated serving-path prompt/prefix caching active;
- Caveman + Cavemem active in validated form;
- WP3 NO_GO explicitly retained with exact evidence and no hidden behavioral transform;
- representative capability smoke tests pass;
- final decode/prefill/E2E/RAM/swap recorded;
- simple documented start/stop/health flow;
- exact artifact/config/source hashes and evidence roots retained.

WP4 may classify GO with WP3 remaining NO_GO, provided all final product acceptance gates pass.

## Global execution rules

1. Do not return after routine internal NO_GO results.
2. Record and revert regressions, then continue.
3. Never relax a frozen scientific gate after seeing its result.
4. Keep a known-good runnable baseline throughout.
5. Prefer small LOOM-native adaptations over installing large upstream stacks.
6. No public internet exposure by default.
7. No SIP/security disabling, destructive system actions, unrelated user-data deletion, or paid-cloud/credential requirements without returning to the user.
8. Default: Pi does not commit/push. At a completed macro boundary, ChatGPT may explicitly authorize one bounded reviewed persistence commit.
9. Intermediate evidence remains under `results-local/`.
10. A macro work package returns one bounded end report with deliverables, measurements, failed/reverted attempts, changed files, commands and evidence roots.

## Current action

Persist the bounded WP3 reproducibility package. WP4 remains not authorized until that persistence is reviewed.
