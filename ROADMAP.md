# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001_BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`
Strategic next: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.13.

## Stable DFlash chain

Still valid:
- target taps `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility baseline:
- frozen `50/63` representable, `13/63` unsupported;
- corrected exact top1 `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` remains invalid current acceptance evidence because it used old decode semantics.

## Closed hypotheses

- temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT` across full `-7..+7`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap interface: static 16/16 PASS, no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Do not revisit without new evidence.

## Representable BF16 target path

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected deterministic states:
- P1 `P1_t32:6`, baseline rank 3, frozen target 326, 79-token prefix;
- P2 `P2_t16:3`, baseline rank 3, frozen target 994, 74-token prefix;
- P3 `P3_t01:2`, baseline rank 2, frozen target 1620, 64-token prefix.

No compute sharing across prompt trajectories.

Cache state:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- total cache `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route planning estimate: 703 unique misses / `6,634,340,352 B`.

BF16 routing may diverge, so actual misses remain unknown until execution.

## BF16 network-cap guard — complete

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Validated behavior:
- 6/6 synthetic tests PASS; compile PASS;
- exact-boundary allow;
- byte/request overflow rejected before HTTPS dispatch;
- deterministic `NETWORK_CAP_ABORT`;
- retries counted and bounded;
- cache hits zero network cost;
- abort preserves partial/complete cache and resumability;
- zero real network dispatches during validation.

## Remote source parity — complete

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-source-payload-handoff-001-result.md`

Received archive:
- bytes `30,095`;
- SHA-256 `0c8fc52938c1be5642b8ca4abc1ba25944e8d44ff78fe038048ede19f433be2e`;
- exactly three validated guard source files.

User commit `01a5f9b` placed those exact files on the branch. Direct remote Git blob identities match `git hash-object` of the received payload:
- range control: `00287bc793fce8b552c55b8706a2d7f4d69be08e`;
- BF16 tap probe: `b2366c1c78b960e0bba224a3eb2da8efe92e7bfc`;
- guard test: `8ded2333d8007abec857d20b82e891b961add69b`.

The remote/fresh-clone reproducibility gate is CLOSED.

## Next — representable BF16 causal pilot

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

Purpose:
Test the remaining material hypothesis: verifier-state precision/distribution (Q4 vs pinned BF16) causes the residual DFlash mismatch on representable targets.

Fixed state set is unchanged. Execution order is frozen from ascending preflight-estimated network exposure:
1. P3 `P3_t01:2`;
2. P1 `P1_t32:6`;
3. P2 `P2_t16:3`.

Hard aggregate limits:
- `8 GiB` network bytes;
- `1,024` requests including retries;
- reject before dispatch with `NETWORK_CAP_ABORT`;
- retain persistent cache and completed partial evidence.

Required per-state sequence:
1. Q4 baseline replay/provenance gate;
2. pinned BF16 teacher-forced verifier to the selected state only;
3. retain BF16 taps `[1,12,23,34,45]`, verifier final logits/top1, routing and network/cache ledger;
4. compute layerwise Q4-vs-BF16 tap movement;
5. unchanged DFlash forward on Q4 taps and BF16 taps with IDs/positions/masks/tap order/weights/mapping frozen;
6. compare full 32k DFlash movement and proposal;
7. preserve both labels: frozen Q4 target token and BF16 verifier top1 token;
8. compare DFlash rank/top5/top10/top50/top100/top1 for each representable label.

Preregistered outcomes:
- `BF16_TARGET_RECOVERY_SIGNAL`: >=2 selected states produce BF16-tap DFlash top1 equal to the representable BF16 verifier top1, while corresponding Q4-tap condition is not exact;
- `NO_USEFUL_BF16_TARGET_RECOVERY`: zero exact BF16-label recoveries and no broad decision-level/top-k improvement;
- `BF16_TARGET_EFFECT_AMBIGUOUS`: exactly one exact recovery, label/support ambiguity, or consistent non-top1 movement insufficient for the recovery criterion;
- `BF16_TARGET_PILOT_NETWORK_CAP_ABORT`: hard cap stops full completion; no inference for unexecuted states.

Q4 baseline failure invalidates the pilot and must STOP without rescue or state replacement.

## Decision after pilot

- broad recovery signal -> continue DFlash salvage only along the isolated BF16 verifier-state mechanism;
- no useful recovery -> explicitly reassess/terminate DFlash salvage before corrected E2E and return to LOOM's higher-leverage 30B-on-8GB serving/I/O path;
- ambiguous -> record only; no post-hoc rescue or candidate/state substitution.

No corrected E2E until a real compatibility/acceptance mechanism exists.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only active delta. Pi executes local work; ChatGPT owns scientific/Git state.
