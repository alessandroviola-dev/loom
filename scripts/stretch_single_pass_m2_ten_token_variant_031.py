#!/usr/bin/env python3
"""LOOM Stretch 031 — M2 ten-token SINGLE_PASS treatment.

Reconstructs the frozen Stretch 027 M5/H36/full-persistent/single-cleanup workload
and changes only oracle block geometry for the controlled Stretch 031 comparison:
10 frozen oracle tokens are verified as five M=2 blocks instead of two M=5 blocks.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_027_PATH = Path("scripts/stretch_full_persistent_single_pass_cleanup_027.py")
SOURCE_027_BLOB = "6636456df5a773ac6062fdad66b7dc96abe8bd81"
TEN_TOKEN_ORACLE = "[1,374,264,4647,1483,304,279,1809,315,5994]"
EXPECTED_CLASSIFICATION = "SINGLE_PASS_M2_TEN_TOKEN_GEOMETRY_PASS"


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


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 031 M2 transform failed for {label}: expected 1 occurrence, found {count}"
        )
    return source.replace(old, new, 1)


def replace_all(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count < 1:
        raise RuntimeError(f"Stretch 031 M2 transform failed for {label}: source text missing")
    return source.replace(old, new)


def inject_geometry_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch027_apply_single_pass_cleanup(source)\n"
    if wrapper_source.count(anchor) != 1:
        raise RuntimeError("Stretch 031 M2 wrapper invariant failed: Stretch 027 callback missing")
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch031_apply_geometry(source)\n",
        1,
    )


def add_geometry(source: str) -> str:
    source = replace_once(
        source,
        "ORACLE_BLOCK_SIZE = 5\n",
        "ORACLE_BLOCK_SIZE = 2\n",
        "M2 block size",
    )
    source = replace_once(
        source,
        "ORACLE_BLOCK_COUNT = 3\n",
        "ORACLE_BLOCK_COUNT = 5\n",
        "M2 ten-token block count",
    )
    source = replace_once(
        source,
        "ORACLE_SEQUENCE = [1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8]\n",
        f"ORACLE_SEQUENCE = {TEN_TOKEN_ORACLE}\n",
        "ten-token oracle prefix",
    )
    source = replace_once(
        source,
        "GENERATED_TOKENS = 15\n",
        "GENERATED_TOKENS = 10\n",
        "ten-token resident continuation",
    )
    source = replace_all(
        source,
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        EXPECTED_CLASSIFICATION,
        "PASS classification",
    )
    source = replace_all(
        source,
        "LOOM Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
        "LOOM Stretch 031 — M2 Ten-Token H36 Full-Persistent Single-Pass Treatment",
        "terminal title",
    )
    source = replace_all(
        source,
        "Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
        "Stretch 031 — M2 Ten-Token H36 Full-Persistent Single-Pass Treatment",
        "summary title",
    )
    source = replace_all(
        source,
        "five-token-h36-full-persistent-single-pass-cleanup-027",
        "m2-ten-token-single-pass-treatment-031",
        "run directory",
    )

    required = [
        "ORACLE_BLOCK_SIZE = 2",
        "ORACLE_BLOCK_COUNT = 5",
        "GENERATED_TOKENS = 10",
        f"ORACLE_SEQUENCE = {TEN_TOKEN_ORACLE}",
        EXPECTED_CLASSIFICATION,
        '"policy": "single_cleanup_after_full_pass"',
        "HOTSET_LAYER_IDS = tuple(range(36))",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 031 M2 runtime invariant failed; missing {missing}")
    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source027_path = repo / SOURCE_027_PATH
    observed027 = git_blob(source027_path, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 031 — M2 Ten-Token SINGLE_PASS Treatment")
        print(f"Frozen Stretch 027 blob: {observed027}")
    if observed027 != SOURCE_027_BLOB:
        print(f"Source provenance: FAIL Stretch027={observed027}", file=sys.stderr)
        return 2

    s027 = load_module(source027_path, "loom_stretch027_for_031_m2")
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

    s026 = load_module(paths["s026"], "loom_stretch026_for_031_m2")
    s025 = load_module(paths["s025"], "loom_stretch025_for_031_m2")
    fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_031_m2")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_031_m2")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_031_m2")
    stretch017 = load_module(paths["s017"], "loom_stretch017_for_031_m2")

    wrapper = h36.transformed_013_wrapper(
        paths["s013"].read_text(encoding="utf-8"), stretch017
    )
    wrapper = fix1.inject_runtime_callback(wrapper)
    wrapper = s025.inject_cleanup_callback(wrapper)
    wrapper = s026.inject_shared_cleanup_callback(wrapper)
    wrapper = s027.inject_single_pass_callback(wrapper)
    wrapper = inject_geometry_callback(wrapper)

    required_wrapper = [
        "__stretch027_apply_single_pass_cleanup(source)",
        "__stretch031_apply_geometry(source)",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required_wrapper if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 031 M2 wrapper invariant failed; missing {missing}")

    if not is_child:
        print("Source provenance: PASS")
        print("Scientific factor: oracle target block size M5 -> M2 at identical 10-token depth")
        print("MLX 0.31.2 / H36 / full persistence / single cleanup / model / KV / gates: UNCHANGED")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": s025.add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": s026.add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": s027.add_single_pass_cleanup,
        "__stretch031_apply_geometry": add_geometry,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
