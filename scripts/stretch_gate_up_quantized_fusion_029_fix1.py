#!/usr/bin/env python3
"""LOOM Stretch 029 — gate+up quantized fusion treatment, harness Fix1.

Harness-only repair of the original Stretch 029 helper. The scientific fusion
transform is imported unchanged from the frozen original helper; Fix1 only repairs
the phase at which wrapper invariants are checked.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ORIGINAL_PATH = Path("scripts/stretch_gate_up_quantized_fusion_029.py")
ORIGINAL_BLOB = "c37ff6313106807c1e2e5070b7fb8f19e97abea6"


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
    original_path = repo / ORIGINAL_PATH
    observed_original = git_blob(original_path, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 029 — Gate+Up Quantized Fusion HARNESS FIX1")
        print(f"Frozen original FUSED helper blob: {observed_original}")
        print("Harness repair: validate injected callback at wrapper phase; do not require post-callback runtime text")
        print("Scientific gate+up fusion transform: UNCHANGED")

    if observed_original != ORIGINAL_BLOB:
        print(
            f"Source provenance: FAIL original={observed_original} expected={ORIGINAL_BLOB}",
            file=sys.stderr,
        )
        return 2

    original = load_module(original_path, "loom_stretch029_original_for_fix1")

    paths = {
        "s027": repo / original.SOURCE_027_PATH,
        "s026": repo / original.SOURCE_026_PATH,
        "s025": repo / original.SOURCE_025_PATH,
        "fix1": repo / original.SOURCE_FIX1_PATH,
        "broken": repo / original.SOURCE_BROKEN_PATH,
        "h36": repo / original.SOURCE_H36_PATH,
        "s017": repo / original.SOURCE_017_PATH,
        "s013": repo / original.SOURCE_013_PATH,
    }
    expected = {
        "s027": original.SOURCE_027_BLOB,
        "s026": original.SOURCE_026_BLOB,
        "s025": original.SOURCE_025_BLOB,
        "fix1": original.SOURCE_FIX1_BLOB,
        "broken": original.SOURCE_BROKEN_BLOB,
        "h36": original.SOURCE_H36_BLOB,
        "s017": original.SOURCE_017_BLOB,
        "s013": original.SOURCE_013_BLOB,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}
    if observed != expected:
        print(f"Source provenance: FAIL observed={observed} expected={expected}", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")
        print("Scientific factor: gate_proj + up_proj two quantized matmuls -> one fused quantized matmul ONLY")
        print("M5 / H36 / full weights / single cleanup / model / runtime / KV / parity / I-O / safety: UNCHANGED")

    s027 = original.load_module(paths["s027"], "loom_stretch027_transform_for_029_fix1")
    s026 = original.load_module(paths["s026"], "loom_stretch026_transform_for_029_fix1")
    s025 = original.load_module(paths["s025"], "loom_stretch025_transform_for_029_fix1")
    shared_fix1 = original.load_module(paths["fix1"], "loom_stretch023_fix1_for_029_fix1")
    broken = original.load_module(paths["broken"], "loom_stretch023_broken_for_029_fix1")
    h36 = original.load_module(paths["h36"], "loom_stretch022_h36_for_029_fix1")
    stretch017 = original.load_module(paths["s017"], "loom_stretch017_for_029_fix1")

    wrapper = h36.transformed_013_wrapper(paths["s013"].read_text(encoding="utf-8"), stretch017)
    wrapper = shared_fix1.inject_runtime_callback(wrapper)
    wrapper = s025.inject_cleanup_callback(wrapper)
    wrapper = s026.inject_shared_cleanup_callback(wrapper)
    wrapper = s027.inject_single_pass_callback(wrapper)
    wrapper = original.inject_fusion_callback(wrapper)

    # Harness Fix1: at this phase the fusion callback has been injected but has
    # not executed yet. Therefore only wrapper-phase facts are valid invariants.
    # The post-callback provenance policy is still enforced by the generated
    # runtime and balanced comparison runner after callback execution.
    required_wrapper_fragments = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "__stretch027_apply_single_pass_cleanup(source)",
        "__stretch029_apply_gate_up_fusion(source)",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required_wrapper_fragments if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 029 Fix1 wrapper invariant failed; missing {missing}")

    original_text = original_path.read_text(encoding="utf-8")
    callback_definition_fragments = [
        "class FusedGateUpMLP",
        "mx.quantized_matmul(",
        '"policy": "single_quantized_matmul_gate_up"',
        "__stretch029_apply_gate_up_fusion",
    ]
    callback_missing = [fragment for fragment in callback_definition_fragments if fragment not in original_text]
    if callback_missing:
        raise RuntimeError(
            f"Stretch 029 Fix1 frozen callback definition invariant failed; missing {callback_missing}"
        )

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": s025.add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": s026.add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": s027.add_single_pass_cleanup,
        "__stretch029_apply_gate_up_fusion": original.add_gate_up_fusion,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
