# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001_Q4_BASELINE_SEGMENTATION_REPAIR_PASS`
Strategic next: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.16.

## Stable DFlash chain

Still valid:
- target taps `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete `680,813,824`-param BF16 drafter port;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- correct mapping `target_id = draft_row + d2t[draft_row]`;
- frozen support `50/63` representable and `13/63` unsupported;
- corrected DFlash top1 `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` is not current acceptance evidence because it used old decode semantics.

Closed explanations:
- temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap interface: `16/16` PASS with no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

## BF16 infrastructure — COMPLETE

Pinned verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Network guard:
`BF16_NETWORK_CAP_GUARD_PASS` with exact remote source parity.

Frozen causal states/order:
1. P3 `P3_t01:2` — target `1620`, baseline rank `2`;
2. P1 `P1_t32:6` — target `326`, rank `3`;
3. P2 `P2_t16:3` — target `994`, rank `3`.

Hard aggregate limits:
- `8 GiB` network bytes;
- `1,024` requests including retries;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache;
- no state substitution/reordering.

## First causal attempt — INVALID BEFORE INTERVENTION

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` stopped before any BF16/network execution because the Q4 P3 baseline used a different producer segmentation than the frozen continuation reference.

Administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

No BF16 scientific conclusion is valid from attempt 001.

## Q4 provenance diagnosis — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001` = `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`.

The mismatch was deterministic segmentation/KV-boundary drift, not serialization/hash semantics. This established producer segmentation as part of exact continuation-state provenance.

## Q4 segmentation replay repair — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001` = `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`.

Report:
`research/architecture/loom-dflash-q4-baseline-segmentation-replay-repair-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-segmentation-replay-repair-001/20260825T132255Z/`

Recovered exact segmentation:
- P3 `[63,1]`, token `3889`, boundary `63`;
- P1 `[43] + 31x[1]`, branch `[1674,52245,9935,11,1187]`, boundary `74`;
- P2 `[57] + 15x[1]`, branch `[30130,84]`, boundary `72`.

Exact final-logit raw-float32 SHA restoration:
- P1 `c3d4987ef17e295ea2a396c60e8dfb273100455059d9e829f4ef75637081c202`;
- P2 `65339a7fd91a8ef7f4cc36a36e897c3fed788cbb57466839b4b8ec3582a50a05`;
- P3 `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

All three exact Q4 provenance gates pass. Unchanged DFlash recovers ranks/proposals:
- P1 rank `3`, proposal `3100`;
- P2 rank `3`, proposal `4057`;
- P3 rank `2`, proposal `5416`.

Zero BF16/network/E2E occurred during repair.

Remote-reproducible source commit:
`8a74c3a2f039a771b4f1a682cc1754e48c76e50e`.

## Next — causal BF16 re-attempt

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002`

Purpose:
Answer the remaining material question: are the residual DFlash mismatches caused primarily by verifier-state precision/distribution differences between the exact Q4 target and the pinned BF16 target?

Pilot 002 is not a new scientific treatment. It repeats the preregistered pilot 001 after a mechanical baseline-producer repair, with every scientific degree of freedom frozen:
- same states;
- same order;
- same labels;
- same DFlash code/mapping;
- same pinned BF16 verifier;
- same network cap;
- same decision thresholds.

Required per state:
1. exact segmented Q4 baseline provenance PASS;
2. pinned BF16 teacher-forced verifier at the same logical state;
3. retain taps `[1,12,23,34,45]`, final verifier logits/top1, routing and network/cache ledger;
4. run unchanged DFlash on Q4 and BF16 taps;
5. compare layerwise tap drift and full 32k DFlash drift/proposal;
6. preserve both frozen-Q4 and BF16 verifier labels and report DFlash ranks/top-k/top1 for each representable label.

Preregistered outcomes:
- `BF16_TARGET_RECOVERY_SIGNAL`: at least 2 states have BF16-tap DFlash top1 equal to representable BF16 verifier top1 while corresponding Q4-tap condition is not exact;
- `NO_USEFUL_BF16_TARGET_RECOVERY`: zero exact BF16-label recoveries and no broad decision-level/top-k improvement;
- `BF16_TARGET_EFFECT_AMBIGUOUS`: exactly one exact recovery, support/label ambiguity, or systematic movement insufficient for the recovery gate;
- `BF16_TARGET_PILOT_NETWORK_CAP_ABORT`: hard cap stops completion; do not infer unexecuted states.

## Decision after pilot 002

- recovery signal -> continue DFlash salvage only along the isolated BF16-state mechanism;
- no useful recovery -> explicitly reassess/terminate DFlash salvage before corrected E2E and return to higher-leverage 30B-on-8GB serving/I/O work;
- ambiguous -> record only, no post-hoc rescue;
- network-cap abort -> retain partial evidence and reassess feasibility without changing the scientific state set.

No corrected E2E until a real compatibility/acceptance mechanism exists.
