# LOOM Stretch 015 — Eight-Token Divergence Attribution — Result

Date: 2026-08-20
Valid run: `20260820-124515`
Classification: **QUANTIZED_LINEAR_SHAPE_DEPENDENCE_CONFIRMED**

## Scientific question

Locate the first numerical divergence between the frozen `M=4` and `M=8` execution paths after Stretch 014 failed exact numerical parity.

## Frozen environment

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64 local artifact
- mlx `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- Stretch 014 runner provenance `6d7afd43969e752a7cce39ae474d7054ccc7edd8`
- Stretch 002 helper provenance `e7bd6bf4c61b44664c0c8421bf230b938509e4ef`
- no runtime upgrade
- no strict-mode patch
- no parity-threshold relaxation

## Launch / provenance

- source provenance: PASS
- version lock: PASS
- model config / quantization: PASS
- layer-0 provenance: PASS
- host samples: 71%, 71%, 72% free
- launch swap: 1232.62 MB
- host-state gate: PASS

## Direct QuantizedLinear result

The first-row input was held identical while only `M` changed.

`M=1` vs `M=4` showed no layer-0 traced divergence.

`M=4` vs `M=8`:

| Projection | Exact | Max abs diff | Mean abs diff |
|---|---:|---:|---:|
| q_proj | yes | 0.0 | 0.0 |
| k_proj | yes | 0.0 | 0.0 |
| v_proj | yes | 0.0 | 0.0 |
| o_proj | yes | 0.0 | 0.0 |
| gate_proj | **no** | 0.001220703125 | 0.00015750739839859307 |
| up_proj | **no** | 0.0009765625 | 0.00014882815594319254 |
| down_proj | **no** | 1.75 | 0.16764232516288757 |

First direct `M=4` / `M=8` divergence: **`gate_proj`**.

## Layer-0 causal trace

All checkpoints remain exact through the complete attention path:

- input_layernorm
- q_proj
- k_proj
- v_proj
- q_norm
- k_norm
- q_rope
- k_rope
- SDPA
- o_proj
- attention residual
- post-attention layernorm

The first divergence is then:

- `gate_proj`: max abs `0.0078125`, mean abs `0.0008744564256630838`
- `up_proj`: max abs `0.00439453125`, mean abs `0.0008224649354815483`
- `swiglu`: max abs `0.005859375`, mean abs `8.76382619026117e-05`
- `down_proj`: max abs `0.03125`, mean abs `0.0007166337454691529`
- block output: max abs `0.0625`, mean abs `0.0007264092564582825`

First layer-0 trace `M=4` / `M=8` divergence: **`gate_proj`**.

First layer-0 trace `M=1` / `M=4` divergence: **none**.

## Resource

- peak MLX memory: 272,389,176 B
- disk after run: 36.715 GiB free

## Interpretation

Stretch 015 rules out the attention/KV/causal-mask path as the origin of the observed Stretch 014 discrepancy at layer 0. The first divergence is already present in the actual quantized MLP linear path when only the `M` dimension changes.

Canonical conclusion:

> **The Stretch 014 eight-token parity failure is attributable to shape-dependent quantized-linear execution in the frozen MLX 0.31.2 / Qwen3-8B 3-bit path. At layer 0, `M=4` remains numerically identical to the sequential reference while `M=8` first diverges at `gate_proj`; the discrepancy then propagates through the MLP and block output.**

This is consistent with upstream MLX documentation showing that `quantized_matmul` dispatches among different kernels according to `M`, with different floating-point reduction trees. It does not by itself prove the exact internal kernel selected on this M1/3-bit workload.

A later MLX `qmv_wide` optimization targets small `M`, but affine quantization is gated to newer GPU generations in that change; therefore an MLX upgrade must not be assumed to fix this M1 3-bit case without a separate controlled experiment.

## Decision

- Freeze Stretch 015 as a successful attribution result.
- Do not rerun Stretch 014 unchanged.
- Do not relax exact-parity gates.
- Do not advance directly to a 16-token oracle block.
- Next map the exact `M` transition for the real layer-0 quantized projections under the frozen 0.31.2 environment.
