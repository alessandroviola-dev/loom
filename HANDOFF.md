# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — verifier provenance/tap-interface static audit PASS with no demonstrated material mismatch; MLX drafter port, corrected mapping, temporal alignment and tap semantics are no longer leading explanations; next isolate tap-transport BF16 sensitivity before new target BF16 computation
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001_PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`
Next core checkpoint: `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.8. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

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

## Mapping correction — resolved

Correct publisher mapping:
`target_id = draft_row + d2t[draft_row]`.

True support:
- 32,000 unique valid target IDs;
- `50/63` frozen targets representable;
- `13/63` unsupported;
- corrected exact top1 remains `0/63`.

Historical first E2E `0/96` used contaminated decode and is not current acceptance evidence.

## Directional signal

For 50 representable targets:
- rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`, top10 `11/50`, top50 `19/50`, top100 `26/50`;
- top1 `0/50`.

The drafter is not random/unrelated; it carries substantial target signal.

## Temporal alignment — closed

Full `-7..+7` audit = `NO_SYSTEMATIC_TEMPORAL_SHIFT`.
Offset 0 remains strongest; only 5 nonzero neighbor matches across 441 valid comparisons, none in P3. Do not change positions/anchors/masks/block semantics/tap order based on shift hypotheses.

## MLX/reference parity — complete

`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`.

On 6 stratified states:
- hashes identical `6/6`;
- argmax exact `6/6`;
- ordered top5/top10 exact `6/6`;
- top50 sets identical `6/6`;
- corrected decode exact `6/6`;
- rel-L2 <= `0.001375`;
- cosine >= `0.999999164`.

The MLX drafter implementation is exonerated as the practical cause on tested states.

## Verifier provenance / tap interface — complete

Checkpoint:
`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

Classification:
`PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`

Report:
`research/architecture/loom-dflash-verifier-provenance-tap-interface-audit-001-result.md`

Evidence:
`results-local/research/dflash-verifier-provenance-tap-interface-audit-001/20260825T103951Z/`

Static contract `16/16` PASS.

Recovered compatible contract:
- layer IDs `[1,12,23,34,45]` are ordered 1-based post-block residual outputs;
- taps are pre-final-norm;
- local taps are float32 with no local tap cast/copy/fusion/reorder;
- no material target revision/config/tokenizer/tap-interface mismatch demonstrated.

Still unpinned:
- exact training-time Qwen revision;
- exact vLLM PR/revision;
- exact Speculators checkout;
- publisher tap-transport dtype.

These are unresolved historical provenance, not demonstrated causal mismatches.

## BF16 context

Available pinned BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 changed hidden states materially but target top1 stayed `12050`; P1_t01 is now known to be outside DFlash 32k support, so it cannot test exact proposal recovery on a representable target.

Persistent BF16 cache ~33 GiB remains available.

## Exact next step

Checkpoint:
`LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`

Cheap one-factor intervention before any new target execution:
- baseline: exact retained float32 taps;
- intervention: same taps round-tripped `float32 -> bfloat16 -> float32` immediately before drafter input;
- everything else frozen.

Use all 63 states, evaluate proposal/logit movement and, for the 50 representable states, target-row rank/top-k/exact-match changes plus per-prompt consistency.

No target/BF16-target forward, downloads, E2E, retraining/remapping, or performance work.

If no material recovery, move to a bounded representable-state Q4-target vs BF16-target hidden-state control with explicit cache/network preflight.