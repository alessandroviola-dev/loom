#!/usr/bin/env python3
"""LOOM Stretch 030 — runtime-portable Stretch 027 workload harness.

Harness-only derivative of the frozen Stretch 027 workload. Scientific workload
is unchanged. The sole harness portability repair makes the historical inner MLX
child inherit the Python interpreter that launched this script, allowing the same
exact workload to run under either the canonical 0.31.2 venv or the isolated
0.32.0 treatment venv.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_027_PATH = Path("scripts/stretch_full_persistent_single_pass_cleanup_027.py")
SOURCE_027_BLOB = "6636456df5a773ac6062fdad66b7dc96abe8bd81"


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


def inject_runtime_portable_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch027_apply_single_pass_cleanup(source)\n"
    if wrapper_source.count(anchor) != 1:
        raise RuntimeError(
            "Stretch 030 portable wrapper invariant failed: Stretch 027 callback missing/ambiguous"
        )
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch030_apply_runtime_portable(source)\n",
        1,
    )


def add_runtime_portable(source: str) -> str:
    old = '    venv_py = mlx_root / "venv-mlx-lm-0.31.3" / "bin" / "python"\n'
    new = '    venv_py = Path(sys.executable).resolve()\n'
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 030 portable child-interpreter transform failed: expected 1 occurrence, found {count}"
        )
    source = source.replace(old, new, 1)
    if old in source or source.count(new) != 1:
        raise RuntimeError("Stretch 030 portable child-interpreter postcondition failed")
    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source027_path = repo / SOURCE_027_PATH
    observed027 = git_blob(source027_path, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 030 — Runtime-Portable SINGLE_PASS Workload")
        print(f"Frozen Stretch 027 blob: {observed027}")
        print(f"Outer interpreter / inherited child interpreter: {Path(sys.executable).resolve()}")
        print("Scientific workload: UNCHANGED")
        print("Harness-only change: historical hard-coded MLX child venv -> current sys.executable")

    if observed027 != SOURCE_027_BLOB:
        print(
            f"Source provenance: FAIL Stretch027={observed027} expected={SOURCE_027_BLOB}",
            file=sys.stderr,
        )
        return 2

    s027 = load_module(source027_path, "loom_stretch027_for_030_portable")

    paths = {
        "s026": repo / s027.SOURCE_026_PATH,
        "s025": repo / s027.SOURCE_025_PATH,
        "fix1": repo / s027.SOURCE_FIX1_PATH,
        "broken": repo / s027.SOURCE_BROKEN_PATH,
        "h36": repo / s027.SOURCE_H36_PATH,
        "s017": repo / s027.SOURCE_017_PATH,
        "s013": repo / s027.SOURCE_013_PATH,
    }
    expected = {
        "s026": s027.SOURCE_026_BLOB,
        "s025": s027.SOURCE_025_BLOB,
        "fix1": s027.SOURCE_FIX1_BLOB,
        "broken": s027.SOURCE_BROKEN_BLOB,
        "h36": s027.SOURCE_H36_BLOB,
        "s017": s027.SOURCE_017_BLOB,
        "s013": s027.SOURCE_013_BLOB,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}
    if observed != expected:
        print(f"Source provenance: FAIL inherited={observed} expected={expected}", file=sys.stderr)
        return 2

    s026 = load_module(paths["s026"], "loom_stretch026_for_030_portable")
    s025 = load_module(paths["s025"], "loom_stretch025_for_030_portable")
    shared_fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_030_portable")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_030_portable")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_030_portable")
    stretch017 = load_module(paths["s017"], "loom_stretch017_for_030_portable")

    wrapper = h36.transformed_013_wrapper(
        paths["s013"].read_text(encoding="utf-8"), stretch017
    )
    wrapper = shared_fix1.inject_runtime_callback(wrapper)
    wrapper = s025.inject_cleanup_callback(wrapper)
    wrapper = s026.inject_shared_cleanup_callback(wrapper)
    wrapper = s027.inject_single_pass_callback(wrapper)
    wrapper = inject_runtime_portable_callback(wrapper)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "__stretch027_apply_single_pass_cleanup(source)",
        "__stretch030_apply_runtime_portable(source)",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 030 portable wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": s025.add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": s026.add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": s027.add_single_pass_cleanup,
        "__stretch030_apply_runtime_portable": add_runtime_portable,
    }

    if not is_child:
        print("Source provenance: PASS")
        print("M5 / H36 / full persistence / single cleanup / model / KV / gates: UNCHANGED")

    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
