# LOOM DFlash D2T Offset Decode Repair 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`
Classification: `MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`
Gate: `COMPLETE`

## Purpose

Mechanically repair the local MLX interpretation of the publisher DFlash `d2t` tensor after authoritative upstream review established that `d2t` stores an offset, not an absolute target-token ID.

Correct semantics:

`target_token_id = draft_row + d2t[draft_row]`

No drafter weights, model math, target taps, attention mask, anchor semantics, target model, BF16 control, or scientific input were changed.

## Mechanical repair

Pi changed 8 local decode/analysis scripts that had interpreted `d2t[draft_row]` directly as the target-token ID.

All repaired paths now reconstruct the target-token ID using:

`draft_row + d2t[draft_row]`

The underlying raw drafter argmax rows remained unchanged for all 63 frozen states.

Therefore this checkpoint changes only output-index interpretation, not the learned drafter distribution.

## Mapping invariants

Corrected mapping invariants: PASS.

Measured:
- draft rows: `32,000`;
- reconstructed target IDs: all in target-vocabulary range;
- reconstructed target IDs: unique `32,000/32,000`;
- reconstructed support equals exactly the TRUE positions of publisher `t2d`;
- corrected effective target-token support cardinality: `32,000`.

This supersedes the earlier erroneous `17,018` support cardinality, which was the count of unique numeric offset values in `d2t`, not unique reconstructed target-token IDs.

## Frozen 63-state support after repair

Using the corrected 32,000-token support:
- representable target tokens: `50/63`;
- unsupported target tokens: `13/63`;
- representable fraction: `79.37%`;
- unsupported fraction: `20.63%`.

The previous `30/63 representable / 33/63 unsupported` partition does not survive corrected decoding.

`P1_t01` remains structurally unsupported:
- frozen target token: `12050`;
- corrected DFlash proposal token: `8747`;
- target match: false.

## Corrected proposal compatibility

Raw draft argmax identity:
- unchanged `63/63` relative to retained pre-repair raw draft-row evidence.

Decoded target-token identity:
- old direct-`d2t` token vs corrected offset-decoded token differs on `63/63` states.

Corrected top-1 compatibility:
- target matches: `0/63`.

Therefore the old numeric proposal IDs were wrong, but the aggregate `0/63` top-1 compatibility result survives after correct publisher decoding.

This is an important distinction:
- the output-mapping bug materially distorted support analysis and all reported proposal token IDs;
- it did **not** explain the catastrophic lack of top-1 agreement on the frozen corpus.

## Metrics not recovered in this checkpoint

Corrected target-distribution top-5/top-10/top-50 compatibility and corrected proposal rank under the target distribution were not recomputed because complete target logits for the frozen 63 states were not retained.

No target forward was authorized or run.

This absence does not affect the corrected top-1 result because exact frozen target next-token IDs and retained raw drafter argmax rows were sufficient for that comparison.

## Scientific interpretation

Measured facts:
1. Local MLX output decoding contained a real mechanical semantics bug.
2. The correct publisher support contains 32,000 unique target tokens, not 17,018.
3. Correct support coverage improves from the previously reported 30/63 to 50/63 frozen targets.
4. 13/63 frozen targets remain structurally unavailable through the reduced draft vocabulary.
5. Correcting the decode changes every decoded proposal token but produces no top-1 target matches: `0/63` remains.

Conclusion:
- the decode bug was important but is not sufficient to explain the DFlash incompatibility;
- reduced-vocabulary coverage remains a material secondary limitation (`13/63` unsupported), not the dominant explanation for the complete top-1 failure;
- for the 50 representable frozen target tokens, another drafter/target compatibility mechanism is required to explain why all 50 are predicted incorrectly.

The first historical E2E `0/96` result remains contaminated until its decode path is mechanically corrected/replayed. It must not be promoted as confirmed merely because frozen top-1 remains `0/63`.

## Evidence

Local:
`results-local/research/dflash-d2t-offset-decode-repair-001/20260825T093731Z/`

## Next checkpoint

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

Goal: cheaply quantify how the unchanged DFlash drafter scores the **correct target token** on the 50 representable frozen states under corrected mapping semantics, without running the target model, BF16 control, or E2E.

Required direction:
- map each representable frozen target token to its unique draft row using corrected `t2d`/offset semantics;
- use retained full 32k drafter logits if available, otherwise perform only the minimum unchanged drafter-only replay on the frozen tap corpus;
- measure the correct target token's drafter rank/probability and top-k placement for all 50 representable states;
- preserve the 13 unsupported states separately;
- do not confuse drafter-side target rank with rank under the target-model distribution.

Decision intent:
- target token frequently near the top but never top-1 -> drafter is directionally aligned and the remaining mismatch may be calibration/interface-sensitive;
- target token generally ranks very poorly -> the remaining incompatibility is structural/model-distributional and DFlash salvage becomes substantially less attractive.

No E2E or expensive target/BF16 work before this cheap diagnostic is reviewed.
