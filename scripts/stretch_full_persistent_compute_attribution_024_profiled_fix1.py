#!/usr/bin/env python3
"""LOOM Stretch 024 preflight fix1 for the profiled attribution helper.

The first, never-run profiling helper used an ambiguous two-line source anchor
when extending per-transformer cycle telemetry. This preflight-only wrapper
keeps the scientific/instrumentation design unchanged and patches only that
source-edit anchor to the unique transformer-cycle context before invoking the
frozen profiling helper.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_PROFILE_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled.py")
SOURCE_PROFILE_BLOB = "b9c233415386ce796a2331cbfd011881b844cb91"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
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
    source_path = repo / SOURCE_PROFILE_PATH
    observed = git_blob(source_path, repo)
    print("LOOM Stretch 024 — Full-Persistent Compute Attribution PROFILED preflight FIX1")
    print(f"Frozen profiling helper blob: {observed}")
    if observed != SOURCE_PROFILE_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Preflight fix only: disambiguate transformer-cycle telemetry source anchor")
    print("Scientific architecture / profiling boundaries / gates: UNCHANGED")

    profile = load_module(source_path, "loom_stretch024_profile_preflight_fix1")
    original_replace_once = profile.replace_once

    def patched_replace_once(text: str, old: str, new: str, label: str) -> str:
        if label != "cycle attribution walls":
            return original_replace_once(text, old, new, label)

        unique_old = '''                "layer_cache_offset_after": int(caches[layer_id].offset),\n                "layer_cache_nbytes_after": int(caches[layer_id].nbytes),\n                "materialize_wall_seconds": round(materialize_wall, 6),\n                "forward_wall_seconds": round(forward_wall, 6),\n'''
        unique_new = '''                "layer_cache_offset_after": int(caches[layer_id].offset),\n                "layer_cache_nbytes_after": int(caches[layer_id].nbytes),\n                "materialize_wall_seconds": round(materialize_wall, 6),\n                "forward_wall_seconds": round(forward_wall, 6),\n                "build_reuse_wall_seconds": round(build_wall, 6),\n                "cleanup_wall_seconds": round(cleanup_wall, 6),\n'''
        count = text.count(unique_old)
        if count != 1:
            raise RuntimeError(
                "Stretch 024 preflight fix1 transformer-cycle anchor invalid: "
                f"expected 1 occurrence, found {count}"
            )
        return text.replace(unique_old, unique_new, 1)

    profile.replace_once = patched_replace_once
    return int(profile.main())


if __name__ == "__main__":
    raise SystemExit(main())
