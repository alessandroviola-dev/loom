#!/usr/bin/env python3
"""LOOM Stretch 023 harness fix1 — M5/H36 full-weight persistence.

Harness-only repair of the frozen Stretch 023 treatment helper. The original
helper applied add_shared_persistence() to the transformed Stretch 013 wrapper
text instead of to the final generated M5/H36 runtime source. This revision
preserves the original shared-persistence transform byte-for-byte and injects
that callback into the wrapper immediately before its final runtime invariants.

Scientific design is unchanged.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_BROKEN_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py")
SOURCE_BROKEN_BLOB = "8c263e7be15441581e481e6f41cbd16f87d4df4b"
SOURCE_H36_PATH = Path("scripts/stretch_five_token_h36_hotset_variant_022.py")
SOURCE_H36_BLOB = "9111dde483206a774a9fe5426522dab6e77cecca"
SOURCE_017_PATH = Path("scripts/stretch_five_token_oracle_block_confirmation_017.py")
SOURCE_017_BLOB = "6171440736badf5150297f9c8945209fe49d0826"
SOURCE_013_PATH = Path("scripts/stretch_four_token_oracle_block_verification_013.py")
SOURCE_013_BLOB = "deeb0339294162f38cd4522d2890b6a0c728f96e"


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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inject_runtime_callback(wrapper_source: str) -> str:
    """Call the frozen persistence transform on the final generated runtime."""
    anchor = "\n\n    required_fragments = [\n"
    count = wrapper_source.count(anchor)
    if count != 1:
        raise RuntimeError(
            "Stretch 023 fix1 wrapper invariant failed: "
            f"required_fragments anchor count={count}"
        )
    replacement = (
        "\n"
        "    # Stretch 023 harness fix1: at this point `source` is the fully\n"
        "    # generated M5/H36 runtime, so the frozen treatment transform now\n"
        "    # sees the runtime fragments it was designed to modify.\n"
        "    source = __stretch023_add_shared_persistence(source)\n"
        "\n"
        "    required_fragments = [\n"
    )
    return wrapper_source.replace(anchor, replacement, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    broken_path = repo / SOURCE_BROKEN_PATH
    h36_path = repo / SOURCE_H36_PATH
    source017_path = repo / SOURCE_017_PATH
    source013_path = repo / SOURCE_013_PATH

    observed_broken = git_blob(broken_path, repo)
    observed_h36 = git_blob(h36_path, repo)
    observed017 = git_blob(source017_path, repo)
    observed013 = git_blob(source013_path, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 023 — H36 Full-Weight Persistent Variant HARNESS FIX1")
        print(f"Frozen broken helper blob: {observed_broken}")
        print(f"Stretch 022 H36 helper blob: {observed_h36}")
        print(f"Stretch 017 source blob: {observed017}")
        print(f"Stretch 013 source blob: {observed013}")

    if (
        observed_broken != SOURCE_BROKEN_BLOB
        or observed_h36 != SOURCE_H36_BLOB
        or observed017 != SOURCE_017_BLOB
        or observed013 != SOURCE_013_BLOB
    ):
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")
        print("Harness fix only: persistence callback moved from wrapper text to generated runtime text")
        print("Frozen shared-persistence transform implementation: UNCHANGED")
        print("Scientific factor: embedding + final norm + LM head streamed -> persistent ONLY")
        print("M=5 / H36 / model / runtime / KV / parity / I-O / safety: UNCHANGED")

    broken = load_module(broken_path, "loom_stretch023_broken_frozen")
    h36 = load_module(h36_path, "loom_stretch022_h36_transform_fix1")
    stretch017 = load_module(source017_path, "loom_stretch017_transform_fix1")

    # Build the exact frozen M5/H36 wrapper, but do NOT apply the persistence
    # transform here. Instead inject the frozen callback into that wrapper so it
    # executes after the wrapper has generated the final runtime source.
    wrapper = h36.transformed_013_wrapper(
        source013_path.read_text(encoding="utf-8"), stretch017
    )
    wrapper = inject_runtime_callback(wrapper)

    required_wrapper_fragments = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "GENERATED_TOKENS = 15\\n",
        "__stretch023_add_shared_persistence(source)",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required_wrapper_fragments if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 023 fix1 wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        # Exact frozen treatment transformation from the preserved broken helper.
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
    }
    exec(compile(wrapper, str(source013_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
