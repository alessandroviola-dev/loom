# LOOM DFlash Q4 Tap Replay Drift Diagnostic 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`
Classification: `MECHANICAL_REPLAY_MISMATCH_REPAIRED`
Gate: `PASS`

## Purpose

Explain why current Q4 replay no longer bitwise reconstructed the frozen `P1_t01` DFlash tap artifact before any BF16 comparison.

## State identity

Frozen/current prefix identity is exact:
- state: `P1_t01`;
- context length: 43 tokens;
- prefill positions: 0..42;
- anchor position: 42;
- anchor token: 271;
- int32 token-prefix SHA-256: `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`.

Tap capture contract is also exact:
- dtype: float32;
- shape: `[5,43,2048]`;
- 1-based post-block taps `[1,12,23,34,45]`.

Model/config/scripts are unchanged and all four local Q4 shards match their download-manifest hashes.

## Root cause

The mismatch is runtime provenance, not model/prefix/capture drift.

Freeze-time replay:
- environment: `results-local/mlx/venv-mlx-lm-0.31.3`;
- MLX version: 0.31.2.

Current range-control replay:
- MLX version: 0.32.0.

Saved range-control tensors reproduce bitwise under MLX 0.32.0, while the original frozen tensors reproduce under MLX 0.31.2.

The first tap divergence appears at layer 1 post-block:
- differing elements: 55,514 / 88,064;
- max absolute error: `2.3841858e-07`.

The earliest localized numerical difference is:
- layer 1;
- position 0;
- expert 116;
- SwiGLU output;
- 157 / 768 elements differ;
- max absolute error: `2.9802322e-08`;
- gate and up projections themselves are bitwise equal.

This is a minute runtime-induced floating-point execution difference that propagates into hidden taps without changing the downstream target decision path.

## Repair and controls

Mechanical repair:
- replay using the freeze-time runtime / MLX 0.31.2;
- no code, model, prefix, position or capture change.

Before repair:
- frozen tap parity: 0/5.

After repair:
- frozen tap parity: **5/5 bitwise**;
- confirmed by instrumented replay and independent exact-oracle rerun;
- router logits: 48/48 bitwise across repaired rerun;
- final logits: bitwise;
- greedy token: 12050;
- finite values: PASS;
- routed-expert leak: none.

## Interpretation

There is no evidence of persistent Q4 hidden-state drift.

The earlier Gate-A failure in `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` was caused by mixing freeze-time MLX 0.31.2 tap evidence with an MLX 0.32.0 replay. The frozen `P1_t01` state remains reproducible when its runtime provenance is respected.

This does not test BF16 and does not support a quantization-causality claim.

The frozen DFlash compatibility corpus does not require refreezing on the basis of this diagnostic. Future one-factor controls that compare against the frozen taps must pin the freeze-time runtime (MLX 0.31.2), or explicitly treat a runtime-version change as a separate experimental variable.

## Evidence

Primary evidence:
`results-local/research/dflash-q4-tap-replay-drift-diag-001/20260824T164505Z/`

Runtime proof:
`results-local/research/dflash-q4-tap-replay-drift-diag-001/20260824T164128Z-mlx032-probe/`

Script:
`scripts/loom_dflash_q4_tap_replay_drift_diag_001.py`

## Next

Resume the bounded `P1_t01` upstream-BF16 range control under the pinned freeze-time MLX 0.31.2 runtime.

The control must first re-pass adapter parity against the 5/5 frozen Q4 taps in that same runtime. Only after that gate passes may the weight source switch to pinned upstream BF16 tensors.
