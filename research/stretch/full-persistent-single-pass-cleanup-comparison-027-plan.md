# Stretch 027 — Full-Persistent Single End-of-Pass Cleanup — Preregistration

Date: 2026-08-20
Status: READY / NOT YET RUN

## Motivation

Stretch 025 showed that replacing 36 per-transformer-layer cleanup sequences with one cleanup after the 36-layer body improved controlled exact M5 target verification by `3.8627785715x`.

Stretch 026 then consolidated persistent shared-stage cleanup from three points (embedding, final norm, LM head) to one post-head cleanup and produced a further controlled `1.1410704391x` gain.

The current canonical schedule therefore still executes two cleanup sequences per target pass:
1. once after the transformer body;
2. once after LM head.

Stretch 027 tests whether the intermediate transformer-body cleanup is still necessary when all raw model weights are persistent and a final cleanup is already retained.

## Scientific question

With M=5, H36, full raw-weight persistence and all other policies frozen, does consolidating cleanup from two points per target pass to one final post-head cleanup improve target verification while preserving exactness and resource safety?

## Scientific factor

Only cleanup schedule changes.

### Baseline — `SHARED_BATCHED`

Source:
`scripts/stretch_full_persistent_shared_batched_cleanup_026.py`

Blob:
`6926e1b1b9a851f23d88ba6b1f1023e13336098a`

Cleanup schedule:
- one `gc.collect() -> mx.clear_cache() -> gc.collect()` after the 36-layer transformer body;
- one identical cleanup after embedding/final-norm/head path.

### Treatment — `SINGLE_PASS`

Source:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`

Blob:
`6636456df5a773ac6062fdad66b7dc96abe8bd81`

Cleanup schedule:
- no cleanup between transformer body and final shared stages;
- one identical `gc.collect() -> mx.clear_cache() -> gc.collect()` after LM head;
- this becomes the only cleanup point in the target pass.

No zero-cleanup variant is allowed in Stretch 027.

## Frozen architecture and policy

Unchanged:
- Qwen3-8B 3-bit/group64 weights;
- MLX `0.31.2`;
- mlx-lm `0.31.3`;
- transformers `5.12.1`;
- exact oracle block `M=5`;
- all 36 transformer layers persistent (`H36`);
- embedding, final RMSNorm and LM head persistent;
- total persistent raw weights `3,583,928,320 B`;
- ordinary BF16 KV;
- exact numerical/top-1 gates;
- inherited process-I/O telemetry;
- inherited memory/swap safety gates;
- no deliberate macOS cache purge;
- no runtime upgrade;
- no drafter;
- no KV quantization;
- no model download.

## Balanced design

Runner:
`scripts/stretch_full_persistent_single_pass_cleanup_comparison_027.py`

Blob:
`665ca882f5067e65779e7e3f1a0c352432aeb113`

Frozen order:

`SHARED_BATCHED -> SINGLE_PASS -> SINGLE_PASS -> SHARED_BATCHED`

No automatic retry, rescue ladder, alternate cleanup frequency or post-hoc threshold change.

## Required constituent gates

Every child must preserve:
- classification `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`;
- hotset layer IDs exactly `0..35`;
- full persistent raw-weight payload within inherited tolerance of `3,583,928,320 B`;
- oracle block size `5`;
- `15` accepted oracle tokens;
- exactly three target block-wall samples;
- inherited numerical/KV/resource gates.

Cleanup provenance:
- SHARED_BATCHED must expose one `transformer_body_cleanup` record with policy `batched_once_after_36_layers` and one final cleanup record with policy `batched_once_after_embedding_norm_head` per target block;
- SINGLE_PASS must expose no `transformer_body_cleanup` record and exactly one final cleanup record with policy `single_cleanup_after_full_pass` per target block.

Any violation stops the comparison with no winner.

## Primary metric

Pooled accepted-token target-verification rate within the balanced experiment.

Primary ratio:

`SINGLE_PASS pooled tok/s / SHARED_BATCHED pooled tok/s`

## Secondary metrics

- median and mean target block wall;
- baseline transformer-body cleanup wall;
- final cleanup wall in both variants;
- minimum observed free-memory percentage;
- peak observed swap;
- disk free after run.

## Success classification

`FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`

## Failure/incomplete classification

`SINGLE_PASS_CLEANUP_COMPARISON_INCOMPLETE`

No partial winner or rescue rerun is allowed.

## Interpretation policy

- If SINGLE_PASS is faster and all gates remain valid, freeze it as the preferred cleanup schedule and consider the cleanup-frequency axis closed at one cleanup per pass.
- If SINGLE_PASS is flat/slower or fails resource/correctness gates, retain the two-point Stretch 026 schedule and close this consolidation branch.
- Do not infer that zero cleanup is safe from a SINGLE_PASS win; zero cleanup would require a separate preregistration if ever justified.
- Absolute rates from separate Stretch experiments remain non-causal; the balanced within-run ratio is primary evidence.

## Next axis after Stretch 027

Once cleanup scheduling is closed, return to the true compute bottleneck characterized in Stretch 024. MLP is `2.6608x` the attention path, with gate/up/down projections each near the top of synchronized transformer compute. A kernel/runtime experiment should therefore be selected from the final Stretch 027 outcome, with any MLX version change treated as a separate environment factor.
