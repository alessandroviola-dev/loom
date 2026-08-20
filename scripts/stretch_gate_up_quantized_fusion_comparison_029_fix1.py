#!/usr/bin/env python3
"""LOOM Stretch 029 — balanced gate+up fusion comparison, harness Fix1.

Reuses the frozen original comparison runner and changes harness provenance/output
location only so the repaired FUSED helper is tested in a completely new ABBA.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ORIGINAL_RUNNER_PATH = Path("scripts/stretch_gate_up_quantized_fusion_comparison_029.py")
ORIGINAL_RUNNER_BLOB = "8d89665b5d3061891a53f1734e19331aa1a4fb34"
FIXED_FUSED_PATH = Path("scripts/stretch_gate_up_quantized_fusion_029_fix1.py")
FIXED_FUSED_BLOB = "93d985a526f4433b10fec39fbaf5807059807821"


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 029 Fix1 runner transform failed for {label}: expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    original_path = repo / ORIGINAL_RUNNER_PATH
    fused_path = repo / FIXED_FUSED_PATH
    observed_original = git_blob(original_path, repo)
    observed_fused = git_blob(fused_path, repo)

    print("LOOM Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison HARNESS FIX1")
    print(f"Frozen original comparison runner blob: {observed_original}")
    print(f"Harness-fixed FUSED helper blob: {observed_fused}")
    if observed_original != ORIGINAL_RUNNER_BLOB or observed_fused != FIXED_FUSED_BLOB:
        print("Source provenance: FAIL")
        return 2
    print("Source provenance: PASS")
    print("Failed 20260820-170503 sequence: PRESERVED; no measurements reused")
    print("Scientific preregistration / ABBA / exactness gates / metrics: UNCHANGED")

    source = original_path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        'SOURCE_FUSED_PATH = Path("scripts/stretch_gate_up_quantized_fusion_029.py")',
        'SOURCE_FUSED_PATH = Path("scripts/stretch_gate_up_quantized_fusion_029_fix1.py")',
        "FUSED helper path",
    )
    source = replace_once(
        source,
        'SOURCE_FUSED_BLOB = "c37ff6313106807c1e2e5070b7fb8f19e97abea6"',
        f'SOURCE_FUSED_BLOB = "{FIXED_FUSED_BLOB}"',
        "FUSED helper blob",
    )
    source = replace_once(
        source,
        'print("LOOM Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison")',
        'print("LOOM Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison HARNESS FIX1")',
        "runner title",
    )
    source = replace_once(
        source,
        '"gate-up-quantized-fusion-comparison-029"',
        '"gate-up-quantized-fusion-comparison-029-fix1"',
        "result root",
    )
    source = replace_once(
        source,
        '"experiment": "Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison",',
        '"experiment": "Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison HARNESS FIX1",\n        "harness_revision": "fix1",',
        "summary harness revision",
    )

    required = [
        'RUN_ORDER = ["CONTROL", "FUSED", "FUSED", "CONTROL"]',
        '"GATE_UP_QUANTIZED_FUSION_NUMERICAL_PARITY_FAIL"',
        '"GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS"',
        '"GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE"',
        'scripts/stretch_gate_up_quantized_fusion_029_fix1.py',
        FIXED_FUSED_BLOB,
        'gate-up-quantized-fusion-comparison-029-fix1',
    ]
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise RuntimeError(f"Stretch 029 Fix1 runner invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(source, str(original_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
