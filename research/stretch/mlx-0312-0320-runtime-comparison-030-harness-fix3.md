# Stretch 030 — Harness Fix3 preregistration

Date: 2026-08-20

## Status

READY FOR FRESH SCIENTIFIC ABBA.

This amendment follows two pre-science runner defects. Neither launched Attempt 1 and neither produced scientific evidence.

## Preserved environment

Setup Fix1 already passed and must not be rerun:
- CONTROL venv: `results-local/mlx/venv-mlx-lm-0.31.3`
  - mlx 0.31.2
  - mlx-metal 0.31.2
- TREATMENT venv: `.venvs/stretch030-mlx0320-fix1`
  - mlx 0.32.0
  - mlx-metal 0.32.0
- both: Python 3.13.0, mlx-lm 0.31.3, transformers 5.12.1, numpy 2.5.2, safetensors 0.8.0.

## Fix2 defect being repaired

Fix2 used:

```python
control_python = (repo / CONTROL_VENV / "bin/python").resolve()
```

and the common portable workload generated:

```python
venv_py = Path(sys.executable).resolve()
```

On this macOS venv layout, `bin/python` is a symlink. Dereferencing it before process launch loses the venv identity and enters the framework/base Python, where MLX packages are missing.

## Fix3 harness-only change

CONTROL outer executable becomes:

```python
control_python = repo / CONTROL_VENV / "bin/python"
```

Inner child executable becomes:

```python
venv_py = Path(sys.executable)
```

The selected venv `bin/python` path is therefore preserved through both process boundaries.

## Frozen common workload

Portable Fix1:
`scripts/stretch_runtime_portable_single_pass_030_fix1.py`

It reuses the previous portable workload and changes only venv-symlink handling. The inherited scientific workload remains Stretch 027 SINGLE_PASS:
- Qwen3-8B 3-bit/group64
- M5
- H36
- all raw weights persistent
- one final cleanup/pass
- BF16 KV
- same oracle tokens
- same exact numerical/top-1/acceptance gates
- same I/O/resource policy.

Its inner version gate still allows only preregistered MLX `{0.31.2, 0.32.0}` and requires mlx-lm 0.31.3 / Transformers 5.12.1.

## Balanced runner

Fix3:
`scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix3.py`

It is a harness-only transform of frozen Fix2 and changes:
1. common workload path/blob to portable Fix1;
2. CONTROL executable path to preserve the venv symlink;
3. result root/harness revision metadata.

It does not change:
- runtime package versions;
- ABBA order;
- scientific metrics;
- failure classes;
- exactness thresholds;
- model/workload;
- resource gates.

## Fresh ABBA

`MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`

No constituent from prior failed preflights exists or may be reused.

## Outcomes

- first genuine MLX0320 frozen numerical/top-1/oracle failure: `MLX_0320_RUNTIME_EXACTNESS_FAIL`, valid scientific FAIL, stop/no rescue;
- complete exact ABBA: `MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS`;
- environment/harness/resource/runtime-provenance issue: `MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE`.

## Execution policy

Do not rerun setup. Do not run Fix1 or Fix2. Compile and run portable Fix1 + runner Fix3 only.
