# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — BF16 network-cap guard is validated and exact remote source parity is established; the final reproducibility blocker is closed and the next checkpoint is the bounded 3-state representable Q4-vs-BF16 causal pilot
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001_BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`
Next core checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.13.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Correct publisher mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility baseline:
- frozen `50/63` target tokens representable, `13/63` unsupported;
- corrected exact top1 remains `0/63`;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` used old decode semantics and is not current acceptance evidence.

Closed leading explanations:
- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static contract: 16/16 PASS, no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Do not reopen these without new evidence.

## Representable BF16 causal path

Pinned available BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected deterministic near-target states:
- P1 `P1_t32:6`, baseline rank 3, frozen Q4 target 326, 79-token prefix;
- P2 `P2_t16:3`, baseline rank 3, frozen Q4 target 994, 74-token prefix;
- P3 `P3_t01:2`, baseline rank 2, frozen Q4 target 1620, 64-token prefix.

No compute sharing across trajectories; fresh KV state per prompt.

BF16 cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections SHA-256 verified;
- integrity failures 0;
- total cache `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route planning estimate: 703 combined unique misses / `6,634,340,352 B` missing.

Actual BF16 routing can diverge.

## BF16 network cap guard — COMPLETE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Validation:
- 6/6 synthetic tests PASS; compile PASS;
- exact-boundary allow;
- byte/request rejects before HTTPS dispatch;
- deterministic `NETWORK_CAP_ABORT`;
- retries explicitly counted and bounded;
- cache hits `0 B / 0 requests`;
- abort preserves complete/partial cache and resumability;
- zero real network dispatches during validation.

## Exact remote source parity — COMPLETE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-source-payload-handoff-001-result.md`

Received payload:
- archive bytes `30,095`;
- archive SHA-256 `0c8fc52938c1be5642b8ca4abc1ba25944e8d44ff78fe038048ede19f433be2e`;
- exactly three preregistered files.

Validated source identities now present on the remote branch via user commit `01a5f9b`:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py` — 74,261 B — SHA-256 `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376` — Git blob `00287bc793fce8b552c55b8706a2d7f4d69be08e`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py` — 26,443 B — SHA-256 `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f` — Git blob `b2366c1c78b960e0bba224a3eb2da8efe92e7bfc`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py` — 11,741 B — SHA-256 `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae` — Git blob `8ded2333d8007abec857d20b82e891b961add69b`.

GitHub blob identities exactly match `git hash-object` computed from the received validated payload. No reconstruction or source modification occurred.

The former local-only/fresh-clone reproducibility blocker is CLOSED.

## Exact next step

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

Purpose:
Test whether Q4-vs-BF16 verifier state precision/distribution is the material cause of the residual DFlash mismatch on representable targets.

Fixed execution order from ascending preflight-estimated network exposure:
1. P3 `P3_t01:2`;
2. P1 `P1_t32:6`;
3. P2 `P2_t16:3`.

Hard aggregate ceilings across the full pilot:
- network `8 GiB`;
- requests `1,024`, retries included;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache and partial completed-state evidence retained.

For each selected state:
1. reproduce/validate Q4 baseline first;
2. teacher-force the pinned BF16 verifier only to the selected prefix/state;
3. retain BF16 taps, verifier final logits/top1, routing and network/cache ledger;
4. compare layerwise Q4-vs-BF16 taps;
5. run unchanged DFlash on Q4 and BF16 taps with all other inputs frozen;
6. compare full 32k DFlash distributions and proposal changes;
7. preserve both labels: frozen Q4 target token and BF16 verifier top1;
8. report DFlash rank/top5/top10/top50/top100/top1 for both labels when representable.

Preregistered classification:
- `BF16_TARGET_RECOVERY_SIGNAL`: >=2 selected states have BF16-tap DFlash top1 equal to representable BF16 verifier top1, while corresponding Q4-tap condition is not exact;
- `NO_USEFUL_BF16_TARGET_RECOVERY`: zero exact BF16-label recoveries and no broad decision-level/top-k improvement;
- `BF16_TARGET_EFFECT_AMBIGUOUS`: exactly one exact recovery, support/label ambiguity, or systematic movement insufficient for the recovery gate;
- `BF16_TARGET_PILOT_NETWORK_CAP_ABORT`: hard cap prevents full completion; retain partial evidence and do not infer missing states.

If Q4 baseline replay/provenance fails, STOP as invalid pilot. No post-hoc state replacement or rescue.

No E2E, retraining, remapping or unrelated performance optimization in this checkpoint.
