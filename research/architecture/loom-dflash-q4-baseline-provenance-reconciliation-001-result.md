# LOOM DFlash Q4 Baseline Provenance Reconciliation 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`
Classification: `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`

## Scope

P3/Q4-only provenance diagnostic after the representable BF16 causal pilot stopped before any BF16/network dispatch. No BF16 target forward or real network was used.

Evidence:
`results-local/research/dflash-q4-baseline-provenance-reconciliation-001/20260825T130903Z/`

## Provenance hashes

Expected final-logit SHA-256:
`58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`

Observed invalid-pilot SHA-256:
`97cde5dd60c4c270152b65d5dee734c9f68b80a392a77522b0de0eba297cd52e`

Expected commitment:
`results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/target-continuation-reference.json`

Observed vector:
`results-local/research/dflash-representable-bf16-target-causal-pilot-001/20260825T125526Z/P3_t01/q4-target.npz`

Failed gate:
`results-local/research/dflash-representable-bf16-target-causal-pilot-001/20260825T125526Z/P3_t01/q4-baseline.json`

## Hash semantics

The mismatch is not NPZ/file serialization or selector semantics.

Both commitments are SHA-256 over contiguous raw `float32` final-logit vector bytes with shape `[151936]`.

The frozen producer emitted logits with shape `[1,1,151936]`; selecting its only vector reproduces the expected SHA exactly. The invalid-pilot producer emitted `[1,64,151936]`; selecting `[0,-1]` reproduces the observed SHA exactly.

## Root cause

The two producers used different execution segmentation for the same 64 token IDs:

- frozen producer: 63-token P3 prefill followed by cached one-token decode `[3889]`;
- invalid pilot: one fresh 64-token full-prefix forward.

Input identity is unchanged: 64 IDs, anchor token `3889` at index `63`, canonical int64 input SHA reported as `782500e...69acdd8`.

Model/config/tokenizer/runtime/source identities match frozen provenance; runtime MLX is `0.31.2`.

Both execution paths are deterministic: replaying the frozen segmentation restores the expected SHA exactly; replaying the full-prefix path restores the observed SHA exactly.

## Earliest divergence

The first numerical divergence is at tap layer 1, final anchor position `[0,63]`. Positions `0..62` remain exact.

All five taps `[1,12,23,34,45]` first differ only at that final anchor position.

Router logits/weights differ at `[0,63]` in all 48 layers. Router IDs diverge at layer 1.

This is therefore real producer-segmentation numerical drift, not a hash bookkeeping issue.

## Decisive final metrics

Final hidden:
- max abs `0.01266575`;
- mean abs `0.00067455`;
- RMSE `0.00098518`;
- rel-L2 `0.00032064`;
- cosine `0.9999999505`.

Final logits:
- max abs `0.00692338`;
- mean abs `0.00144157`;
- RMSE `0.00172441`;
- rel-L2 `0.00037988`;
- cosine `0.9999999411`.

Decision level:
- verifier top1 remains `1620`;
- ordered top10 parity is exact.

## Scientific interpretation

The frozen expected SHA remains valid and must not be replaced or tolerance-relaxed. The correct exact provenance contract binds:

- P3 token IDs;
- segmentation `[63,1]`;
- cached BF16-KV boundary between prefill and one-token decode;
- selector `[0,-1]` on the decode output;
- `float32` vector shape `[151936]`;
- contiguous raw-byte SHA-256 `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

The invalid BF16 pilot remains scientifically unclassified because no BF16 intervention ran.

## Next direction

Before any BF16/network retry, mechanically repair the pilot baseline producer to replay the frozen continuation segmentation rather than a fresh full-prefix forward. Validate exact frozen Q4 provenance for all three preregistered pilot states under their original producer segmentation so the expensive pilot cannot fail later on the same class of mismatch.
