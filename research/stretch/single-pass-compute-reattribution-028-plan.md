# Stretch 028 — SINGLE_PASS Compute Re-Attribution — PLAN

Date: 2026-08-20
Status: PREREGISTERED / READY

## Motivation

Stretch 024 identified cleanup/framework overhead as the largest measured category, but its component profile was collected before the cleanup schedule was optimized. Stretch 025–027 then changed only cleanup scheduling and produced large controlled gains, culminating in a canonical one-final-cleanup-per-pass schedule.

Therefore the Stretch 024 component ranking must not be treated as the final attribution for the optimized execution path. Stretch 028 re-measures compute on the canonical Stretch 027 baseline before any kernel/runtime optimization is attempted.

## Frozen baseline

- Qwen3-8B 3-bit/group64
- Apple M1 / 8 GB
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- M=5 exact oracle block
- H36 transformer residency
- full raw-weight persistence `3,583,928,320 B`
- ordinary BF16 KV
- one final `gc.collect() -> mx.clear_cache() -> gc.collect()` cleanup per pass
- inherited numerical parity, I/O and resource gates
- no deliberate cache purge

Canonical CONTROL:

- `scripts/stretch_full_persistent_single_pass_cleanup_027.py`
- blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`

## PROFILED treatment

- `scripts/stretch_single_pass_compute_reattribution_028_profiled.py`
- blob `0858e39a46bf09fe7750691b6dcd95b6753e5c70`

Scientific change: **instrumentation boundaries only**.

Prompt remains unprofiled. Only the three M5 oracle target blocks receive explicit `mx.eval` boundaries after:

1. input RMSNorm
2. attention
3. residual 1
4. post-attention RMSNorm
5. gate projection
6. up projection
7. SwiGLU
8. down projection
9. residual 2

The single final cleanup policy remains unchanged.

PROFILED throughput is intentionally perturbation telemetry and must never be promoted as a production speed result.

## Balanced runner

- `scripts/stretch_single_pass_compute_reattribution_comparison_028.py`
- blob `65d1c93967ed786623a3899e0f510ad9ef8de1e2`

Frozen order:

`CONTROL -> PROFILED -> PROFILED -> CONTROL`

No automatic retry, no cache purge, no rescue variant.

## Primary scientific outputs

- mean synchronized transformer compute per target block
- attention path wall
- MLP path wall
- MLP/attention ratio
- individual component ranking/share
- final cleanup wall
- persistent shared-stage forward/materialization wall
- residual unattributed wall
- accounted share of PROFILED full wall
- slowest layer candidates

CONTROL/PROFILED throughput and block-wall ratios are interpreted only as instrumentation perturbation.

## Required gates

Every constituent must retain:

- child classification `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- H36 layer IDs 0..35
- full persistent raw-weight payload near `3,583,928,320 B`
- oracle block size M=5
- 15 accepted oracle target tokens
- three target-block wall samples
- exactly one final cleanup record per target block with policy `single_cleanup_after_full_pass`

Each PROFILED constituent must additionally contain:

- exactly 108 target layer profiles = 3 blocks × 36 layers
- exactly three aggregated block totals

Any failure => `SINGLE_PASS_COMPUTE_REATTRIBUTION_INCOMPLETE` and stop without ranking or retry.

Valid completion => `SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS`.

## Decision policy after valid result

- If MLP remains the dominant compute path, prioritize a separately preregistered MLP/quantized-linear factor.
- If attention becomes comparable/dominant under the optimized schedule, prioritize attention/SDPA work instead.
- If residual/framework cost is still unexpectedly material, isolate that path before changing kernels.
- A newer MLX runtime remains a separate environment factor and must not rewrite the frozen MLX 0.31.2 evidence.
- Real drafter integration remains separate from target-side oracle verification.

## Exact run

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_single_pass_compute_reattribution_028_profiled.py
python3 -m py_compile scripts/stretch_single_pass_compute_reattribution_comparison_028.py
python3 scripts/stretch_single_pass_compute_reattribution_comparison_028.py
```
