#!/usr/bin/env python3
"""LOOM Stretch 030 — balanced MLX 0.31.2 vs 0.32.0 comparison, Fix1.

Harness/pre-run provenance repair only. Reuses the frozen original scientific
runner logic, but points CONTROL at the canonical LOOM MLX venv and TREATMENT at
the cloned coherent MLX 0.32.0 venv. The macOS MLX runtime factor is represented
by the coupled mlx + mlx-metal package pair.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ORIGINAL_RUNNER_PATH = Path("scripts/stretch_mlx_0312_0320_runtime_comparison_030.py")
ORIGINAL_RUNNER_BLOB = "0d0a27549067cef61a1dca7d3bf8f0e1f954d98b"
SETUP_FIX1_PATH = Path("scripts/stretch_mlx_0320_env_setup_030_fix1.py")
SETUP_FIX1_BLOB = "dfcc05aa6f730756056a75d5bf867bbd717ac31f"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo,
        capture_output=True, text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 030 Fix1 runner transform failed for {label}: expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    original_path = repo / ORIGINAL_RUNNER_PATH
    setup_fix1 = repo / SETUP_FIX1_PATH
    observed_original = git_blob(original_path, repo)
    observed_setup = git_blob(setup_fix1, repo)

    print("LOOM Stretch 030 — Balanced MLX 0.31.2 vs 0.32.0 Runtime Comparison FIX1")
    print(f"Frozen original runner blob: {observed_original}")
    print(f"Environment setup FIX1 blob: {observed_setup}")
    if observed_original != ORIGINAL_RUNNER_BLOB or observed_setup != SETUP_FIX1_BLOB:
        print("Source provenance: FAIL")
        return 2

    source = original_path.read_text(encoding="utf-8")

    source = replace_once(
        source,
        'SETUP_PATH = Path("scripts/stretch_mlx_0320_env_setup_030.py")',
        'SETUP_PATH = Path("scripts/stretch_mlx_0320_env_setup_030_fix1.py")',
        "setup path",
    )
    source = replace_once(
        source,
        'SETUP_BLOB = "fde39967be02cba81ea14bb043c9fdacd24db861"',
        f'SETUP_BLOB = "{SETUP_FIX1_BLOB}"',
        "setup blob",
    )
    source = replace_once(
        source,
        'TREATMENT_VENV = Path(".venvs/stretch030-mlx0320")',
        'CONTROL_VENV = Path("results-local/mlx/venv-mlx-lm-0.31.3")\nTREATMENT_VENV = Path(".venvs/stretch030-mlx0320-fix1")',
        "canonical/treatment venvs",
    )
    source = replace_once(
        source,
        'ENV_MARKER = "loom_stretch030_env.json"',
        'ENV_MARKER = "loom_stretch030_env_fix1.json"',
        "marker name",
    )
    source = replace_once(
        source,
        'EXPECTED_TREATMENT_MLX = "0.32.0"',
        'EXPECTED_TREATMENT_MLX = "0.32.0"\nEXPECTED_CONTROL_MLX_METAL = "0.31.2"\nEXPECTED_TREATMENT_MLX_METAL = "0.32.0"',
        "mlx-metal expected versions",
    )
    source = replace_once(
        source,
        'names = ["mlx", "mlx-lm", "transformers", "numpy", "safetensors"]',
        'names = ["mlx", "mlx-metal", "mlx-lm", "transformers", "numpy", "safetensors"]',
        "environment query distributions",
    )
    source = replace_once(
        source,
        '    control_python = Path(sys.executable).resolve()\n',
        '    control_python = (repo / CONTROL_VENV / "bin/python").resolve()\n    if not control_python.is_file():\n        print(f"Canonical control interpreter missing: {control_python}", file=sys.stderr)\n        return 2\n',
        "canonical control interpreter",
    )
    source = replace_once(
        source,
        '        control_env.get("mlx") == EXPECTED_CONTROL_MLX\n        and treatment_env.get("mlx") == EXPECTED_TREATMENT_MLX\n',
        '        control_env.get("mlx") == EXPECTED_CONTROL_MLX\n        and control_env.get("mlx-metal") == EXPECTED_CONTROL_MLX_METAL\n        and treatment_env.get("mlx") == EXPECTED_TREATMENT_MLX\n        and treatment_env.get("mlx-metal") == EXPECTED_TREATMENT_MLX_METAL\n',
        "coherent MLX package-pair provenance",
    )
    source = replace_once(
        source,
        '        and marker.get("treatment", {}).get("mlx") == EXPECTED_TREATMENT_MLX\n',
        '        and marker.get("control", {}).get("mlx") == EXPECTED_CONTROL_MLX\n        and marker.get("control", {}).get("mlx-metal") == EXPECTED_CONTROL_MLX_METAL\n        and marker.get("treatment", {}).get("mlx") == EXPECTED_TREATMENT_MLX\n        and marker.get("treatment", {}).get("mlx-metal") == EXPECTED_TREATMENT_MLX_METAL\n',
        "marker runtime-pair provenance",
    )
    source = replace_once(
        source,
        'print("Scientific factor: mlx 0.31.2 -> mlx 0.32.0 ONLY")',
        'print("Scientific factor: coherent macOS MLX runtime (mlx + mlx-metal) 0.31.2 -> 0.32.0 ONLY")',
        "scientific factor display",
    )
    source = replace_once(
        source,
        '"scientific_factor": "MLX runtime 0.31.2 -> 0.32.0 only",',
        '"scientific_factor": "coherent macOS MLX runtime package pair (mlx + mlx-metal) 0.31.2 -> 0.32.0 only",\n        "harness_revision": "fix1",',
        "scientific factor metadata",
    )
    source = replace_once(
        source,
        '"mlx-0312-0320-runtime-comparison-030"',
        '"mlx-0312-0320-runtime-comparison-030-fix1"',
        "result root",
    )

    required = [
        'RUN_ORDER = ["MLX0312", "MLX0320", "MLX0320", "MLX0312"]',
        'CONTROL_VENV = Path("results-local/mlx/venv-mlx-lm-0.31.3")',
        'TREATMENT_VENV = Path(".venvs/stretch030-mlx0320-fix1")',
        'EXPECTED_CONTROL_MLX_METAL = "0.31.2"',
        'EXPECTED_TREATMENT_MLX_METAL = "0.32.0"',
        '"MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS"',
        '"MLX_0320_RUNTIME_NUMERICAL_PARITY_FAIL"',
        '"MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE"',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 030 Fix1 runner invariant failed; missing {missing}")

    print("Source provenance: PASS")
    print("Scientific ABBA / workload / exactness / resource gates: UNCHANGED")
    print("Harness Fix1: explicit canonical LOOM venv + coherent mlx/mlx-metal treatment pair")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(original_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
