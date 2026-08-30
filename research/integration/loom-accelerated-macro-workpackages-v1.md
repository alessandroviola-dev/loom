# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: ACTIVE — WP3-R2 behavioral unlock achieved locally; persistence pending

## Purpose

Replace user-facing micro-checkpoints with substantial Pi work packages. Scientific gates remain internal. Pi records failures, reverts regressions and continues inside the active work package instead of returning after every GO/NO_GO.

## WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_RUNTIME_PRODUCTIZATION_WP1`

Outcome:
- canonical S32 runtime at `5.596 tok/s` median matched decode;
- persistent localhost `llama-server`;
- WebUI/API/Pi/cache/lifecycle validated;
- S24 rollback retained.

## WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Outcome:
- Caveman deterministic packing/compression/recovery;
- Cavemem SQLite/FTS5 progressive project memory;
- `23.24%` median heavy-context provider-input reduction;
- `0%` no-op overhead;
- `6/6` SHA-verified exact recovery;
- easy rollback.

## WP3 — Behavioral Transform — COMPLETE / VALID NO_GO

Checkpoint:
`LOOM_BEHAVIORAL_TRANSFORM_WP3`

Outcome:
- rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates were built and served;
- frozen held-out refusal remained `6/6` for all;
- those adapter families are rejected;
- result did not prove architecture-level impossibility.

## WP3-R2 — Behavioral Unlock — COMPLETE LOCALLY / GO / PERSISTENCE PENDING

Checkpoint:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

Contract:
`research/integration/loom-behavioral-unlock-wp3-r2.md`

Local result:
`research/integration/loom-behavioral-unlock-wp3-r2-result.md`

Evidence:
`results-local/behavioral-unlock-wp3-r2/20260830T160845Z/`

Classification:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO`.

Selected route:
exact-lineage Huihui abliterated replacement, Q3_K_S GGUF.

Selected model:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

Local SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Validated outcome:
- original frozen explicit-refusal gate `6/6 -> 0/6`, `100%` relative reduction;
- benign capability `8/8 -> 8/8`;
- no increased degeneration in frozen evaluation;
- loopback API/WebUI stable;
- real Pi + WP2 request passed;
- rollback to canonical S32 + WP2 passed.

Tradeoff:
- fresh candidate decode about `55%` of fresh S32 baseline under the R2 comparison;
- materially higher swap pressure;
- behavioral/disposition drift recorded and retained.

Product decision:
retain two selectable DEEP profiles rather than replacing the fast baseline:
1. `loom-deep-30b-s32` — fast/default;
2. `loom-deep-30b-unlocked` — behaviorally unlocked Candidate A, slower/more resource-intensive.

The unlocked GGUF is a local model artifact and must not be committed. Persist only provenance/hash, small operational code/config, frozen specs and result documentation.

## Current action

Persist and review the bounded WP3-R2 reproducibility/product-profile package. Do not begin WP4 before that review.

## WP4 — FINAL INTEGRATION + ACCEPTANCE — PLANNED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

WP4 should integrate both validated DEEP profiles plus WP2 and test profile switching/rollback, API/WebUI/Pi, capability, performance, RAM/swap and exact provenance.

## Global execution rules

1. Do not return after routine internal NO_GO results.
2. Record and revert regressions, then continue.
3. Never relax a frozen scientific gate after seeing its result.
4. Keep a known-good runnable baseline throughout.
5. Prefer practical LOOM-native or already-compatible artifacts over unnecessary framework ports.
6. No public internet exposure by default.
7. No SIP/security disabling, destructive system actions, unrelated user-data deletion, or paid-cloud/credential requirements without returning to the user.
8. Default: Pi does not commit/push. At a completed macro boundary, ChatGPT may explicitly authorize one bounded reviewed persistence commit.
9. Intermediate evidence remains under `results-local/`.
10. A macro work package returns one bounded end report with candidates, measurements, failed/reverted attempts, changed files, commands and evidence roots.

## Current work package

WP3-R2 execution is complete locally with GO; bounded persistence is the current action.
