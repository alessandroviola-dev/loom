# Stretch 031 — M2 vs M5 SINGLE_PASS geometry comparison result

Date: 2026-08-20
Status: COMPLETE PASS

## Valid run

Balanced fresh Fix3 ABBA:

`results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix3/20260820-184128/summary.json`

Order: `M5 -> M2 -> M2 -> M5`.

All four constituents passed their expected classification, H36 `0..35`, full raw-weight persistence `3,583,928,320 B`, single final cleanup policy, exact ten accepted oracle tokens, and the frozen resource/provenance gates. No historical constituent or measurement was reused.

## Preflight provenance

Immediately before the ABBA, Fix3 passed source rendering, normalized one-factor comparison, canonical venv provenance and M5/M2 no-model dispatch markers:

`results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix3/preflight/20260820-184128/preflight-summary.json`

The marker paths preserved the literal canonical venv launcher and reported `model_loaded: false` / `target_compute_executed: false`.

## Pooled target-verification result

| Metric | M5 control | M2 treatment |
|---|---:|---:|
| Runs / accepted tokens | 2 / 20 | 2 / 20 |
| Pooled target-verification tok/s | 14.3307127237 | 11.8349427869 |
| Wall / accepted token (s) | 0.06978020 | 0.08449555 |
| Median block wall (s) | 0.3487060 | 0.1672135 |
| Final cleanup / accepted token (s) | 0.0091132 | 0.0169262 |
| Minimum free memory | 18% | 24% |
| Peak swap | 2068.12 MB | 2083.69 MB |

Primary ratio: `M2/M5 = 0.8258446747`.

M2 was `17.42%` slower in pooled target-verification rate; its wall-per-token ratio was `1.2108814535`, and cleanup-per-token ratio `1.8573278322`.

## Decision

M5 is the observed winner and remains the canonical target oracle geometry on the frozen M1 architecture. This result rejects the local M2 small-block throughput hypothesis for this workload; it does not establish a global optimum. Do not rescue M2 or reuse prior attempts. The next experiment, if authorized, must change a new independently preregistered compute factor rather than block geometry.
