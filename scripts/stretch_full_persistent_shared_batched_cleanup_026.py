#!/usr/bin/env python3
"""LOOM Stretch 026 — shared-stage batched cleanup treatment.

Reuses the successful Stretch 025 M5/H36/full-persistent transformer-body
cleanup policy and changes one runtime factor only: cleanup around persistent
shared stages. Embedding, final RMSNorm, and LM head no longer each execute
`gc.collect() -> mx.clear_cache() -> gc.collect()`; the identical cleanup
sequence is executed exactly once after LM head.

Transformer-body cleanup remains once-per-body exactly as in Stretch 025.
Model/runtime/M5/H36/full persistence/KV/parity/I-O/resource gates are unchanged.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_025_PATH = Path("scripts/stretch_full_persistent_batched_cleanup_025.py")
SOURCE_025_BLOB = "5ca3572f3269899e7c3fc23b9e136381ce864d99"
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


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Stretch 026 shared-cleanup transform failed for {label}: "
            f"expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def inject_shared_cleanup_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch025_apply_batched_cleanup(source)\n"
    if wrapper_source.count(anchor) != 1:
        raise RuntimeError("Stretch 026 wrapper invariant failed: Stretch 025 callback missing")
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch026_apply_shared_batched_cleanup(source)\n",
        1,
    )


def add_shared_batched_cleanup(source: str) -> str:
    source = source.replace(
        "LOOM Stretch 025 — Five-Token H36 Full-Persistent Batched-Cleanup Variant",
        "LOOM Stretch 026 — Five-Token H36 Full-Persistent Shared-Batched-Cleanup Variant",
    )
    source = source.replace(
        "Stretch 025 — Five-Token H36 Full-Persistent Batched-Cleanup Variant",
        "Stretch 026 — Five-Token H36 Full-Persistent Shared-Batched-Cleanup Variant",
    )
    source = source.replace(
        "five-token-h36-full-persistent-batched-cleanup-025",
        "five-token-h36-full-persistent-shared-batched-cleanup-026",
    )

    source = replace_once(
        source,
        "        del embed_stage\n"
        "        gc.collect()\n"
        "        mx.clear_cache()\n"
        "        gc.collect()\n"
        "        embed_post_clear_active = int(mx.get_active_memory())\n",
        "        del embed_stage\n"
        "        embed_post_clear_active = int(mx.get_active_memory())\n",
        "remove embedding cleanup",
    )
    source = replace_once(
        source,
        "        del old_h, norm_stage\n"
        "        gc.collect()\n"
        "        mx.clear_cache()\n"
        "        gc.collect()\n"
        "        norm_post_clear_active = int(mx.get_active_memory())\n",
        "        del old_h, norm_stage\n"
        "        norm_post_clear_active = int(mx.get_active_memory())\n",
        "remove norm cleanup",
    )
    source = replace_once(
        source,
        "        del h, head_stage\n"
        "        gc.collect()\n"
        "        mx.clear_cache()\n"
        "        gc.collect()\n"
        "        head_post_clear_active = int(mx.get_active_memory())\n",
        "        del h, head_stage\n"
        "        head_post_clear_active = int(mx.get_active_memory())\n",
        "remove head cleanup",
    )

    anchor = (
        '        save_state(f"stream_{label}_head_complete", '
        'stage=stage_records["head"], cache=cache_snapshot(caches))\n\n'
    )
    batched = anchor + (
        "        # Shared-stage cleanup — Stretch 026 treatment.\n"
        "        # Embedding, final norm, and head are persistent; perform their\n"
        "        # inherited cleanup sequence once after the complete shared path.\n"
        "        shared_cleanup_pre_active = int(mx.get_active_memory())\n"
        "        shared_cleanup_started = time.perf_counter()\n"
        "        gc.collect()\n"
        "        mx.clear_cache()\n"
        "        gc.collect()\n"
        "        shared_cleanup_wall = time.perf_counter() - shared_cleanup_started\n"
        "        shared_cleanup_post_active = int(mx.get_active_memory())\n"
        "        stage_records[\"shared_stage_cleanup\"] = {\n"
        "            \"policy\": \"batched_once_after_embedding_norm_head\",\n"
        "            \"pre_active_bytes\": shared_cleanup_pre_active,\n"
        "            \"post_active_bytes\": shared_cleanup_post_active,\n"
        "            \"active_delta_bytes\": shared_cleanup_post_active - shared_cleanup_pre_active,\n"
        "            \"wall_seconds\": round(shared_cleanup_wall, 6),\n"
        "        }\n"
        "        save_state(\n"
        "            f\"stream_{label}_shared_stage_cleanup_complete\",\n"
        "            stage=stage_records[\"shared_stage_cleanup\"],\n"
        "            cache=cache_snapshot(caches),\n"
        "        )\n\n"
    )
    source = replace_once(source, anchor, batched, "insert shared batched cleanup")

    if source.count('"policy": "batched_once_after_36_layers"') != 1:
        raise RuntimeError("Stretch 026 invariant failed: Stretch 025 body cleanup not preserved")
    if source.count('"policy": "batched_once_after_embedding_norm_head"') != 1:
        raise RuntimeError("Stretch 026 invariant failed: shared cleanup marker invalid")

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    paths = {
        "s025": repo / SOURCE_025_PATH,
        "fix1": repo / SOURCE_FIX1_PATH,
        "broken": repo / SOURCE_BROKEN_PATH,
        "h36": repo / SOURCE_H36_PATH,
        "s017": repo / SOURCE_017_PATH,
        "s013": repo / SOURCE_013_PATH,
    }
    expected = {
        "s025": SOURCE_025_BLOB,
        "fix1": SOURCE_FIX1_BLOB,
        "broken": SOURCE_BROKEN_BLOB,
        "h36": SOURCE_H36_BLOB,
        "s017": SOURCE_017_BLOB,
        "s013": SOURCE_013_BLOB,
    }
    observed = {key: git_blob(path, repo) for key, path in paths.items()}

    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"
    if not is_child:
        print("LOOM Stretch 026 — Full-Persistent Shared-Stage Batched Cleanup")
        for key in ["s025", "fix1", "broken", "h36", "s017", "s013"]:
            print(f"{key} blob: {observed[key]}")
    if observed != expected:
        print(f"Source provenance: FAIL observed={observed} expected={expected}", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")
        print("Scientific factor: shared cleanup 3x per-pass -> 1x post-head ONLY")
        print("Transformer-body cleanup: preserved once-per-body from Stretch 025")
        print("M5 / H36 / full weights / model / runtime / KV / parity / I-O / safety: UNCHANGED")

    s025 = load_module(paths["s025"], "loom_stretch025_transform_for_026")
    fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_026")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_026")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_026")
    stretch017 = load_module(paths["s017"], "loom_stretch017_for_026")

    wrapper = h36.transformed_013_wrapper(
        paths["s013"].read_text(encoding="utf-8"), stretch017
    )
    wrapper = fix1.inject_runtime_callback(wrapper)
    wrapper = s025.inject_cleanup_callback(wrapper)
    wrapper = inject_shared_cleanup_callback(wrapper)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "__stretch023_add_shared_persistence(source)",
        "__stretch025_apply_batched_cleanup(source)",
        "__stretch026_apply_shared_batched_cleanup(source)",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 026 wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": s025.add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": add_shared_batched_cleanup,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
