#!/usr/bin/env python3
"""LOOM Stretch 023 harness fix1 — balanced shared-stage comparison.

Reuses the frozen Stretch 023 comparison runner byte-for-byte except for:
1) routing the PERSISTENT constituent to the harness-fixed treatment helper;
2) routing outputs to a distinct fix1 result directory;
3) a terminal/summary identity marker for auditability.

Scientific design, ABBA order, metrics and gates are unchanged.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_RUNNER_PATH = Path("scripts/stretch_m5_h36_shared_streamed_persistent_comparison_023.py")
SOURCE_RUNNER_BLOB = "b8d69c218ee251662fc54a809ca6bf13a4a4e4da"
SOURCE_FIX_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py")
SOURCE_FIX_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 023 fix1 runner transform failed for {label}: "
            f"expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source_runner = repo / SOURCE_RUNNER_PATH
    source_fix = repo / SOURCE_FIX_PATH

    observed_runner = git_blob(source_runner, repo)
    observed_fix = git_blob(source_fix, repo)

    print("LOOM Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison HARNESS FIX1")
    print(f"Frozen original comparison runner blob: {observed_runner}")
    print(f"Harness-fixed PERSISTENT helper blob: {observed_fix}")
    if observed_runner != SOURCE_RUNNER_BLOB or observed_fix != SOURCE_FIX_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Scientific preregistration / ABBA order / metrics / gates: UNCHANGED")
    print("Failed 20260820-151540 attempt: PRESERVED; not reused")

    source = source_runner.read_text(encoding="utf-8")
    source = replace_once(
        source,
        'SOURCE_PERSISTENT_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py")',
        'SOURCE_PERSISTENT_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py")',
        "persistent helper path",
    )
    source = replace_once(
        source,
        'SOURCE_PERSISTENT_BLOB = "8c263e7be15441581e481e6f41cbd16f87d4df4b"',
        'SOURCE_PERSISTENT_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"',
        "persistent helper blob",
    )
    source = replace_once(
        source,
        'print("LOOM Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison")',
        'print("LOOM Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison HARNESS FIX1")',
        "terminal identity",
    )
    source = replace_once(
        source,
        '"experiment": "Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison",',
        '"experiment": "Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison — HARNESS FIX1",\n        "harness_revision": "fix1",',
        "summary identity",
    )
    source = replace_once(
        source,
        'root = repo / "results-local" / "stretch" / "m5-h36-shared-stage-persistence-023"',
        'root = repo / "results-local" / "stretch" / "m5-h36-shared-stage-persistence-023-fix1"',
        "result root",
    )

    required = [
        'RUN_ORDER = ["STREAMED", "PERSISTENT", "PERSISTENT", "STREAMED"]',
        'SOURCE_PERSISTENT_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"',
        '"harness_revision": "fix1"',
        'M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS',
        'SHARED_STAGE_COMPARISON_INCOMPLETE',
        'steady_state_rate_excludes_one_time_shared_setup',
        'estimated_shared_setup_break_even_target_blocks',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 023 fix1 runner invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(source_runner), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
