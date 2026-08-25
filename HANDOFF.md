# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — exact Q4 continuation segmentation has been restored for P1/P2/P3 and all frozen provenance gates pass. The Q4 blocker is closed; next checkpoint is the bounded re-attempt of the preregistered Q4-vs-BF16 causal pilot.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001_Q4_BASELINE_SEGMENTATION_REPAIR_PASS`
Next core checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent Pi context: `/AGENTS.md` v3.16.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Correct publisher mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility baseline:
- frozen `50/63` representable, `13/63` unsupported;
- corrected DFlash exact top1 `0/63`;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Closed leading explanations:
- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static interface: `16/16` PASS, no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Historical E2E `0/96` used old decode semantics and is not current acceptance evidence.

## BF16 bounded infrastructure

Pinned BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Network-cap guard:
`BF16_NETWORK_CAP_GUARD_PASS` with remote source parity PASS.

Aggregate pilot ceilings remain frozen:
- network `8 GiB`;
- requests `1,024`, retries included;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache.

Frozen state order remains:
1. P3 `P3_t01:2` — target `1620`;
2. P1 `P1_t32:6` — target `326`;
3. P2 `P2_t16:3` — target `994`.

No substitutions.

## First causal attempt — INVALID BEFORE BF16

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` stopped before BF16/network because its P3 Q4 baseline used the wrong producer segmentation.

Administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

It contains no evidence for or against the BF16 recovery hypothesis.

## Q4 provenance diagnosis — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001` = `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`.

Root cause was deterministic execution segmentation/KV-boundary drift, not hash semantics. P3 frozen producer used a 63-token prefill plus one cached decode; the invalid pilot used a fresh 64-token forward.

## Q4 segmentation replay repair — COMPLETE

Checkpoint:
`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`

Classification:
`Q4_BASELINE_SEGMENTATION_REPAIR_PASS`

Report:
`research/architecture/loom-dflash-q4-baseline-segmentation-replay-repair-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-segmentation-replay-repair-001/20260825T132255Z/`

Recovered exact segmentation:
- P3: `[63,1]`, cached token `3889`, KV boundary `63`;
- P1: `[43] + 31x[1]`, branch tokens `[1674,52245,9935,11,1187]`, KV boundary `74`;
- P2: `[57] + 15x[1]`, branch tokens `[30130,84]`, KV boundary `72`.

Exact expected=observed final-logit raw-float32 SHA-256:
- P1 `c3d4987ef17e295ea2a396c60e8dfb273100455059d9e829f4ef75637081c202`;
- P2 `65339a7fd91a8ef7f4cc36a36e897c3fed788cbb57466839b4b8ec3582a50a05`;
- P3 `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

All selected states pass exact IDs, frozen base taps, KV boundaries/offsets, selector `[0,-1]`, `float32 [151936]`, final SHA, finite/no-leak gates.

Unchanged DFlash baseline is restored:
- P1 rank `3`, proposal `3100`;
- P2 rank `3`, proposal `4057`;
- P3 rank `2`, proposal `5416`.

Execution isolation: zero BF16 target forwards, zero network bytes/requests, zero downloads and zero E2E.

Remote-reproducible repair source is committed at:
`8a74c3a2f039a771b4f1a682cc1754e48c76e50e`.

Source identities:
- `scripts/loom_dflash_q4_baseline_replay_shared_001.py` — SHA-256 `6da9e920f24e3c66ac8d37056d13e544dc70194b1d83987a5875db54590e1ea0`, Git blob `f75771e99ca8e604521094ed494422409e31e65c`;
- `scripts/loom_dflash_representable_bf16_target_causal_pilot_001.py` — SHA-256 `2882a8168612d1a3b6d0151b1b4511d21a51c0ba90b209f145f2fd3cc64a5e2b`, Git blob `3e3639749078c6ef60b25846a6df8d1ce4a4f48f`.

The Q4 provenance blocker is CLOSED.

## Exact next step

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002`

Purpose:
Re-attempt the original causal question after a purely mechanical Q4 baseline producer repair: does replacing exact Q4 verifier states with pinned BF16 verifier states materially recover DFlash compatibility?

The scientific contract is unchanged:
- same P3 -> P1 -> P2 states/order;
- same frozen targets;
- same exact Q4 baseline gates;
- same pinned BF16 revision;
- same DFlash implementation/mapping;
- same `8 GiB / 1,024 request` aggregate cap;
- same preregistered decision classifications.

Before each BF16 state, exact segmented Q4 replay must PASS. BF16 evidence must preserve taps, verifier logits/top1, routing, network/cache ledger, DFlash full-32k distribution and both frozen-Q4/BF16 labels.

No E2E, retraining, remapping, state substitution, tolerance relaxation or unrelated optimization.
