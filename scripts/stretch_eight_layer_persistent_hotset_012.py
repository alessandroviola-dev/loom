#!/usr/bin/env python3
"""LOOM Stretch 012 — eight-layer persistent transformer hotset.

Builds the exact frozen Stretch 011 workload from its frozen upstream transforms,
then changes one scientific factor: transformer layers 0..7 are materialized once
and retained across prompt + 16 autoregressive feedback passes. Layers 8..35 and
all shared stages remain streamed. Darwin I/O attribution and all correctness /
resource gates remain inherited.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SOURCE_009_BLOB = "3e0780850bb65f9dccf07946f89597fa2e4d17e1"
SOURCE_010_BLOB = "ff3dc83abc6388113fca15594eef6b3ec00ebe50"
SOURCE_011_BLOB = "16125f7eb0b2fb662591e194de0498513a563a6d"


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


def replace_exact(text: str, old: str, new: str, expected_count: int, label: str) -> str:
    observed = text.count(old)
    if observed != expected_count:
        raise RuntimeError(
            f"hotset transform failed for {label}: expected {expected_count} occurrence(s), found {observed}"
        )
    return text.replace(old, new)


def add_hotset_transform(source: str) -> str:
    # Experiment identity only.
    source = replace_exact(
        source,
        'print("LOOM Stretch 011 — Materialization I/O Attribution")',
        'print("LOOM Stretch 012 — Eight-Layer Persistent Hotset")',
        1,
        "terminal title",
    )
    source = replace_exact(
        source,
        '"experiment": "Stretch 011 — Materialization I/O Attribution",',
        '"experiment": "Stretch 012 — Eight-Layer Persistent Hotset",',
        1,
        "summary title",
    )
    source = replace_exact(
        source,
        '"materialization-io-attribution-011"',
        '"eight-layer-persistent-hotset-012"',
        1,
        "run directory",
    )

    # Frozen hotset constants.
    source = replace_exact(
        source,
        'FINAL_OFFSET = PROMPT_LEN + GENERATED_TOKENS\n',
        'FINAL_OFFSET = PROMPT_LEN + GENERATED_TOKENS\nHOTSET_LAYER_IDS = tuple(range(8))\nEXPECTED_HOTSET_BYTES = 8 * EXPECTED_LAYER_BYTES\nHOTSET_ACTIVE_TOLERANCE = 8 * 1024 * 1024\n',
        1,
        "hotset constants",
    )

    # Persistent block dictionary is closed over by build_block().
    source = replace_exact(
        source,
        '    quant = config["quantization"]\n\n    class RUsageInfoV2',
        '    quant = config["quantization"]\n    persistent_blocks = {}\n\n    class RUsageInfoV2',
        1,
        "persistent block dictionary",
    )

    # Reuse already-materialized hot blocks; normal path remains byte-identical
    # for layers 8..35.
    source = replace_exact(
        source,
        '    def build_block(layer_id: int):\n        marker = f"model.layers.{layer_id}."\n',
        '    def build_block(layer_id: int):\n        if layer_id in persistent_blocks:\n            return persistent_blocks[layer_id], None\n        marker = f"model.layers.{layer_id}."\n',
        1,
        "build_block persistent reuse",
    )

    # Materialize the frozen eight-layer hotset exactly once after clearing the
    # resident control and before the streamed prompt begins.
    source = replace_exact(
        source,
        '''    resident_after_clear = mem()\n    save_state("resident_control_cleared", memory_after_clear=resident_after_clear)\n\n    # ------------------------------------------------------------------\n    # Streamed prompt + four feedback passes.\n    # ------------------------------------------------------------------\n    mx.reset_peak_memory()\n''',
        '''    resident_after_clear = mem()\n    save_state("resident_control_cleared", memory_after_clear=resident_after_clear)\n\n    # ------------------------------------------------------------------\n    # Persistent transformer hotset: layers 0..7, materialized once.\n    # ------------------------------------------------------------------\n    hotset_pre_active = int(mx.get_active_memory())\n    hotset_io_start = rusage_snapshot()\n    hotset_started = time.perf_counter()\n    hotset_layers = []\n    for hot_layer_id in HOTSET_LAYER_IDS:\n        layer_pre_active = int(mx.get_active_memory())\n        io_before_build = rusage_snapshot()\n        hot_block, hot_selected = build_block(hot_layer_id)\n        io_after_build = rusage_snapshot()\n        layer_pre_eval_active = int(mx.get_active_memory())\n        eval_started = time.perf_counter()\n        mx.eval(hot_block.parameters())\n        eval_wall = time.perf_counter() - eval_started\n        io_after_materialize = rusage_snapshot()\n        layer_post_active = int(mx.get_active_memory())\n        persistent_blocks[hot_layer_id] = hot_block\n        selected_count = len(hot_selected) if hot_selected is not None else 0\n        selected_nbytes = selected_bytes(hot_selected) if hot_selected is not None else 0\n        del hot_selected, hot_block\n        gc.collect()\n        mx.clear_cache()\n        gc.collect()\n        hotset_layers.append({\n            "layer_id": hot_layer_id,\n            "selected_tensors": selected_count,\n            "selected_bytes": selected_nbytes,\n            "pre_active_bytes": layer_pre_active,\n            "pre_eval_active_bytes": layer_pre_eval_active,\n            "post_active_bytes": layer_post_active,\n            "materialized_delta_bytes": layer_post_active - layer_pre_active,\n            "materialize_wall_seconds": round(eval_wall, 6),\n            "io_build_delta": rusage_delta(io_before_build, io_after_build),\n            "io_materialize_delta": rusage_delta(io_after_build, io_after_materialize),\n        })\n    hotset_post_active = int(mx.get_active_memory())\n    hotset_io_end = rusage_snapshot()\n    hotset_record = {\n        "layer_ids": list(HOTSET_LAYER_IDS),\n        "count": len(persistent_blocks),\n        "expected_payload_bytes": EXPECTED_HOTSET_BYTES,\n        "pre_active_bytes": hotset_pre_active,\n        "post_active_bytes": hotset_post_active,\n        "materialized_delta_bytes": hotset_post_active - hotset_pre_active,\n        "wall_seconds": round(time.perf_counter() - hotset_started, 6),\n        "io_delta": rusage_delta(hotset_io_start, hotset_io_end),\n        "layers": hotset_layers,\n    }\n    save_state("stream_hotset_ready", hotset=hotset_record)\n\n    # ------------------------------------------------------------------\n    # Streamed prompt + sixteen feedback passes with persistent hotset.\n    # ------------------------------------------------------------------\n    mx.reset_peak_memory()\n''',
        1,
        "hotset initial materialization",
    )

    # Persist hotset accounting into child-final.json.
    source = replace_exact(
        source,
        '    final = {\n        "ok": True,\n',
        '    final = {\n        "ok": True,\n        "hotset": hotset_record,\n',
        1,
        "child final hotset record",
    )

    # Parent imports hotset child payload.
    source = replace_exact(
        source,
        '''    for key in [\n        "resident", "stream", "prompt_parity", "step_parities",\n        "generated_sequence_equal", "expected_kv_total_bytes",\n    ]:\n''',
        '''    for key in [\n        "resident", "stream", "hotset", "prompt_parity", "step_parities",\n        "generated_sequence_equal", "expected_kv_total_bytes",\n    ]:\n''',
        1,
        "parent hotset payload promotion",
    )

    # Validation now distinguishes persistent hotset cycles from normal streamed
    # cycles. No layer-sized rematerialization is allowed for layers 0..7.
    source = replace_exact(
        source,
        '''    for cycle in cycles:\n        pre_eval = int(cycle.get("pre_eval_delta_bytes", 10**18))\n        materialized = int(cycle.get("materialized_delta_bytes", -10**18))\n        if pre_eval > 32 * 1024 * 1024:\n            return f"{label}: layer {cycle.get('layer_id')} pre-eval delta {pre_eval} >32 MiB"\n        if abs(materialized - EXPECTED_LAYER_BYTES) > 1 * 1024 * 1024:\n            return f"{label}: layer {cycle.get('layer_id')} materialized {materialized} not near {EXPECTED_LAYER_BYTES}"\n    return None\n''',
        '''    for cycle in cycles:\n        layer_id = int(cycle.get("layer_id", -1))\n        pre_eval = int(cycle.get("pre_eval_delta_bytes", 10**18))\n        materialized = int(cycle.get("materialized_delta_bytes", -10**18))\n        if layer_id in HOTSET_LAYER_IDS:\n            if abs(pre_eval) > 4 * 1024 * 1024:\n                return f"{label}: persistent layer {layer_id} pre-eval delta {pre_eval} exceeds ±4 MiB"\n            if abs(materialized) > 4 * 1024 * 1024:\n                return f"{label}: persistent layer {layer_id} rematerialized {materialized} B"\n        else:\n            if pre_eval > 32 * 1024 * 1024:\n                return f"{label}: layer {layer_id} pre-eval delta {pre_eval} >32 MiB"\n            if abs(materialized - EXPECTED_LAYER_BYTES) > 1 * 1024 * 1024:\n                return f"{label}: layer {layer_id} materialized {materialized} not near {EXPECTED_LAYER_BYTES}"\n    return None\n''',
        1,
        "hotset-aware streamed pass validation",
    )

    # Add hotset residency gate after the inherited resident accounting gate.
    source = replace_exact(
        source,
        '''    resident_delta = int(child["resident"]["materialized_delta_bytes"])\n    if abs(resident_delta - EXPECTED_TOTAL_BYTES) > 64 * 1024 * 1024:\n        summary["classification"] = "RESIDENT_CONTROL_SIZE_MISMATCH"\n        summary["failure_reason"] = f"resident delta {resident_delta} B not near {EXPECTED_TOTAL_BYTES}"\n        return finish(7)\n\n    # Cache gates: prompt then four feedback positions.\n''',
        '''    resident_delta = int(child["resident"]["materialized_delta_bytes"])\n    if abs(resident_delta - EXPECTED_TOTAL_BYTES) > 64 * 1024 * 1024:\n        summary["classification"] = "RESIDENT_CONTROL_SIZE_MISMATCH"\n        summary["failure_reason"] = f"resident delta {resident_delta} B not near {EXPECTED_TOTAL_BYTES}"\n        return finish(7)\n\n    hotset = child.get("hotset", {})\n    observed_hotset_ids = [int(x) for x in hotset.get("layer_ids", [])]\n    hotset_delta = int(hotset.get("materialized_delta_bytes", -10**18))\n    if observed_hotset_ids != list(HOTSET_LAYER_IDS) or int(hotset.get("count", -1)) != len(HOTSET_LAYER_IDS):\n        summary["classification"] = "HOTSET_PROVENANCE_FAIL"\n        summary["failure_reason"] = f"hotset IDs/count invalid: {hotset!r}"\n        return finish(7)\n    if abs(hotset_delta - EXPECTED_HOTSET_BYTES) > HOTSET_ACTIVE_TOLERANCE:\n        summary["classification"] = "HOTSET_MATERIALIZATION_SIZE_MISMATCH"\n        summary["failure_reason"] = f"hotset delta {hotset_delta} B not near {EXPECTED_HOTSET_BYTES}"\n        return finish(7)\n\n    # Cache gates: prompt then sixteen feedback positions.\n''',
        1,
        "hotset accounting gate",
    )

    # Promote the true simultaneous raw-weight budget: persistent hotset plus
    # largest newly-materialized shared/streamed stage.
    source = replace_exact(
        source,
        '''    summary["per_token_timing"] = {\n        "layer_materialize_seconds": materialize_times,\n''',
        '''    max_new_stage = int(child["stream"]["max_weight_stage_materialized_delta_bytes"])\n    hybrid_weight_budget = hotset_delta + max_new_stage\n    summary["hybrid_weight_residency"] = {\n        "persistent_hotset_bytes": hotset_delta,\n        "max_new_stage_bytes": max_new_stage,\n        "max_simultaneous_raw_weight_budget_bytes": hybrid_weight_budget,\n        "resident_to_hybrid_raw_weight_budget_ratio": resident_delta / hybrid_weight_budget if hybrid_weight_budget > 0 else None,\n    }\n\n    summary["per_token_timing"] = {\n        "layer_materialize_seconds": materialize_times,\n''',
        1,
        "hybrid raw-weight budget",
    )

    # Extend terminal summary with hotset/hybrid budget.
    source = replace_exact(
        source,
        '''            print(f"Resident/max-streamed-stage ratio: {summary['stream'].get('resident_to_max_streamed_stage_ratio')}")\n            print(f"Resident cache offsets final: {sorted(set(summary['resident']['steps'][-1]['cache']['offsets']))}")\n''',
        '''            print(f"Resident/max newly-materialized stage ratio (hotset excluded): {summary['stream'].get('resident_to_max_streamed_stage_ratio')}")\n            if summary.get("hotset"):\n                print(f"Persistent hotset materialized delta: {summary['hotset'].get('materialized_delta_bytes')} B")\n            if summary.get("hybrid_weight_residency"):\n                hw = summary["hybrid_weight_residency"]\n                print(f"Hybrid max simultaneous raw-weight budget: {hw.get('max_simultaneous_raw_weight_budget_bytes')} B")\n                print(f"Resident/hybrid raw-weight budget ratio: {hw.get('resident_to_hybrid_raw_weight_budget_ratio')}")\n            print(f"Resident cache offsets final: {sorted(set(summary['resident']['steps'][-1]['cache']['offsets']))}")\n''',
        1,
        "hotset terminal display",
    )

    # The inherited I/O attribution remains complete; rename PASS only after all
    # inherited scientific and telemetry gates have succeeded.
    source = replace_exact(
        source,
        '    summary["classification"] = "MATERIALIZATION_IO_ATTRIBUTION_PASS"\n',
        '    summary["classification"] = "EIGHT_LAYER_PERSISTENT_HOTSET_PASS"\n',
        1,
        "PASS classification",
    )

    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    source009 = repo / "scripts" / "stretch_four_token_kv_autoregressive_parity_009.py"
    source010 = repo / "scripts" / "stretch_sixteen_token_autoregressive_stability_010.py"
    source011 = repo / "scripts" / "stretch_materialization_io_attribution_011.py"

    observed009 = git_blob(source009, repo)
    observed010 = git_blob(source010, repo)
    observed011 = git_blob(source011, repo)
    is_child = len(sys.argv) > 1 and sys.argv[1] == "--child"

    if not is_child:
        print("LOOM Stretch 012 — Eight-Layer Persistent Hotset frozen transform")
        print(f"Stretch 009 source blob: {observed009}")
        print(f"Stretch 010 transform blob: {observed010}")
        print(f"Stretch 011 instrumentation blob: {observed011}")

    if (
        observed009 != SOURCE_009_BLOB
        or observed010 != SOURCE_010_BLOB
        or observed011 != SOURCE_011_BLOB
    ):
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    if not is_child:
        print("Source provenance: PASS")

    transform010 = load_module(source010, "loom_stretch010_transform")
    transform011 = load_module(source011, "loom_stretch011_transform")

    source = transform010.transformed_source(source009.read_text(encoding="utf-8"))
    source = transform011.add_io_instrumentation(source)
    source = add_hotset_transform(source)

    required_fragments = [
        'GENERATED_TOKENS = 16',
        'HOTSET_LAYER_IDS = tuple(range(8))',
        'EXPECTED_HOTSET_BYTES = 8 * EXPECTED_LAYER_BYTES',
        'EIGHT_LAYER_PERSISTENT_HOTSET_PASS',
        'persistent_blocks',
        'stream_hotset_ready',
        'io_materialize_delta',
        'proc_pid_rusage',
        'stdout=out_handle',
        'stderr=err_handle',
        'MIN_FREE_PERCENT = 5',
        'MAX_SWAP_MB = 5600.0',
    ]
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise RuntimeError(f"hotset transformed-source invariant failed; missing {missing}")

    if not is_child:
        print("Frozen Stretch 011 workload/instrumentation reconstruction: PASS")
        print("Scientific change: retain transformer layers 0..7 across prompt + 16 tokens ONLY")
        print("Expected persistent hotset payload: 675418112 B")
        print("Layers 8..35/shared stages: streamed as before")
        print("Darwin I/O attribution: PRESERVED")
        print("Model/KV/parity/safety gates: PRESERVED")

    transformed_globals = {
        "__name__": "__main__",
        # Parent child subprocess must execute this wrapper again so both modes
        # use the identical transformed source.
        "__file__": str(Path(__file__).resolve()),
    }
    exec(compile(source, str(source009), "exec"), transformed_globals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
