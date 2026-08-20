# LOOM Stretch 025 — Full-Persistent Batched Cleanup Comparison — Preregistered Plan

Status: **READY / NOT YET RUN**

## Motivation

Stretch 024 valid run `20260820-160140` classified:

`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Under canonical `M5 + H36 + full raw-weight persistence`, synchronized attribution measured approximately:
- transformer compute: `0.8081826820 s/block`
- attention path: `0.2207656117 s/block`
- MLP path: `0.5874170703 s/block`
- per-layer cleanup summed across the 36 transformer layers: `0.9268928333 s/block`
- shared forward: `0.0552578333 s/block`
- residual unattributed: `0.0995254846 s/block`
- accounted share: `~94.74%`.

The cleanup category is the largest measured remaining target-side cost and is ~`1.1469x` the profiled transformer-compute total.

## Question

With every transformer layer and every shared model weight already persistent, is it still necessary to execute the full `gc.collect() -> mx.clear_cache() -> gc.collect()` cleanup sequence after every transformer layer?

## Scientific factor

One factor only: transformer cleanup schedule.

CONTROL:
- canonical Stretch 023 full-persistent target;
- after each of 36 transformer layers: `gc.collect() -> mx.clear_cache() -> gc.collect()`.

BATCHED:
- remove that cleanup sequence from the per-layer loop;
- execute the same cleanup sequence exactly once after the complete 36-layer transformer body and before final RMSNorm.

Shared-stage cleanup behavior is unchanged.

This is a schedule/frequency experiment, not a deletion of cleanup from the pass.

## Frozen sources

CONTROL:
- `scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`
- blob `120ad7be2f275559898bf636ca8e8fe039a56c60`.

BATCHED treatment:
- `scripts/stretch_full_persistent_batched_cleanup_025.py`
- blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`.

Balanced runner:
- `scripts/stretch_full_persistent_batched_cleanup_comparison_025.py`
- blob `5fa702d7236888a55b33031c832ce12c79c0e55a`.

## Frozen environment / architecture

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64
- MLX `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- exact oracle block `M=5`
- three target traversals / 15 accepted oracle tokens per constituent run
- H36 transformer residency, layers `0..35`
- full raw-weight persistence `3,583,928,320 B`
- ordinary BF16 KV
- inherited resident sequential control
- exact numerical/top-1 gates
- inherited launch/runtime memory/swap gates
- inherited Darwin process-I/O policy
- no tokenizer/sampling/drafter/KV/quantization/runtime/prefetch change
- no deliberate macOS cache purge
- no network/model download.

## Balanced order

`CONTROL -> BATCHED -> BATCHED -> CONTROL`

No result from Stretch 024 is reused in this comparison.

No automatic retry and no cache purge between constituent runs.

## Treatment provenance requirements

Every BATCHED target pass must expose:

`stages["transformer_body_cleanup"]["policy"] == "batched_once_after_36_layers"`

and record exactly one body-cleanup wall per target block.

The frozen treatment transform additionally requires the canonical per-layer transformer cleanup source sequence to be absent after transformation.

CONTROL must not expose `transformer_body_cleanup` stage records.

## Primary comparison

Pooled target verification rate:

`total accepted oracle tokens / total target-block wall seconds`

computed separately over the two CONTROL and two BATCHED constituents.

This is a real optimization comparison; unlike Stretch 024 PROFILED timing, no explicit component-level synchronization boundaries are introduced by Stretch 025.

## Secondary measurements

- median/mean target-block wall
- BATCHED one-per-body cleanup wall
- minimum observed system free-memory percentage
- peak observed swap
- inherited exactness/KV/resource outcomes.

## Success classification

If all four constituents pass all inherited and cleanup-provenance gates:

`FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS`

If any constituent fails, rejects, is host-state ineligible, or has invalid cleanup provenance:

`CLEANUP_COMPARISON_INCOMPLETE`

Stop immediately. No winner is inferred from partial data.

## Interpretation policy

1. Use the within-experiment balanced BATCHED/CONTROL ratio as causal speed evidence; do not compare absolute rates with historical Stretch runs causally.
2. If BATCHED is clearly faster and remains resource-safe, freeze one-post-body cleanup as the preferred full-persistent target schedule.
3. If BATCHED is flat/slower, retain canonical per-layer cleanup and move to the actual compute bottleneck identified by Stretch 024.
4. If BATCHED fails resource gates, do not post-hoc search 2x/4x/8x cleanup frequencies under this preregistration. Any intermediate schedule requires a separate preregistered factor.
5. The higher/lower observed free-memory percentage alone is not causal RAM evidence; system host state varies.
6. No fixed numerical materiality threshold is invented post-hoc; interpret effect size, paired direction, correctness and resource gates together.

## Next decision

If BATCHED succeeds materially, Stretch 026 should re-profile or move directly to the next residual factor, likely quantized-linear/MLP compute under the faster cleanup schedule.

If BATCHED does not improve the target, Stretch 026 should target the MLP/quantized-linear path because Stretch 024 measured MLP at ~`2.66x` the attention path.
