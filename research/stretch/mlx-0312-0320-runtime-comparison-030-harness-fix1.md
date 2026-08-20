# LOOM Stretch 030 — Environment / Harness Fix1

Status: **FIX1 READY — NO SCIENTIFIC RUN YET**

Date: 2026-08-20

## Preserved pre-run failure

The original setup utility failed before provisioning because it inspected the shell-side Python instead of the canonical LOOM MLX child interpreter.

Record:
`research/stretch/mlx-0312-0320-runtime-comparison-030-setup-defect-20260820.md`

Scientific result: **NONE**.

## Canonical interpreter correction

The frozen LOOM execution chain uses:

`results-local/mlx/venv-mlx-lm-0.31.3/bin/python`

for the actual MLX workload.

Fix1 uses this interpreter explicitly for CONTROL provenance and CONTROL constituents. It no longer assumes `sys.executable` of the shell wrapper is the MLX runtime.

## Treatment environment correction

Original setup attempted `venv --system-site-packages`, which cannot guarantee inheritance of packages installed only in another venv.

Fix1 instead clones the canonical LOOM MLX venv into:

`.venvs/stretch030-mlx0320-fix1`

The clone is created before scientific execution. The canonical venv is never modified.

## Coherent macOS MLX runtime factor

On macOS the runtime is version-coupled across:
- `mlx`
- `mlx-metal`

CONTROL requires:
- `mlx==0.31.2`
- `mlx-metal==0.31.2`

TREATMENT requires:
- `mlx==0.32.0`
- `mlx-metal==0.32.0`

The treatment clone is updated with:

```text
python -m pip install --no-deps --upgrade mlx==0.32.0 mlx-metal==0.32.0
```

This installation happens only during pre-run provisioning, never inside the scientific runner.

Tracked non-runtime packages must match exactly between CONTROL and TREATMENT:
- `mlx-lm==0.31.3`
- `transformers==5.12.1`
- NumPy version identical
- safetensors version identical
- Python version identical.

## Fix1 files

Setup Fix1:
`scripts/stretch_mlx_0320_env_setup_030_fix1.py`

Blob:
`dfcc05aa6f730756056a75d5bf867bbd717ac31f`

Balanced runner Fix1:
`scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix1.py`

Blob:
`eb629a518edba8b9665785858bfe37402adc17e2`

Frozen original scientific runner:
`scripts/stretch_mlx_0312_0320_runtime_comparison_030.py`

Blob:
`0d0a27549067cef61a1dca7d3bf8f0e1f954d98b`

## Scientific design unchanged

Same workload on both sides:
`scripts/stretch_full_persistent_single_pass_cleanup_027.py`

Frozen blob:
`6636456df5a773ac6062fdad66b7dc96abe8bd81`

Unchanged:
- Qwen3-8B 3-bit/group64
- M=5
- H36
- full raw-weight persistence
- one final cleanup/pass
- mlx-lm 0.31.3
- transformers 5.12.1
- BF16 KV
- oracle sequence
- exact numerical/top-1/acceptance gates
- I/O/resource policy
- no cache purge
- no package installation during scientific ABBA
- no automatic retry/rescue.

Balanced order remains:

`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`

## Outcome policy

If the first valid MLX0320 constituent reaches numerical/top-1/acceptance gates and fails, classify the runtime comparison as a valid scientific numerical failure and stop without rescue.

If all four constituents pass, compare pooled target-verification token/s and median block wall within ABBA.

Any environment/provenance/resource/harness failure remains incomplete and is not a scientific speed result.

## Run policy

1. Run Setup Fix1 once.
2. Require `Environment setup FIX1: PASS`.
3. Only then run the balanced Fix1 comparison.
4. Do not use the original failed setup or original runner.
