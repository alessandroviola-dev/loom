#!/usr/bin/env python3
"""LOOM Stretch 030 — balanced MLX runtime comparison Fix3.

Harness-only repair over frozen Fix2. Preserves the selected venv executable
paths instead of dereferencing macOS `bin/python` symlinks with Path.resolve().
Uses the portable-workload Fix1 with the same correction for the inner child.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

SOURCE_FIX2_PATH = Path("scripts/stretch_mlx_0312_0320_runtime_comparison_030_fix2.py")
SOURCE_FIX2_BLOB = "6dd993418bff0bf9ec65c6b9a80f4bb382eb4976"
PORTABLE_FIX1_PATH = Path("scripts/stretch_runtime_portable_single_pass_030_fix1.py")
PORTABLE_FIX1_BLOB = "44251a524c77a379f43445444fa8a2643f1bfbdf"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo,
        capture_output=True, text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_count(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise RuntimeError(
            f"Stretch 030 Fix3 transform failed for {label}: expected {expected} occurrence(s), found {count}"
        )
    return text.replace(old, new)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    fix2_path = repo / SOURCE_FIX2_PATH
    portable_fix1_path = repo / PORTABLE_FIX1_PATH
    observed_fix2 = git_blob(fix2_path, repo)
    observed_portable = git_blob(portable_fix1_path, repo)

    print("LOOM Stretch 030 — Balanced MLX 0.31.2 vs 0.32.0 Runtime Comparison FIX3")
    print(f"Frozen Fix2 runner blob: {observed_fix2}")
    print(f"Portable workload Fix1 blob: {observed_portable}")
    if observed_fix2 != SOURCE_FIX2_BLOB or observed_portable != PORTABLE_FIX1_BLOB:
        print("Source provenance: FAIL")
        return 2

    source = fix2_path.read_text(encoding="utf-8")
    source = replace_count(
        source,
        "scripts/stretch_runtime_portable_single_pass_030.py",
        "scripts/stretch_runtime_portable_single_pass_030_fix1.py",
        3,
        "portable workload path references",
    )
    source = replace_count(
        source,
        "16243fd78a6eb5a831c426e0c1e432a4f45db988",
        PORTABLE_FIX1_BLOB,
        1,
        "portable workload blob",
    )
    source = replace_count(
        source,
        '(repo / CONTROL_VENV / "bin/python").resolve()',
        'repo / CONTROL_VENV / "bin/python"',
        1,
        "CONTROL venv executable symlink preservation",
    )
    source = replace_count(
        source,
        "fix2-runtime-portable",
        "fix3-venv-symlink-preserved",
        1,
        "harness revision",
    )
    source = replace_count(
        source,
        "mlx-0312-0320-runtime-comparison-030-fix2",
        "mlx-0312-0320-runtime-comparison-030-fix3",
        2,
        "result root references",
    )
    source = source.replace(
        "Runtime Comparison FIX2",
        "Runtime Comparison FIX3",
    )
    source = source.replace(
        "Harness Fix2: correct failure-class invariant + identical runtime-portable workload + child runtime provenance",
        "Harness Fix3: preserve venv executable symlink paths + identical portable Fix1 workload + child runtime provenance",
    )

    required = [
        'PORTABLE_WORKLOAD_PATH = Path("scripts/stretch_runtime_portable_single_pass_030_fix1.py")',
        PORTABLE_FIX1_BLOB,
        'control_python = repo / CONTROL_VENV / "bin/python"',
        'TREATMENT_VENV = Path(".venvs/stretch030-mlx0320-fix1")',
        '"MLX_0320_RUNTIME_EXACTNESS_FAIL"',
        'child_runtime_ok',
        'mlx-0312-0320-runtime-comparison-030-fix3',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 030 Fix3 invariant failed; missing {missing}")
    if '(repo / CONTROL_VENV / "bin/python").resolve()' in source:
        raise RuntimeError("Stretch 030 Fix3 invariant failed: CONTROL resolve remains")

    print("Source provenance: PASS")
    print("Validated Setup Fix1 treatment venv reused; no package installation")
    print("Scientific ABBA / runtime versions / workload / M5 / H36 / persistence / cleanup / KV / gates: UNCHANGED")
    print("Harness Fix3 only: venv bin/python paths are executed without Path.resolve()")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(fix2_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
