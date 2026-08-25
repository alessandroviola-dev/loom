# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001_BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`
Strategic next: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.10.

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

Support / compatibility:
- frozen 50/63 representable, 13/63 unsupported;
- corrected exact top1 0/63;
- representable target ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` remains invalid as current acceptance evidence because it used the old decode.

## Closed hypotheses

- Temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT` across full `-7..+7`.
- MLX port: `FULL_LOGIT_REFERENCE_PARITY_PASS` on stratified states.
- Verifier/tap static contract: 16/16 PASS with no material mismatch demonstrated.
- Tap transport BF16 sensitivity: `NO_MATERIAL_TAP_DTYPE_EFFECT`, proposal changes 0/63, no top-k crossings.

## BF16 target context

Available pinned BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Prior P1_t01 BF16 intervention proved that target precision can materially move hidden states and DFlash logits, but P1_t01 is outside DFlash support and cannot measure exact proposal recovery.

## Completed — representable BF16 target pilot preflight

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

Classification:
`BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`

Report:
`research/architecture/loom-dflash-representable-bf16-target-control-preflight-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z/`

Selected deterministic states:
- P1 `P1_t32:6`, rank 3, target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, target 1620, 64-token prefix.

Cache state:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- 0 integrity failures;
- total BF16 cache `35,837,957,463 B`;
- external disk free `1,152.25 GiB`.

Q4-trace planning estimate only:
- combined unique cache hits 2,325;
- combined unique misses 703;
- estimated missing bytes `6,634,340,352 B`.

BF16 routing may differ, so exact future miss count is unknown before execution.

The on-demand BF16 cache is atomic and resumable, but currently lacks a hard **pre-dispatch** byte/request guard.

## Next — BF16 network-cap guard

Checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`

Purpose:
Make the later expensive causal pilot safely bounded before any new target/network execution.

Mechanical scope:
1. add explicit cumulative byte and request caps to the shared BF16 fetch/cache path;
2. preflight every network dispatch and reject if the proposed request would exceed either cap;
3. emit deterministic `NETWORK_CAP_ABORT` with ledger/cost/cap evidence;
4. cache hits cost zero;
5. retries are explicitly counted and bounded;
6. successful requests update accounting exactly once;
7. abort preserves valid persistent partial cache and resumability;
8. validate locally with synthetic tests only.

Required tests:
- exact-boundary allow;
- byte-cap reject before dispatch;
- request-cap reject before dispatch;
- cache-hit zero cost;
- retry accounting;
- resume/partial-cache preservation.

No real network or target execution is authorized in this checkpoint.

## After guard PASS

Authorize one preregistered 3-state Q4-target vs BF16-target causal pilot:
- P1_t32:6;
- P2_t16:3;
- P3_t01:2;
- separate fresh KV trajectory per prompt;
- hard network ceiling `8 GiB`;
- hard request ceiling `1,024`;
- clean pre-dispatch abort;
- persistent/resumable cache.

Compare:
- layerwise target-tap drift;
- DFlash full-32k movement;
- corrected target rank;
- top5/top10/top50/top100;
- exact target top1.

If BF16 produces no useful representable-target recovery signal, explicitly reassess/terminate DFlash salvage before any corrected E2E and return to LOOM's higher-leverage 30B-on-8GB serving/I/O path.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
