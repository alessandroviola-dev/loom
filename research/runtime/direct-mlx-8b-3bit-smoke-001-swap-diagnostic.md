# LOOM — Direct MLX 8B 3-bit Smoke 001 Swap Diagnostic

Date: 2026-08-19
Status: **CLOSED — TELEMETRY PARSER DEFECT IDENTIFIED**

## Scope

Read-only diagnosis after Direct MLX 8B 3-bit Smoke 001 run `20260819-121656`.

The original generation succeeded, but swap telemetry was `None`, so the preregistered two-channel safety gate could not be accepted as complete.

## Observed macOS output

`sysctl -n vm.swapusage` returned:

```text
total = 2048,00M  used = 1121,88M  free = 926,12M  (encrypted)
```

`sysctl vm.swapusage` returned the same localized numeric format prefixed by `vm.swapusage:`.

Both diagnostic parsers returned `None`.

Current system state during diagnosis:
- parsed-by-eye swap used: **1121.88 MB**
- memory free: **72%**
- disk free: **40.647 GiB**

The swap value is far below the frozen 5600 MB abort threshold, but this current-state observation does not retroactively validate the missing swap samples from run `20260819-121656`.

## Root cause

The runner regex accepted decimal points only:

```python
r"used\s*=\s*([0-9.]+)([KMGT])"
```

The reference Mac is emitting locale-formatted decimal commas (`1121,88M`). Therefore the regex does not match and `swap_used_mb()` returns `None`.

The first diagnostic "robust" regex was also point-only and therefore failed for the same reason.

This is a **telemetry/harness parser defect**, not an MLX runtime or model failure.

## Disk observation

The original smoke showed 39.668 GiB free immediately after runtime, whereas this later read-only diagnostic observes 40.647 GiB free. The approximately 1 GiB delta was therefore not persistent model growth. No causal attribution to swap, APFS, caches, or another mechanism is made.

## Corrective action

Do not alter the original run or its record.

Create a telemetry-only rerun wrapper that:
- imports the frozen `direct_mlx_8b_3bit_smoke.py` implementation;
- overrides only `swap_used_mb()`;
- accepts either `.` or `,` as the decimal separator;
- normalizes comma to point before `float()` conversion;
- leaves model, SHA, prompt, generation, `max_kv_size=4096`, unquantized KV, memory threshold and swap threshold unchanged.

The already-downloaded verified model must be reused; no new model acquisition is intended beyond Hugging Face snapshot verification/reuse.

## Decision rule

If the otherwise-identical rerun:
- captures numeric swap samples,
- stays at or below 5600 MB swap,
- stays at or above the 5% free-memory boundary,
- and generation otherwise satisfies the frozen Smoke 001 criteria,

then the rerun may become the canonical safety-valid Direct MLX 8B 3-bit smoke and authorize a separately preregistered T01 workload-safety probe.
