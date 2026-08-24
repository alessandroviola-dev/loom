# LOOM DFlash Unquantized Target P1T01 Range Control 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`
Classification: `CONTROL_ADAPTER_PARITY_FAIL`
Gate: `STOP`

## Purpose

Run a one-factor P1_t01 control in which a new bounded BF16-capable target path is first required to reproduce the canonical local Q4 target before any upstream BF16 weight access or interpretation.

## Result

Gate A failed before BF16 access.

The new control adapter and the current local Q4 oracle agree bitwise with each other for the current replay, including router/logit/greedy behavior. However, the current canonical Q4 replay does **not** bitwise reconstruct the previously frozen `P1_t01` target taps.

Observed:
- frozen 4-bit tap parity: FAIL at all five taps `[1,12,23,34,45]`;
- first tap mismatch: layer 1;
- adapter vs current oracle: bitwise parity PASS;
- current router/logits/greedy checks: PASS;
- deterministic rerun: PASS;
- no NaN/Inf/leak.

No upstream BF16 weights were accessed.

## BF16 access

- pinned BF16 provenance accessed: NO;
- bytes fetched: `0 B`;
- dedicated peak disk usage: `0 B`.

Therefore this checkpoint provides no BF16-vs-Q4 comparison and no evidence for or against quantization causality.

## Interpretation

The immediate blocker is now local Q4 tap replay integrity, not BF16 availability.

The important distinction is:
- the new adapter is consistent with the **current** Q4 oracle;
- the **current** Q4 oracle is inconsistent with the previously frozen `P1_t01` tap artifact at every required DFlash tap;
- downstream router/logit/greedy behavior can remain correct despite this internal-state mismatch.

This reopens the provenance/semantic validity of the frozen target-tap corpus for live-target compatibility interpretation. It does not by itself prove that the target weights changed. Possible classes include prefix/state identity drift, off-by-one/capture semantics, runtime/code-path drift, or genuine deterministic hidden-state drift.

Do not access BF16 weights until this is localized.

## Evidence

`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T161949Z/`

Local script:
`scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`

## Next checkpoint

`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

Reconstruct the exact provenance and replay contract of frozen `P1_t01` and localize the first cause of tap mismatch before any unquantized control. Compare exact prefix/token identity, state position semantics, tap extraction contract, model/runtime provenance and current-vs-frozen layer outputs. If a mechanical capture/replay mismatch is found, repair only that variable and re-freeze/validate the affected corpus under explicit provenance before resuming compatibility or BF16 testing.
