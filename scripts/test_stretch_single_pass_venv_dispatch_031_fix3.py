#!/usr/bin/env python3
"""Static no-model regression test for Stretch 031 Fix3 venv dispatch."""
from __future__ import annotations

from pathlib import Path

from stretch_single_pass_geometry_harness_031_fix3 import assert_no_venv_python_dereference, child_interpreter_info


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    guard = assert_no_venv_python_dereference(repo)
    provenance = child_interpreter_info(repo)
    print("Classification: STRETCH_031_FIX3_VENV_PATH_REGRESSION_GUARD_PASS")
    print(f"Launcher: {provenance['configured_launcher_path']}")
    print(f"Prefix: {provenance['expected_prefix']}")
    print(f"Runtime: {provenance['query']['versions']}")
    print(f"Scanned files: {len(guard['scanned_files'])}")
