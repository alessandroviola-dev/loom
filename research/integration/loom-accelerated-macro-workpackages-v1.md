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

## WP3 — Behavioral Transform — ACTIVE

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Contract:
`research/integration/loom-behavioral-transform-wp3.md`

Goal:
produce and validate an actual model/adapter-level behavioral transform for canonical LOOM DEEP. Prompt-only behavior does not count.

Method/reference order:
1. LOOM-native Heretic/projected single-direction low-rank adapter;
2. Abliterix-derived MoE-aware refinement when measured evidence supports it;
3. Senbonzakura-derived multi-direction/subspace when single-direction remains materially insufficient;
4. clean low-rank alternative if required by representation/toolchain constraints.

Preferred final artifact:
a small reversible **GGUF LoRA adapter** loaded separately by canonical `llama-server`, rather than a second full model copy.

Preferred technical path:

`frozen contrast/evaluation sets -> streamed residual statistics -> stable direction/subspace -> low-rank delta -> GGUF adapter -> llama-server -> frozen base/transformed behavior/capability/resource A/B`

Important constraints:
- preserve canonical S32 and WP2 rollback paths;
- avoid a full resident BF16/FP16 30B representation when selected-tensor streaming can avoid it;
- use FP32/FP64 for sensitive geometric accumulation;
- start with deterministic/searchless rank-1 / attention-output candidates;
- do not begin with broad TPE;
- escalate to MoE-specific or multi-direction methods only when evidence supports it;
- do not copy AGPL implementation code without explicit license review.

WP3 completion requires an actual runtime-loadable transform, material frozen target-behavior improvement, capability preservation, safe resources/throughput, real Pi transformed-profile validation, exact hashes and successful rollback.

## WP4 — Final Integration + Acceptance — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Goal:
assemble the best validated outputs of WP1-WP3 into the final practical LOOM system.

Required acceptance:
- reliable clean startup;
- localhost serving/API healthy;
- selected existing browser WebUI works;
- Pi works against local LOOM;
- S32 or later better validated runtime active;
- validated serving-path prompt/prefix caching active;
- Caveman + Cavemem active in validated form;
- behavioral-transform profile loaded and validated, or exact evidenced blocker classified;
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
8. Default: Pi does not commit/push. At a completed macro boundary, ChatGPT may explicitly authorize one bounded reviewed persistence commit.
9. Intermediate evidence remains under `results-local/`.
10. A macro work package returns one bounded end report with deliverables, measurements, failed/reverted attempts, changed files, commands and evidence roots.

## Current work package

`LOOM_BEHAVIORAL_TRANSFORM_WP3`
