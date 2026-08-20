# LOOM Stretch 015 — Eight-Token Divergence Attribution

Date: 2026-08-20
Status: READY

## Trigger

Stretch 014 produced a valid scientific failure:

`ORACLE_BLOCK_NUMERICAL_PARITY_FAIL`

Canonical result:
`research/stretch/eight-token-oracle-block-verification-014-result.md`.

The first position of the first 8-token block already diverged from the resident sequential control (`max_abs_diff=0.34375`), while Stretch 013 with 4-token blocks had exact position-level parity. The root cause is not yet established.

## Objective

Identify the earliest reproducible numerical divergence introduced when the same frozen Qwen3-8B 3-bit workload changes its sequence/batch-row dimension from `M=4` to `M=8`.

This is an attribution experiment, not a speed experiment and not a rescue attempt for Stretch 014.

## Frozen baseline

Preserve:

- Qwen3-8B 3-bit/group64 local artifact
- MLX `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- Apple M1 / 8 GB reference system
- Stretch 014 runner blob `6d7afd43969e752a7cce39ae474d7054ccc7edd8`
- frozen prompt `[1,42,2048,151935]`
- first eight frozen oracle tokens `[1,374,264,4647,1483,304,279,1809]`
- ordinary BF16 `KVCache`
- no tokenizer, sampling, model download, KV quantization, prefetch, MLX upgrade, numerical-strict mode, or threshold relaxation.

Runner:
`scripts/stretch_eight_token_divergence_attribution_015.py`

Frozen runner blob:
`933c366220625e845e788b2ab1521ae78d9e7d15`.

## Motivation / hypothesis boundary

MLX 0.31.2 quantized matrix multiplication dispatch is shape-dependent in `M`, and upstream work has documented numerically different equivalent paths for different `M` values. This makes quantized-linear dispatch a concrete candidate for the Stretch 014 failure.

This is **not** frozen as the answer. Stretch 015 must distinguish it from attention/causal-block or other layer-internal causes by direct measurement.

## Diagnostic design

Use only transformer layer 0 and the actual frozen model weights.

### A. Direct QuantizedLinear shape probes

For the actual quantized layer-0 modules:

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`
- `gate_proj`
- `up_proj`
- `down_proj`

feed tensors whose first row is identical while only the number of rows changes:

- `M=1`
- `M=4`
- `M=8`.

Compare the first output row exactly for:

- M1 vs M4
- M1 vs M8
- M4 vs M8.

Any nonzero first-row difference in this direct test is sufficient evidence that the corresponding quantized linear operation is shape-dependent under the frozen runtime.

### B. Layer-0 internal causal trace

Recreate the real four-token prompt in an ordinary `KVCache`, then process the same oracle prefix with `M=1`, `M=4`, and `M=8`.

Capture the first current-token vector after, in order:

1. input RMSNorm
2. Q projection
3. K projection
4. V projection
5. Q normalization
6. K normalization
7. Q RoPE
8. K RoPE
9. scaled dot-product attention
10. O projection
11. attention residual
12. post-attention RMSNorm
13. gate projection
14. up projection
15. SwiGLU
16. down projection
17. block output.

The earliest nonzero M4/M8 difference is the primary layer-internal attribution point.

## State gates

- source provenance: Stretch 014 and Stretch 002 helper blobs exact
- frozen version lock exact
- Qwen3 config/3-bit quantization exact
- layer-0 safetensors provenance exact: 25 tensors / 84,427,264 B
- host launch state: all three samples >=60% free memory and swap <=5600 MB
- prompt cache offset before target probe: 4
- expected target cache offsets: M1 -> 5, M4 -> 8, M8 -> 12.

## Classifications

### `QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED`

At least one direct quantized-linear probe has a nonzero M4/M8 first-row difference.

Interpretation: the frozen runtime itself changes the numerical result of at least one row-wise quantized linear operation when `M` changes from 4 to 8. This is sufficient to explain why exact 4-token and 8-token block parity can differ, though downstream amplification still remains to be characterized.

### `BLOCK_INTERNAL_SHAPE_DEPENDENCE_CONFIRMED`

All direct quantized-linear probes are exact, but the causal layer trace develops a nonzero M4/M8 difference.

Interpretation: continue attribution inside the earliest non-linear/attention stage before any MLX change.

### `LAYER0_M8_DIVERGENCE_NOT_REPRODUCED`

Layer-0 direct probes and causal trace remain exact for M4/M8.

Interpretation: extend the same diagnostic across later layers / full streamed context; do not infer that Stretch 014 was spurious.

Harness/preflight failures remain non-scientific.

## Decision rule after Stretch 015

Do not proceed to a 16-token oracle block yet.

If quantized-linear shape dependence is confirmed, freeze that result first and design a separate controlled experiment to determine whether a shape-independent/strict kernel path restores numerical equivalence and what speed cost it introduces. That future experiment must be separate because changing MLX/kernel policy is a new scientific factor.

If the quantized-linear probe is exact, follow the earliest layer-internal divergence instead.
