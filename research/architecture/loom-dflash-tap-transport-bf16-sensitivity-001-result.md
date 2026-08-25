# LOOM DFlash Tap Transport BF16 Sensitivity 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`
Classification: `NO_MATERIAL_TAP_DTYPE_EFFECT`
Gate: `PASS`

## Purpose

Isolate the remaining cheap tap-interface variable by changing only the representation immediately before drafter input:

- baseline: retained float32 frozen taps;
- intervention: the same taps round-tripped elementwise `float32 -> bfloat16 -> float32`;
- target states, input IDs, positions, masks, tap order, drafter weights/math, and corrected mapping unchanged.

No target-model forward, BF16-target forward, download, E2E, retraining or remapping was performed.

## Evidence

`results-local/research/dflash-tap-transport-bf16-sensitivity-001/20260825T105437Z/`

## Baseline integrity

Baseline replay PASS:
- retained full-logit numeric parity: `9/9`;
- argmax rows exact;
- provenance/hash gates PASS.

## Intervention result

Across all 63 frozen states:
- proposal changes: `0/63`;
- max absolute logit movement: `0.011943`;
- mean absolute movement: `0.001128`;
- RMSE: `0.001457`;
- relative-L2: `0.000671`;
- cosine: `0.999999776`.

For the 50 representable target states:
- mean correct-target rank: `438.96 -> 438.72`;
- rank improved / unchanged / worsened: `11 / 32 / 7`;
- no top-k boundary crossings;
- top5: `8 -> 8`;
- top10: `11 -> 11`;
- top50: `19 -> 19`;
- top100: `26 -> 26`;
- exact target matches: `0/50 -> 0/50`.

Per-prompt:
- P1: `0/21` proposal changes; top-k counts unchanged;
- P2: `0/21` proposal changes; top-k counts unchanged;
- P3: `0/21` proposal changes; top-k counts unchanged.

## Scientific interpretation

The BF16 tap-transport round trip causes only very small numerical movement and no decision-level recovery. It does not explain the corrected DFlash incompatibility.

Publisher tap-transport dtype may remain historically unpinned, but the tested BF16 transport hypothesis is now non-causal for the frozen corpus.

Do not modify tap dtype or transport as a rescue treatment.

## Next decision

The next scientifically relevant variable is verifier-state precision/distribution itself: Q4-target hidden states versus BF16-target hidden states on a small representable subset.

Before any expensive target execution or download, perform a static cache/network preflight that:
- selects a minimal representable pilot subset across P1/P2/P3;
- determines minimal prefixes/state reproduction requirements;
- audits persistent BF16 cache coverage and resumability;
- estimates network/compute exposure conservatively, explicitly accounting for possible BF16 routing divergence;
- proposes hard stop/cost gates for the later causal pilot.
