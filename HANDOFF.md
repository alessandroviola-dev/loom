# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — pilot 002 hit the network cap after P3, but the P3 causal interpretation is withheld because the reported Q4-tap rank conflicts with the exact repaired baseline and the remote predecessor source contains likely scoring/segmentation confounders.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002_BF16_TARGET_PILOT_NETWORK_CAP_ABORT_WITH_INTERPRETATION_HELD`
Next core checkpoint: `LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent Pi context: `/AGENTS.md` v3.17.

## Stable DFlash state

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

Stable compatibility baseline:
- `50/63` frozen target tokens representable, `13/63` unsupported;
- corrected DFlash exact top1 `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Closed leading explanations remain closed:
- temporal shift;
- MLX drafter implementation;
- static verifier/tap interface;
- tap transport dtype.

## Exact Q4 baseline — CLOSED/PASS

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001` = `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`.

Exact frozen states:
- P3 `P3_t01:2`: segmentation `[63,1]`, target `1620`, rank `2`, proposal `5416`;
- P1 `P1_t32:6`: `[43] + 31x[1]` then branch `[1674,52245,9935,11,1187]`, target `326`, rank `3`, proposal `3100`;
- P2 `P2_t16:3`: `[57] + 15x[1]` then branch `[30130,84]`, target `994`, rank `3`, proposal `4057`.

All final-logit SHA commitments reproduce exactly. Repair source is remote-reproducible at commit `8a74c3a2f039a771b4f1a682cc1754e48c76e50e`.

## BF16 pilot 002 — cap abort, interpretation held

Operational classification reported:
`BF16_TARGET_PILOT_NETWORK_CAP_ABORT`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-002-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-002/20260825T134150Z/`

Execution:
- P3 BF16 completed;
- P1 exact Q4 baseline passed, BF16 then hit cap;
- P2 unexecuted.

Cap accounting:
- `8,583,061,312 B` (`7.994 GiB`);
- `1,007` requests;
- `7` retries;
- `20,832` cache hits / `898` misses;
- next `9,437,184 B` request rejected before dispatch.

The guard worked correctly and the persistent cache gained useful material.

Reported P3:
- BF16 verifier top1 `1620`, representable;
- tap drift exists;
- DFlash proposal reported `4330 -> 2790`;
- label `1620` reported rank `5 -> 13`;
- no exact recovery reported.

These P3 treatment numbers are NOT yet accepted as causal evidence.

Reason:
- exact repaired P3 Q4 baseline is rank `2`/proposal `5416`, but pilot reports rank `5`/proposal `4330` for its Q4-tap condition;
- review of remote predecessor `scripts/loom_dflash_representable_bf16_target_causal_pilot_001.py` shows three likely confounders: shared replay returns `full_taps` while frozen scoring uses `base_taps`; DFlash row is hardcoded `[0,1]`; BF16 helper uses a fresh full-prefix forward rather than frozen-equivalent segmentation/KV boundary.

The exact executed `_002.py` source is local-only and must be audited byte-exactly before scientific interpretation.

## Exact next step

Checkpoint:
`LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001`

Strictly offline. No BF16 forward and no network.

Audit exact `_002.py`, compare with remote `_001`, trace Q4/BF16 tap provenance and DFlash row selection, recompute P3 Q4 scoring from existing arrays only, and decide whether existing P3 BF16 artifacts are causally valid or treatment-confounded.

Classifications:
- `PILOT_002_CAUSAL_PATH_VALID`;
- `PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL`;
- `PILOT_002_CAUSAL_VALIDITY_AMBIGUOUS`.

If invalid, repair/validate the pilot source offline before any new network attempt. Do not conclude that BF16 helps or hurts DFlash from pilot 002 until this audit closes.