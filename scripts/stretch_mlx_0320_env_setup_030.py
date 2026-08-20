#!/usr/bin/env python3
"""LOOM Stretch 030 — provision isolated MLX 0.32.0 treatment environment.

This is a PRE-RUN environment setup utility, not a scientific constituent.
It creates a venv that inherits the canonical Python environment and overlays
ONLY mlx==0.32.0 with --no-deps. The canonical environment is not modified.
"""
from __future__ import annotations

import importlib.metadata as md
import json
import subprocess
import sys
from pathlib import Path

TARGET_MLX = "0.32.0"
EXPECTED_CONTROL_MLX = "0.31.2"
EXPECTED_MLX_LM = "0.31.3"
EXPECTED_TRANSFORMERS = "5.12.1"
VENV_REL = Path(".venvs/stretch030-mlx0320")
MARKER_NAME = "loom_stretch030_env.json"


def version(dist: str) -> str:
    try:
        return md.version(dist)
    except md.PackageNotFoundError:
        return "MISSING"


def run_checked(cmd: list[str], cwd: Path) -> None:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(cmd)}")


def query_env(python: Path, repo: Path) -> dict:
    code = r'''
import importlib.metadata as md, json, platform, sys
names = ["mlx", "mlx-lm", "transformers", "numpy", "safetensors"]
out = {"python": sys.version.split()[0], "python_executable": sys.executable, "platform": platform.platform()}
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
    control = {
        "mlx": version("mlx"),
        "mlx-lm": version("mlx-lm"),
        "transformers": version("transformers"),
        "numpy": version("numpy"),
        "safetensors": version("safetensors"),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
    }

    print("LOOM Stretch 030 — isolated MLX 0.32.0 environment setup")
    print("Canonical environment will NOT be modified")
    print("Treatment overlay: mlx==0.32.0 --no-deps")
    print("Control versions:", json.dumps(control, sort_keys=True))

    if control["mlx"] != EXPECTED_CONTROL_MLX:
        raise RuntimeError(f"canonical mlx must be {EXPECTED_CONTROL_MLX}, observed {control['mlx']}")
    if control["mlx-lm"] != EXPECTED_MLX_LM:
        raise RuntimeError(f"canonical mlx-lm must be {EXPECTED_MLX_LM}, observed {control['mlx-lm']}")
    if control["transformers"] != EXPECTED_TRANSFORMERS:
        raise RuntimeError(
            f"canonical transformers must be {EXPECTED_TRANSFORMERS}, observed {control['transformers']}"
        )

    venv = repo / VENV_REL
    python = venv / "bin/python"
    marker = venv / MARKER_NAME

    if not python.is_file():
        if venv.exists():
            raise RuntimeError(
                f"incomplete existing treatment venv at {venv}; remove it manually before provisioning"
            )
        venv.parent.mkdir(parents=True, exist_ok=True)
        run_checked([sys.executable, "-m", "venv", "--system-site-packages", str(venv)], repo)
        run_checked(
            [str(python), "-m", "pip", "install", "--disable-pip-version-check", "--no-deps", f"mlx=={TARGET_MLX}"],
            repo,
        )
    else:
        print(f"Existing treatment venv found: {venv}; validating without reinstall")

    treatment = query_env(python, repo)
    print("Treatment versions:", json.dumps(treatment, sort_keys=True))

    required = {
        "mlx": TARGET_MLX,
        "mlx-lm": EXPECTED_MLX_LM,
        "transformers": EXPECTED_TRANSFORMERS,
        "numpy": control["numpy"],
        "safetensors": control["safetensors"],
        "python": control["python"],
    }
    mismatches = {
        key: {"expected": expected, "observed": treatment.get(key)}
        for key, expected in required.items()
        if treatment.get(key) != expected
    }
    if mismatches:
        raise RuntimeError(f"treatment environment mismatch: {mismatches}")

    record = {
        "experiment": "Stretch 030 — isolated MLX runtime treatment environment",
        "scientific_run": False,
        "venv": str(VENV_REL),
        "control": control,
        "treatment": treatment,
        "only_intended_package_difference": {"mlx": [EXPECTED_CONTROL_MLX, TARGET_MLX]},
        "install_policy": "venv --system-site-packages; pip install --no-deps mlx==0.32.0",
    }
    marker.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    print("Environment setup: PASS")
    print(f"Marker: {marker}")
    print("No scientific measurement has been run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
