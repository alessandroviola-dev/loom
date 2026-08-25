# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002_BF16_TARGET_PILOT_NETWORK_CAP_ABORT_WITH_INTERPRETATION_HELD`
Strategic next: `LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.17.

## Stable DFlash chain

Still valid:
- target taps `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete `680,813,824`-param BF16 drafter port;
- publisher mask repair;
- deterministic finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- mapping `target_id = draft_row + d2t[draft_row]`;
- support `50/63` representable, `13/63` unsupported;
- corrected DFlash exact top1 `0/63`;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Closed explanations remain closed: temporal alignment, MLX drafter implementation, static verifier/tap interface, tap-transport dtype.

## BF16 infrastructure

Pinned verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Network guard and remote guard-source parity are complete.

Frozen causal states/order:
1. P3 `P3_t01:2` — target `1620`, exact Q4 rank `2`;
2. P1 `P1_t32:6` — target `326`, rank `3`;
3. P2 `P2_t16:3` — target `994`, rank `3`.

No substitutions/reordering.

## Q4 segmentation repair — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001` = `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`.

Exact segmented producer and final-logit SHA commitments reproduce for all three states. DFlash baselines restore exactly:
- P3 rank `2`, proposal `5416`;
- P1 rank `3`, proposal `3100`;
- P2 rank `3`, proposal `4057`.

The Q4 baseline blocker is closed.

## BF16 causal pilot 002 — OPERATIONAL CAP ABORT

Reported classification:
`BF16_TARGET_PILOT_NETWORK_CAP_ABORT`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-002-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-002/20260825T134150Z/`

Operational outcome:
- P3 BF16 completed;
- P1 Q4 baseline passed, then BF16 cap-aborted;
- P2 unexecuted;
- network `8,583,061,312 B`, `1,007` requests, `7` retries;
- next `9,437,184 B` request blocked before dispatch;
- cache `20,832` hits / `898` misses.

The guard worked and cache growth can be reused later.

## Scientific validity hold

Do not yet interpret reported P3 `rank 5 -> 13` as BF16 harm/non-recovery.

The exact repaired P3 Q4 condition is rank `2`, proposal `5416`, while pilot 002 reports Q4-tap rank `5`, proposal `4330`. Review of remote predecessor source reveals likely confounders:
- Q4 paired scoring may receive `full_taps` instead of frozen `base_taps`;
- DFlash scoring uses a fixed row instead of the selected continuation-position row;
- BF16 treatment uses fresh full-prefix execution rather than the same segmented/KV-boundary state producer.

The exact executed `_002.py` is not yet remote-reproducible, so causal interpretation is withheld pending a byte-exact offline audit.

## Next — pilot 002 causal validity audit

Checkpoint:
`LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001`

Purpose:
Determine whether the completed P3 evidence from pilot 002 actually isolates Q4-vs-BF16 precision/distribution or is mechanically confounded by tap provenance, DFlash row selection, and/or producer segmentation.

Strictly offline:
1. hash the exact executed `_002.py` source;
2. compare `_002` with remote `_001` for causal-relevant differences;
3. trace exact Q4 and BF16 tap tensors passed to DFlash;
4. identify the correct DFlash continuation row for P3 position `2` and recompute Q4 scoring from existing arrays only;
5. require exact frozen Q4 rank `2`/proposal `5416` when correct inputs/selectors are used;
6. determine whether existing P3 BF16 taps/logits were generated with fresh full-prefix or frozen-equivalent segmented/KV-boundary execution;
7. use existing artifacts only; no BF16 forward and no network;
8. classify existing P3 evidence as valid, mechanically invalid, or ambiguous.

Outcomes:
- `PILOT_002_CAUSAL_PATH_VALID` -> existing P3 evidence can contribute to later bounded continuation;
- `PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL` -> repair and validate source offline, then preregister a new attempt using persistent cache;
- `PILOT_002_CAUSAL_VALIDITY_AMBIGUOUS` -> no new treatment until ambiguity is closed.

No conclusion on DFlash salvage/termination until causal validity is established.