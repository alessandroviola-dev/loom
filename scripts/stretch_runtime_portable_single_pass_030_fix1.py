#!/usr/bin/env python3
"""LOOM Stretch 030 — runtime-portable SINGLE_PASS workload harness Fix1.

Harness-only repair for macOS venv executable handling. Reuses the frozen
runtime-portable workload unchanged except that the inner child keeps the venv
`bin/python` path instead of dereferencing its symlink with Path.resolve().
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

SOURCE_PATH = Path("scripts/stretch_runtime_portable_single_pass_030.py")
SOURCE_BLOB = "16243fd78a6eb5a831c426e0c1e432a4f45db988"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo,
        capture_output=True, text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source_path = repo / SOURCE_PATH
    observed = git_blob(source_path, repo)

    print("LOOM Stretch 030 — Runtime-Portable SINGLE_PASS Workload FIX1")
    print(f"Frozen portable workload blob: {observed}")
    if observed != SOURCE_BLOB:
        print("Source provenance: FAIL")
        return 2

    portable = load_module(source_path, "loom_stretch030_portable_fix1_base")
    original_add_runtime_portable = portable.add_runtime_portable

    def add_runtime_portable_fix1(source: str) -> str:
        out = original_add_runtime_portable(source)
        old = "    venv_py = Path(sys.executable).resolve()\n"
        new = "    venv_py = Path(sys.executable)\n"
        count = out.count(old)
        if count != 1:
            raise RuntimeError(
                f"Stretch 030 portable Fix1 venv transform failed: expected 1 occurrence, found {count}"
            )
        out = out.replace(old, new, 1)
        if old in out or out.count(new) != 1:
            raise RuntimeError("Stretch 030 portable Fix1 venv postcondition failed")
        return out

    portable.add_runtime_portable = add_runtime_portable_fix1

    print("Source provenance: PASS")
    print("Harness Fix1 only: preserve selected venv bin/python symlink path for inner child")
    print("Scientific workload / two-version lock / M5 / H36 / persistence / cleanup / KV / gates: UNCHANGED")
    return portable.main()


if __name__ == "__main__":
    raise SystemExit(main())
