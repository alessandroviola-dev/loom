# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — P3 Q4 provenance mismatch is resolved as deterministic producer-segmentation drift; frozen expected SHA remains valid. Next checkpoint repairs the pilot Q4 replay to reproduce original continuation segmentation for all three preregistered states before any BF16/network retry.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001_Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`
Next core checkpoint: `LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent Pi context: `/AGENTS.md` v3.15.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Correct publisher mapping:
`target_id = draft_row + d2t[draft_row]`.

Compatibility baseline:
- frozen `50/63` representable, `13/63` unsupported;
- corrected DFlash exact top1 `0/63`;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Closed leading explanations:
- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static interface: 16/16 PASS, no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Historical E2E `0/96` used old decode semantics and is not current acceptance evidence.

## BF16 pilot infrastructure

Pinned BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Network-cap guard:
`BF16_NETWORK_CAP_GUARD_PASS`, remote source parity PASS.

Future BF16 pilot ceilings remain frozen:
- aggregate network `8 GiB`;
- aggregate requests `1,024`, retries included;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache.

Frozen state set/order remains:
1. P3 `P3_t01:2` — target 1620;
2. P1 `P1_t32:6` — target 326;
3. P2 `P2_t16:3` — target 994.

No substitutions.

## First BF16 causal attempt — INVALID BEFORE BF16

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` stopped on the P3 Q4 baseline provenance gate before any BF16/network execution.

Administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

No BF16 scientific conclusion is valid from that attempt.

## Q4 provenance reconciliation — COMPLETE

Checkpoint:
`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

Classification:
`Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`

Report:
`research/architecture/loom-dflash-q4-baseline-provenance-reconciliation-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-provenance-reconciliation-001/20260825T130903Z/`

P3 expected raw-float32 logit SHA:
`58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

Invalid-pilot full-prefix SHA:
`97cde5dd60c4c270152b65d5dee734c9f68b80a392a77522b0de0eba297cd52e`.

Root cause:
- frozen producer: 63-token P3 prefill + cached one-token decode `[3889]`;
- invalid pilot: fresh 64-token full-prefix forward.

The hashes have identical semantics: contiguous raw `float32` final-logit vector, shape `[151936]`. The mismatch is real deterministic numerical drift from execution segmentation.

Original segmentation exactly restores the frozen SHA. Full-prefix replay exactly restores the observed SHA.

Earliest divergence:
- layer-1 tap at anchor `[0,63]`;
- positions `0..62` remain exact;
- all five taps first differ at anchor;
- router logits/weights differ at anchor in all 48 layers;
- router IDs diverge at layer 1.

Final logits drift:
- max abs `0.00692338`;
- mean abs `0.00144157`;
- RMSE `0.00172441`;
- rel-L2 `0.00037988`;
- cosine `0.9999999411`;
- top1 still `1620`;
- ordered top10 parity exact.

The frozen expected SHA is authoritative and must not be replaced or tolerance-relaxed. Producer segmentation/KV boundary is part of the state provenance.

## Exact next step

Checkpoint:
`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`

Mechanical Q4-only repair before BF16 retry.

Required:
1. modify only the pilot/shared baseline replay code needed to reproduce frozen continuation segmentation;
2. recover original segmentation/KV boundary independently for P1, P2 and P3 from frozen evidence/code;
3. P3 must use the proven `[63,1]` prefill/decode boundary and reproduce exact SHA `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`;
4. require exact raw-logit SHA equality for all three selected Q4 states;
5. verify IDs, segmentation, cache semantics, selector, dtype/shape and any available tap/router/final-hidden commitments;
6. rerun unchanged DFlash baseline on restored taps and require corrected target ranks P1=3, P2=3, P3=2;
7. prove zero BF16/network execution.

Classification:
- `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`;
- `Q4_BASELINE_SEGMENTATION_REPAIR_FAIL`;
- `Q4_BASELINE_SEGMENTATION_REPAIR_AMBIGUOUS`.

If PASS, re-authorize the same P3 -> P1 -> P2 BF16 pilot under unchanged cost caps.
