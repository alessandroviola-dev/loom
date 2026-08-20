#!/usr/bin/env python3
"""LOOM Stretch 027 — single end-of-pass cleanup treatment.

Reuses the successful Stretch 026 M5/H36/full-persistent cleanup schedule and
changes one runtime factor only: two cleanup points per target pass become one.
The Stretch 025 transformer-body cleanup is removed; the Stretch 026 final
post-head cleanup is retained and becomes the single cleanup for the full pass.

Model/runtime/M5/H36/full persistence/KV/parity/I-O/resource gates are unchanged.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_026_PATH = Path("scripts/stretch_full_persistent_shared_batched_cleanup_026.py")
SOURCE_026_BLOB = "6926e1b1b9a851f23d88ba6b1f1023e13336098a"
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
            f"Stretch 027 single-pass cleanup transform failed for {label}: "
            f"expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def inject_single_pass_callback(wrapper_source: str) -> str:
    anchor = "    source = __stretch026_apply_shared_batched_cleanup(source)\n"
    if wrapper_source.count(anchor) != 1:
        raise RuntimeError("Stretch 027 wrapper invariant failed: Stretch 026 callback missing")
    return wrapper_source.replace(
        anchor,
        anchor + "    source = __stretch027_apply_single_pass_cleanup(source)\n",
        1,
    )


def add_single_pass_cleanup(source: str) -> str:
    source = source.replace(
        "LOOM Stretch 026 — Five-Token H36 Full-Persistent Shared-Batched-Cleanup Variant",
        "LOOM Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
    )
    source = source.replace(
        "Stretch 026 — Five-Token H36 Full-Persistent Shared-Batched-Cleanup Variant",
        "Stretch 027 — Five-Token H36 Full-Persistent Single-Pass-Cleanup Variant",
    )
    source = source.replace(
        "five-token-h36-full-persistent-shared-batched-cleanup-026",
        "five-token-h36-full-persistent-single-pass-cleanup-027",
    )

    body_cleanup = (
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
    )
    source = replace_once(source, body_cleanup, "", "remove intermediate transformer-body cleanup")

    source = replace_once(
        source,
        '            "policy": "batched_once_after_embedding_norm_head",\n',
        '            "policy": "single_cleanup_after_full_pass",\n',
        "promote final cleanup policy",
    )
    source = source.replace(
        "        # Shared-stage cleanup — Stretch 026 treatment.\n"
        "        # Embedding, final norm, and head are persistent; perform their\n"
        "        # inherited cleanup sequence once after the complete shared path.\n",
        "        # Full-pass cleanup — Stretch 027 treatment.\n"
        "        # This is now the only cleanup point in the target pass.\n",
    )

    if '"policy": "batched_once_after_36_layers"' in source:
        raise RuntimeError("Stretch 027 invariant failed: transformer-body cleanup marker remains")
    if source.count('"policy": "single_cleanup_after_full_pass"') != 1:
        raise RuntimeError("Stretch 027 invariant failed: final single-cleanup marker invalid")

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    paths = {
        "s026": repo / SOURCE_026_PATH,
        "s025": repo / SOURCE_025_PATH,
        "fix1": repo / SOURCE_FIX1_PATH,
        "broken": repo / SOURCE_BROKEN_PATH,
        "h36": repo / SOURCE_H36_PATH,
        "s017": repo / SOURCE_017_PATH,
        "s013": repo / SOURCE_013_PATH,
    }
    expected = {
        "s026": SOURCE_026_BLOB,
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
        print("LOOM Stretch 027 — Full-Persistent Single End-of-Pass Cleanup")
        for key in ["s026", "s025", "fix1", "broken", "h36", "s017", "s013"]:
            print(f"{key} blob: {observed[key]}")
    if observed != expected:
        print(f"Source provenance: FAIL observed={observed} expected={expected}", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")
        print("Scientific factor: cleanup points per pass 2 -> 1 final post-head cleanup ONLY")
        print("M5 / H36 / full weights / model / runtime / KV / parity / I-O / safety: UNCHANGED")

    s026 = load_module(paths["s026"], "loom_stretch026_transform_for_027")
    s025 = load_module(paths["s025"], "loom_stretch025_transform_for_027")
    fix1 = load_module(paths["fix1"], "loom_stretch023_fix1_for_027")
    broken = load_module(paths["broken"], "loom_stretch023_broken_for_027")
    h36 = load_module(paths["h36"], "loom_stretch022_h36_for_027")
    stretch017 = load_module(paths["s017"], "loom_stretch017_for_027")

    wrapper = h36.transformed_013_wrapper(
        paths["s013"].read_text(encoding="utf-8"), stretch017
    )
    wrapper = fix1.inject_runtime_callback(wrapper)
    wrapper = s025.inject_cleanup_callback(wrapper)
    wrapper = s026.inject_shared_cleanup_callback(wrapper)
    wrapper = inject_single_pass_callback(wrapper)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "__stretch023_add_shared_persistence(source)",
        "__stretch025_apply_batched_cleanup(source)",
        "__stretch026_apply_shared_batched_cleanup(source)",
        "__stretch027_apply_single_pass_cleanup(source)",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in wrapper]
    if missing:
        raise RuntimeError(f"Stretch 027 wrapper invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
        "__stretch023_add_shared_persistence": broken.add_shared_persistence,
        "__stretch025_apply_batched_cleanup": s025.add_batched_cleanup,
        "__stretch026_apply_shared_batched_cleanup": s026.add_shared_batched_cleanup,
        "__stretch027_apply_single_pass_cleanup": add_single_pass_cleanup,
    }
    exec(compile(wrapper, str(paths["s013"]), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
