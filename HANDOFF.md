# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — the preregistered representable BF16 causal pilot stopped before any BF16/network execution because the first P3 Q4 baseline failed its final-logit provenance SHA gate despite matching verifier top1; next checkpoint is a P3-only Q4 provenance reconciliation
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001_INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`
Next core checkpoint: `LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.14.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Correct publisher mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility baseline:
- frozen `50/63` target tokens representable, `13/63` unsupported;
- corrected exact DFlash top1 remains `0/63`;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` used old decode semantics and is not current acceptance evidence.

Closed leading explanations:
- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static contract: 16/16 PASS, no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Do not reopen without new evidence.

## BF16 causal path state

Pinned available BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected deterministic states:
- P1 `P1_t32:6`, baseline DFlash rank 3, frozen Q4 verifier target 326, 79-token prefix;
- P2 `P2_t16:3`, baseline DFlash rank 3, frozen Q4 verifier target 994, 74-token prefix;
- P3 `P3_t01:2`, baseline DFlash rank 2, frozen Q4 verifier target 1620, 64-token prefix.

BF16 cache remains reusable and the network-cap guard is complete, tested, and remote-reproducible.

Hard ceilings for any future valid pilot re-attempt remain frozen:
- network `8 GiB` aggregate;
- requests `1,024` aggregate including retries;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache.

## Invalid pilot stop — COMPLETE

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

Administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-001/20260825T125526Z/`

Pre-dispatch gates:
- guard source SHA-256 values matched `AGENTS`;
- guard synthetic tests `6/6` PASS;
- storage/cache available;
- free external disk `1,152.25 GiB`;
- network ledger `0 B / 0 requests / 0 retries`.

First fixed-order state P3 `P3_t01:2`:
- Q4 verifier top1 still matched frozen target `1620`;
- final-logit provenance SHA did not match;
- observed abbreviated hash `97cde5dd...297cd52e`;
- expected abbreviated hash `58d20d90...185432`.

Completed BF16 states: `0`.
Network use: `0 B / 0 requests / 0 retries`.

This is not evidence for or against the BF16 recovery hypothesis. None of the preregistered BF16 scientific classifications is valid because the intervention never ran.

## Exact next step

Checkpoint:
`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

Purpose:
Determine why P3 Q4 replay preserves verifier top1 but fails the full-logit provenance hash gate.

Scope:
- P3 only;
- Q4 only;
- no BF16;
- no network.

Required diagnostic:
1. recover full expected/observed hashes and exact artifacts from invalid-pilot evidence;
2. determine hash semantics exactly: raw vector vs serialized file, dtype, shape, position and canonicalization;
3. recover exact frozen-producer and pilot-replay code paths;
4. compare input IDs/prefix, model/config/tokenizer/runtime/code provenance;
5. compare original and current Q4 producer paths locally;
6. find earliest divergence through taps, router IDs/weights, final hidden and final logits;
7. quantify every numerical difference with max abs/mean abs/RMSE/rel-L2/cosine and decision-level parity;
8. compute explicit canonical raw-array hashes for both sides;
9. do not weaken or redefine the frozen gate unless a concrete mechanical hash/selector semantics error is demonstrated.

Classify:
- `Q4_BASELINE_EXACT_REPLAY_RESTORED`;
- `Q4_BASELINE_HASH_SEMANTICS_RECONCILED`;
- `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`;
- `Q4_BASELINE_PROVENANCE_AMBIGUOUS`.

Only after this checkpoint resolves the Q4 gate may the same preregistered BF16 state set/order be reconsidered. No state substitution or post-hoc rescue.
