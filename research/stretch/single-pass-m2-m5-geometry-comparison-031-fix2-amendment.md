# Stretch 031 — Fix2 dispatch-preflight amendment

Date: 2026-08-20
Status: **HARNESS BLOCKED — no scientific run**.

## Scope

Fix2 is a harness-only amendment over the preserved original and Fix1 artifacts. Its intended scientific workload is unchanged: M5 control `2 x 5`, M2 treatment `5 x 2`, same ten-token oracle prefix, frozen MLX 0.31.2/H36/full persistence/single cleanup/BF16 KV gates, and ABBA `M5 -> M2 -> M2 -> M5`.

Fix2 adds explicit shim-path propagation and a no-model parent/child dispatch sentinel. The sentinel records the outer/child Python and script paths, variant, geometry, 10-token prefix and runtime versions. It must create a child marker without importing MLX or loading the model.

## Preflight failure 20260820-183232

The first Fix2 preflight compiled all Fix2 files and successfully rendered/compiled both final runtime sources. Its normalized source comparison passed before dispatch.

The M5 dispatch stage failed before a child marker was written. Preserved evidence:

- `results-local/stretch/single-pass-m2-m5-geometry-comparison-031-fix2/preflight/20260820-183232/dispatch-m5-parent.json`;
- rendered M5/M2 sources in the same directory;
- no model child state, marker, benchmark output, or scientific measurement.

Exact harness root cause: `dispatch_preflight()` applied `.resolve()` to the canonical venv `bin/python` path. On this macOS layout that dereferences the venv symlink to framework Python `.../python3.13`; the child consequently could not find `mlx` package metadata. The preserved parent state proves the wrong child executable path.

This is a no-model harness failure, scientific result **NONE**. It is not an M5 result and the ABBA was not started. Per stop policy, no Fix2 retry and no ABBA were run.

## Required next action

Create a distinct Fix2a/Fix3 dispatch revision that preserves the literal canonical venv `bin/python` path (no `.resolve()`), then rerun the complete source-plus-dispatch preflight. It must produce valid markers for **both** M5 and M2 before a new fresh ABBA is allowed.
