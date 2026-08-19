#!/usr/bin/env python3
"""LOOM Stretch 008 — harness-only stdout pipe deadlock fix.

Executes the exact frozen Stretch 008 runner after one deterministic textual
transformation: suppress per-state LOOM_CHILD_STATE stdout prints. The state is
already persisted to child-state.json. The final LOOM_CHILD_COMPLETE payload,
scientific computation, provenance checks, cache policy, parity gates, resource
guardrails, and output parsing remain unchanged.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_008_BLOB = "03e7a04bb42ad1e3ac4709d0a745bfdbf491e9bf"


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


def replace_exact(text: str, old: str, new: str, expected_count: int, label: str) -> str:
    observed = text.count(old)
    if observed != expected_count:
        raise RuntimeError(
            f"pipefix invariant failed for {label}: expected {expected_count} occurrence(s), found {observed}"
        )
    return text.replace(old, new)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source008 = repo / "scripts" / "stretch_one_token_kv_autoregressive_parity_008.py"

    observed = git_blob(source008, repo)
    print("LOOM Stretch 008 — stdout-pipe harness fix")
    print(f"Frozen Stretch 008 source blob: {observed}")
    if observed != SOURCE_008_BLOB:
        print(f"Source provenance: FAIL expected {SOURCE_008_BLOB}", file=sys.stderr)
        return 2
    print("Source provenance: PASS")

    source = source008.read_text(encoding="utf-8")
    source = replace_exact(
        source,
        '    print("LOOM_CHILD_STATE=" + json.dumps(payload), flush=True)\n',
        '    # PIPEFIX: state already persisted to child-state.json; do not fill captured stdout pipe.\n',
        1,
        "per-state child stdout emission",
    )

    if source.count('print("LOOM_CHILD_COMPLETE=" + json.dumps(final), flush=True)') != 1:
        raise RuntimeError("pipefix invariant failed: final completion payload is not uniquely preserved")

    print("Pipefix transform: PASS")
    print("Scientific design/gates: UNCHANGED")
    print("Per-state child-state.json writes: PRESERVED")
    print("Final LOOM_CHILD_COMPLETE stdout payload: PRESERVED")

    transformed_globals = {
        "__name__": "__main__",
        "__file__": str(source008),
    }
    exec(compile(source, str(source008), "exec"), transformed_globals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
