# LOOM Stretch 030 — Runner Fix1 Defect — 2026-08-20 17:38

Status: **HARNESS PREFLIGHT DEFECT — NO SCIENTIFIC RESULT**

## Sequence observed

Environment provisioning Fix1 completed successfully before the runner was launched.

Validated CONTROL environment:
- interpreter: `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`
- mlx `0.31.2`
- mlx-metal `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- numpy `2.5.2`
- safetensors `0.8.0`
- Python `3.13.0`.

Validated treatment clone:
- `.venvs/stretch030-mlx0320-fix1`
- mlx `0.32.0`
- mlx-metal `0.32.0`
- all tracked non-runtime packages equal to CONTROL.

Setup classification:
`Environment setup FIX1: PASS`.

No scientific measurement was performed during setup.

## Runner failure

The Fix1 balanced runner aborted before creating a scientific run directory or starting attempt 1.

Exact failure:

```text
RuntimeError: Stretch 030 Fix1 runner invariant failed; missing ['"MLX_0320_RUNTIME_NUMERICAL_PARITY_FAIL"']
```

Root cause:
- the frozen original runner's valid treatment exactness-failure classification is `MLX_0320_RUNTIME_EXACTNESS_FAIL`;
- Fix1's own static preflight mistakenly required the non-existent string `MLX_0320_RUNTIME_NUMERICAL_PARITY_FAIL`;
- therefore Fix1 rejected the frozen runner before executing it.

Scientific result: **NONE**.

No ABBA constituent launched and no scientific attempt was consumed.

## Additional pre-run issue discovered before repair

The canonical Stretch 027 workload ultimately derives from the historical Stretch 009 parent harness, which selects the MLX child interpreter through the hard-coded path:

```python
venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"
```

Therefore merely launching Stretch 027 itself with the treatment Python is insufficient: without a harness-only portability repair, both CONTROL and TREATMENT can still launch the inner model child with canonical MLX 0.31.2.

A valid Stretch 030 comparison must therefore use one identical runtime-portable workload harness in both variants, where only the child-interpreter selection changes from the historical hard-coded canonical path to the current outer `sys.executable`.

This portability change is harness-only and must be identical for CONTROL and TREATMENT. Model, oracle block, M5, H36, persistence, cleanup schedule, KV, numerical gates and resource policy remain unchanged.

## Repair policy

Fix2 may only:
1. preserve the already validated treatment environment;
2. correct the static failure-class invariant to `MLX_0320_RUNTIME_EXACTNESS_FAIL`;
3. route both ABBA variants through the same runtime-portable Stretch 027 workload;
4. force the inner child to inherit the currently selected CONTROL/TREATMENT interpreter via `sys.executable`;
5. start a fresh complete `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312` sequence.

Do not rerun Fix1. Do not reinstall the valid treatment venv. Do not reuse any data because no scientific data were produced.