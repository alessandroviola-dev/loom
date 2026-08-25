# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001_BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_PASS`
Strategic next: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.12.

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

Historical E2E `0/96` remains invalid current acceptance evidence because it used old decode semantics.

## Closed hypotheses

- temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT` across full `-7..+7`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap interface: static 16/16 PASS, no material mismatch demonstrated;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

## Representable BF16 target path

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected deterministic states:
- P1 `P1_t32:6`, rank 3, target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, target 1620, 64-token prefix.

Cache state:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- total cache `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route planning estimate: 703 unique misses / `6,634,340,352 B`.

BF16 routing may diverge, so actual misses remain unknown until execution.

## BF16 network-cap guard — validated

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Behavior:
- 6/6 synthetic tests PASS;
- exact-boundary allow;
- byte/request overflow rejected before HTTPS dispatch;
- deterministic `NETWORK_CAP_ABORT`;
- retries counted and bounded;
- cache hits zero network cost;
- abort preserves partial/complete cache and resumability;
- zero real network dispatches in validation.

## Completed — exact source export

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001` = `BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-source-sync-001-result.md`

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-source-sync-001/20260825T122613Z/`

Export method: full UTF-8 contents.

Pinned local source identities:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py` — 74,261 B — SHA-256 `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py` — 26,443 B — SHA-256 `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py` — 11,741 B — SHA-256 `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae`.

The local exported copies byte-match the validated state.

## Immediate reproducibility gate — payload handoff

The source export exists on the user's Mac, but its full bytes were not included in the chat payload. ChatGPT cannot access the local evidence directory directly and hashes cannot reconstruct source.

Next checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001`

Purpose:
- package the already-exported exact files without modifying them;
- produce one deterministic payload/artifact accessible to ChatGPT;
- include payload SHA-256 and per-file SHA-256;
- ChatGPT writes exact files to branch and verifies remote content identities.

This is a mechanical transfer gate only. No scientific change is permitted.

## After remote source parity

Authorize one bounded representable-state Q4-vs-BF16 target causal pilot:
- P1_t32:6;
- P2_t16:3;
- P3_t01:2;
- separate fresh KV trajectory per prompt;
- hard network ceiling `8 GiB`;
- hard request ceiling `1,024`;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache.

Measure:
- Q4-vs-BF16 target tap drift;
- target final-logit/top1 drift;
- DFlash full-32k movement;
- frozen-Q4-target rank/top5/top10/top50/top100/top1;
- BF16 verifier top1 and its DFlash rank/top-k/top1 when representable;
- routing/network/cache ledger.

Decision after pilot:
- broad representable-target recovery -> continue DFlash salvage only on isolated mechanism;
- no useful recovery -> explicitly reassess/terminate DFlash salvage before corrected E2E and return to higher-leverage 30B-on-8GB serving/I/O work;
- mixed/label-changing evidence -> classify ambiguous; no post-hoc rescue.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only active delta. Pi executes local work; ChatGPT owns scientific/Git state.
