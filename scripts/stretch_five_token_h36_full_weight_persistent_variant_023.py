#!/usr/bin/env python3
"""LOOM Stretch 023 helper — M5/H36 with persistent shared weight stages.

Reconstructs the frozen Stretch 022 H36 exact-oracle workload and changes one
scientific factor only: embedding, final RMSNorm, and LM head are materialized
once and retained alongside all 36 already-persistent transformer layers.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

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
            f"Stretch 023 transform failed for {label}: expected 1 occurrence, found {count}"
        )
    return text.replace(old, new, 1)


def replace_span(text: str, start: str, end: str, replacement: str, label: str) -> str:
    if text.count(start) != 1:
        raise RuntimeError(f"Stretch 023 span start invalid for {label}: {text.count(start)}")
    start_index = text.index(start)
    end_index = text.find(end, start_index + len(start))
    if end_index < 0:
        raise RuntimeError(f"Stretch 023 span end missing for {label}")
    return text[:start_index] + replacement + text[end_index:]


def add_shared_persistence(source: str) -> str:
    # Distinct experiment identity only.
    source = source.replace(
        "LOOM Stretch 022 — Five-Token H36 Hotset Variant",
        "LOOM Stretch 023 — Five-Token H36 Full-Weight Persistent Variant",
    )
    source = source.replace(
        "Stretch 022 — Five-Token H36 Hotset Variant",
        "Stretch 023 — Five-Token H36 Full-Weight Persistent Variant",
    )
    source = source.replace(
        "five-token-h36-hotset-022-h36",
        "five-token-h36-full-persistent-023-full",
    )

    source = replace_once(
        source,
        "EXPECTED_HOTSET_BYTES = 36 * EXPECTED_LAYER_BYTES\nHOTSET_ACTIVE_TOLERANCE = 8 * 1024 * 1024\n",
        "EXPECTED_HOTSET_BYTES = 36 * EXPECTED_LAYER_BYTES\n"
        "HOTSET_ACTIVE_TOLERANCE = 8 * 1024 * 1024\n"
        "EXPECTED_SHARED_PERSISTENT_BYTES = EXPECTED_EMBED_BYTES + EXPECTED_NORM_BYTES + EXPECTED_HEAD_BYTES\n"
        "SHARED_ACTIVE_TOLERANCE = 16 * 1024 * 1024\n",
        "shared persistence constants",
    )
    source = replace_once(
        source,
        '    persistent_blocks = {}\n\n    class RUsageInfoV2',
        '    persistent_blocks = {}\n    persistent_shared = {}\n\n    class RUsageInfoV2',
        "persistent shared dictionary",
    )

    embedding_start = "        # Embedding.\n"
    embedding_end = "        # Transformer body with persistent per-layer cache.\n"
    embedding_replacement = '''        # Embedding — persistent shared stage.\n        embed_pre_active = int(mx.get_active_memory())\n        embed_io_before_select = rusage_snapshot()\n        embed_stage = persistent_shared["embedding"]\n        embed_io_after_select = rusage_snapshot()\n        embed_bytes = EXPECTED_EMBED_BYTES\n        embed_pre_eval_active = int(mx.get_active_memory())\n        started = time.perf_counter()\n        mx.eval(embed_stage.parameters())\n        embed_materialize_wall = time.perf_counter() - started\n        embed_io_after_materialize = rusage_snapshot()\n        embed_post_materialize_active = int(mx.get_active_memory())\n        started = time.perf_counter()\n        h = embed_stage(ids)\n        mx.eval(h)\n        embed_forward_wall = time.perf_counter() - started\n        del embed_stage\n        gc.collect()\n        mx.clear_cache()\n        gc.collect()\n        embed_post_clear_active = int(mx.get_active_memory())\n        stage_records["embedding"] = {\n            "selected_bytes": embed_bytes,\n            "pre_active_bytes": embed_pre_active,\n            "pre_eval_active_bytes": embed_pre_eval_active,\n            "post_materialize_active_bytes": embed_post_materialize_active,\n            "post_clear_active_bytes": embed_post_clear_active,\n            "pre_eval_delta_bytes": embed_pre_eval_active - embed_pre_active,\n            "materialized_delta_bytes": embed_post_materialize_active - embed_pre_active,\n            "post_clear_delta_bytes": embed_post_clear_active - embed_pre_active,\n            "materialize_wall_seconds": round(embed_materialize_wall, 6),\n            "forward_wall_seconds": round(embed_forward_wall, 6),\n            "persistent": True,\n        }\n        stage_records["embedding"]["io_select_delta"] = rusage_delta(embed_io_before_select, embed_io_after_select)\n        stage_records["embedding"]["io_materialize_delta"] = rusage_delta(embed_io_after_select, embed_io_after_materialize)\n        save_state(f"stream_{label}_embedding_complete", stage=stage_records["embedding"], cache=cache_snapshot(caches))\n\n'''
    source = replace_span(source, embedding_start, embedding_end, embedding_replacement, "embedding stage")

    norm_start = "        # Final RMSNorm.\n"
    norm_end = "        # LM head.\n"
    norm_replacement = '''        # Final RMSNorm — persistent shared stage.\n        norm_pre_active = int(mx.get_active_memory())\n        norm_io_before_select = rusage_snapshot()\n        norm_stage = persistent_shared["norm"]\n        norm_io_after_select = rusage_snapshot()\n        norm_bytes = EXPECTED_NORM_BYTES\n        norm_pre_eval_active = int(mx.get_active_memory())\n        started = time.perf_counter()\n        mx.eval(norm_stage.parameters())\n        norm_materialize_wall = time.perf_counter() - started\n        norm_io_after_materialize = rusage_snapshot()\n        norm_post_materialize_active = int(mx.get_active_memory())\n        started = time.perf_counter()\n        norm_out = norm_stage(h)\n        mx.eval(norm_out)\n        norm_forward_wall = time.perf_counter() - started\n        old_h = h\n        h = norm_out\n        del old_h, norm_stage\n        gc.collect()\n        mx.clear_cache()\n        gc.collect()\n        norm_post_clear_active = int(mx.get_active_memory())\n        stage_records["norm"] = {\n            "selected_bytes": norm_bytes,\n            "pre_active_bytes": norm_pre_active,\n            "pre_eval_active_bytes": norm_pre_eval_active,\n            "post_materialize_active_bytes": norm_post_materialize_active,\n            "post_clear_active_bytes": norm_post_clear_active,\n            "pre_eval_delta_bytes": norm_pre_eval_active - norm_pre_active,\n            "materialized_delta_bytes": norm_post_materialize_active - norm_pre_active,\n            "post_clear_delta_bytes": norm_post_clear_active - norm_pre_active,\n            "materialize_wall_seconds": round(norm_materialize_wall, 6),\n            "forward_wall_seconds": round(norm_forward_wall, 6),\n            "persistent": True,\n        }\n        stage_records["norm"]["io_select_delta"] = rusage_delta(norm_io_before_select, norm_io_after_select)\n        stage_records["norm"]["io_materialize_delta"] = rusage_delta(norm_io_after_select, norm_io_after_materialize)\n        save_state(f"stream_{label}_norm_complete", stage=stage_records["norm"], cache=cache_snapshot(caches))\n\n'''
    source = replace_span(source, norm_start, norm_end, norm_replacement, "norm stage")

    head_start = "        # LM head.\n"
    head_end = "        max_layer_delta = max(c[\"materialized_delta_bytes\"] for c in cycles)\n"
    head_replacement = '''        # LM head — persistent shared stage.\n        head_pre_active = int(mx.get_active_memory())\n        head_io_before_select = rusage_snapshot()\n        head_stage = persistent_shared["head"]\n        head_io_after_select = rusage_snapshot()\n        head_bytes = EXPECTED_HEAD_BYTES\n        head_pre_eval_active = int(mx.get_active_memory())\n        started = time.perf_counter()\n        mx.eval(head_stage.parameters())\n        head_materialize_wall = time.perf_counter() - started\n        head_io_after_materialize = rusage_snapshot()\n        head_post_materialize_active = int(mx.get_active_memory())\n        started = time.perf_counter()\n        logits = head_stage(h)\n        mx.eval(logits)\n        head_forward_wall = time.perf_counter() - started\n        del h, head_stage\n        gc.collect()\n        mx.clear_cache()\n        gc.collect()\n        head_post_clear_active = int(mx.get_active_memory())\n        stage_records["head"] = {\n            "selected_bytes": head_bytes,\n            "pre_active_bytes": head_pre_active,\n            "pre_eval_active_bytes": head_pre_eval_active,\n            "post_materialize_active_bytes": head_post_materialize_active,\n            "post_clear_active_bytes": head_post_clear_active,\n            "pre_eval_delta_bytes": head_pre_eval_active - head_pre_active,\n            "materialized_delta_bytes": head_post_materialize_active - head_pre_active,\n            "post_clear_delta_bytes": head_post_clear_active - head_pre_active,\n            "materialize_wall_seconds": round(head_materialize_wall, 6),\n            "forward_wall_seconds": round(head_forward_wall, 6),\n            "persistent": True,\n        }\n        stage_records["head"]["io_select_delta"] = rusage_delta(head_io_before_select, head_io_after_select)\n        stage_records["head"]["io_materialize_delta"] = rusage_delta(head_io_after_select, head_io_after_materialize)\n        save_state(f"stream_{label}_head_complete", stage=stage_records["head"], cache=cache_snapshot(caches))\n\n'''
    source = replace_span(source, head_start, head_end, head_replacement, "head stage")

    # Shared modules are materialized exactly once after the H36 transformer
    # hotset and before the measured streamed prompt/target passes.
    setup_anchor = '    save_state("stream_hotset_ready", hotset=hotset_record)\n'
    setup = '''    save_state("stream_hotset_ready", hotset=hotset_record)\n\n    # ------------------------------------------------------------------\n    # Persistent shared weight stages: embedding + final norm + LM head.\n    # ------------------------------------------------------------------\n    shared_pre_active = int(mx.get_active_memory())\n    shared_io_start = rusage_snapshot()\n    shared_started = time.perf_counter()\n    shared_stage_records = {}\n\n    shared_selected = select_weights("model.embed_tokens.", "model.")\n    if selected_bytes(shared_selected) != EXPECTED_EMBED_BYTES:\n        raise RuntimeError("persistent embedding payload mismatch")\n    shared_stage = EmbeddingStage()\n    quantize_and_load(shared_stage, shared_selected)\n    eval_started = time.perf_counter()\n    mx.eval(shared_stage.parameters())\n    shared_stage_records["embedding"] = {\n        "selected_bytes": EXPECTED_EMBED_BYTES,\n        "materialize_wall_seconds": round(time.perf_counter() - eval_started, 6),\n    }\n    persistent_shared["embedding"] = shared_stage\n    del shared_selected, shared_stage\n\n    shared_selected = select_weights("model.norm.", "model.")\n    if selected_bytes(shared_selected) != EXPECTED_NORM_BYTES:\n        raise RuntimeError("persistent norm payload mismatch")\n    shared_stage = NormStage()\n    quantize_and_load(shared_stage, shared_selected)\n    eval_started = time.perf_counter()\n    mx.eval(shared_stage.parameters())\n    shared_stage_records["norm"] = {\n        "selected_bytes": EXPECTED_NORM_BYTES,\n        "materialize_wall_seconds": round(time.perf_counter() - eval_started, 6),\n    }\n    persistent_shared["norm"] = shared_stage\n    del shared_selected, shared_stage\n\n    shared_selected = select_weights("lm_head.")\n    if selected_bytes(shared_selected) != EXPECTED_HEAD_BYTES:\n        raise RuntimeError("persistent head payload mismatch")\n    shared_stage = HeadStage()\n    quantize_and_load(shared_stage, shared_selected)\n    eval_started = time.perf_counter()\n    mx.eval(shared_stage.parameters())\n    shared_stage_records["head"] = {\n        "selected_bytes": EXPECTED_HEAD_BYTES,\n        "materialize_wall_seconds": round(time.perf_counter() - eval_started, 6),\n    }\n    persistent_shared["head"] = shared_stage\n    del shared_selected, shared_stage\n    gc.collect()\n    mx.clear_cache()\n    gc.collect()\n\n    shared_post_active = int(mx.get_active_memory())\n    shared_io_end = rusage_snapshot()\n    shared_persistence_record = {\n        "stage_names": ["embedding", "norm", "head"],\n        "expected_payload_bytes": EXPECTED_SHARED_PERSISTENT_BYTES,\n        "pre_active_bytes": shared_pre_active,\n        "post_active_bytes": shared_post_active,\n        "materialized_delta_bytes": shared_post_active - shared_pre_active,\n        "wall_seconds": round(time.perf_counter() - shared_started, 6),\n        "io_delta": rusage_delta(shared_io_start, shared_io_end),\n        "stages": shared_stage_records,\n    }\n    save_state("stream_shared_persistence_ready", shared_persistence=shared_persistence_record)\n'''
    source = replace_once(source, setup_anchor, setup, "shared setup")

    # Child/parent payload promotion.
    source = replace_once(
        source,
        '        "hotset": hotset_record,\n',
        '        "hotset": hotset_record,\n        "shared_persistence": shared_persistence_record,\n',
        "child shared payload",
    )
    source = replace_once(
        source,
        '        "resident", "stream", "hotset", "oracle_sequence_provenance",\n',
        '        "resident", "stream", "hotset", "shared_persistence", "oracle_sequence_provenance",\n',
        "parent shared payload promotion",
    )

    # Shared stages must now be reused rather than rematerialized each pass.
    old_validation = '''    for stage_name, expected in [\n        ("embedding", EXPECTED_EMBED_BYTES),\n        ("norm", EXPECTED_NORM_BYTES),\n        ("head", EXPECTED_HEAD_BYTES),\n    ]:\n        stage = stages.get(stage_name, {})\n        observed = int(stage.get("materialized_delta_bytes", -10**18))\n        if abs(observed - expected) > 1 * 1024 * 1024:\n            return f"{label}: {stage_name} materialized delta {observed} not near {expected}"\n'''
    new_validation = '''    for stage_name, expected in [\n        ("embedding", EXPECTED_EMBED_BYTES),\n        ("norm", EXPECTED_NORM_BYTES),\n        ("head", EXPECTED_HEAD_BYTES),\n    ]:\n        stage = stages.get(stage_name, {})\n        if int(stage.get("selected_bytes", -1)) != expected:\n            return f"{label}: persistent {stage_name} payload provenance mismatch"\n        if not stage.get("persistent"):\n            return f"{label}: {stage_name} not marked persistent"\n        observed = int(stage.get("materialized_delta_bytes", -10**18))\n        if abs(observed) > 4 * 1024 * 1024:\n            return f"{label}: persistent {stage_name} rematerialized {observed} B"\n'''
    source = replace_once(source, old_validation, new_validation, "persistent shared validation")

    # Gate the one-time persistent shared materialization after the inherited
    # H36 hotset gate and before cache/parity evaluation.
    gate_anchor = '    # Cache gates: resident remains sequential; streamed target advances by four.\n'
    gate = '''    shared_persistence = child.get("shared_persistence", {})\n    shared_names = list(shared_persistence.get("stage_names", []))\n    shared_delta = int(shared_persistence.get("materialized_delta_bytes", -10**18))\n    if shared_names != ["embedding", "norm", "head"]:\n        summary["classification"] = "SHARED_PERSISTENCE_PROVENANCE_FAIL"\n        summary["failure_reason"] = f"shared stage names invalid: {shared_names!r}"\n        return finish(7)\n    if int(shared_persistence.get("expected_payload_bytes", -1)) != EXPECTED_SHARED_PERSISTENT_BYTES:\n        summary["classification"] = "SHARED_PERSISTENCE_PROVENANCE_FAIL"\n        summary["failure_reason"] = "shared expected payload mismatch"\n        return finish(7)\n    if abs(shared_delta - EXPECTED_SHARED_PERSISTENT_BYTES) > SHARED_ACTIVE_TOLERANCE:\n        summary["classification"] = "SHARED_PERSISTENCE_SIZE_MISMATCH"\n        summary["failure_reason"] = f"shared delta {shared_delta} B not near {EXPECTED_SHARED_PERSISTENT_BYTES}"\n        return finish(7)\n\n    # Cache gates: resident remains sequential; streamed target advances by four.\n'''
    source = replace_once(source, gate_anchor, gate, "shared persistence gate")

    # Correct raw-weight accounting: all model weights are now persistent.
    old_budget = '''    max_new_stage = int(child["stream"]["max_weight_stage_materialized_delta_bytes"])\n    hybrid_weight_budget = hotset_delta + max_new_stage\n    summary["hybrid_weight_residency"] = {\n        "persistent_hotset_bytes": hotset_delta,\n        "max_new_stage_bytes": max_new_stage,\n        "max_simultaneous_raw_weight_budget_bytes": hybrid_weight_budget,\n        "resident_to_hybrid_raw_weight_budget_ratio": resident_delta / hybrid_weight_budget if hybrid_weight_budget > 0 else None,\n    }\n'''
    new_budget = '''    max_new_stage = int(child["stream"]["max_weight_stage_materialized_delta_bytes"])\n    persistent_weight_bytes = hotset_delta + shared_delta\n    hybrid_weight_budget = persistent_weight_bytes + max(0, max_new_stage)\n    summary["hybrid_weight_residency"] = {\n        "persistent_hotset_bytes": hotset_delta,\n        "persistent_shared_bytes": shared_delta,\n        "persistent_total_raw_weight_bytes": persistent_weight_bytes,\n        "max_new_stage_bytes": max_new_stage,\n        "max_simultaneous_raw_weight_budget_bytes": hybrid_weight_budget,\n        "resident_to_hybrid_raw_weight_budget_ratio": resident_delta / hybrid_weight_budget if hybrid_weight_budget > 0 else None,\n    }\n    summary["full_weight_persistence"] = {\n        "expected_total_weight_bytes": EXPECTED_TOTAL_BYTES,\n        "persistent_transformer_bytes": hotset_delta,\n        "persistent_shared_bytes": shared_delta,\n        "persistent_total_raw_weight_bytes": persistent_weight_bytes,\n        "one_time_shared_setup_wall_seconds": shared_persistence.get("wall_seconds"),\n        "one_time_shared_setup_io_delta": shared_persistence.get("io_delta"),\n    }\n'''
    source = replace_once(source, old_budget, new_budget, "full persistence budget")

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    h36_path = repo / SOURCE_H36_PATH
    source017_path = repo / SOURCE_017_PATH
    source013_path = repo / SOURCE_013_PATH
    observed_h36 = git_blob(h36_path, repo)
    observed017 = git_blob(source017_path, repo)
    observed013 = git_blob(source013_path, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 023 — H36 Full-Weight Persistent Variant frozen transform")
        print(f"Stretch 022 H36 helper blob: {observed_h36}")
        print(f"Stretch 017 source blob: {observed017}")
        print(f"Stretch 013 source blob: {observed013}")
    if observed_h36 != SOURCE_H36_BLOB or observed017 != SOURCE_017_BLOB or observed013 != SOURCE_013_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    if not is_child:
        print("Source provenance: PASS")
        print("Scientific change: embedding + final norm + LM head streamed -> persistent ONLY")
        print("Transformer hotset: H36 unchanged")
        print("M=5 / model / runtime / KV / parity / I-O / safety: UNCHANGED")

    h36 = load_module(h36_path, "loom_stretch022_h36_transform")
    stretch017 = load_module(source017_path, "loom_stretch017_transform_full")
    transformed = h36.transformed_013_wrapper(
        source013_path.read_text(encoding="utf-8"), stretch017
    )
    transformed = add_shared_persistence(transformed)

    required = [
        "ORACLE_BLOCK_SIZE = 5",
        "ORACLE_BLOCK_COUNT = 3",
        "GENERATED_TOKENS = 15\\n",
        "HOTSET_LAYER_IDS = tuple(range(36))",
        "EXPECTED_SHARED_PERSISTENT_BYTES",
        'persistent_shared["embedding"]',
        'persistent_shared["norm"]',
        'persistent_shared["head"]',
        "SHARED_PERSISTENCE_SIZE_MISMATCH",
        "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
        "five-token-h36-full-persistent-023-full",
        "MAX_SWAP_MB = 5600.0",
    ]
    missing = [fragment for fragment in required if fragment not in transformed]
    if missing:
        raise RuntimeError(f"Stretch 023 transformed-source invariant failed; missing {missing}")

    namespace = {
        "__name__": "__main__",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(transformed, str(source013_path), "exec"), namespace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
