#!/usr/bin/env python3
"""LOOM Stretch 025 — M5/H36/full-persistent batched transformer cleanup variant.

Reuses the canonical Stretch 023 full-weight-persistent target and changes one
runtime factor only: the transformer loop cleanup schedule. The control performs
gc.collect() -> mx.clear_cache() -> gc.collect() after every persistent layer.
This treatment removes those 36 per-layer cleanup calls and performs the same
cleanup sequence exactly once after the 36-layer transformer body in each pass.

Model, M=5, H36/full-weight residency, KV, parity, I/O and resource gates remain
unchanged. Shared-stage cleanup behavior is unchanged.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_FIX1_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py")
SOURCE_FIX1_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"
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


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 025 cleanup transform failed for {label}: "
            f"expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def inject_cleanup_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch023_add_shared_persistence(source)\n"
    if wrapper_source.count(anchor) != 1:
        raise RuntimeError(
            "Stretch 025 wrapper invariant failed: expected one shared-persistence callback"
        )
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch025_apply_batched_cleanup(source)\n",
        1,
    )


def add_batched_cleanup(source: str) -> str:
    source = source.replace(
        "LOOM Stretch 023 — Five-Token H36 Full-Weight Persistent Variant",
        "LOOM Stretch 025 — Five-Token H36 Full-Persistent Batched-Cleanup Variant",
    )
    source = source.replace(
        "Stretch 023 — Five-Token H36 Full-Weight Persistent Variant",
        "Stretch 025 — Five-Token H36 Full-Persistent Batched-Cleanup Variant",
    )
    source = source.replace(
        "five-token-h36-full-persistent-023-full",
        "five-token-h36-full-persistent-batched-cleanup-025",
    )

    per_layer = (
        "            old_h = h\n"
        "            h = out\n"
        "            del old_h, block, selected\n"
        "            gc.collect()\n"
        "            mx.clear_cache()\n"
        "            gc.collect()\n"
        "            post_clear_active = int(mx.get_active_memory())\n"
    )
    per_layer_replacement = (
        "            old_h = h\n"
        "            h = out\n"
        "            del old_h, block, selected\n"
        "            post_clear_active = int(mx.get_active_memory())\n"
    )
    source = replace_once(
        source,
        per_layer,
        per_layer_replacement,
        "remove per-layer transformer cleanup",
    )

    final_norm_anchor = "        # Final RMSNorm — persistent shared stage.\n"
    batched = (
        "        # Transformer-body cleanup — Stretch 025 treatment.\n"
        "        # All 36 transformer weights are already persistent; cleanup is batched\n"
        "        # once here instead of after every layer.\n"
        "        body_cleanup_pre_active = int(mx.get_active_memory())\n"
        "        body_cleanup_started = time.perf_counter()\n"
        "        gc.collect()\n"
        "        mx.clear_cache()\n"
        "        gc.collect()\n"
        "        body_cleanup_wall = time.perf_counter() - body_cleanup_started\n"
        "        body_cleanup_post_active = int(mx.get_active_memory())\n"
        "        stage_records[\"transformer_body_cleanup\"] = {\n"
        "            \"policy\": \"batched_once_after_36_layers\",\n"
        "            \"pre_active_bytes\": body_cleanup_pre_active,\n"
        "            \"post_active_bytes\": body_cleanup_post_active,\n"
        "            \"active_delta_bytes\": body_cleanup_post_active - body_cleanup_pre_active,\n"
        "            \"wall_seconds\": round(body_cleanup_wall, 6),\n"
        "        }\n"
        "        save_state(\n"
        "            f\"stream_{label}_transformer_body_cleanup_complete\",\n"
        "            stage=stage_records[\"transformer_body_cleanup\"],\n"
        "            cache=cache_snapshot(caches),\n"
        "        )\n\n"
        "        # Final RMSNorm — persistent shared stage.\n"
    )
    source = replace_once(
        source,
        final_norm_anchor,
        batched,
        "insert batched transformer-body cleanup",
    )

    if per_layer in source:
        raise RuntimeError("Stretch 025 invariant failed: per-layer cleanup sequence remains")
    if source.count('"policy": "batched_once_after_36_layers"') != 1:
        raise RuntimeError("Stretch 025 invariant failed: batched cleanup marker invalid")

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    paths = {
        "fix1": repo / SOURCE_FIX1_PATH,
        "broken": repo / SOURCE_BROKEN_PATH,
        "h36": repo / SOURCE_H36_PATH,
        "s017": repo / SOURCE_017_PATH,
        "s013": repo / SOURCE_013_PATH,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}
    expected = {
        "fix1": SOURCE_FIX1_BLOB,
        "broken": SOURCE_BROKEN_BLOB,
        "h36": SOURCE_H36_BLOB,
        "s017": SOURCE_017_BLOB,
        "s013": SOURCE_013_BLOB,
    }

    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"
    if not is_child:
        print("LOOM Stretch 025 — Full-Persistent Batched Transformer Cleanup")
        for key in ["fix1", "broken", "h36", "s017", "s013"]:
            print(f"{key} blob: {observed[key]}")

    if observed != expected:
        print(f"Source provenance: FAIL observed={observed} expected={expected}", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")
        print("Scientific factor: transformer cleanup schedule 36x per-layer -> 1x post-body ONLY")
        print("M=5 / H36 / full weights / model / runtime / KV / parity / I-O / safety: UNCHANGED")
        print("Shared-stage cleanup: UNCHANGED")

    fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_025")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_025")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_025")
    stretch017 = load_module(paths["s017"], "loom_stretch017_for_025")

    wrapper = h36.transformed_013_wrapper(
        paths["s013"].read_text(encoding="utf-8"), stretch017
    )
    wrapper = fix1.inject_runtime_callback(wrapper)
    wrapper = inject_cleanup_callback(wrapper)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "__stretch023_add_shared_persistence(source)",
        "__stretch025_apply_batched_cleanup(source)",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 025 wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": add_batched_cleanup,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
