#!/usr/bin/env python3
"""LOOM Stretch 022 helper — M5 with thirty-six-layer persistent hotset.

Reuses the frozen Stretch 017 M=5 exact oracle path and changes one runtime
factor only: persistent transformer hotset layers 0..7 -> 0..35. All model,
MLX, quantization, KV, oracle geometry, parity, I/O and safety logic is inherited.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

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


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"H36 transform failed for {label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


def transformed_013_wrapper(source013: str, stretch017) -> str:
    # First reproduce the exact frozen Stretch 017 M=5 wrapper.
    transformed = stretch017.transform_stretch_013(source013)

    # Distinct experiment/run identity; scientific PASS semantics remain the
    # inherited Stretch 017 exactness classification and are additionally
    # checked by the balanced Stretch 022 parent using hotset provenance.
    transformed = transformed.replace(
        "LOOM Stretch 017 — Five-Token Oracle Block Confirmation",
        "LOOM Stretch 022 — Five-Token H36 Hotset Variant",
    )
    transformed = transformed.replace(
        "Stretch 017 — Five-Token Oracle Block Confirmation",
        "Stretch 022 — Five-Token H36 Hotset Variant",
    )
    transformed = transformed.replace(
        "five-token-oracle-block-confirmation-017",
        "five-token-h36-hotset-022-h36",
    )

    # Update the transformed Stretch 013 wrapper invariant to the requested
    # persistent geometry.
    transformed = replace_once(
        transformed,
        '        "HOTSET_LAYER_IDS = tuple(range(8))",\n',
        '        "HOTSET_LAYER_IDS = tuple(range(36))",\n',
        "required H36 fragment",
    )

    # Inject the only scientific change after the frozen Stretch 012 hotset
    # transform creates final-source constants. EXPECTED_HOTSET_BYTES changes
    # only because it is the derived residency/provenance gate for H36.
    anchor = "    source = hotset012.add_hotset_transform(source)\n    source = add_oracle_block_transform(source)\n"
    replacement = (
        "    source = hotset012.add_hotset_transform(source)\n"
        "    source = replace_exact(\n"
        "        source,\n"
        "        \"HOTSET_LAYER_IDS = tuple(range(8))\\nEXPECTED_HOTSET_BYTES = 8 * EXPECTED_LAYER_BYTES\\n\",\n"
        "        \"HOTSET_LAYER_IDS = tuple(range(36))\\nEXPECTED_HOTSET_BYTES = 36 * EXPECTED_LAYER_BYTES\\n\",\n"
        "        1,\n"
        "        \"thirty-six-layer persistent hotset\",\n"
        "    )\n"
        "    source = add_oracle_block_transform(source)\n"
    )
    transformed = replace_once(transformed, anchor, replacement, "H36 injection")

    transformed = transformed.replace(
        'print("Eight-layer persistent hotset: PRESERVED")',
        'print("Persistent hotset: H36 layers 0..35 (only changed runtime factor)")',
    )
    return transformed


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source017 = repo / SOURCE_017_PATH
    source013 = repo / SOURCE_013_PATH

    observed017 = git_blob(source017, repo)
    observed013 = git_blob(source013, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 022 — Five-Token H36 Hotset Variant frozen transform")
        print(f"Stretch 017 source blob: {observed017}")
        print(f"Stretch 013 source blob: {observed013}")
    if observed017 != SOURCE_017_BLOB or observed013 != SOURCE_013_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    if not is_child:
        print("Source provenance: PASS")
        print("Scientific change: persistent transformer hotset H8 -> H36 ONLY")
        print("M=5 oracle geometry / runtime / model / KV / parity / I-O / safety: UNCHANGED")

    stretch017 = load_module(source017, "loom_stretch017_transform_h36")
    source = transformed_013_wrapper(source013.read_text(encoding="utf-8"), stretch017)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "ORACLE_BLOCK_COUNT = 3",
        "GENERATED_TOKENS = 15\\n",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "five-token-h36-hotset-022-h36",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"H36 transformed-wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(source013), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
