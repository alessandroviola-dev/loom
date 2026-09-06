# LOOM UNLOCKED Speed Optimization UOPT-006 — Result

Date: 2026-09-05
Status: **COMPLETE / NO_GO**

## Objective

Evaluate draftless speculative decoding on the retained UNLOCKED UOPT-003 S40 runtime without changing model weights, routing, or production state.

## Tested modes

The active llama.cpp runtime exposed:

- `--spec-type none`
- `--spec-type ngram-simple`
- `--spec-type ngram-mod`

The short phase-1 A/B used the same S40 model/runtime parameters and deterministic greedy output for parity checking.

## Results

### Baseline

Production S40 remained the unchanged reference.

### `ngram-simple`

- greedy output parity: PASS
- decode change: `+0.52%`
- drafted tokens: `0`
- accepted tokens: `0`
- acceptance: N/A (`0/0`)
- verdict: **NO_GO**

### `ngram-mod`

- greedy output parity: PASS
- decode change: `-0.45%`
- drafted tokens: `0`
- accepted tokens: `0`
- acceptance: N/A (`0/0`)
- verdict: **NO_GO**

## Resources / stability

- RSS approximately `4.676 GiB`
- no meaningful swap growth during the short probes
- no errors
- no stalls
- production S40 unchanged

## Decision

The decisive result was not the sub-percent speed delta but `0 drafted / 0 accepted` for both draftless modes. The mechanism did not provide useful speculation on the tested workload, so a longer phase 2 was not justified.

No model-based speculative decoding, EAGLE, additional draft model, runtime update, promotion, or production mutation was performed.

UOPT-006 is closed **NO_GO**.
