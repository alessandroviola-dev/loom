# Stretch 040 — explicit Python GC cleanup-composition feasibility

Date: 2026-08-20
Status: **`STRETCH_040_GC_COMPOSITION_FEASIBILITY_NO_GO` — no scientific preregistration or ABBA.**

## Scope and preserved checkpoint

This feasibility run retained Qwen3-8B affine 3-bit/group64 BF16 on Apple M1
8 GB (`applegpu_g13g`), MLX/mlx-metal 0.31.2, mlx-lm 0.31.3, transformers
5.12.1, M5, H36, full raw-weight persistence, ordinary BF16 KV, and the
promoted process-local M1 S1_R8 custom qmv path.  No runtime, model, kernel,
quantization, threshold, M5 cadence, cache purge, or previous Stretch result
was changed or rerun.

The frozen promoted event remains exactly one event after two M5 blocks / ten
accepted tokens:

```python
gc.collect()
mx.clear_cache()
gc.collect()
```

Its audited source identity is Stretch-038 runner Git blob
`97339280aec0a9bb2fb4b196795f05cd23ef52a4`, promoted S1_R8 render SHA-256
`82888b134a6c4e0ba56bb24896bce2fd37c9d78c899380af35e0e823ad5fcbe3`, and
literal cleanup-snippet SHA-256
`6ce1b7154fbacbb3aa0b60c36e4ba26841e543382f74ea53e823d55c59568baf`.

A first local Stretch-040 generated-source attempt at `20260820-212047` is
preserved but excluded: its post-cycle final-payload serialization still
referenced the removed `__stretch038_result` field.  It produced no usable
Stretch-040 payload.  Distinct Fix1 only removed that obsolete payload field;
its render/compile check passed before the complete one-load run below.  This
was a harness-only defect, not a Stretch-037/038/039 rerun and not scientific
ABBA evidence.

Evidence: `results-local/stretch/s1r8-gc-cleanup-composition-040-feasibility/20260820-212227/summary.json`.

## Design

Eight timed **diagnostic CONTROL** cycles first instrumented the canonical
composition without changing its call order.  Only because the fresh
perfect-elimination bound reached 5% were treatment cycles admitted.

- **CONTROL:** after block 2 only, `gc.collect(); mx.clear_cache(); gc.collect()`.
- **TREATMENT:** at the same point and cadence, `mx.clear_cache()` only.

Both sides therefore execute exactly one cleanup event / two M5 blocks / ten
accepted tokens.  The balanced feasibility schedule was `C,T,T` repeated six
times (6 C, 12 T); the 12 extra T-only cycles are resource diagnostics only
and are excluded from the primary timing comparison.  The child loaded the
model once.  Python GC remained enabled; no `gc.disable()` or alternate
composition was tested.

## Component attribution and upside bound

Across the eight canonical diagnostic cycles:

| canonical cleanup component | median | mean |
|---|---:|---:|
| first `gc.collect()` | 19.842 ms | 19.805 ms |
| `mx.clear_cache()` | 0.311 ms | 0.333 ms |
| second `gc.collect()` | 16.337 ms | 16.385 ms |
| combined explicit GC | 36.330 ms | 36.190 ms |
| complete CONTROL 10-token wall | 749.598 ms | 750.448 ms |

Both `gc.collect()` calls returned **0 objects in all 8/8 cycles**;
`gc.garbage` stayed length zero and automatic Python GC was enabled.  This is
evidence of no cyclic garbage at those calls, not proof that the calls are
safe to remove.

Fresh pooled arithmetic was:

```text
CONTROL wall                 = 6.003584210 s
explicit-GC component wall   = 0.289520836 s
ideal no-explicit-GC wall    = 5.714063374 s
maximum throughput ratio     = 6.003584210 / 5.714063374 = 1.050668118
maximum gain                 = 5.066811777%
```

Thus the factor was only narrowly available for the required >=5% feasibility
treatment; `mx.clear_cache()` was retained in every treatment cycle.

## Correctness and frozen invariants

