# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001_INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`
Strategic next: `LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.14.

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
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` remains invalid as current acceptance evidence because it used old decode semantics.

## Closed hypotheses

- temporal alignment: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap interface: static 16/16 PASS with no demonstrated material mismatch;
- tap transport dtype: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

## BF16 representable-state infrastructure — COMPLETE

Preflight:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Frozen states:
- P1 `P1_t32:6`, target 326, 79-token prefix;
- P2 `P2_t16:3`, target 994, 74-token prefix;
- P3 `P3_t01:2`, target 1620, 64-token prefix.

Network-cap guard:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Remote source parity:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Any later valid pilot re-attempt remains bounded by:
- aggregate `8 GiB` network bytes;
- aggregate `1,024` requests including retries;
- pre-dispatch `NETWORK_CAP_ABORT`;
- persistent/resumable cache;
- fixed state set and no post-hoc substitutions.

## Attempted BF16 causal pilot — INVALID BEFORE INTERVENTION

Checkpoint:
`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

Administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-001/20260825T125526Z/`

The pilot stopped on the first fixed-order state P3 before any BF16/network dispatch.

Observed:
- guard source hashes PASS;
- guard tests `6/6` PASS;
- storage/cache PASS;
- free external disk `1,152.25 GiB`;
- ledger `0 B / 0 requests / 0 retries`;
- P3 Q4 verifier top1 remained frozen token `1620`;
- final-logit provenance SHA mismatched the expected frozen hash;
- reported observed abbreviated hash `97cde5dd...297cd52e`;
- reported expected abbreviated hash `58d20d90...185432`;
- BF16 states completed `0`;
- network usage `0 B / 0 requests / 0 retries`.

Therefore the BF16 scientific hypothesis remains untested. No recovery/non-recovery classification is valid.

## Next — Q4 baseline provenance reconciliation

Checkpoint:
`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

Purpose:
Determine whether the failed P3 Q4 provenance gate is caused by hash/serialization semantics, a mechanically different replay path, or material numerical drift.

P3-only, Q4-only, no BF16/network.

Required:
1. recover exact full observed/expected hashes and artifact paths;
2. identify the exact hash object and canonicalization used by the frozen reference;
3. recover frozen-producer and current pilot-producer paths;
4. compare token IDs/prefix, model/config/tokenizer/runtime/source identities;
5. run the minimum local Q4 reproduction under the same environment;
6. locate earliest divergence across taps -> router IDs/weights -> final hidden -> final logits;
7. quantify numerical drift with max abs/mean abs/RMSE/rel-L2/cosine plus top1/top-k parity;
8. compute canonical contiguous raw-array SHA-256 for both sides with explicit dtype/shape;
9. if the mismatch is purely mechanical hash/selector semantics, demonstrate it exactly; do not silently weaken the gate;
10. if true numerical drift exists, identify its earliest material source without model/math rescue.

Classifications:
- `Q4_BASELINE_EXACT_REPLAY_RESTORED`;
- `Q4_BASELINE_HASH_SEMANTICS_RECONCILED`;
- `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`;
- `Q4_BASELINE_PROVENANCE_AMBIGUOUS`.

## Later order

1. reconcile P3 Q4 provenance;
2. only if the Q4 gate is legitimately restored/reconciled, reconsider the same preregistered P3 -> P1 -> P2 BF16 pilot;
3. if the BF16 pilot eventually yields no useful recovery signal, explicitly reassess/terminate DFlash salvage before corrected E2E;
4. return to LOOM's higher-leverage 30B-on-8GB serving/I/O path when DFlash salvage is exhausted.

No corrected E2E until a real compatibility/acceptance mechanism exists.
