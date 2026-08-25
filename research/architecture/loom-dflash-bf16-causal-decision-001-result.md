# LOOM — DFlash BF16 causal decision 001

Date: 2026-08-25

## Outcome

Classification: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`

The preregistered DFlash recovery signal required exact BF16-label top1 recovery in at least 2 of 3 fixed states. P3 and P1 both failed exact recovery, therefore the >=2/3 gate became mathematically impossible and P2 was correctly not executed.

This rejects the hypothesis that replacing the exact Q4 verifier state with the pinned BF16 verifier state is sufficient, by itself, to recover DFlash exact speculation on the preregistered causal set.

It does not show that BF16 has no effect: BF16 materially changes DFlash distributions and improves P1 target rank from 3 to 2, but does not produce exact top1 recovery.

## Causal-path repair / validation

The pilot-002 producer artifacts were audited after mechanical scoring bugs were found. The final validated causal coordinates are:

- P3 `P3_t01:2`: anchor `271`, continuation position `2`, raw DFlash row `2`;
- P1 `P1_t32:6`: anchor `13`, continuation position `6`, raw row `6`;
- P2 `P2_t16:3`: anchor `11`, continuation position `3`, raw row `3`.

Offline runner validation reproduced the frozen Q4 references exactly:

- P3 target 1620: rank `2`, proposal `5416`;
- P1 target 326: rank `3`, proposal `3100`;
- P2 target 994: rank `3`, proposal `4057`.

Existing P3 BF16 base state was recovered at shape `[5,63,2048]`, same causal context, anchor 271, with zero new BF16 forward/network.

## P3

Evidence:
`results-local/research/dflash-p3-bf16-correct-anchor-rescoring-001/20260825T162101Z/recovery.json`

- BF16 verifier top1: `1620`, representable;
- Q4-tap DFlash: target 1620 rank `2`, proposal `5416`;
- BF16-tap DFlash: target 1620 rank `2`, proposal `350`;
- BF16 exact top1 recovery: NO;
- BF16 target remains top5/top10/top50/top100;
- selected-row 32k Q4-vs-BF16 drift: max abs `2.9441383`, mean abs `0.3287709`, RMSE `0.4144891`, rel-L2 `0.2037589`, cosine `0.9793963`.

Scientific interpretation: large distribution/proposal movement, no target-rank improvement and no exact recovery.

## Offline causal-runner gate

Evidence:
`results-local/research/dflash-causal-runner-offline-repair-validation-001/20260825T162819Z/validation.json`

Classification: `CAUSAL_RUNNER_OFFLINE_VALIDATION_PASS`.

- exact Q4 P3/P1/P2 ranks/proposals reproduced;
- existing P3 BF16 rank `2` / proposal `350` reproduced;
- fail-closed pre-treatment gate PASS;
- P1->P2 early-stop gate PASS;
- network `0`; BF16 forwards `0`.

## P1 decisive causal test

Evidence:
`results-local/research/dflash-p1-bf16-causal-test-001/20260825T163821Z/`

Classification: `P1_NO_EXACT_BF16_RECOVERY`.

- exact Q4 gate PASS: target 326 rank `3`, proposal `3100`, certified KV boundary `74`;
- BF16 verifier top1: `326`, representable;
- BF16-tap DFlash target 326: rank `2`, proposal `3100`;
- exact top1 recovery: NO;
- target top5/top10/top50/top100: YES;
- selected-row drift: rel-L2 `0.08663982`, cosine `0.99626342`;
- network: `87,265,184 B`, `57` requests, `2` retries;
- cache: `17,294` hits, `6` misses.

Because P3 already failed exact recovery, P1 failure makes the preregistered 2-of-3 recovery signal impossible. P2 and E2E were therefore not executed.

## Decision

- `BF16_TARGET_RECOVERY_SIGNAL`: NOT MET and cannot be met on the frozen 3-state set.
- No P2 treatment is justified for this hypothesis.
- No corrected DFlash E2E is justified from this mechanism.
- Preserve the BF16 cache/artifacts for possible future diagnostics, but do not continue DFlash salvage as the active LOOM path absent a new independent mechanism.
- Return research priority to the core 30B-on-8GB serving/I/O problem.
