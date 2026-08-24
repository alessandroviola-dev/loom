# LOOM DFlash Unquantized Control Preflight 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001`
Classification: `CONDITIONAL_PREFLIGHT_DISK_AND_ADAPTATION_REQUIRED`
Gate: `STOP — metadata-only/no-weight-artifact verification PASS`

## Purpose

Determine the minimum valid unquantized-target control needed to test whether target hidden-state/precision drift explains the validated DFlash drafter incompatibility, without first downloading or running the full BF16 target.

## Upstream control candidate

Public upstream target:
`Qwen/Qwen3-30B-A3B`

Preflight revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`

This revision is public and ungated, but is not proven to be the exact revision used during DFlash training.

Artifact layout:
- BF16;
- 16 safetensors shards plus index;
- 18,867 tensors;
- total download bytes: `61,066,575,648`.

Public provenance review performed after the local preflight shows that the current BF16 weight shard objects and `tokenizer.json` trace to the original upstream upload commit `fd4bf3b`; the DFlash model card identifies the verifier as `Qwen/Qwen3-30B-A3B` but does not pin a target commit. Therefore future controls should pin the exact upstream weight-object/LFS hashes they use and must not claim exact reproduction of the historical DFlash training environment.

## Disk gate

Measured free disk:
`60,668,579,840 B` (`56.50 GiB`).

Estimated full-snapshot peak including largest staging shard:
`65,066,551,120 B`.

Shortfall:
`4,397,971,280 B`.

Therefore a normal full local BF16 snapshot is not authorized.

## Runtime feasibility

External-expert reuse: `CONDITIONAL`.

Current quantized-triplet `os.pread` runtime is not drop-in compatible with upstream BF16 tensors.

Required adaptation:
- upstream BF16 tensor/name catalog;
- BF16 dense and expert math path;
- three-projection expert reader;
- bounded range-backed or bounded-staging storage.

Analytical P1 control footprint:
- BF16 resident backbone: `3,082,186,752 B`;
- one live BF16 expert: `9,437,184 B`;
- KV at context 43: `4,227,072 B`.

## Minimum first control

Frozen state:
`P1_t01`, context 43.

Required comparison:
- post-block taps `[1,12,23,34,45]` at final prefix position;
- final normalized hidden state;
- full final logits;
- all 48 router logits/top-k/weights;
- greedy top1 and top1/top2 margin.

Metrics:
- max/mean absolute error;
- RMSE;
- relative L2;
- cosine similarity;
- logits top1/margin/top5 overlap.

No causal threshold was preregistered in this preflight.

## Required one-factor safeguard

The BF16 control requires a new reader/math path. Therefore it must not be interpreted until that path is first validated independently against the canonical local target using the same local/dequantized 4-bit weight values.

Hard adapter gate:
1. run `P1_t01` through the new control path with local target weight values;
2. require canonical target replay/tap/router/logit parity within the exact/tight tolerances already established for LOOM;
3. if adapter parity fails, classify `CONTROL_ADAPTER_PARITY_FAIL` and STOP;
4. only after adapter parity passes may the weight source alone be switched to pinned upstream BF16 objects.

This preserves a one-factor comparison: weight representation/values rather than kernel/reader semantics plus weight precision simultaneously.

## Cleanup

Retain only:
- comparison evidence;
- pinned object/range manifest;
- provenance/hashes.

Release runtime tensors and delete only the dedicated BF16 control cache/staging data after verification.

## Decision

The full snapshot route is blocked by disk and is unnecessary for the first causal control.

Next checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

The control may use bounded byte-range or bounded shard-staging access, but must not materialize the full 61-GB snapshot. It must pin exact upstream object hashes, pass adapter parity first, and distinguish a pinned-current-upstream BF16 control from an exact historical DFlash-training replica.

## Evidence

`results-local/research/dflash-unquantized-control-preflight-001/20260824T160413Z/`

Files:
- `preflight.json`
- `upstream-manifest.json`
- `provenance.json`
- source metadata JSONs
