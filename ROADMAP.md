# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001_BF16_NETWORK_CAP_GUARD_PASS`
Strategic next: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.11.

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
- frozen 50/63 representable, 13/63 unsupported;
- corrected exact top1 0/63;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` remains invalid as current acceptance evidence because it used old decode semantics.

## Closed hypotheses

- temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT` across full `-7..+7`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap interface: static 16/16 PASS, no material mismatch demonstrated;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

## Representable BF16 target path

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected states:
- P1 `P1_t32:6`, rank 3, target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, target 1620, 64-token prefix.

Cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- total cache 35,837,957,463 B;
- free external disk 1,152.25 GiB;
- Q4-route planning estimate: 703 unique misses / 6,634,340,352 B.

BF16 routing may diverge, so actual future misses are unknown until execution.

## Completed — BF16 network-cap guard

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-001-result.md`

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-001/20260825T121354Z/`

Validated local behavior:
- 6/6 synthetic tests PASS; compile PASS;
- exact-boundary request allowed;
- byte/request overflow rejected before HTTPS dispatch;
- deterministic `NETWORK_CAP_ABORT`;
- retries explicitly charged and bounded;
- cache hits cost 0 B / 0 requests;
- abort preserves valid complete/partial cache and resumability;
- zero real network dispatches during validation.

Validated local files:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py`.

## Immediate reproducibility gate — source sync

The validated guard source delta is still local-only. The branch result documents know that the guard passed, but the branch does not yet contain the exact implementation.

Next checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001`

Purpose:
- export exact local contents/complete patches without Git or behavior change;
- include SHA-256 for each validated file;
- ChatGPT applies exact source to branch;
- verify remote parity before expensive execution.

This gate is mechanical but mandatory for reproducibility.

## After exact source sync

Authorize one bounded representable-state Q4-vs-BF16 target causal pilot under:
- hard network ceiling `8 GiB`;
- hard request ceiling `1,024`;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache;
- distinct fresh KV trajectory per P1/P2/P3.

Measure for each selected state:
- Q4-vs-BF16 target tap drift;
- target final-logit/top1 drift;
- DFlash full-32k movement;
- frozen-Q4-target rank/top5/top10/top50/top100/top1;
- BF16 verifier top1 token and its DFlash rank/top-k/top1 when representable;
- routing and network/cache ledger.

Preserving both the frozen Q4 target token and BF16 verifier top1 avoids confusing hidden-state precision effects with a changed verifier label.

Decision after pilot:
- broad representable-target recovery -> continue DFlash salvage with the isolated mechanism;
- no useful recovery -> explicitly reassess/terminate DFlash salvage before corrected E2E and return to LOOM's higher-leverage 30B-on-8GB serving/I/O work;
- mixed/label-changing evidence -> classify ambiguous, no post-hoc rescue.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only active delta. Pi executes local work; ChatGPT owns scientific/Git state.
