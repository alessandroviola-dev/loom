# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001_PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`
Strategic next: `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.8.

## Stable DFlash chain

Still valid:
- target taps `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Mapping / support — resolved

Correct mapping:
`target_id = draft_row + d2t[draft_row]`.

True support:
- 32,000 valid unique target IDs;
- frozen `50/63` representable, `13/63` unsupported;
- corrected exact top1 remains `0/63`.

Historical E2E `0/96` is contaminated by the old decode and is not current acceptance evidence.

## Directional compatibility

For 50 representable targets:
- rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

The candidate remains mismatched at top1 but carries non-trivial target-directional signal.

## Temporal alignment — rejected

Full preregistered `-7..+7` classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

Offset 0 is strongest aggregate alignment; no nonzero offset consistently dominates. Do not modify positions/anchors/masks/block semantics/tap order based on off-by-N hypotheses.

## MLX drafter port — exonerated

`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`.

Six stratified states show exact decision-level parity and extremely close full 32k logits between MLX and authoritative local reference. The current drafter implementation is not the leading explanation for the mismatch.

## Verifier provenance / tap interface — static audit complete

`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001` = `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`.

Report:
`research/architecture/loom-dflash-verifier-provenance-tap-interface-audit-001-result.md`

Evidence:
`results-local/research/dflash-verifier-provenance-tap-interface-audit-001/20260825T103951Z/`

Static contract `16/16` PASS.

Compatible semantics recovered:
- layer IDs `[1,12,23,34,45]` = ordered 1-based post-block residual outputs;
- pre-final-norm;
- local frozen tap transport currently float32;
- no local cast/copy/fusion/reordering;
- no demonstrated material target revision/config/tokenizer/tap-interface mismatch.

Unpinned historical details:
- exact Qwen training revision;
- exact vLLM revision/PR;
- exact Speculators checkout;
- publisher tap-transport dtype.

Unpinned provenance alone is not causal evidence.

## BF16 target context

Pinned available BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Previous P1_t01 Q4->BF16 intervention changed hidden states materially but cannot test exact DFlash recovery because target token `12050` is outside DFlash support. Persistent ~33 GiB BF16 cache remains available.

## Next — tap transport BF16 sensitivity

Checkpoint:
`LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`

Purpose:
Resolve the cheapest remaining interface uncertainty before spending more on BF16 target execution.

Single intervention:
- take exact retained float32 frozen taps;
- round-trip each tap `float32 -> bfloat16 -> float32` immediately before drafter input;
- leave target state, IDs, positions, masks, ordering, drafter weights/math and corrected mapping frozen.

Measure over all 63 states:
- baseline replay integrity;
- 32k-logit movement;
- proposal-row/token changes.

For 50 representable targets:
- exact target matches;
- correct-row rank changes;
- top5/top10/top50/top100 changes;
- prompt-level consistency.

Decision:
- broad decision-level improvement -> investigate training-time tap transport dtype as a real compatibility mechanism;
- no material recovery -> proceed to bounded representable-state Q4-target vs BF16-target hidden-state precision/distribution control;
- ambiguous isolated movement -> do not rescue; record and proceed only with a separately preregistered discriminator.

Restrictions:
- no target/BF16-target forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance optimization.

## Later order

1. `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`;
2. if no recovery, bounded representable-state Q4-target vs BF16-target control with cache/network preflight;
3. corrected bounded E2E only after a useful compatibility/acceptance mechanism exists;
4. if candidate remains incompatible, explicitly terminate DFlash salvage and return to LOOM's high-leverage 30B-on-8GB serving/I/O path.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.