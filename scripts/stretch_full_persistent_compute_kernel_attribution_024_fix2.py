#!/usr/bin/env python3
"""LOOM Stretch 024 balanced runner harness fix2.

Standalone canonical runner for the repaired Stretch 024 experiment. It keeps the
original balanced runner logic, carries forward the never-run runner-fix1 consumer
correction, routes PROFILED to the parent-geometry fix2 helper, and writes to a
new result directory. Scientific design, ABBA order, metrics and gates are unchanged.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_RUNNER_PATH = Path("scripts/stretch_full_persistent_compute_kernel_attribution_024.py")
SOURCE_RUNNER_BLOB = "88ef0115d7b806d52d390fb660c852ff96b9fc84"
SOURCE_RUNNER_FIX1_PATH = Path("scripts/stretch_full_persistent_compute_kernel_attribution_024_fix1.py")
SOURCE_RUNNER_FIX1_BLOB = "f298d32f39cbed6410a1d395a735fce819f354f3"
SOURCE_PROFILED_FIX2_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py")
SOURCE_PROFILED_FIX2_BLOB = "83f9e12dfa30445810ca4d39150dbcd151ad3e66"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 024 runner fix2 {label}: expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    base_path = repo / SOURCE_RUNNER_PATH
    fix1_path = repo / SOURCE_RUNNER_FIX1_PATH
    profiled_fix2_path = repo / SOURCE_PROFILED_FIX2_PATH

    observed_base = git_blob(base_path, repo)
    observed_fix1 = git_blob(fix1_path, repo)
    observed_profiled_fix2 = git_blob(profiled_fix2_path, repo)

    print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution runner FIX2")
    print(f"Frozen base runner blob: {observed_base}")
    print(f"Frozen runner preflight fix1 blob: {observed_fix1}")
    print(f"PROFILED harness fix2 blob: {observed_profiled_fix2}")
    if (
        observed_base != SOURCE_RUNNER_BLOB
        or observed_fix1 != SOURCE_RUNNER_FIX1_BLOB
        or observed_profiled_fix2 != SOURCE_PROFILED_FIX2_BLOB
    ):
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Harness fix2 only: repaired PROFILED parent geometry + preserved runner consumer fix1")
    print("Scientific design / CONTROL / ABBA / component boundaries / gates: UNCHANGED")
    print("Failed 20260820-155313 sequence: PRESERVED; no measurements reused")

    source = base_path.read_text(encoding="utf-8")

    # Route only the PROFILED constituent to the repaired helper.
    source = replace_once(
        source,
        'SOURCE_PROFILED_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py")',
        'SOURCE_PROFILED_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py")',
        "PROFILED helper path",
    )
    source = replace_once(
        source,
        'SOURCE_PROFILED_BLOB = "845b10da26a70455cd40f483cea5d313f9ac12dd"',
        'SOURCE_PROFILED_BLOB = "83f9e12dfa30445810ca4d39150dbcd151ad3e66"',
        "PROFILED helper blob",
    )

    # Carry forward runner fix1 exactly: the helper exports only its eight
    # slowest layer candidates, not an `all_layer_means` field.
    source = replace_once(
        source,
        '        for row in ca["all_layer_means"]:\n',
        '        for row in ca.get("slowest_layers_by_mean_profiled_compute", []):\n',
        "profiled layer candidate field",
    )

    source = replace_once(
        source,
        'run_dir = repo / "results-local" / "stretch" / "full-persistent-compute-kernel-attribution-024" / run_id',
        'run_dir = repo / "results-local" / "stretch" / "full-persistent-compute-kernel-attribution-024-fix2" / run_id',
        "result directory",
    )
    source = replace_once(
        source,
        'print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution")',
        'print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution runner FIX2")',
        "terminal identity",
    )
    source = replace_once(
        source,
        '"experiment": "Stretch 024 — Full-Persistent Compute/Kernel Attribution",',
        '"experiment": "Stretch 024 — Full-Persistent Compute/Kernel Attribution — runner FIX2",\n        "harness_revision": "runner-fix2",',
        "summary identity",
    )

    required = [
        'RUN_ORDER = ["CONTROL", "PROFILED", "PROFILED", "CONTROL"]',
        'SOURCE_PROFILED_BLOB = "83f9e12dfa30445810ca4d39150dbcd151ad3e66"',
        'FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS',
        'COMPUTE_ATTRIBUTION_INCOMPLETE',
        'slowest_layers_by_mean_profiled_compute',
        '"harness_revision": "runner-fix2"',
        'instrumentation perturbation only; not a target optimization result',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 024 runner fix2 invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(base_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
