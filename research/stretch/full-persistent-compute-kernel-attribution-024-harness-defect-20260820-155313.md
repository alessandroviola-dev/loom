# LOOM Stretch 024 — Harness/Telemetry Defect — 20260820-155313

Status: **HARNESS / TELEMETRY DEFECT — NO SCIENTIFIC RESULT**

Run directory:
`results-local/stretch/full-persistent-compute-kernel-attribution-024-fix1/20260820-155313`

Outer summary:
`results-local/stretch/full-persistent-compute-kernel-attribution-024-fix1/20260820-155313/summary.json`

## What happened

The preregistered ABBA sequence was:

`CONTROL -> PROFILED -> PROFILED -> CONTROL`

Attempt 1 CONTROL completed its inherited M5/H36/full-persistence scientific gates.

Attempt 2 PROFILED executed far enough to produce a child summary, but terminated with:

- return code `12`
- classification `COMPUTE_ATTRIBUTION_TELEMETRY_FAIL`
- failure reason:
  `compute attribution incomplete: NameError: name 'args' is not defined`

The outer runner therefore stopped immediately and did not run attempts 3–4.

## Exact cause

The PROFILED transform collects per-component timing in the child runtime, then aggregates those records in parent-side code.

That parent-side aggregation references `args.num_hidden_layers` in three geometry expressions:

1. `expected_profile_count = ORACLE_BLOCK_COUNT * args.num_hidden_layers`
2. `layer_accum = {layer_id: [] for layer_id in range(args.num_hidden_layers)}`
3. `ids != list(range(args.num_hidden_layers))`

`args` is local to `child_main()` and is not defined in the parent aggregation scope. Therefore the aggregation raises `NameError` after profiling data has been collected.

## Scientific interpretation

None.

This run does **not** demonstrate:
- a model failure;
- an M5/H36/full-persistence failure;
- a memory or swap limit;
- a correctness/parity failure;
- a compute/kernel attribution result.

Attempt 1 CONTROL is not reused as a scientific comparison point because the ABBA sequence is incomplete.

No partial winner or component ranking may be inferred from this run.

## Harness-only repair policy

Fix2 may change only the invalid parent-side layer-count references.

Frozen replacement geometry:
- `len(HOTSET_LAYER_IDS)` = `36`.

The repair must preserve:
- M=5 exact oracle geometry;
- H36 transformer residency;
- full raw-weight persistence;
- Qwen3-8B 3-bit/group64;
- MLX 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1;
- ordinary BF16 KV;
- all exact numerical/top-1 gates;
- all host/resource/I-O gates;
- the exact profiling boundaries;
- prompt unprofiled;
- balanced order `CONTROL -> PROFILED -> PROFILED -> CONTROL`;
- no deliberate cache purge;
- no automatic retry/rescue.

A completely new four-run ABBA must be executed after Fix2. No measurements from `20260820-155313` are reused.
