#!/usr/bin/env python3
"""LOOM Stretch 024 PROFILED harness fix2.

Harness-only repair of the never-completed Stretch 024 profiling path.
Fix1 already disambiguated the transformer-cycle telemetry source anchor.
Fix2 additionally replaces three invalid parent-side references to the child-local
`args.num_hidden_layers` with the already-frozen H36 geometry expressed as
`len(HOTSET_LAYER_IDS)`.

Scientific architecture, profiling boundaries, metrics, parity and resource gates
are unchanged.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_PROFILE_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled.py")
SOURCE_PROFILE_BLOB = "b9c233415386ce796a2331cbfd011881b844cb91"
SOURCE_FIX1_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py")
SOURCE_FIX1_BLOB = "845b10da26a70455cd40f483cea5d313f9ac12dd"


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


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 024 fix2 {label}: expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    profile_path = repo / SOURCE_PROFILE_PATH
    fix1_path = repo / SOURCE_FIX1_PATH
    observed_profile = git_blob(profile_path, repo)
    observed_fix1 = git_blob(fix1_path, repo)

    print("LOOM Stretch 024 — Full-Persistent Compute Attribution PROFILED FIX2")
    print(f"Frozen base profiling helper blob: {observed_profile}")
    print(f"Frozen preflight fix1 blob: {observed_fix1}")
    if observed_profile != SOURCE_PROFILE_BLOB or observed_fix1 != SOURCE_FIX1_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Harness fix2 only: parent layer geometry uses frozen H36 IDs, not child-local args")
    print("Profiling boundaries / model / M5 / H36 / full persistence / gates: UNCHANGED")

    profile = load_module(profile_path, "loom_stretch024_profile_fix2")
    original_replace_once = profile.replace_once
    original_add_compute_attribution = profile.add_compute_attribution

    # Preserve the exact preflight fix1 behavior for the unique transformer-cycle
    # telemetry anchor. The fix1 source is provenance-frozen above; its behavior
    # is reproduced here explicitly so this file is a standalone canonical entrypoint.
    def patched_replace_once(text: str, old: str, new: str, label: str) -> str:
        if label != "cycle attribution walls":
            return original_replace_once(text, old, new, label)

        unique_old = '''                "layer_cache_offset_after": int(caches[layer_id].offset),\n                "layer_cache_nbytes_after": int(caches[layer_id].nbytes),\n                "materialize_wall_seconds": round(materialize_wall, 6),\n                "forward_wall_seconds": round(forward_wall, 6),\n'''
        unique_new = '''                "layer_cache_offset_after": int(caches[layer_id].offset),\n                "layer_cache_nbytes_after": int(caches[layer_id].nbytes),\n                "materialize_wall_seconds": round(materialize_wall, 6),\n                "forward_wall_seconds": round(forward_wall, 6),\n                "build_reuse_wall_seconds": round(build_wall, 6),\n                "cleanup_wall_seconds": round(cleanup_wall, 6),\n'''
        count = text.count(unique_old)
        if count != 1:
            raise RuntimeError(
                "Stretch 024 fix2 transformer-cycle anchor invalid: "
                f"expected 1 occurrence, found {count}"
            )
        return text.replace(unique_old, unique_new, 1)

    def fixed_add_compute_attribution(source: str) -> str:
        transformed = original_add_compute_attribution(source)

        # These three expressions execute in the parent aggregation scope, where
        # `args` does not exist. H36 geometry is already frozen by provenance and
        # HOTSET_LAYER_IDS, so use that immutable runtime constant instead.
        transformed = replace_exact(
            transformed,
            "expected_profile_count = ORACLE_BLOCK_COUNT * args.num_hidden_layers",
            "expected_profile_count = ORACLE_BLOCK_COUNT * len(HOTSET_LAYER_IDS)",
            "expected profile count",
        )
        transformed = replace_exact(
            transformed,
            "layer_accum = {layer_id: [] for layer_id in range(args.num_hidden_layers)}",
            "layer_accum = {layer_id: [] for layer_id in range(len(HOTSET_LAYER_IDS))}",
            "layer accumulator geometry",
        )
        transformed = replace_exact(
            transformed,
            "if ids != list(range(args.num_hidden_layers)):",
            "if ids != list(range(len(HOTSET_LAYER_IDS))):",
            "profiled layer-id validation geometry",
        )
        return transformed

    profile.replace_once = patched_replace_once
    profile.add_compute_attribution = fixed_add_compute_attribution
    return int(profile.main())


if __name__ == "__main__":
    raise SystemExit(main())
