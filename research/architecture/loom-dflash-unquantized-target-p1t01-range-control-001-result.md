# LOOM DFlash Unquantized Target P1T01 Range Control 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`
Classification: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`
Gate: `COMPLETE`

## Purpose

Run a bounded one-factor control on frozen state `P1_t01` that first proves the new target adapter reproduces the canonical local Q4 target under the freeze-time runtime, then changes only the target weight source from local Q4 values to pinned upstream BF16 values.

The purpose is to measure whether target precision/weight-source materially changes the DFlash tap states, MoE routing and final target distribution before making any claim about DFlash incompatibility causality.

## Runtime and frozen state

Runtime:
- environment: `results-local/mlx/venv-mlx-lm-0.31.3`;
- MLX: exactly `0.31.2`.

Frozen state:
- state: `P1_t01`;
- context length: 43 tokens;
- prefix SHA-256: `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- positions: `0..42`;
- anchor: position 42, token 271;
- DFlash target taps: `[1,12,23,34,45]` as 1-based post-block outputs.

## Gate A — Q4 adapter parity

Gate A PASS under MLX 0.31.2:
- frozen taps: 5/5 bitwise;
- router decisions/logits: 48/48 bitwise;
- final logits: bitwise;
- greedy token: `12050`, bitwise parity;
- deterministic rerun: PASS;
- finite: PASS;
- no routed-expert leak: PASS.

Therefore the bounded adapter/capture path is not an uncontrolled variable in Gate B.

## Gate B — pinned upstream BF16 control

Only the target weight source changed to the pinned upstream BF16 control. Runtime, prefix, target architecture, routing/expert math, capture semantics, comparison code and scientific gates remained fixed.

Completed Gate B:
- deterministic rerun: PASS;
- finite: PASS;
- no routed-expert leak: PASS;
- BF16 layer-expert pairs completed: `3,470`;
- expert payload fetched: `32,747,028,480 B`;
- dense cache reused: 435 tensors / `3,082,186,752 B`;
- no dense redownload;
- network retries: `13`;
- exhausted network failures: `0`;
- peak dedicated disk: `3,091,655,835 B` (< 12 GiB);
- wall time: `5,888.0 s`.

The transport implementation used bounded pooled/coalesced HTTPS range access and ephemeral expert staging. Mechanical transport remediation changed I/O only, not scientific target semantics.

## Scientific measurements

### Router divergence

- first router divergence: layer 0, position 1;
- layers with identical Q4/BF16 router top-k over the full prefix: `0/48`.

Thus target routing diverges essentially immediately on this state.

### DFlash tap drift

Relative-L2 Q4 vs BF16 at the five required target taps:

| Post-block tap | Relative-L2 |
| --- | ---: |
| 1 | 0.114863 |
| 12 | 0.345792 |
| 23 | 0.310635 |
| 34 | 0.198639 |
| 45 | 0.274675 |

The drift is substantial and non-monotonic across depth rather than a tiny numerical replay effect.

### Final normalized hidden

- relative-L2: `0.270665`;
- cosine: `0.964671`.

### Final logits

- relative-L2: `0.336189`;
- cosine: `0.957269`.

### Final token behavior

- Q4 top1: `12050`;
- BF16 top1: `12050`;
- top1 parity: PASS;
- Q4 top1/top2 margin: `12.90015`;
- BF16 top1/top2 margin: `11.875`;
- top-5 overlap: `4/5`.

## Interpretation

This control establishes a measured fact: on frozen `P1_t01`, changing the target weight source from local Q4 to pinned upstream BF16 while holding the runtime and target execution path fixed causes material hidden-state, router and logit drift.

The result is stronger than the earlier MLX-version replay mismatch: the five DFlash tap states show relative-L2 differences of roughly 0.11–0.35, the first router difference appears at layer 0 / position 1, and no layer preserves identical full-prefix router top-k decisions.

At the same time, Q4 and BF16 still select the same greedy next token `12050`. Therefore this result does **not** establish that Q4 precision changes the target's next-token decision on this state.

For DFlash specifically, same-target-token parity does not eliminate precision drift as a candidate cause: DFlash consumes internal target taps `[1,12,23,34,45]`, and those inputs are materially different under BF16. The result therefore promotes target precision/hidden-state distribution shift to a serious mechanistic hypothesis for the observed drafter incompatibility.

However this checkpoint remains `NOT_CAUSAL`:
- it covers one frozen state only;
- the BF16 control is a pinned current-upstream target, not a proven exact historical DFlash-training verifier revision;
- it measures target drift but does not yet intervene on the DFlash drafter input to show that BF16 taps recover proposal compatibility.

It is therefore not valid to claim that quantization caused the earlier `0/63` drafter/target top1 compatibility result from this checkpoint alone.

## Mechanical execution note

The bounded BF16 reader required transport-only remediation before the completed run:
- expert-major execution replaced repeated position-major expert fetches;
- pooled HTTPS and range coalescing reduced request overhead;
- a transport microbenchmark selected a 64 MiB maximum coalesced range;
- an initial stale preflight branch stopped before Gate B and was bypassed without changing scientific logic;
- the completed Gate B is the evidence source for the measurements above.

These are feasibility/I/O changes only and are not interpreted as scientific treatments.

## Evidence

Completed local evidence:
`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T212818Z/`

Primary files:
- `summary.json`;
- `bf16-control.json`;
- `progress.json`.

Transport selection evidence:
`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T212313Z/transport-microbenchmark-aggregate.json`

Local script:
`scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`

## Next checkpoint

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

Use the completed `P1_t01` BF16 target taps as a one-factor intervention into the unchanged, already validated DFlash drafter. Compare the drafter proposal produced from Q4 target taps versus BF16 target taps, and score both against the pinned BF16 target distribution/next token for the same state.

The purpose is not broader confirmation yet; it is to test whether the measured BF16/Q4 tap shift actually moves DFlash proposal compatibility in the predicted direction. If BF16-tap input produces a material recovery, preregister a broader frozen-state confirmation before any causal promotion. If it does not, simple target-tap precision drift becomes less likely to explain the catastrophic compatibility failure.
