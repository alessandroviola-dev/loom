#!/usr/bin/env python3
"""LOOM Stretch 017 — five-token oracle block confirmation.

Frozen diagnostic transform of Stretch 013. The scientific goal is to confirm
end-to-end exactness at the M=5 boundary mapped by Stretch 016. It uses three
5-token oracle blocks over the frozen first-15 token prefix. Runtime/model/KV/
hotset/parity/safety policy remains unchanged.
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
        raise RuntimeError(f"Stretch 017 transform failed for {label}: source text not found")
    return source.replace(old, new)


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 017 transform failed for {label}: expected 1 occurrence, found {count}"
        )
    return source.replace(old, new, 1)


def transform_stretch_013(source: str) -> str:
    source = replace_all(
        source,
        "LOOM Stretch 013 — Four-Token Oracle Block Verification",
        "LOOM Stretch 017 — Five-Token Oracle Block Confirmation",
        "title",
    )
    source = replace_all(
        source,
        "four-token-oracle-block-verification-013",
        "five-token-oracle-block-confirmation-017",
        "run directory",
    )

    # Diagnostic block geometry discovered by Stretch 016.
    source = replace_all(source, "ORACLE_BLOCK_SIZE = 4", "ORACLE_BLOCK_SIZE = 5", "block size")
    source = replace_all(source, "ORACLE_BLOCK_COUNT = 4", "ORACLE_BLOCK_COUNT = 3", "block count")
    source = replace_all(
        source,
        "ORACLE_SEQUENCE = [1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8,311]",
        "ORACLE_SEQUENCE = [1,374,264,4647,1483,304,279,1809,315,5994,320,1654,23740,285,8]",
        "oracle prefix",
    )
    source = replace_all(
        source,
        "four target traversals x four oracle tokens",
        "three target traversals x five oracle tokens",
        "block-loop description",
    )
    source = replace_all(
        source,
        "FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "PASS classification",
    )
    source = replace_all(
        source,
        "16 one-token target traversals -> 4 x 4-token oracle target blocks ONLY",
        "15 sequential resident positions -> 3 x 5-token oracle target blocks; diagnostic continuation length 16 -> 15",
        "scientific-change display",
    )

    # Stretch 013 reconstructs GENERATED_TOKENS=16 through Stretch 010. After
    # its full transform stack has run, reduce the generated continuation to 15
    # so all oracle traversals are exactly M=5 and provenance remains exact.
    injection_old = "    source = add_oracle_block_transform(source)\n\n    required_fragments = [\n"
    injection_new = (
        "    source = add_oracle_block_transform(source)\n"
        "    source = replace_exact(\n"
        "        source,\n"
        "        \"GENERATED_TOKENS = 16\\n\",\n"
        "        \"GENERATED_TOKENS = 15\\n\",\n"
        "        1,\n"
        "        \"five-token diagnostic continuation depth\",\n"
        "    )\n\n"
        "    required_fragments = [\n"
    )
    source = replace_once(source, injection_old, injection_new, "15-token continuation injection")

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    wrapper_path = Path(__file__).resolve()
    source_path = repo / SOURCE_013_PATH
    if not source_path.is_file():
        print(f"ERROR: frozen source missing: {source_path}", file=sys.stderr)
        return 2

    actual_blob = git_blob(source_path, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"
    if not is_child:
        print("LOOM Stretch 017 — Five-Token Oracle Block Confirmation frozen transform")
        print(f"Stretch 013 source blob: {actual_blob}")
    if actual_blob != SOURCE_013_BLOB:
        print(
            "Source provenance: FAIL "
            f"expected {SOURCE_013_BLOB}, got {actual_blob}",
            file=sys.stderr,
        )
        return 3
    if not is_child:
        print("Source provenance: PASS")

    source = source_path.read_text(encoding="utf-8")
    transformed = transform_stretch_013(source)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "ORACLE_BLOCK_COUNT = 3",
        "GENERATED_TOKENS = 15\\n",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "oracle_target_verification_tokens_per_second",
        "HOTSET_LAYER_IDS = tuple(range(8))",
        "MIN_FREE_PERCENT = 5",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in transformed]
    if missing:
        raise RuntimeError(f"Stretch 017 transformed-source invariant failed; missing {missing}")

    if not is_child:
        print("Frozen transform: PASS")
        print("Diagnostic change: exact candidate block size M=5")
        print("Resident continuation: 15 frozen-prefix positions")
        print("Streamed target traversals: 3 x 5 oracle tokens")
        print("Expected streamed KV offsets: 4 -> 9 -> 14 -> 19")
        print("Model/runtime/KV/hotset/parity/I-O/safety policy: UNCHANGED")
        print("Real draft model: NONE (oracle upper bound)")

    # Preserve wrapper routing for inherited parent/child execution.
    code = compile(transformed, str(source_path), "exec")
    namespace = {
        "__name__": "__main__",
        "__file__": str(wrapper_path),
        "__package__": None,
        "__cached__": None,
    }
    exec(code, namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