All **38** complete cycles (8 diagnostic C, 6 primary C, 12 primary T, 12
extended T) passed every inherited gate: prompt logits, all ten target logits,
top-1 equality, exact oracle sequence, generated-sequence equality, and
10/10 accepted tokens.  Every cycle retained exactly `3,583,928,320 B` raw
weights.  S1_R8 stayed four specializations with zero target-time
recompilations and all four retained real-weight bit-exact parity checks.

## Primary balanced timing

Primary performance uses only 6 CONTROL and 12 TREATMENT cycles, comparing
mean (and separately median) 10-token walls because the deliberate C,T,T
schedule has unequal counts.

| metric | CONTROL | TREATMENT (`mx.clear_cache()` only) |
|---|---:|---:|
| mean block-1 compute | 319.228 ms | 322.250 ms |
| mean block-2 compute | 312.286 ms | 311.867 ms |
| mean cleanup | 36.558 ms | 0.348 ms |
| mean 10-token wall | **754.609 ms** | **720.190 ms** |
| median 10-token wall | 755.512 ms | 725.297 ms |

The direct full-cycle transition timestamp was inadvertently omitted from the
Fix1 payload.  The reproducible residual `total wall - outer block-1 wall -
outer block-2 wall` (which also includes correctness/snapshot work, so is not
claimed as a pure transition) was 50.279 ms mean CONTROL and 49.170 ms mean
TREATMENT.  This omission does not affect the direct full 10-token wall,
component walls, correctness result, or the NO-GO gates; it is recorded as a
harness limitation.

Correct equal-cycle arithmetic:

```text
wall ratio (T/C)                    = 0.954389294
throughput-equivalent ratio (T/C)   = 1.047790463
gain                                = +4.779046308%
```

The raw evidence initially compared 6 CONTROL total seconds against 12
TREATMENT total seconds.  A post-run aggregation correction in the parent
summary replaces that invalid unequal-count ratio with the equal-cycle mean
calculation above; no cycle or workload was rerun.  The conclusion remains
NO-GO both because the corrected gain is below 5% and because the Python
object trajectory fails its independent stability gate.

## Treatment resource and Python trajectory

All 24 treatment cycles completed without an abort: minimum free memory was
24%; peak swap was 2021.44 MB.  MLX recovery was exact/stable across treatment
cycles:

| T snapshot | free % | swap MB | MLX active B | MLX cache B |
|---|---:|---:|---:|---:|
| before block 1 | 24–26 | 1909.38–2021.44 | 3,665,291,272 | 9,436,196 |
| after block 1 / before block 2 | 24–26 | 1909.38–2021.44 | 3,665,291,272 | 10,074,404–10,074,408 |
| after block 2 / before clear | 24–26 | 1909.38–2021.44 | 3,666,913,308 | 8,452,368–8,452,372 |
| after retained `mx.clear_cache()` | 24–26 | 1909.38–2021.44 | 3,665,291,272 | 2,867,744–2,868,260 |
| before next cycle | 24–26 | 1909.38–2021.44 | 3,665,291,272 | 2,867,744–2,868,260 |

So `mx.clear_cache()` alone restored MLX active/cache state to a stable band.
It did **not** establish Python-object safety.  Treatment tracked objects
immediately after clear rose strictly through all 24 cycles,
`84,797 -> 85,354` (+557); after the first 12 primary T cycles, the bounded
extension continued the same cumulative direction.  `gc.get_count()[0]`
cycled 395/446 during primary T cycles and then rose 495 -> 1,030 through the
T-only extension.  `gc.garbage` remained zero.  Diagnostic process maximum
RSS stayed at the same macOS `ru_maxrss` raw value, 2,308,308,992 (Darwin
reports this value in bytes despite the historical payload field name ending
`_kb`).  MLX stability alone is therefore insufficient.

## Decision

**NO-GO.**  The composition factor had a narrowly plausible theoretical
upside, and treatment remained exactly correct with stable MLX recovery, but
its measured primary gain was only **4.779%** (<5%) and the 24-cycle
no-explicit-GC trajectory showed cumulative tracked Python-object growth.
Keep the promoted canonical composition unchanged:

```python
gc.collect()
mx.clear_cache()
gc.collect()
```

once per two M5 blocks.  Do not create a Stretch-040 scientific preregistration
and do not run a scientific ABBA from this evidence.
