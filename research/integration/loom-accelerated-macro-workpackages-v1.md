# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-30
Status: WP4 completed locally with GO; final bounded persistence pending

## Purpose

Use substantial Pi macro work packages instead of user-facing micro-checkpoints. Pi records/fixes/reverts routine failures internally and returns at macro completion or a genuine user-action blocker.

## WP1 — Runtime + Product Serving — COMPLETE / GO / PERSISTED

Outcome:
- canonical FAST S32 runtime;
- historical validated median matched decode `5.596 tok/s`;
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

## WP4 — Final Integration + Acceptance — COMPLETE LOCALLY / GO / PERSISTENCE PENDING

Checkpoint:
`LOOM_FINAL_ACCEPTANCE_WP4`

Classification:
`LOOM_FINAL_ACCEPTANCE_WP4_GO`.

Contract:
`research/integration/loom-final-acceptance-wp4.md`

Local result:
`research/integration/loom-final-acceptance-wp4-result.md`

Evidence:
`results-local/final-acceptance-wp4/20260830T182958Z/`

Final product:
1. `loom-deep-30b-s32` — FAST/default;
2. `loom-deep-30b-unlocked` — validated behavioral-unlock profile.

Final UX:
```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable local endpoint for either active profile:
`127.0.0.1:18080`.

Final acceptance passed:
- stable hard-linked ignored model artifacts with hash preservation;
- FAST -> UNLOCKED -> FAST switching twice;
- only one resident 30B profile at a time;
- loopback-only serving;
- health/models/API/WebUI for both;
- Pi + WP2 for both;
- Context Intelligence disable rollback;
- UNLOCKED frozen reproduction: refusal `0/6`, degeneration `0/6`, benign `8/8`;
- prompt/KV cache for both, repeated 1,149-token prefix reduced to one evaluated token;
- final rollback to FAST + WP2.

Final WP4 performance snapshot:
- FAST: decode `6.209 tok/s`, prefill `3.438 tok/s`, E2E `7.131 s`, RSS `4.00->4.01 GiB`, swap `1269->1308 MiB`;
- UNLOCKED: decode `2.963 tok/s`, prefill `1.673 tok/s`, E2E `9.129 s`, RSS `4.13->4.16 GiB`, swap `1667->1708 MiB`.

Final active state after execution: FAST + WP2.

## Current action

Create one bounded final persistence commit containing only reviewed WP4 product/config/result/docs, optionally plus the reviewed historical WP3 NO_GO result.

Exclude:
- `models/` and all GGUFs;
- `.loom/`;
- `results-local/`;
- home-directory Pi configuration;
- caches/secrets;
- unrelated historical untracked scripts.

After that commit is pushed and reviewed, LOOM is FINAL / GO / FULLY PERSISTED.

## Global execution rules

1. Evidence over narrative.
2. Never relax frozen gates after seeing results.
3. Preserve exact provenance and hashes.
4. No public internet exposure by default.
5. No SIP/security disabling or destructive unrelated cleanup.
6. Large local models remain outside Git.
7. Pi commits only under the explicit bounded macro-boundary exception.
