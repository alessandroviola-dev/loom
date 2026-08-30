# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: ACTIVE — user-approved structure with behavioral-unlock continuation after WP3 NO_GO

## Purpose

Replace user-facing micro-checkpoints with substantial Pi work packages. Scientific gates remain internal. Pi records failures, reverts regressions and continues inside the active work package instead of returning after every GO/NO_GO.

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
- embedded WebUI and OpenAI-compatible local API;
- Pi connected/tested;
- serving-path prompt/KV reuse verified;
- lifecycle workflow persisted.

## WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Checkpoint:
`LOOM_CONTEXT_INTELLIGENCE_WP2`

Contract:
`research/integration/loom-context-intelligence-wp2.md`

Result:
`research/integration/loom-context-intelligence-wp2-result.md`

Outcome:
- Caveman deterministic packing/compression/recovery;
- Cavemem SQLite/FTS5 progressive project memory;
- Pi host-side provider integration;
- `23.24%` median heavy-context provider-input reduction;
- `0%` no-op overhead;
- `6/6` SHA-verified exact recovery;
- easy rollback.

## WP3 — Behavioral Transform — COMPLETE / VALID NO_GO

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
- real GGUF LoRA candidates were constructed and served;
- rank-1 directional, MoE-router and rank-4 subspace routes were tested;
- frozen held-out refusal remained `6/6` for all;
- target-behavior reduction `0%`;
- no adapter promoted;
- base S32 + WP2 restored and rollback-tested.

Interpretation:
WP3 rejects those three bounded adapter families. It does not establish that the architecture cannot be behaviorally unlocked.

## WP3-R2 — Behavioral Unlock — ACTIVE

Checkpoint:
`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`

Contract:
`research/integration/loom-behavioral-unlock-wp3-r2.md`

User goal:
continue research until a materially different route to an actually behaviorally unlocked local model has been tested; do not move to WP4 merely because the original adapter families failed.

### Route A — exact-base external abliterated replacement

Research discovered:
- upstream behavioral derivative `huihui-ai/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated`;
- declared base `Qwen/Qwen3-30B-A3B-Instruct-2507`;
- GGUF source `mradermacher/Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated-GGUF`;
- Q3_K_S candidate around 13.3 GB, architecture `qwen3moe`.

This is a full model-level candidate, not a small adapter approximation. Treat it as untrusted until local provenance/hash/metadata/behavior/capability/resource evaluation passes.

### Route B — native llama.cpp activation/control-vector steering

Current llama.cpp supports runtime control vectors and includes a GGUF `cvector-generator`. This intervention acts on activations during inference and is materially different from the failed WP3 LoRA weight edits.

Use frozen contrast data disjoint from the final held-out set; bounded mean/PCA, layer range and scale tests only.

### Route C — evidence-backed Qwen3-A3B derivative fallback

If A/B fail, inspect current exact-/near-lineage derivatives with transparent published behavior evidence, then test locally under the same frozen R2 gates.

### External-compute boundary

If local replacement/control-vector routes are exhausted but evidence supports a full-weight editing/fine-tuning procedure that cannot run on the M1 8 GiB host, return with the exact justified compute/storage plan. Do not buy cloud compute or require new credentials autonomously.

### R2 promotion

`LOOM_BEHAVIORAL_UNLOCK_WP3_R2_GO` requires:
- actual model-level or activation-level intervention;
- >=50% relative reduction against the original frozen `6/6` behavior baseline;
- practical capability preservation;
- stable local serving;
- exact hashes/provenance;
- throughput/RAM/swap evidence;
- Pi/WP2 compatibility;
- clean rollback to canonical S32 + WP2.

Do not rewrite the original WP3 held-out gate after seeing R2 outputs.

## WP4 — FINAL INTEGRATION + ACCEPTANCE — BLOCKED / NOT AUTHORIZED

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

WP4 remains blocked while WP3-R2 is active.

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

`LOOM_BEHAVIORAL_UNLOCK_WP3_R2`
