#!/usr/bin/env python3
"""LOOM Stretch 006 — frozen transform to full 36-layer streamed body parity.

This wrapper executes an exact, preregistered transform of the frozen Stretch 005
runner. It changes chain depth and experiment naming/tolerance only; the actual
resident/streamed computation, per-layer gates, parity formula and safety logic
remain sourced from Stretch 005.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_005_BLOB = "8bbfff727a0131c48d4ba71edc8de485182b7fbe"


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
            f"transform invariant failed for {label}: expected {expected_count} occurrence(s), found {observed}"
        )
    return text.replace(old, new)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source005 = repo / "scripts" / "stretch_eight_layer_streamed_forward_scaling_005.py"

    print("LOOM Stretch 006 — Full 36-Layer Streamed Body Parity frozen transform")
    observed_blob = git_blob(source005, repo)
    print(f"Stretch 005 source blob: {observed_blob}")
    if observed_blob != SOURCE_005_BLOB:
        print(f"Source provenance: FAIL expected {SOURCE_005_BLOB}", file=sys.stderr)
        return 2
    print("Source provenance: PASS")

    source = source005.read_text(encoding="utf-8")

    source = replace_exact(
        source,
        '"""LOOM Stretch 005 — eight-layer streamed forward scaling.\n\nExtends the exact Stretch 004 resident-vs-streamed Qwen3 micro-forward from\n2 to 8 consecutive transformer blocks while preserving the frozen input,',
        '"""LOOM Stretch 006 — full 36-layer streamed body parity.\n\nExtends the exact Stretch 005 resident-vs-streamed Qwen3 micro-forward from\n8 to all 36 transformer blocks while preserving the frozen input,',
        1,
        "module description",
    )
    source = replace_exact(
        source,
        "LAYERS = [14, 15, 16, 17, 18, 19, 20, 21]",
        "LAYERS = list(range(36))",
        1,
        "layer chain",
    )
    source = replace_exact(
        source,
        "# Resident control: all eight blocks materialized together.",
        "# Resident control: all 36 transformer blocks materialized together.",
        1,
        "resident comment",
    )
    source = replace_exact(
        source,
        "LOOM Stretch 005 — Eight-Layer Streamed Forward Scaling",
        "LOOM Stretch 006 — Full 36-Layer Streamed Body Parity",
        2,
        "experiment labels",
    )
    source = replace_exact(
        source,
        '"eight-layer-streamed-forward-scaling-005"',
        '"full-36-layer-streamed-body-parity-006"',
        1,
        "result directory",
    )
    source = replace_exact(
        source,
        "Resident eight-layer materialized delta:",
        "Resident 36-layer materialized delta:",
        1,
        "resident output label",
    )
    source = replace_exact(
        source,
        "if abs(resident_delta - expected_resident) > 8 * 1024 * 1024:",
        "if abs(resident_delta - expected_resident) > 36 * 1024 * 1024:",
        1,
        "resident tolerance",
    )
    source = replace_exact(
        source,
        'summary["classification"] = "EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS"',
        'summary["classification"] = "FULL_36_LAYER_STREAMED_BODY_PARITY_PASS"',
        1,
        "primary classification",
    )
    source = replace_exact(
        source,
        '"source_002_blob": observed002,\n        "disk_before": helpers.disk_snapshot(repo),',
        f'"source_002_blob": observed002,\n        "source_005_blob": "{SOURCE_005_BLOB}",\n        "disk_before": helpers.disk_snapshot(repo),',
        1,
        "summary source provenance",
    )

    print("Frozen transform: PASS")
    print("Layer policy: exact 0..35")
    print("Resident tolerance: +/-36 MiB (same +/-1 MiB per-layer scaling)")
    print("Per-layer streamed/parity/safety gates: UNCHANGED")

    transformed_globals = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
    }
    exec(compile(source, str(source005), "exec"), transformed_globals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
