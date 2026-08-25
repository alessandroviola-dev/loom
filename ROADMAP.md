# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001_Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`
Strategic next: `LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.15.

## Stable DFlash chain

Still valid:
- target taps `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- correct mapping `target_id = draft_row + d2t[draft_row]`;
- frozen support `50/63` representable and `13/63` unsupported;
- corrected DFlash top1 `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` remains invalid current acceptance evidence because it used old decode semantics.

Closed explanations:
- temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap interface: 16/16 PASS with no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

## BF16 bounded infrastructure — COMPLETE

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Frozen states:
- P1 `P1_t32:6`, target 326;
- P2 `P2_t16:3`, target 994;
- P3 `P3_t01:2`, target 1620.

Network-cap guard:
`BF16_NETWORK_CAP_GUARD_PASS`.

Remote source parity:
`BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Any later valid BF16 retry remains bounded by:
- aggregate `8 GiB` network bytes;
- aggregate `1,024` requests including retries;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache;
- fixed order P3 -> P1 -> P2;
- no state substitutions.

## First BF16 pilot attempt — INVALID

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` stopped before BF16/network because P3 Q4 final-logit provenance SHA failed.

Administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

No BF16 hypothesis was tested.

## Completed — Q4 provenance reconciliation

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001` = `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`.

Report:
`research/architecture/loom-dflash-q4-baseline-provenance-reconciliation-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-provenance-reconciliation-001/20260825T130903Z/`

Expected P3 raw-float32 final-logit SHA:
`58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

Invalid-pilot full-prefix SHA:
`97cde5dd60c4c270152b65d5dee734c9f68b80a392a77522b0de0eba297cd52e`.

Root cause is deterministic producer segmentation:
- frozen producer = 63-token prefill + cached one-token decode `[3889]`;
- invalid pilot = fresh 64-token full-prefix forward.

Both hashes use identical raw contiguous float32-vector semantics; not serialization error.

Original segmentation reproduces the frozen SHA exactly; full-prefix segmentation reproduces the observed SHA exactly.

Earliest divergence is layer-1 tap at anchor position `[0,63]`; positions `0..62` remain exact. Router IDs already diverge at layer 1. Final top1 remains 1620 and ordered top10 parity remains exact, but the provenance gate correctly treats the states as different.

The frozen expected commitment remains authoritative. Execution segmentation/KV boundary is now explicitly part of continuation-state provenance.

## Next — Q4 segmentation replay repair

Checkpoint:
`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`

Purpose:
Mechanically align the causal-pilot Q4 baseline producer with the original frozen continuation producer before any BF16/network retry.

Q4-only, no network/BF16.

Required:
1. change only baseline replay/instrumentation code needed to reproduce frozen execution segmentation;
2. recover each selected state's exact original segmentation/KV-cache boundary from frozen evidence/code rather than extrapolating from P3;
3. P3 must replay `[63-token prefill, 1-token cached decode]` and reproduce exact SHA `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`;
4. P1/P2 must reproduce their own exact frozen final-logit raw-byte SHA commitments;
5. verify IDs, segment boundaries, selector, dtype/shape, cache semantics and available intermediate commitments;
6. run unchanged DFlash on restored Q4 taps and require corrected frozen-target ranks P1=3, P2=3, P3=2;
7. prove zero network/BF16 dispatch;
8. no tolerance/hash relaxation or frozen-evidence edits.

Classifications:
- `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`;
- `Q4_BASELINE_SEGMENTATION_REPAIR_FAIL`;
- `Q4_BASELINE_SEGMENTATION_REPAIR_AMBIGUOUS`.

## Later order

1. exact three-state Q4 segmentation replay repair;
2. if PASS, re-run the same preregistered P3 -> P1 -> P2 BF16 causal pilot under unchanged caps;
3. if eventual BF16 evidence yields no useful recovery, explicitly reassess/terminate DFlash salvage before corrected E2E;
4. return to higher-leverage 30B-on-8GB serving/I/O work when DFlash salvage is exhausted.

No corrected E2E until a real compatibility/acceptance mechanism exists.
