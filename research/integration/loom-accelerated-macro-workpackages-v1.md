# LOOM Accelerated Macro Work Packages v1

Date: 2026-08-31
Status: FINAL product persisted; UOPT-001 UNLOCKED speed optimization active

## Purpose

Use substantial Pi macro work packages instead of user-facing micro-checkpoints. Pi records/fixes/reverts routine failures internally and returns at macro completion or a genuine user-action blocker.

## Finished product

Final persistence commit:
`98949e77863c93a7d9dba266204a911ab85db09c`.

Final profiles:
1. `loom-deep-30b-s32` — FAST/default;
2. `loom-deep-30b-unlocked` — validated behavioral-unlock profile.

Final UX:
```text
scripts/loom-deep use fast|unlocked
scripts/loom-deep start|stop|status|health|current
```

Stable local endpoint for either active profile:
`127.0.0.1:18080`.

WP1 Runtime + Product Serving: GO / persisted.

WP2 Context Intelligence: GO / persisted. Caveman deterministic packing/recovery + Cavemem SQLite/FTS5 memory.

WP3 Behavioral Transform: valid NO_GO for rank-1 directional, MoE-router and rank-4 subspace families.

WP3-R2 Behavioral Unlock: GO / persisted. Frozen UNLOCKED result `0/6` refusal, `8/8` benign, `0/6` held-out degeneration.

WP4 Final Integration + Acceptance: GO / persisted. FAST -> UNLOCKED -> FAST, loopback API/WebUI/Pi+WP2/cache and rollback validated.

WP4 performance snapshot:
- FAST decode `6.209 tok/s`;
- UNLOCKED decode `2.963 tok/s`.

## UOPT-001 — UNLOCKED Speed Optimization — ACTIVE

Checkpoint:
`LOOM_UNLOCKED_SPEED_UOPT_001`

Branch:
`research/unlocked-speed-001`

Contract:
`research/integration/loom-unlocked-speed-optimization-001.md`

Goal:
maximize validated UNLOCKED throughput on Apple M1 8 GiB while preserving the finished product and frozen behavior/capability gates.

Primary target:
**>= 5.0 tok/s matched fresh decode median**.

Stretch target:
beat FAST historical `5.596 tok/s` if possible without regression.

Research ladder:
1. current exact-model runtime frontier: MoE slots/residency, mmap/no-mmap, CPU/Metal placement, batch/ubatch, relevant thread/Metal knobs;
2. newer evidence-backed Qwen3-MoE paging/residency implementations, with exact revision audit and local reproduction;
3. if runtime work cannot reach target, a small exact-lineage quantization frontier of the validated Huihui derivative;
4. combine only independently validated winners.

Promotion gates remain frozen:
- explicit refusal `0/6`;
- benign capability `8/8`;
- held-out degeneration `0/6`;
- exact provenance/hashes;
- loopback-only serving;
- API/WebUI/Pi+WP2/cache;
- no crash/OOM/corruption;
- clean rollback to current FAST and current validated UNLOCKED.

Intermediate evidence:
`results-local/unlocked-speed-uopt-001/<timestamp>/`.

Pi does not commit/push during execution.

## Global execution rules

1. Evidence over narrative.
2. Do not return after routine experiment NO_GO results.
3. Never relax frozen gates after seeing results.
4. Preserve exact provenance and hashes.
5. Keep known-good FAST and UNLOCKED rollback baselines.
6. No public internet exposure by default.
7. No SIP/security disabling or destructive unrelated cleanup.
8. Large local models remain outside Git.
9. External benchmark claims are hypotheses until locally reproduced.
10. Pi commits only under the explicit bounded macro-boundary exception.
