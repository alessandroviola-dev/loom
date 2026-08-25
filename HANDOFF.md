# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — representable BF16 target pilot preflight is PASS with bounded missing cache; scientific pilot is ready in principle, but the current BF16 fetcher lacks pre-dispatch byte/request caps, so next checkpoint is a mechanical network-cap guard before any target execution
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001_BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`
Next core checkpoint: `LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.10. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

## Stable DFlash facts

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Still valid:
- exact target-tap implementation;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen target continuation SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

Frozen support:
- 50/63 representable;
- 13/63 unsupported;
- corrected exact top1 remains 0/63.

For 50 representable targets:
- rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`;
- top1 `0/50`.

Historical first E2E `0/96` is contaminated by the former direct-d2t decode and is not current acceptance evidence.

## Leading explanations already closed

- Temporal/off-by-N alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT` over full `-7..+7`.
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS` on 6 stratified states.
- Verifier/tap static interface: `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`, static contract 16/16 PASS.
- Tap transport float32-vs-BF16 round trip: `NO_MATERIAL_TAP_DTYPE_EFFECT`, proposal changes 0/63 and no top-k crossings.

Do not reopen these without new evidence.

## BF16 target context

Pinned available BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Earlier P1_t01 Q4->BF16 changed routing/taps/logits materially while target top1 stayed 12050, but P1_t01 is outside DFlash support. It cannot answer representable-target recovery.

Persistent BF16 cache remains reusable.

## Representable BF16 pilot preflight — COMPLETE

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

Classification:
`BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`

Report:
`research/architecture/loom-dflash-representable-bf16-target-control-preflight-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z/`

Selected one near-target representable state per prompt:
- P1 `P1_t32:6`, rank 3, target 326, verifier prefix 79 tokens;
- P2 `P2_t16:3`, rank 3, target 994, prefix 74 tokens;
- P3 `P3_t01:2`, rank 2, target 1620, prefix 64 tokens.

No compute sharing: distinct trajectories and fresh KV caches.

BF16 cache integrity:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified SHA-256;
- failures 0;
- dense 3,082,218,423 B;
- expert cache 32,755,649,797 B;
- total 35,837,957,463 B;
- external free disk 1,152.25 GiB.

Q4-routing cache estimate only; exact BF16 misses remain unknowable pre-execution:
- P1 1,942 hits / 315 misses / 2,972,712,960 B;
- P2 1,476 / 507 / 4,784,652,288 B;
- P3 371 / 13 / 122,683,392 B;
- combined unique 2,325 hits / 703 misses / 6,634,340,352 B.

Existing fetch/cache behavior:
- atomic persistent expert cache: YES;
- resumability: YES;
- preserves partial valid cache: YES;
- hard byte/request pre-dispatch guard: NO.

Proposed causal pilot after guard validation:
- selected P1/P2/P3 states above;
- Q4 baseline vs BF16 teacher-forced verifier states;
- hard network cap 8 GiB;
- hard request cap 1,024;
- `NETWORK_CAP_ABORT` before dispatch if next request would exceed either cap;
- retain taps, target logits, routing, DFlash 32k logits, rank/top-k/top1 and network/cache ledgers.

Decisive metrics:
- Q4-vs-BF16 tap drift;
- DFlash 32k movement;
- corrected target rank;
- top5/top10/top50/top100;
- exact DFlash target top1.

## Exact next step

Checkpoint:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`

Mechanical safety repair only.

Add a pre-dispatch byte/request budget guard to the shared on-demand BF16 fetch/cache path. It must reject the next request before dispatch if cumulative accounting would exceed either cap, count retries explicitly, charge cache hits zero, preserve persistent partial cache/resumability on abort, and emit deterministic `NETWORK_CAP_ABORT` ledger evidence.

Required local synthetic tests:
- exact boundary allowed;
- byte-cap reject before dispatch;
- request-cap reject before dispatch;
- cache-hit zero cost;
- retry accounting;
- resume/partial-cache preservation.

No real network, target/BF16 forward, E2E, retraining/remapping, unrelated performance work, Git or docs edits.

If guard PASS, next checkpoint may authorize the preregistered 3-state causal pilot under hard `8 GiB / 1,024 request` limits.
