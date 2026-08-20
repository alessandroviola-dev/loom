# Stretch 027 — Single End-of-Pass Cleanup Comparison — RESULT

Date: 2026-08-20
Run: `20260820-163715`
Classification: `FULL_PERSISTENT_SINGLE_PASS_CLEANUP_COMPARISON_PASS`

## Frozen architecture

- Qwen3-8B 3-bit/group64
- M=5 exact oracle block
- H36 transformer residency
- full raw-weight persistence `3,583,928,320 B`
- mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- ordinary BF16 KV
- inherited parity/I-O/resource gates
- no deliberate cache purge

## Scientific factor

Cleanup points per target pass only:

- `SHARED_BATCHED`: one cleanup after transformer body plus one final cleanup after embedding/final norm/LM head.
- `SINGLE_PASS`: remove the transformer-body cleanup and retain exactly one final post-head `gc.collect() -> mx.clear_cache() -> gc.collect()` sequence for the complete pass.

Everything else remained frozen.

Balanced order:
`SHARED_BATCHED -> SINGLE_PASS -> SINGLE_PASS -> SHARED_BATCHED`.

Frozen sources:

- SHARED_BATCHED baseline blob `6926e1b1b9a851f23d88ba6b1f1023e13336098a`
- SINGLE_PASS treatment blob `6636456df5a773ac6062fdad66b7dc96abe8bd81`
- balanced runner blob `665ca882f5067e65779e7e3f1a0c352432aeb113`

## Controlled result

- SHARED_BATCHED pooled target-verification rate: `11.71484200192592 token/s`
- SINGLE_PASS pooled target-verification rate: `12.730685322495841 token/s`
- SINGLE_PASS/SHARED_BATCHED ratio: `1.0867142143618256x`
- controlled gain: **~+8.67%**

Target block wall:

- SHARED_BATCHED median: `0.4188015 s`
- SINGLE_PASS median: `0.396305 s`
- SINGLE_PASS/SHARED_BATCHED median ratio: `0.9462836212382238x`
- median reduction: **~5.37%**

Cleanup telemetry:

- SHARED_BATCHED mean transformer-body cleanup: `0.05322433333333333 s/block`
- SHARED_BATCHED mean final cleanup: `0.03469283333333333 s/block`
- SHARED_BATCHED combined measured cleanup: `0.08791716666666666 s/block`
- SINGLE_PASS mean final cleanup: `0.05584016666666667 s/block`
- measured cleanup reduction: `0.032077 s/block`

Resource telemetry:

- SHARED_BATCHED minimum free memory: `18%`
- SINGLE_PASS minimum free memory: `23%`
- SHARED_BATCHED peak swap: `2509.62 MB`
- SINGLE_PASS peak swap: `2562.94 MB`
- disk free after: `35.660 GiB`

All inherited exactness/provenance/resource gates passed.

## Decision

**Freeze SINGLE_PASS as the preferred cleanup schedule under MLX 0.31.2.**

Canonical target-side architecture is now:

`M5 + H36 + full raw-weight persistence + one final cleanup per pass`.

The cleanup axis is closed at one final cleanup per pass. A zero-cleanup policy is not promoted here: the remaining final cleanup is only ~14.1% of the observed median target-block wall, and even an idealized removal of that entire measured cleanup would imply only about `14.7 token/s` from the same median geometry, still below the ~20 token/s promotion target. The next work therefore returns to compute/kernel attribution and optimization.

Absolute rates across separate Stretch experiments remain host/cache-state dependent; the causal evidence is the balanced within-Stretch-027 ratio.

## Next step

Re-profile compute on the new SINGLE_PASS baseline before changing kernels or runtime. Stretch 024 profiling was collected under an obsolete cleanup schedule and should not be used as the final ranking for the optimized execution path.
