# Stretch 038 — S1_R8 deferred cleanup cadence scientific result

Date: 2026-08-20
Status: **`STRETCH_038_CLEANUP_CADENCE_PASS` — valid fresh ABBA.**

## Scientific identity and evidence

The distinct committed runner is
`scripts/stretch_s1r8_deferred_cleanup_comparison_038.py` at
`429c47e1e3ffce2ca3ecf4af212939c07467c4dd`.  Its final fresh scientific
root is:

```text
results-local/stretch/s1r8-deferred-cleanup-038-comparison/20260820-224921/
```

The two earlier roots `20260820-224800` and `20260820-224834` are preserved
as harness failures (generated-source import and payload-routing,
respectively).  Neither is a complete scientific ABBA and none of their
artifacts, cycles, or timings was reused.
The final root had its own in-harness preflight and the only valid ABBA.

The promoted Stretch-037 source identity was unchanged: canonical control
render SHA-256 `9f94787f7a002a8da95e8352f134eac11f1b072b9363fe600dcac1122080a54c`,
S1_R8 render SHA-256
`82888b134a6c4e0ba56bb24896bce2fd37c9d78c899380af35e0e823ad5fcbe3`, and
S1_R8 injection SHA-256
`a086806a314d387770dac54e9140b9526bf7fe9097819f449bba17b7fc1f3ad4`.

## Metric semantic audit and preflight

Source audit passed: `run_streamed_pass()` begins its pass wall before target
compute and completes `shared_stage_cleanup` (`gc.collect() ->
mx.clear_cache() -> gc.collect()`) before returning.  The primary constituent
wall was additionally measured directly from the start of target block 1 to
after block 2's final cleanup.  Thus the primary wall includes the studied
cleanup cadence, including block-1 cleanup in CONTROL and final cleanup in
both sides.

The fresh in-harness preflight passed py_compile, final CONTROL/TREATMENT
renders, literal non-dereferenced launcher
`results-local/mlx/venv-mlx-lm-0.31.3/bin/python`, runtime provenance
(mlx/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers 5.12.1), promoted S1_R8
hashes, four real-weight kernel specializations and exact parity.  Both
parent/child no-model runs passed with `model_loaded=false` and
`target_compute_executed=false`.

The normalized scientific source diff passed: the sole difference is the
literal cleanup-after-block-1 control (`present` for CONTROL, `absent` for
TREATMENT); block-2 final cleanup is identically enabled in both renders.

## Frozen factor, host, and ABBA

All frozen conditions remained Qwen3-8B affine 3-bit/group64 BF16, Apple M1
gen13, M5, H36, full raw-weight persistence, BF16 KV, promoted custom S1_R8,
and zero target-time recompilation.  CONTROL executed the explicit cleanup
after each M5 block (2/10 accepted tokens).  TREATMENT omitted it only after
block 1 and retained the identical final cleanup after block 2 (1/10).

The passive host gate before the final fresh run passed naturally at 69% free
memory and 1677.25 MB swap.  No purge, out-of-flow cache clear, artificial
allocation, or automatic kill was used.  Fresh order completed exactly:
`CONTROL -> TREATMENT -> TREATMENT -> CONTROL`.

| Constituent | Launch free % / swap MB | Accepted | Target wall (s) | Result |
|---|---:|---:|---:|---|
| CONTROL 1 | 69 / 1677.25 | 10 | 0.750816417 | PASS |
| TREATMENT 1 | 73 / 2043.38 | 10 | 0.720280042 | PASS |
| TREATMENT 2 | 72 / 2007.88 | 10 | 0.709245583 | PASS |
| CONTROL 2 | 73 / 2058.50 | 10 | 0.759182375 | PASS |

Every constituent passed prompt logits, all ten target logits, top-1 equality,
exact oracle sequence, generated-sequence equality, ten accepted tokens and
full raw-weight persistence exactly `3,583,928,320 B`.

## Primary result

The primary metric is pooled accepted tokens / pooled constituent target wall.

| Metric | CONTROL | TREATMENT |
|---|---:|---:|
| Constituents / accepted tokens | 2 / 20 | 2 / 20 |
| Pooled target wall | 1.509998792 s | 1.429525625 s |
| Pooled throughput | 13.245043710 tok/s | 13.990655117 tok/s |
| Wall / accepted token | 0.075499940 s | 0.071476281 s |

`TREATMENT / CONTROL = 1.056293616`: **+5.629361621% throughput**.
The total-wall ratio is `0.946706469`, so the independently reported wall
reduction is **5.329353065%** (not the same quantity as throughput gain).

## Component timing and resources

| Side / constituent | Block-1 compute | Cleanup 1 | Transition | Block-2 compute | Final cleanup |
|---|---:|---:|---:|---:|---:|
| CONTROL 1 | 0.282909 s | 0.067713 s | 0.019577208 s | 0.295277 s | 0.066087 s |
| TREATMENT 1 | 0.287349 s | 0.000000 s | 0.031079375 s | 0.320058 s | 0.064861 s |
| TREATMENT 2 | 0.291563 s | 0.000001 s | 0.027591667 s | 0.307173 s | 0.065340 s |
| CONTROL 2 | 0.286655 s | 0.065951 s | 0.019637458 s | 0.301033 s | 0.067746 s |

Required four-point resource telemetry was recorded for every constituent.
At all final cleanups MLX active memory returned from the pre-cleanup
`3,666,913,308 B` to the stable `3,665,291,272 B` baseline; no cumulative
active/cache growth occurred.  Cache after final cleanup remained in the
stable 2,867,744–2,868,256 B band.  Minimum free memory was 24%; peak swap
was 2127.88 MB; observed MLX peak was 3,671,402,524 B in the first three
constituents and 3,671,402,520 B in the fourth.  No runtime abort fired.

## Decision and promotion

All preregistered promotion gates passed: complete ABBA, full correctness,
stable resources, stable final-cleanup recovery, no problematic cumulative
memory/cache trajectory, and pooled improvement >=5%.

**Promote the frozen M1 path as: promoted S1_R8 plus one explicit cleanup
every two M5 blocks.**  The correct claim is that explicit cleanup cadence was
reduced from 2 to 1 per 10 accepted tokens; cleanup was not eliminated.
