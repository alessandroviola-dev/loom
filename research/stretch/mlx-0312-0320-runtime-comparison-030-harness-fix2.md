# LOOM Stretch 030 — Harness Fix2

Status: **READY — SCIENTIFIC DESIGN UNCHANGED**

Date: 2026-08-20

## Preserved setup / runner history

Original setup failed before provisioning because shell `python3` was not the canonical LOOM MLX interpreter. Scientific result: NONE.

Environment setup Fix1 subsequently completed successfully and produced a validated isolated treatment clone:

`.venvs/stretch030-mlx0320-fix1`

Validated runtime pair:
- CONTROL: mlx `0.31.2`, mlx-metal `0.31.2`
- TREATMENT: mlx `0.32.0`, mlx-metal `0.32.0`
- mlx-lm `0.31.3` both
- Transformers `5.12.1` both
- NumPy `2.5.2` both
- safetensors `0.8.0` both
- Python `3.13.0` both.

Fix1 runner then stopped before starting the ABBA because its own static invariant incorrectly required:

`MLX_0320_RUNTIME_NUMERICAL_PARITY_FAIL`

The frozen runner actually defines:

`MLX_0320_RUNTIME_EXACTNESS_FAIL`.

Runner defect record:
`research/stretch/mlx-0312-0320-runtime-comparison-030-runner-defect-20260820-1738.md`

No scientific attempt was consumed.

## Second pre-run harness issue

Historical Stretch 027 ultimately inherits the Stretch 009 parent harness, which hard-codes its inner MLX child to:

`results-local/mlx/venv-mlx-lm-0.31.3/bin/python`

Launching Stretch 027 itself with another interpreter therefore does not guarantee that the actual model child uses that interpreter.

Without repair, a nominal 0.31.2-vs-0.32.0 outer comparison could silently execute both actual model children under 0.31.2.

## Runtime-portable workload

New common workload harness:

`scripts/stretch_runtime_portable_single_pass_030.py`

Blob:
`16243fd78a6eb5a831c426e0c1e432a4f45db988`

It reconstructs frozen Stretch 027 unchanged and applies only two harness portability changes to the final historical runtime source:

1. inner model child interpreter:
   - old: hard-coded canonical LOOM venv;
   - new: `Path(sys.executable).resolve()`;
2. historical inner version preflight:
   - old: fixed `mlx==0.31.2`;
   - new: mlx must be one of the two preregistered Stretch 030 variants `{0.31.2, 0.32.0}`, while mlx-lm remains exactly `0.31.3` and Transformers exactly `5.12.1`.

This workload source is identical for CONTROL and TREATMENT. It does not choose which runtime is used; the balanced runner does that by selecting the outer interpreter.

The model workload remains unchanged:
- Qwen3-8B 3-bit/group64
- M5 oracle blocks
- H36
- full raw-weight persistence
- one final cleanup/pass
- BF16 KV
- frozen oracle sequence
- numerical/top-1/acceptance gates
- memory/swap gates
- no cache purge.

## Runner Fix2

`scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix2.py`

Blob:
`6dd993418bff0bf9ec65c6b9a80f4bb382eb4976`

Harness-only differences from the frozen original runner:
- uses the validated setup Fix1 marker/venv;
- CONTROL interpreter is explicitly the canonical LOOM venv;
- TREATMENT interpreter is explicitly the validated 0.32.0 clone;
- both execute the exact same runtime-portable workload blob;
- correct exactness-failure invariant is `MLX_0320_RUNTIME_EXACTNESS_FAIL`;
- records and gates the inner child summary `versions` so CONTROL must actually report mlx `0.31.2` and TREATMENT must actually report mlx `0.32.0`;
- result root is `mlx-0312-0320-runtime-comparison-030-fix2`.

## Scientific design remains frozen

Balanced order:

`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`

Scientific factor:
coherent macOS MLX runtime package pair (`mlx` + `mlx-metal`) `0.31.2 -> 0.32.0` only.

No package installation occurs during scientific execution.

Outcome policy remains:
- first MLX0320 numerical/top-1/oracle failure under frozen gates => `MLX_0320_RUNTIME_EXACTNESS_FAIL`, valid scientific FAIL, stop/no rescue;
- complete exact ABBA => `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`;
- environment/harness/resource/provenance issue => `MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE`.

## Execution policy

Do not rerun setup Fix1: its treatment venv is already validated.

Do not run original runner or runner Fix1.

Run a fresh complete ABBA through Fix2 only.