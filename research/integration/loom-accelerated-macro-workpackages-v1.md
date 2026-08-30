# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: ACTIVE — WP4 final integration authorized

## Purpose

Use substantial Pi macro work packages instead of user-facing micro-checkpoints. Pi records/fixes/reverts routine failures internally and returns at macro completion or a genuine user-action blocker.

## WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Outcome:
- canonical FAST S32 runtime;
- `5.596 tok/s` validated median matched decode;
- persistent localhost llama-server;
- WebUI/API/Pi/cache/lifecycle validated;
- S24 rollback retained.

## WP2 — Context Intelligence — COMPLETE / GO / PERSISTED

Outcome:
- Caveman deterministic packing/compression/recovery;
- Cavemem SQLite/FTS5 progressive project memory;
- `23.24%` median heavy-context provider-input reduction;
- `0%` no-op overhead;
- `6/6` exact recovery;
- independent rollback.

## WP3 — Behavioral Transform — COMPLETE / VALID NO_GO

Outcome:
- rank-1 directional, MoE-router and rank-4 subspace GGUF-LoRA candidates were built/served;
- frozen refusal stayed `6/6`;
- those three adapter families rejected;
- no architecture-level impossibility conclusion.

## WP3-R2 — Behavioral Unlock — COMPLETE / GO / PERSISTED

Persistence commit:
`1252fcfad73878981a1aa1844a484949a12d5ff4`

Selected UNLOCKED model:
`Huihui-Qwen3-30B-A3B-Instruct-2507-abliterated.Q3_K_S.gguf`

SHA256:
`734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c`

Outcome:
- frozen explicit refusals `6/6 -> 0/6`;
- benign capability `8/8 -> 8/8`;
- API/WebUI and real Pi + WP2 passed;
- rollback to FAST + WP2 passed;
- accepted with explicit slower/high-swap/disposition-drift caveat.

Product decision: retain FAST and UNLOCKED as separate selectable profiles.

## WP4 — Final Integration + Acceptance — ACTIVE

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Contract:
`research/integration/loom-final-acceptance-wp4.md`

Goal:
turn all validated results into the final practical LOOM product.

Final product target:
1. `loom-deep-30b-s32` — FAST/default;
2. `loom-deep-30b-unlocked` — validated behavioral-unlock profile.

WP4 must provide:
- stable ignored `models/` artifact paths without unnecessary GGUF duplication;
- one resident 30B at a time;
- simple profile selection/switching;
- stable localhost serving endpoint where practical;
- API/WebUI/Pi + WP2 validation for both;
- unchanged frozen UNLOCKED behavior/capability reproduction;
- FAST health/performance;
- UNLOCKED decode/prefill/E2E/RSS/swap/memory-pressure evidence;
- prompt/KV cache compatibility;
- Context Intelligence rollback;
- clean FAST -> UNLOCKED -> FAST acceptance sequence;
- operations documentation and final result/evidence.

Pi does not commit/push during WP4 execution. Final persistence follows review.

## Global execution rules

1. Do not return after routine internal failures.
2. Record and fix/revert regressions, then continue.
3. Never relax frozen gates after seeing results.
4. Preserve a known-good FAST baseline.
5. Do not run both 30B profiles concurrently for convenience.
6. Avoid unnecessary multi-GB model duplication or redownload.
7. No public internet exposure by default.
8. No SIP/security disabling, destructive unrelated cleanup, paid-cloud or new credential requirements.
9. Intermediate evidence stays under `results-local/`.
10. Return one bounded final report with implementation, acceptance measurements, changed files and evidence roots.

## Current work package

`LOOM_FINAL_ACCEPTANCE_WP4`
