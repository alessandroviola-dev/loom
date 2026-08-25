# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — tap-transport BF16 round-trip produces no material DFlash recovery; mapping, temporal alignment, MLX drafter parity, verifier/tap semantics and transport dtype are no longer leading explanations; next preflight a bounded representable-state Q4-target vs BF16-target causal pilot
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001_NO_MATERIAL_TAP_DTYPE_EFFECT`
Next core checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.9. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

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

## Mapping / support — resolved

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

The drafter is not random/unrelated; substantial target-directional signal exists.

## Eliminated leading explanations

Temporal alignment:
- full `-7..+7` audit = `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- offset 0 strongest aggregate alignment.

MLX drafter implementation:
- `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- exact decision-level parity on 6 stratified states; full 32k vectors extremely close.

Verifier provenance/tap semantics:
- `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001` = `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`;
- static contract `16/16` PASS;
- `[1,12,23,34,45]` = ordered 1-based post-block residuals, pre-final-norm;
- no demonstrated material target revision/config/tokenizer/tap mismatch.

## Tap transport BF16 sensitivity — COMPLETE

Checkpoint:
`LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`

Classification:
`NO_MATERIAL_TAP_DTYPE_EFFECT`

Report:
`research/architecture/loom-dflash-tap-transport-bf16-sensitivity-001-result.md`

Evidence:
`results-local/research/dflash-tap-transport-bf16-sensitivity-001/20260825T105437Z/`

Single intervention: retained float32 taps round-tripped `float32 -> bfloat16 -> float32` immediately before drafter input.

Results:
- baseline replay PASS: `9/9` retained full-logit parity, argmax/provenance/hash gates PASS;
- proposal changes `0/63`;
- logit movement max abs `0.011943`, mean abs `0.001128`, RMSE `0.001457`, rel-L2 `0.000671`, cosine `0.999999776`;
- 50 representable target mean rank `438.96 -> 438.72`;
- improved/unchanged/worsened ranks `11/32/7`;
- no top-k boundary crossings;
- top5/top10/top50/top100 unchanged `8/11/19/26`;
- exact target matches `0/50 -> 0/50`;
- P1/P2/P3 each `0/21` proposal changes and unchanged top-k counts.

Conclusion: tap transport dtype is not a useful compatibility mechanism. Do not rescue by changing tap transport precision.

## BF16 target context

Available pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 changed routing/taps/final logits materially but target top1 stayed `12050`; P1_t01 is outside the DFlash 32k support, so it cannot test exact proposal recovery.

Persistent BF16 cache ~33 GiB and exact P1_t01 BF16 taps/logits remain reusable. Q4->BF16 P1_t01 taps materially move DFlash logits, so verifier-state precision/distribution remains a plausible variable on representable targets.

## Exact next step

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

Static preflight only; no target execution or download.

Purpose:
Define the smallest informative representable-state Q4-target vs BF16-target pilot and bound its cost before authorization.

Required:
1. select one lowest-baseline-rank representable state from each P1/P2/P3, tie-break state ID;
2. determine minimal verifier prefixes/state reproduction and shared-work opportunities;
3. audit BF16 cache manifest/integrity, dense/routed coverage, size, hashes, resumability and disk availability;
4. compare retained Q4 routing traces with current cache only as a cache-hit/miss estimate, explicitly noting BF16 routing can diverge;
5. verify later on-demand BF16 execution can enforce a hard network/request cap and stop safely;
6. propose the exact later pilot contract, retention plan, hard abort gates and decisive metrics: target tap drift, drafter 32k movement, correct-row rank/top-k/top1 Q4 vs BF16.

Classify:
- `BF16_TARGET_PILOT_READY`;
- `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`;
- `BF16_TARGET_PILOT_NOT_FEASIBLE`;
- `BF16_TARGET_PREFLIGHT_AMBIGUOUS`.

No target/BF16 forward, downloads, E2E, retraining/remapping or performance work.