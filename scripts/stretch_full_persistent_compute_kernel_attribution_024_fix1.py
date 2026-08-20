#!/usr/bin/env python3
"""LOOM Stretch 024 runner preflight fix1.

The never-run base runner expected an `all_layer_means` field while the frozen
PROFILED helper exports `slowest_layers_by_mean_profiled_compute`. This wrapper
changes only that consumer key and routes output to a distinct fix1 directory.
Scientific design, ABBA order, gates and component timing are unchanged.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_RUNNER_PATH = Path("scripts/stretch_full_persistent_compute_kernel_attribution_024.py")
SOURCE_RUNNER_BLOB = "88ef0115d7b806d52d390fb660c852ff96b9fc84"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Stretch 024 runner fix1 {label}: expected 1, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source_path = repo / SOURCE_RUNNER_PATH
    observed = git_blob(source_path, repo)
    print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution runner FIX1")
    print(f"Frozen base runner blob: {observed}")
    if observed != SOURCE_RUNNER_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Preflight fix only: consume exported slowest-layer candidate field")
    print("Scientific design / ABBA / gates / metrics: UNCHANGED")

    source = source_path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        '        for row in ca["all_layer_means"]:\n',
        '        for row in ca.get("slowest_layers_by_mean_profiled_compute", []):\n',
        "profiled layer candidate field",
    )
    source = replace_once(
        source,
        'run_dir = repo / "results-local" / "stretch" / "full-persistent-compute-kernel-attribution-024" / run_id',
        'run_dir = repo / "results-local" / "stretch" / "full-persistent-compute-kernel-attribution-024-fix1" / run_id',
        "result directory",
    )
    source = replace_once(
        source,
        'print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution")',
        'print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution runner FIX1")',
        "terminal identity",
    )
    source = replace_once(
        source,
        '"experiment": "Stretch 024 — Full-Persistent Compute/Kernel Attribution",',
        '"experiment": "Stretch 024 — Full-Persistent Compute/Kernel Attribution — runner FIX1",\n        "harness_revision": "runner-fix1",',
        "summary identity",
    )

    required = [
        'RUN_ORDER = ["CONTROL", "PROFILED", "PROFILED", "CONTROL"]',
        'FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS',
        'COMPUTE_ATTRIBUTION_INCOMPLETE',
        'slowest_layers_by_mean_profiled_compute',
        '"harness_revision": "runner-fix1"',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 024 runner fix1 invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(source_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
