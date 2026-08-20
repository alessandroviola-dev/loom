# LOOM Stretch 026 — Full-Persistent Shared-Stage Batched Cleanup — Preregistered Plan

Status: **READY / NOT YET RUN**

## Question

After Stretch 025 removed redundant per-transformer-layer cleanup and raised balanced M5/H36/full-persistent target verification to `10.6674 token/s`, does consolidating the remaining cleanup around persistent shared stages yield another controlled speed gain without violating correctness/resource gates?

## Scientific factor

One factor only: cleanup scheduling for the three persistent shared stages.

Baseline `BATCHED`:
- canonical Stretch 025 treatment;
- transformer cleanup exactly once after the 36-layer body;
- embedding cleanup once after embedding;
- final RMSNorm cleanup once after norm;
- LM-head cleanup once after head.

Treatment `SHARED_BATCHED`:
- same one-per-transformer-body cleanup as Stretch 025;
- no `gc.collect() -> mx.clear_cache() -> gc.collect()` after embedding;
- no such cleanup after final norm;
- no such cleanup immediately after LM head;
- the identical cleanup sequence executes exactly once after the complete embedding/norm/head shared-stage path.

This changes only shared-stage cleanup scheduling from 3 cleanup sequences to 1.

## Frozen sources

BATCHED baseline:
- `scripts/stretch_full_persistent_batched_cleanup_025.py`
- blob `5ca3572f3269899e7c3fc23b9e136381ce864d99`.

SHARED_BATCHED treatment:
- `scripts/stretch_full_persistent_shared_batched_cleanup_026.py`
- blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`.

Balanced runner:
- `scripts/stretch_full_persistent_shared_batched_cleanup_comparison_026.py`
- blob `e958bde5d8a239ffa5fd192922e0693854d478e0`.

## Frozen architecture/workload

- Apple M1 / 8 GB reference system;
- Qwen3-8B 3-bit/group64;
- `mlx 0.31.2`;
- `mlx-lm 0.31.3`;
- `transformers 5.12.1`;
- exact oracle block `M=5`;
- 3 target traversals × 5 accepted oracle tokens = 15 accepted tokens per constituent run;
- H36 transformer hotset layers `0..35`;
- all raw model weights persistent: expected `3,583,928,320 B`;
- ordinary BF16 KV;
- exact numerical/top-1 parity gates;
- inherited process-I/O telemetry and host/resource gates;
- no model/runtime/quantization/KV/drafter/prefetch change;
- no deliberate cache purge.

## Balanced order

`BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED`

No automatic retry. No cache purge between constituents.

Every constituent must independently pass inherited correctness/resource gates.

## Required provenance

Both variants must demonstrate:
- exact H36 layer IDs `0..35`;
- full persistent raw-weight payload near `3,583,928,320 B` within inherited tolerance;
- exact M5 oracle geometry;
- 15 accepted oracle tokens;
- inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`;
- transformer-body cleanup record with policy `batched_once_after_36_layers` for all 3 target blocks.

SHARED_BATCHED additionally must demonstrate for all 3 target blocks:
- one `shared_stage_cleanup` record;
- policy exactly `batched_once_after_embedding_norm_head`.

BATCHED must not expose a `shared_stage_cleanup` record.

## Primary comparison

Pooled target-verification rate:

`total accepted oracle tokens / total target-block wall seconds`

computed separately over the two BATCHED and two SHARED_BATCHED constituents.

## Secondary comparison

- median/mean target block wall;
- mean transformer-body cleanup wall;
- treatment mean one-per-shared-path cleanup wall;
- minimum observed free memory;
- peak observed swap;
- disk free after run.

## Success classification

If all four constituents pass all inherited/provenance gates:

`FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS`

If any constituent fails or provenance is invalid:

`SHARED_CLEANUP_COMPARISON_INCOMPLETE`

Stop immediately. No winner from partial data and no post-hoc retry/rescue.

## Interpretation policy

1. Only the within-experiment SHARED_BATCHED/BATCHED ratio is causal evidence.
2. Absolute rate from Stretch 026 must not be compared causally with absolute rates from Stretch 025 or other separate experiments.
3. If SHARED_BATCHED materially improves rate and remains resource-safe, it becomes the preferred cleanup policy while retaining one transformer-body cleanup plus one shared-path cleanup per pass.
4. If the gain is small, shared cleanup is effectively closed and the remaining single transformer-body cleanup or compute/kernel path becomes the next axis.
5. If SHARED_BATCHED fails resource/correctness gates, do not weaken gates or search partial shared-stage subsets under this preregistration.

## Next decision

After Stretch 026:
- if shared cleanup remains material, freeze the winning cleanup schedule and consider a separately preregistered single-cleanup-at-end-of-pass experiment;
- if cleanup gains saturate, return to the compute/kernel evidence from Stretch 024, where MLP path was ~2.66x attention and gate/up/down were the major measured projections;
- real drafter integration remains separate from target-side optimization.
