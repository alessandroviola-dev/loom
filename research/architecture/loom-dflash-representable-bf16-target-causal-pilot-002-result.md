# LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002 — Result

Date: 2026-08-25

Operational classification: `BF16_TARGET_PILOT_NETWORK_CAP_ABORT`

Scientific interpretation status: `WITHHELD_PENDING_CAUSAL_VALIDITY_AUDIT`

Evidence reported by Pi:
`results-local/research/dflash-representable-bf16-target-causal-pilot-002/20260825T134150Z/`

## What completed

- P3 BF16 completed.
- P1 exact Q4 baseline passed, then BF16 hit the hard network cap.
- P2 was not executed.
- P3 and P1 Q4 provenance gates were reported PASS.
- No inference is allowed for P1 BF16 or P2.

## Hard-cap behavior

Reported aggregate network accounting:
- bytes: `8,583,061,312 B` (`7.994 GiB`);
- requests: `1,007`;
- retries: `7`;
- cache: `20,832` hits / `898` misses, including partial P1;
- next request size: `9,437,184 B`;
- the next request was rejected before dispatch.

The network guard therefore behaved as intended and the operational cap-abort classification is accepted.

## Reported P3 treatment output

BF16 verifier top1: `1620`, representable by DFlash.

Reported tap rel-L2 / cosine by layer:
- L1: `0.1054 / 0.99467`;
- L12: `0.02035 / 0.99987`;
- L23: `0.02761 / 0.99970`;
- L34: `0.03706 / 0.99937`;
- L45: `0.09591 / 0.99549`.

Reported DFlash 32k movement:
- max abs `1.4325`;
- mean abs `0.2265`;
- RMSE `0.2860`;
- rel-L2 `0.13194`;
- cosine `0.99127`;
- proposal changed `4330 -> 2790`.

Reported label `1620` ranks:
- Q4-tap rank `5`;
- BF16-tap rank `13`;
- no exact top1 recovery.

## Causal-validity concern discovered during ChatGPT review

The reported Q4-tap rank `5` conflicts with the preregistered and exact repaired P3 baseline rank `2` (`Q4_BASELINE_SEGMENTATION_REPAIR_PASS`). This is not accepted as a harmless reporting difference without proof.

Review of the remote pilot source at user commit `8a74c3a2f039a771b4f1a682cc1754e48c76e50e` identified three concrete hazards in `scripts/loom_dflash_representable_bf16_target_causal_pilot_001.py`:

1. `q4_baseline(...)` returns the shared replay's `full_taps`, while the exact frozen DFlash rank/proposal gate is computed from the frozen `base_taps`.
2. `dflash_scores(...)` selects DFlash logits with a fixed `[0,1]` row instead of selecting the preregistered continuation-position row for each state.
3. `bf_forward_single(...)` runs BF16 from a fresh full-prefix input vector, while the scientific contract requires the same logical continuation segmentation/KV-boundary semantics as the frozen state.

Any of these can confound a Q4-vs-BF16 causal comparison. Together they are sufficient reason to withhold the P3 recovery/non-recovery interpretation.

The exact source actually executed was reported as:
`scripts/loom_dflash_representable_bf16_target_causal_pilot_002.py`.

That `_002.py` source is not yet remote-reproducible, so the review above is a high-confidence warning based on the remote predecessor and the observed rank inconsistency, not yet a byte-exact audit of the executed `_002` source.

## Decision

Accept only:
- the hard network-cap accounting;
- the fact that P3 BF16 artifacts were produced;
- the fact that P1 Q4 baseline passed before the cap;
- the persistent cache gained useful BF16 material.

Do **not** use the reported P3 rank movement (`5 -> 13`), proposal movement, or tap drift as evidence for or against the BF16 recovery hypothesis until the exact `_002` source and artifact selectors are audited.

Next checkpoint:
`LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001`.

The next checkpoint is strictly offline: no BF16 target execution, no network/downloads, no new scientific treatment.