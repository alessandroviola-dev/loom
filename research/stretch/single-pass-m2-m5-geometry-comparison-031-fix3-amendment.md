# Stretch 031 — Fix3 venv-dispatch amendment

Date: 2026-08-20
Status: COMPLETE PREFLIGHT PASS; harness-only amendment.

## Scope

Fix3 preserves all scientific conditions from the Stretch 031 preregistration. It changes only harness dispatch provenance after Fix2's no-model failure: the selected canonical launcher remains the literal path

`results-local/mlx/venv-mlx-lm-0.31.3/bin/python`

through subprocess execution. It is never dereferenced with `Path.resolve()`, `realpath`, or equivalent.

## Regression guard

`scripts/test_stretch_single_pass_venv_dispatch_031_fix3.py` and Fix3 `--preflight` scan all Fix3 harness files for venv-launcher dereference patterns. The preflight executes the literal launcher and requires:

- `sys.prefix == results-local/mlx/venv-mlx-lm-0.31.3`;
- `mlx == 0.31.2`, `mlx-metal == 0.31.2`, `mlx-lm == 0.31.3`, `transformers == 5.12.1`;
- M5 and M2 no-model parent-to-child markers from their actual executable shims;
- `model_loaded == false` and `target_compute_executed == false` in both markers.

## Valid Fix3 preflight

`results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix3/preflight/20260820-184109/preflight-summary.json`

Classification: `STRETCH_031_FIX3_PREFLIGHT_PASS`.

M5 and M2 rendered and compiled; normalized M5→M2 equality passed after only block geometry plus non-scientific identity substitutions. Dispatch markers confirmed respectively M5 `2 x 5` and M2 `5 x 2`, identical ten-token oracle prefix/hash, H36/full persistence/single cleanup source facts, the literal venv launcher, expected venv prefix, and the pinned runtime metadata.

This preflight contains no model load or target computation and reuses no scientific measurement.
