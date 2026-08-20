#!/usr/bin/env python3
"""LOOM Stretch 030 — isolated MLX 0.32.0 environment setup, Fix1.

PRE-RUN provisioning only. The canonical LOOM MLX venv is never modified.
Fix1 clones the exact canonical venv and changes only the coherent macOS MLX
runtime package pair: mlx + mlx-metal 0.31.2 -> 0.32.0.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

TARGET_MLX = "0.32.0"
EXPECTED_CONTROL_MLX = "0.31.2"
EXPECTED_MLX_LM = "0.31.3"
EXPECTED_TRANSFORMERS = "5.12.1"
CANONICAL_VENV_REL = Path("results-local/mlx/venv-mlx-lm-0.31.3")
TREATMENT_VENV_REL = Path(".venvs/stretch030-mlx0320-fix1")
MARKER_NAME = "loom_stretch030_env_fix1.json"
TRACKED_DISTS = ["mlx", "mlx-metal", "mlx-lm", "transformers", "numpy", "safetensors"]


def run_checked(cmd: list[str], cwd: Path) -> None:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(cmd)}")


def query_env(python: Path, repo: Path) -> dict:
    code = r'''
import importlib.metadata as md, json, platform, sys
names = ["mlx", "mlx-metal", "mlx-lm", "transformers", "numpy", "safetensors"]
out = {
    "python": sys.version.split()[0],
    "python_executable": sys.executable,
    "prefix": sys.prefix,
    "platform": platform.platform(),
}
for name in names:
    try:
        out[name] = md.version(name)
    except md.PackageNotFoundError:
        out[name] = "MISSING"
print(json.dumps(out, sort_keys=True))
'''
    proc = subprocess.run([str(python), "-c", code], cwd=repo, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"environment query failed for {python}: {proc.stderr.strip()}")
    return json.loads(proc.stdout.strip())


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    canonical_venv = repo / CANONICAL_VENV_REL
    canonical_python = canonical_venv / "bin/python"
    treatment_venv = repo / TREATMENT_VENV_REL
    treatment_python = treatment_venv / "bin/python"
    marker = treatment_venv / MARKER_NAME

    print("LOOM Stretch 030 — isolated MLX 0.32.0 environment setup FIX1")
    print(f"Canonical LOOM venv: {canonical_venv}")
    print("Canonical environment will NOT be modified")
    print("Treatment policy: clone canonical venv, then replace mlx + mlx-metal with 0.32.0 only")

    if not canonical_python.is_file():
        raise RuntimeError(f"canonical LOOM MLX python missing: {canonical_python}")

    control = query_env(canonical_python, repo)
    print("Canonical versions:", json.dumps(control, sort_keys=True))

    expected_control = {
        "mlx": EXPECTED_CONTROL_MLX,
        "mlx-metal": EXPECTED_CONTROL_MLX,
        "mlx-lm": EXPECTED_MLX_LM,
        "transformers": EXPECTED_TRANSFORMERS,
    }
    control_mismatches = {
        key: {"expected": expected, "observed": control.get(key)}
        for key, expected in expected_control.items()
        if control.get(key) != expected
    }
    if control_mismatches:
        raise RuntimeError(f"canonical LOOM environment mismatch: {control_mismatches}")

    if not treatment_python.is_file():
        if treatment_venv.exists():
            raise RuntimeError(
                f"incomplete existing treatment clone at {treatment_venv}; preserve it and inspect manually"
            )
        treatment_venv.parent.mkdir(parents=True, exist_ok=True)
        print(f"Cloning canonical venv -> {treatment_venv}")
        shutil.copytree(canonical_venv, treatment_venv, symlinks=True)
        run_checked(
            [
                str(treatment_python), "-m", "pip", "install",
                "--disable-pip-version-check", "--no-deps", "--upgrade",
                f"mlx=={TARGET_MLX}", f"mlx-metal=={TARGET_MLX}",
            ],
            repo,
        )
    else:
        print(f"Existing treatment clone found: {treatment_venv}; validating without reinstall")

    treatment = query_env(treatment_python, repo)
    print("Treatment versions:", json.dumps(treatment, sort_keys=True))

    required_treatment = {
        "mlx": TARGET_MLX,
        "mlx-metal": TARGET_MLX,
        "mlx-lm": EXPECTED_MLX_LM,
        "transformers": EXPECTED_TRANSFORMERS,
        "numpy": control["numpy"],
        "safetensors": control["safetensors"],
        "python": control["python"],
    }
    mismatches = {
        key: {"expected": expected, "observed": treatment.get(key)}
        for key, expected in required_treatment.items()
        if treatment.get(key) != expected
    }
    if mismatches:
        raise RuntimeError(f"treatment environment mismatch: {mismatches}")

    non_runtime_diffs = {
        key: {"control": control.get(key), "treatment": treatment.get(key)}
        for key in TRACKED_DISTS
        if key not in {"mlx", "mlx-metal"} and control.get(key) != treatment.get(key)
    }
    if non_runtime_diffs:
        raise RuntimeError(f"unexpected non-MLX package differences: {non_runtime_diffs}")

    record = {
        "experiment": "Stretch 030 — isolated coherent MLX 0.32.0 runtime environment FIX1",
        "scientific_run": False,
        "canonical_venv": str(CANONICAL_VENV_REL),
        "treatment_venv": str(TREATMENT_VENV_REL),
        "control": control,
        "treatment": treatment,
        "scientific_runtime_factor": {
            "mlx": [EXPECTED_CONTROL_MLX, TARGET_MLX],
            "mlx-metal": [EXPECTED_CONTROL_MLX, TARGET_MLX],
        },
        "install_policy": "clone canonical LOOM venv; pip --no-deps --upgrade mlx==0.32.0 mlx-metal==0.32.0 in clone only",
        "canonical_modified": False,
    }
    marker.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    print("Environment setup FIX1: PASS")
    print(f"Marker: {marker}")
    print("No scientific measurement has been run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
