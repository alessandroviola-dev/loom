# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — BF16 network cap guard source export PASS and exact local source identities are pinned; remote source parity is still blocked because the exported full file bytes remain only on the user's local filesystem and were not included in the chat payload
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001_BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_PASS`
Next core checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.12.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility baseline:
- frozen 50/63 representable, 13/63 unsupported;
- corrected exact top1 0/63;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Closed leading explanations:
- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static contract: 16/16 PASS, no material mismatch demonstrated;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Historical E2E `0/96` used old decode semantics and is not current acceptance evidence.

## Representable BF16 causal pilot

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected states:
- P1 `P1_t32:6`, rank 3, frozen target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, frozen target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, frozen target 1620, 64-token prefix.

No compute sharing across trajectories.

BF16 cache:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- 0 integrity failures;
- total `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route planning estimate: 703 unique misses / `6,634,340,352 B`.

Pilot hard ceilings after source parity:
- network `8 GiB`;
- requests `1,024`;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache.

## BF16 network-cap guard

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-001/20260825T121354Z/`

Validation:
- 6/6 synthetic tests PASS; compile PASS;
- exact-boundary allow;
- byte/request rejects before HTTPS dispatch;
- deterministic `NETWORK_CAP_ABORT`;
- retries counted and bounded;
- cache hits `0 B / 0 requests`;
- abort preserves complete/partial cache and resumability;
- real network dispatches observed 0.

## Source export — COMPLETE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001` = `BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-source-sync-001-result.md`

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-source-sync-001/20260825T122613Z/`

Export method: `FULL_CONTENT` UTF-8 copies.

Exact validated local source identities:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py` — 74,261 B — `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py` — 26,443 B — `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py` — 11,741 B — `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae`.

All exported copies byte-match the locally validated sources and prior hashes.

## Exact remaining reproducibility blocker

The full exported file contents live only under the user's local evidence directory and were not included in the chat message. ChatGPT cannot access that local filesystem and cannot reconstruct bytes from SHA-256 values.

Therefore:
- local guard behavior is validated;
- exact source identity is pinned;
- branch/fresh-clone source parity remains unestablished;
- expensive BF16 target pilot remains blocked only on exact source payload transfer.

## Exact next step

Checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001`

Pi must make no source changes and no Git calls. Package the three already-exported UTF-8 files into one deterministic payload/artifact and expose it so the user can attach or paste it into ChatGPT. Include payload SHA-256 and the three per-file hashes above.

Once ChatGPT receives the actual bytes, it will write the three files to GitHub, verify remote file identities, update docs, and authorize the preregistered BF16 pilot.

No target/BF16 forward, downloads, E2E, retraining/remapping or unrelated optimization during payload handoff.

## Later pilot measurement rule

For each selected state preserve both:
1. frozen Q4 target token;
2. BF16 verifier top1 token at the same state.

Compare DFlash under Q4 vs BF16 taps against both labels when representable, retaining target taps/logits, routing, DFlash 32k logits, ranks/top-k/top1 and network/cache ledgers.
