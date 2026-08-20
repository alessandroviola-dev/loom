# LOOM Stretch 023 — Harness Defect Record

Status: **HARNESS DEFECT / NO SCIENTIFIC RESULT**

Attempt:
`20260820-151540`

Outer run directory:
`results-local/stretch/m5-h36-shared-stage-persistence-023/20260820-151540`

Outer classification emitted by the frozen comparison runner:
`SHARED_STAGE_COMPARISON_INCOMPLETE`

Scientific interpretation:
**NONE.** The treatment did not reach model execution or produce a constituent `summary.json`.

## What happened

The balanced sequence was preregistered as:

`STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`

Attempt 1 (`STREAMED`) completed normally and reached inherited:
`FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`.

Attempt 2 (`PERSISTENT`) exited with return code 1 after ~0.37 s and produced no child summary.
The outer runner therefore stopped exactly as preregistered. Attempts 3–4 were not run.

Observed traceback:

```text
RuntimeError: Stretch 023 transform failed for shared persistence constants: expected 1 occurrence, found 0
```

The exception occurs inside:
`scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py`
while calling `add_shared_persistence(transformed)`.

## Root cause

The frozen treatment helper blob
`8c263e7be15441581e481e6f41cbd16f87d4df4b`
first calls `h36.transformed_013_wrapper(...)` and then applies `add_shared_persistence()` to that returned text.

That returned text is still the transformed **Stretch 013 wrapper program**. It is not yet the final generated runtime source.

`add_shared_persistence()` intentionally searches for runtime fragments created only after the Stretch 010 -> 011 -> 012 -> 013 -> 017 -> H36 transform stack has executed, including the hotset constants and persistent runtime structures. Therefore its first runtime-fragment invariant (`shared persistence constants`) sees zero matches and raises before scientific execution starts.

## Why this is not a model/resource failure

- source provenance checks passed;
- the treatment failed before its scientific parent/runtime launched;
- no treatment model load occurred;
- no treatment memory/swap telemetry was produced;
- no treatment parity, KV, I/O or performance data exists;
- the failure is deterministic transformation-level harness logic.

Therefore this attempt cannot support any claim about full-weight persistence, memory feasibility, MLX behavior, numerical exactness or target performance.

## Frozen partial control data

The single STREAMED control attempt is preserved for audit only. It is **not** a comparison result and must not be used to infer a winner.

Observed control details from the outer summary:
- accepted oracle tokens: 15
- target rate: `1.7713653826078375 token/s`
- target-block wall total: `8.468043999999999 s`
- minimum observed free memory: `17%`
- peak swap: `2087.12 MB`.

## Authorized harness-only repair

The repair may change only how the already-preregistered shared-persistence transform is attached to the generated runtime source.

Frozen scientific design remains unchanged:
- M=5;
- H36 transformer residency;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- ordinary BF16 KV;
- exact parity/top-1 gates;
- inherited host/resource/I-O gates;
- treatment = embedding + final RMSNorm + LM head persistent once;
- control = those same stages streamed per pass;
- balanced order `STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED`;
- no cache purge, automatic retry, threshold relaxation or scientific fallback;
- one-time treatment setup excluded from steady-state rate and reported separately.

The broken helper and failed run remain preserved unchanged for provenance.