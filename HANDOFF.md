# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — BF16 network cap guard behavior PASS locally; expensive representable-state BF16 pilot is scientifically ready but exact validated guard source remains local-only and must be synchronized to GitHub before remote reproducibility/pilot authorization
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001_BF16_NETWORK_CAP_GUARD_PASS`
Next core checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.11.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Validated chain:
- exact target-tap implementation;
- exact B7 wavefront verifier;
- 680,813,824 learned BF16 drafter params mapped;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state continuation SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility:
- 50/63 frozen targets representable;
- 13/63 unsupported;
- exact corrected top1 0/63;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` is contaminated by old decode and not current acceptance evidence.

## Closed leading explanations

- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT` across `-7..+7`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static contract: `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`, 16/16 PASS;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`, 0/63 proposal changes.

Do not reopen without new evidence.

## Representable BF16 target pilot preflight

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-control-preflight-001-result.md`

Selected states:
- P1 `P1_t32:6`, rank 3, frozen target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, frozen target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, frozen target 1620, 64-token prefix.

No compute sharing across prompt trajectories.

BF16 cache:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- 0 integrity failures;
- total 35,837,957,463 B;
- free external disk 1,152.25 GiB.

Q4-route planning estimate only:
- combined unique missing experts 703;
- estimated missing bytes 6,634,340,352 B;
- exact BF16 misses may differ because BF16 routing can diverge.

Pilot hard ceilings:
- network `8 GiB`;
- requests `1,024`;
- `NETWORK_CAP_ABORT` before dispatch.

## BF16 network cap guard — PASS locally

Checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`

Classification:
`BF16_NETWORK_CAP_GUARD_PASS`

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-001-result.md`

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-001/20260825T121354Z/`

Local files changed by Pi:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py`.

Validation:
- 6/6 synthetic tests PASS; compile PASS;
- exact-boundary allow PASS;
- byte and request rejection occurs before HTTPS dispatch;
- deterministic `NETWORK_CAP_ABORT`;
- retries explicitly counted and bounded;
- cache hits 0 B / 0 requests;
- abort preserves complete/partial cache and resumability;
- observed real network dispatches 0.

## Reproducibility blocker

The exact guard implementation is currently present only in the user's local working tree. Those three script changes have not yet been written to the GitHub branch because Pi cannot use Git and ChatGPT cannot directly read local working-tree files.

Therefore:
- same-machine local guard behavior is validated;
- remote/fresh-clone source parity is NOT yet established;
- do not authorize the expensive BF16 pilot until exact source synchronization is complete.

## Exact next step

Checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001`

Pi must make no code changes and no Git calls. Export exact full contents or complete deterministic patches for the three validated files plus SHA-256 for each. ChatGPT will apply the exact local implementation to GitHub, verify remote content, update docs, then authorize the expensive pilot.

No target/BF16 forward, downloads, E2E, retraining/remapping or unrelated optimization in source sync.

## Later BF16 pilot measurement rule

For each selected state preserve and report both:
1. frozen Q4 target token;
2. BF16 verifier top1 token at the same state.

Compare DFlash Q4-tap vs BF16-tap distributions against the frozen token and, if representable, the BF16 verifier top1. Also retain taps, target logits, routing, DFlash 32k logits, ranks/top-k/top1 and network/cache ledgers.
