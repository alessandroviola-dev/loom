# Stretch 034 candidate — fused residual add + RMSNorm feasibility

Date: 2026-08-20

Status: **NO-GO — diagnostic only; no Stretch 034 scientific runner, preregistration, source transform, preflight, or ABBA was created.**

## Git audit before work

```text
branch = research/stretch-015-divergence-attribution
status = clean
HEAD = 8d0097bbc91d5e05b30d7081eb64d5eea4e187b7
origin/research/stretch-015-divergence-attribution = c73e2a89a3a9a8d3eb3637ed6c400bd9cff4b36a
origin...HEAD left/right = 0 / 7
merge-base(main, HEAD) = f345bcf0c98e8747531a56a7df14c95cc4f40efb
```

This was the expected comprehensible fast-forward state. No pull, push, rebase, merge, PR, or `main` modification occurred.

## Scope and real payloads

Canonical runtime provenance passed under the literal venv launcher: mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`, with `sys.prefix` equal to the canonical venv. The checkpoint is Qwen3-8B 3-bit/group64 affine, SHA-256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`; config confirms hidden size `4096`, 36 layers and `rms_norm_eps=1e-6`.

Safetensors headers confirm the actual norm vectors used:

| Qwen3 tensor | Shape | dtype |
|---|---:|---|
| `model.layers.0.input_layernorm.weight` | `[4096]` | BF16 |
| `model.layers.0.post_attention_layernorm.weight` | `[4096]` | BF16 |
| `model.norm.weight` | `[4096]` | BF16 |

The target was BF16 `[1, 5, 4096]`. Installed Qwen3 source confirms the real traversal is `h = x + r`, then `post_attention_layernorm(h)`, then `out = h + r`, with final `self.norm(h)`. No alternate “fast norm” was tested: control uses the already-canonical `mx.fast.rms_norm`.

## Implementation and JIT provenance

`scripts/stretch_fused_residual_rmsnorm_034_feasibility.py` builds one `mx.fast.metal_kernel` with fixed BF16 template, grid `(256, 5, 1)`, and threadgroup `(256, 1, 1)`. One threadgroup owns each 4096-wide row. Each thread:

1. computes and writes 16 BF16 `h = x + residual` elements;
2. retains those 16 values privately, accumulates squares in FP32;
3. participates in a 256-way threadgroup FP32 tree reduction;
4. uses `metal::rsqrt(mean + 1e-6)`; and
5. writes the BF16 weighted normalized output from its private `h` values.

Thus the normalized-output phase does not read the materialized `raw_residual` output. The source SHA-256 is `714d6e152ffb79c6a2132360ee201db4012c3f2c66c2fc75737e56c1c39b0dda`. The exact kernel source is stored in the evidence JSON and runner.

`metal_kernel` factory creation took `0.0430 ms`; first dispatch plus `mx.eval` took `101.4082 ms`. It was then reused as one object with one fixed template/grid throughout 40 excluded warmups and all timed work. MLX 0.31.2 exposes no public compilation-count API; this fixed-object provenance and separate first-dispatch timing are the available evidence against per-pass recreation. Excluded fused warmups had median `270.854 µs`.

## Numerical validation before timing

Three controlled random BF16 input/residual seeds (`11`, `29`, `47`) were each tested with real input-layer and post-attention norm vectors. A true model activation was not retrieved: that would require attention/MLP execution or dequantization of the quantized embedding table, neither is necessary for this real-norm microbenchmark.

`h` was bit-exact in all six cases: `max_abs_diff = 0`, `mean_abs_diff = 0`.

Normalized outputs were not bit-exact, consistent with a different FP32 reduction order. The predeclared compatibility ceilings were max `0.03125` and mean `0.0009765625`; observed worst values were:

```text
max_abs_diff  = 0.00390625
mean_abs_diff = 0.0001372101
```

They are within the gate, so numerical behavior was diagnostically plausible. The two-pair pattern repeated this behavior: both raw residuals exact; post-attention normalized max/mean `0.00390625 / 0.0001353021`, next-input normalized `0.000244140625 / 0.0000120564`.

## Reference and fused timing

All samples synchronize with `mx.eval`, exclude 40 warmups, use no cache purge, and use the mirrored interleaving `add → rms → control → fused → fused → control → rms → add`, repeated 60 times. Every reported side has 120 samples. Values are microseconds, median `[p25, p75]`.

| Operation | Median [p25, p75] | Total synchronized wall |
|---|---:|---:|
| add standalone | `212.52 [196.61, 223.33]` | `25.2688 ms` |
| `mx.fast.rms_norm` standalone | `231.69 [218.54, 248.09]` | `28.0400 ms` |
| control pair (both `h`, `n`) | `245.31 [228.68, 258.82]` | `29.3292 ms` |
| custom fused pair (both outputs) | `276.10 [258.84, 291.19]` | `33.0263 ms` |

`fused/control = 1.1255195`: the custom kernel is **12.55% slower**, losing `30.7915 µs` per pair. Pair telemetry after warmup: active `516,112 B`, peak `663,568 B`. It is memory-compatible but not performance-compatible.

The conditional two-pair layer-pattern diagnostic used Pair A (attention residual + post-attention norm) and Pair B (MLP residual + next-layer input norm), with no attention/MLP in the custom kernel. Control was `240.10 µs`; fused was `265.79 µs`; ratio `1.1069828`, a loss of `25.6870 µs` per two pairs. Active/peak were `860,176 / 1,253,392 B`.

## Fusion opportunities and projected block effect

For the 36-layer Qwen3 traversal:

- **A — simple intra-layer:** residual1 + post-attention norm: `36` opportunities.
- **B — cross-layer scheduling:** residual2 layer *i* + input norm layer *i+1*: `35` opportunities.
- **C — final:** residual2 of layer 35 + final model norm: potential `1` opportunity.
- Layer-0 input norm remains standalone.

Applying the measured per-pair *loss* to the canonical Stretch 031 M5 median target-block wall (`0.3487060 s`) gives:

| Scope | Pairs | Estimated effect |
|---|---:|---:|
| A: intra-layer only | 36 | `-1.10849 ms/block`, `-0.31789%` |
| A + B: intra plus cross | 71 | `-2.18620 ms/block`, `-0.62695%` |
| optimistic A + B + C | 72 | `-2.21699 ms/block`, `-0.63578%` |

B is not an automatic local replacement: `TransformerBlock` would need to expose its final raw residual and `Qwen3Model` would need to schedule the next layer’s input norm together with its following attention residual. C needs a separate final-traversal hook. Neither restructure was implemented, and the measured result would not justify it.

## Decision

`STRETCH_034_FUSED_RESIDUAL_RMSNORM_FEASIBILITY_NO_GO`.

The custom kernel compiled once, preserved raw-residual exactness, and had plausibly compatible normalized differences, but it is slower for both the single pair and the representative two-pair pattern. Intra-only and even the optimistic cross-layer arithmetic are negative rather than the required concrete `>=5%` upside. Do not create a Stretch 034 scientific ABBA or a rescue variant; retain separate residual add plus canonical `mx.fast.rms_norm`.

## Evidence

- Runner: `scripts/stretch_fused_residual_rmsnorm_034_feasibility.py`
- Parent summary: `results-local/stretch/fused-residual-rmsnorm-034-feasibility/20260820-201000/summary.json`
- Child evidence: `results-local/stretch/fused-residual-rmsnorm-034-feasibility/20260820-201000/child-summary.json`
