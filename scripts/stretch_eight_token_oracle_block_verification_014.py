#!/usr/bin/env python3
"""LOOM Stretch 014 — eight-token oracle block verification.

Frozen transform of Stretch 013. The only scientific workload change is the
oracle verification block size: 4 tokens -> 8 tokens, with the same 16-token
frozen oracle sequence and all other model/KV/safety gates unchanged.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_013_BLOB = "deeb0339294162f38cd4522d2890b6a0c728f96e"
SOURCE_013_PATH = Path("scripts/stretch_four_token_oracle_block_verification_013.py")


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


def replace_all(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count == 0:
        raise RuntimeError(f"Stretch 014 transform failed for {label}: source text not found")
    return source.replace(old, new)


def transform_stretch_013(source: str) -> str:
    # Identity/title transform.
    source = replace_all(
        source,
        "LOOM Stretch 013 — Four-Token Oracle Block Verification",
        "LOOM Stretch 014 — Eight-Token Oracle Block Verification",
        "title",
    )
    source = replace_all(
        source,
        "four-token-oracle-block-verification-013",
        "eight-token-oracle-block-verification-014",
        "run directory",
    )

    # Scientific change: exactly 4-token blocks -> 8-token blocks and
    # correspondingly 4 target traversals -> 2 target traversals.
    source = replace_all(
        source,
        "ORACLE_BLOCK_SIZE = 4",
        "ORACLE_BLOCK_SIZE = 8",
        "block size",
    )
    source = replace_all(
        source,
        "ORACLE_BLOCK_COUNT = 4",
        "ORACLE_BLOCK_COUNT = 2",
        "block count",
    )
    source = replace_all(
        source,
        "four target traversals x four oracle tokens",
        "two target traversals x eight oracle tokens",
        "block-loop description",
    )

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source_path = repo / SOURCE_013_PATH
    if not source_path.is_file():
        print(f"ERROR: frozen source missing: {source_path}", file=sys.stderr)
        return 2

    actual_blob = git_blob(source_path, repo)
    print("LOOM Stretch 014 — Eight-Token Oracle Block Verification frozen transform")
    print(f"Stretch 013 source blob: {actual_blob}")
    if actual_blob != SOURCE_013_BLOB:
        print(
            "Source provenance: FAIL "
            f"expected {SOURCE_013_BLOB}, got {actual_blob}",
            file=sys.stderr,
        )
        return 3
    print("Source provenance: PASS")

    source = source_path.read_text(encoding="utf-8")
    transformed = transform_stretch_013(source)
    print("Frozen transform: PASS")
    print("Scientific change: oracle block size 4 -> 8 ONLY")
    print("Model/KV/parity/I-O/safety policy: UNCHANGED")

    code = compile(transformed, str(source_path), "exec")
    namespace = {
        "__name__": "__main__",
        "__file__": str(source_path),
        "__package__": None,
        "__cached__": None,
    }
    exec(code, namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
