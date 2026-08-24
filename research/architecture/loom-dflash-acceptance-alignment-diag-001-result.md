# LOOM DFlash Acceptance Alignment Diagnostic 001 — Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_ACCEPTANCE_ALIGNMENT_DIAG_001_REPAIRED_PROBE_ZERO_ACCEPTANCE`

## Purpose

Explain the zero proposal acceptance observed in `LOOM_DFLASH_GREEDY_E2E_001` before attempting memory or performance remediation.

## Evidence

Local raw evidence:
`results-local/research/dflash-acceptance-alignment-diag-001/20260824T141239Z/`

Local runners:
- `scripts/loom_dflash_greedy_e2e_001.py`
- `scripts/loom_dflash_acceptance_alignment_diag_001.py`

## Diagnostic corpus

Three deterministic P1 speculative cycles were inspected: C=43–45.

## First concrete mismatch

The current MLX drafter path was missing the publisher-required anchor/block attention-mask semantics.

Observed incorrect behavior:
- the port exposed the anchor feature C-1 and future `MASK` slots incorrectly;
- the publisher contract requires base positions strictly before the anchor plus causal same-block synthetic attention.

Publisher/source contract recovered in this checkpoint:
- proposal slots 1–7 map via `d2t`;
- `sample_from_anchor=False`;
- target taps remain post-block `[1,12,23,34,45]`;
- no draft-KV carry between speculative cycles;
- target correction/bonus-token logic in the E2E runner was aligned.

## Repair

A single mechanical repair was applied locally: only `Drafter.propose` masking semantics changed.

No weights, target verifier, cache, packing, quantization, memory policy or other runtime variable was changed.

## Short acceptance probe

After the mask repair, a preregistered three-cycle probe was run rather than the full E2E benchmark.

Result:
- accepted proposals: `0/21`;
- acceptance prefixes: `[0,0,0]`.

Offset checks showed no simple systematic shift:
- k-1 matches: 0/20;
- k matches: 0/21;
- k+1 matches: 0/21.

Therefore the original missing mask was real, but repairing it did **not** restore proposal acceptance.

## Interpretation

The result does not yet establish drafter/target incompatibility.

The previous independent NumPy translation and MLX decision-stability checkpoint were validated before the publisher mask semantics were corrected. A masked publisher-semantics parity checkpoint is therefore still required.

Do not:
- optimize memory or verifier speed;
- rerun the full E2E benchmark;
- blame the local 4-bit target yet;
- change drafter weights or acceptance thresholds.

## Next checkpoint

`LOOM_DFLASH_MASKED_REFERENCE_PARITY_001`

Required goal: independently implement the publisher mask semantics in the reference path, then compare corrected MLX versus that reference on real frozen target-tap states and full seven-step rollouts. Only after masked reference parity passes may persistent zero acceptance be interpreted as evidence for target/drafter compatibility investigation.

## Gate

`FIRST_CONCRETE_SEMANTIC_MISMATCH_IDENTIFIED`

Repair completed, short probe still zero acceptance; full speculative promotion remains blocked.
