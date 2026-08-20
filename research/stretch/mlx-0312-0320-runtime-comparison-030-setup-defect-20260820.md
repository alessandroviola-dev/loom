# LOOM Stretch 030 — Pre-Run Environment Setup Defect — 2026-08-20

Status: **PRE-RUN HARNESS/ENVIRONMENT SETUP DEFECT — NO SCIENTIFIC RESULT**

## Observed failure

The initial environment setup utility was launched from the user's shell with:

```text
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
```

and reported:

```text
Control versions: {"mlx": "MISSING", "mlx-lm": "MISSING", "transformers": "MISSING", ...}
RuntimeError: canonical mlx must be 0.31.2, observed MISSING
```

The utility aborted before creating a valid treatment environment and before any balanced MLX 0.31.2/0.32.0 scientific constituent was executed.

Scientific result: **NONE**.

## Root cause 1 — wrong control interpreter assumption

The original setup and comparison harness assumed that `sys.executable` of the shell-side wrapper was the canonical MLX runtime.

That assumption is false for LOOM. The frozen Stretch execution chain uses:

```text
results-local/mlx/venv-mlx-lm-0.31.3/bin/python
```

for the actual MLX child workload. The shell-side Python is intentionally able to be a standard-library-only wrapper.

Therefore the failed setup inspected the wrong interpreter.

## Root cause 2 — venv inheritance policy was insufficient

The original setup planned to create a fresh venv with `--system-site-packages`. That does not inherit packages installed only in another venv, so it would not guarantee that `mlx-lm`, Transformers, NumPy, safetensors and the remaining canonical package set matched the actual LOOM MLX venv.

The repaired setup must derive the treatment from the canonical LOOM MLX venv itself.

## Packaging correction before science

On macOS the MLX Python distribution and its Metal backend are version-coupled (`mlx` + `mlx-metal`). A valid runtime comparison must therefore move both distributions together from 0.31.2 to 0.32.0. Installing `mlx==0.32.0 --no-deps` alone could leave `mlx-metal==0.31.2` and would not represent a coherent MLX 0.32.0 runtime.

This correction is made before any scientific Stretch 030 run and therefore does not modify observed scientific evidence.

## Fix policy

A harness-only/pre-run repair may:

1. Use the canonical control interpreter explicitly:
   `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`.
2. Verify the canonical environment has:
   - `mlx==0.31.2`
   - `mlx-metal==0.31.2`
   - `mlx-lm==0.31.3`
   - `transformers==5.12.1`.
3. Clone the canonical venv into a new treatment directory rather than inherit shell/system site-packages.
4. In the clone only, replace both `mlx` and `mlx-metal` with 0.32.0.
5. Verify all tracked non-MLX package versions remain identical between control and treatment.
6. Keep the canonical venv untouched.
7. Run a fresh complete ABBA; no setup failure data are reusable.

## Scientific design remains frozen

Unchanged:
- exact same Stretch 027 workload source/blob on both sides;
- Qwen3-8B 3-bit/group64;
- M=5;
- H36;
- full raw-weight persistence;
- one final cleanup/pass;
- mlx-lm 0.31.3;
- transformers 5.12.1;
- BF16 KV;
- oracle sequence and exactness/top-1/acceptance gates;
- resource/I-O policy;
- no deliberate cache purge;
- balanced order `MLX0312 -> MLX0320 -> MLX0320 -> MLX0312`;
- no automatic retry/rescue.

The scientific factor is the coherent MLX runtime version, represented on macOS by the coupled package pair `mlx` + `mlx-metal`: 0.31.2 -> 0.32.0.
