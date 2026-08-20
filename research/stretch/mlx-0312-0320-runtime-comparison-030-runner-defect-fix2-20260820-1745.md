# Stretch 030 — Runner Fix2 venv-resolution defect — 2026-08-20 17:45

## Classification

`STRETCH_030_RUNNER_FIX2_ENV_PROVENANCE_DEFECT`

Scientific result: **NONE**.

No ABBA constituent launched.

## Observed execution

The already-provisioned treatment clone from Setup Fix1 remained valid:
- mlx 0.32.0
- mlx-metal 0.32.0
- mlx-lm 0.31.3
- transformers 5.12.1
- numpy 2.5.2
- safetensors 0.8.0
- Python 3.13.0.

Runner Fix2 then stopped at environment provenance before Attempt 1.

Observed CONTROL query:
- `python_executable = /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13`
- mlx = MISSING
- mlx-metal = MISSING
- mlx-lm = MISSING
- transformers = MISSING
- safetensors = MISSING.

Observed TREATMENT query remained valid at `.venvs/stretch030-mlx0320-fix1/bin/python` with mlx/mlx-metal 0.32.0.

## Root cause

Fix2 constructed the CONTROL interpreter as:

```python
(repo / CONTROL_VENV / "bin/python").resolve()
```

On this macOS venv, `bin/python` is a symlink to the framework Python. `Path.resolve()` dereferenced the symlink before process launch, so Python no longer entered the venv and queried the base framework environment instead.

The same semantic defect was also present in the runtime-portable workload callback:

```python
venv_py = Path(sys.executable).resolve()
```

That would have dereferenced either selected variant's venv interpreter before launching the inner model child. It was identified before any ABBA constituent launched.

## Harness-only correction

Fix3 must preserve the venv executable path without resolving the final `bin/python` symlink:

```python
control_python = repo / CONTROL_VENV / "bin/python"
venv_py = Path(sys.executable)
```

Path existence may still be checked, but the executable path itself must not be canonicalized through `resolve()`.

No model, M, H, persistence, cleanup, KV, exactness threshold, runtime package, ABBA order, metric, or resource policy changes are authorized by this fix.

## Evidence policy

- Preserve this failed Fix2 invocation.
- Do not reinterpret it as a runtime result.
- Do not rerun Fix2.
- Reuse the already validated Setup Fix1 treatment clone; no reinstall is required.
- Fix3 must start a fresh complete `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312` ABBA.
