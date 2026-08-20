#!/usr/bin/env python3
"""Stretch 040: explicit Python GC cleanup-composition feasibility only.

The promoted cadence is frozen: exactly one final cleanup after two M5 blocks
(ten accepted oracle tokens).  Eight canonical diagnostic cycles first time
``gc.collect -> mx.clear_cache -> gc.collect`` component walls.  Only if their
fresh ideal-elimination bound reaches 5% does this one-load harness compare
that CONTROL with ``mx.clear_cache`` only.  It is not an ABBA.
"""
from __future__ import annotations

import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_LAUNCHER = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
STRETCH038_RUNNER = "scripts/stretch_s1r8_deferred_cleanup_comparison_038.py"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
PROMOTED_CONTROL_SHA256 = "9f94787f7a002a8da95e8352f134eac11f1b072b9363fe600dcac1122080a54c"
PROMOTED_S1_R8_SHA256 = "82888b134a6c4e0ba56bb24896bce2fd37c9d78c899380af35e0e823ad5fcbe3"
PROMOTED_S1_R8_INJECTION_SHA256 = "a086806a314d387770dac54e9140b9526bf7fe9097819f449bba17b7fc1f3ad4"
TOTAL_WEIGHTS = 3_583_928_320
DIAGNOSTIC_CYCLES = 8
PRIMARY_SCHEDULE = ("CONTROL", "TREATMENT", "TREATMENT") * 6
EXTENDED_TREATMENT_CYCLES = 12
HARNESS_REVISION = "STRETCH_040_GC_COMPOSITION_FEASIBILITY_ONE_LOAD_FIX1"
CLEANUP_SNIPPET = "gc.collect()\nmx.clear_cache()\ngc.collect()\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def host_sample(abort: bool) -> dict:
    pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
    free_match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
    swap_match = re.search(r"used = ([0-9.,]+)([MG])", swap_text)
    if not free_match or not swap_match:
        raise RuntimeError("STRETCH040_TELEMETRY_UNAVAILABLE")
    free = int(free_match.group(1))
    swap = float(swap_match.group(1).replace(",", ".")) * (1024.0 if swap_match.group(2) == "G" else 1.0)
    sample = {"free_memory_percent": free, "swap_used_mb": swap, "sampled_at_utc": utc_now()}
    if abort and (free < 5 or swap > 5600):
        raise RuntimeError(f"STRETCH040_RESOURCE_ABORT free={free}% swap={swap:.2f}MB")
    return sample


def literal_launcher(repo: Path) -> Path:
    path = repo / CANONICAL_LAUNCHER
    if not path.is_symlink():
        raise RuntimeError("STRETCH040_LITERAL_CANONICAL_VENV_LAUNCHER_FAIL")
    return path


def git_blob(repo: Path, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=repo, text=True).strip()


def patch_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"STRETCH040_{label}_ANCHOR expected once, found {count}")
    return source.replace(old, new, 1)


def extension_source() -> str:
    """Inserted in place of Stretch-038's one scientific constituent.

    The inherited resident/prompt sequence remains an excluded warmup.  Timed
    cycles do not invoke an extra prompt cleanup: their one final cleanup is
    exactly the frozen once-per-two-M5-block event under study.
    """
    return r'''    # Stretch 040 feasibility: same one cleanup / two M5 blocks; composition only.
    import statistics as __stretch040_statistics
    import resource as __stretch040_resource
    __stretch040_result = {"harness_revision": "STRETCH_040_GC_COMPOSITION_FEASIBILITY_ONE_LOAD_FIX1", "warmup_excluded": True, "diagnostic_cycles_requested": 8, "primary_schedule_requested": ["CONTROL", "TREATMENT", "TREATMENT"] * 6, "extended_treatment_cycles_requested": 12, "cycles": [], "deliberate_cache_purge": False, "runtime_or_model_change": False}

    def __stretch040_mem():
        return {"mlx_active_bytes": int(mx.get_active_memory()), "mlx_peak_bytes": int(mx.get_peak_memory()), "mlx_cache_bytes": int(mx.get_cache_memory()) if hasattr(mx, "get_cache_memory") else None}

    def __stretch040_snapshot():
        pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
        match = __import__("re").search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
        swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
        swap_match = __import__("re").search(r"used = ([0-9.,]+)([MG])", swap_text)
        if not match or not swap_match:
            raise RuntimeError("STRETCH040_TELEMETRY_UNAVAILABLE")
        free = int(match.group(1)); swap = float(swap_match.group(1).replace(",", ".")) * (1024.0 if swap_match.group(2) == "G" else 1.0)
        if free < 5 or swap > 5600:
            raise RuntimeError(f"STRETCH040_RESOURCE_ABORT free={free}% swap={swap:.2f}MB")
        return {"free_memory_percent": free, "swap_used_mb": swap, "python_gc_enabled": bool(gc.isenabled()), "python_gc_count": list(gc.get_count()), "python_gc_garbage_length": len(gc.garbage), "python_tracked_objects": len(gc.get_objects()), "process_rss_max_kb": int(__stretch040_resource.getrusage(__stretch040_resource.RUSAGE_SELF).ru_maxrss), **__stretch040_mem()}

    __stretch040_current_cycle = None
    def __stretch040_instrumented_cleanup_callback():
        # No telemetry or work is placed between the canonical component calls:
        # CONTROL is exactly gc.collect(); mx.clear_cache(); gc.collect().
        global __stretch040_current_cycle
        cycle = __stretch040_current_cycle
        if cycle is None:
            raise RuntimeError("STRETCH040_CLEANUP_WITHOUT_CYCLE")
        composition = cycle["composition"]
        record = {"composition": composition, "python_gc_enabled_before": bool(gc.isenabled()), "python_gc_count_before": list(gc.get_count()), "python_gc_garbage_length_before": len(gc.garbage), "python_tracked_objects_before": len(gc.get_objects())}
        if composition == "CONTROL":
            first_started = time.perf_counter(); first_collected = gc.collect(); first_wall = time.perf_counter() - first_started
        else:
            first_collected = None; first_wall = 0.0
        clear_started = time.perf_counter(); mx.clear_cache(); clear_wall = time.perf_counter() - clear_started
        if composition == "CONTROL":
            second_started = time.perf_counter(); second_collected = gc.collect(); second_wall = time.perf_counter() - second_started
        else:
            second_collected = None; second_wall = 0.0
        record.update({"first_gc_collect_wall_seconds": first_wall, "first_gc_collected_objects": first_collected, "mx_clear_cache_wall_seconds": clear_wall, "second_gc_collect_wall_seconds": second_wall, "second_gc_collected_objects": second_collected, "cleanup_total_wall_seconds": first_wall + clear_wall + second_wall, "python_gc_enabled_after": bool(gc.isenabled()), "python_gc_count_after": list(gc.get_count()), "python_gc_garbage_length_after": len(gc.garbage), "python_tracked_objects_after": len(gc.get_objects()), **__stretch040_mem()})
        cycle["cleanup"] = record

    # Keep the callback module-global so inherited run_streamed_pass() retains
    # its original scope and all pre-extension warmup cleanups use its exact
    # fallback triple before this instrumentation is installed.
    globals()["__stretch040_cleanup_callback"] = __stretch040_instrumented_cleanup_callback

    def __stretch040_rows(logits, start, prompt_prediction, previous_prediction, draft):
        predictions = [prompt_prediction if start == 0 else previous_prediction] + [token_value(logits[:, pos:pos+1, :]) for pos in range(ORACLE_BLOCK_SIZE - 1)]
        rows = []
        for pos, expected in enumerate(draft):
            resident_logits = resident_step_logits[start + pos]; target_logits = logits[:, pos:pos+1, :]
            delta = mx.abs(resident_logits.astype(mx.float32) - target_logits.astype(mx.float32)); mx.eval(delta)
            maximum, mean = float(mx.max(delta).item()), float(mx.mean(delta).item())
            threshold = 1e-5 + 1e-5 * float(mx.max(mx.abs(resident_logits.astype(mx.float32))).item())
            resident_top1, target_top1 = resident_steps[start + pos]["predicted_top1"], token_value(target_logits)
            rows.append({"step": start + pos + 1, "oracle_token": int(expected), "prediction": int(predictions[pos]), "accepted": int(predictions[pos]) == int(expected), "max_abs_diff": maximum, "mean_abs_diff": mean, "threshold": threshold, "logits_pass": maximum <= threshold, "resident_top1": int(resident_top1), "target_top1": int(target_top1), "top1_equal": int(resident_top1) == int(target_top1)})
            del delta
        return rows, token_value(logits[:, ORACLE_BLOCK_SIZE-1:ORACLE_BLOCK_SIZE, :])

    def __stretch040_cycle(composition, phase, ordinal):
        global __stretch038_cleanup_enabled, __stretch038_before_cleanup, __stretch040_current_cycle
        cycle = {"phase": phase, "ordinal": ordinal, "composition": composition, "cleanup_cadence": {"block1_executed": False, "block2_executed": True}, "snapshots": {}, "blocks": []}
        # A fresh BF16 KV cache establishes the fixed prompt for this cycle.
        # Cleanup remains disabled for prompt and block 1; the sole timed-cycle
        # cleanup event is after block 2, exactly once per ten accepted tokens.
        caches = [KVCache() for _ in range(args.num_hidden_layers)]
        __stretch038_cleanup_enabled = False; __stretch038_before_cleanup = None; __stretch040_current_cycle = None
        prompt_ids = make_ids(prompt_token_ids); prompt_logits, _ = run_streamed_pass(prompt_ids, caches, f"stretch040_prompt_{ordinal}")
        prompt_token = token_value(prompt_logits); prompt_delta = mx.abs(resident_prompt_logits.astype(mx.float32) - prompt_logits.astype(mx.float32)); mx.eval(prompt_delta)
        prompt_max = float(mx.max(prompt_delta).item()); prompt_threshold = 1e-5 + 1e-5 * resident_prompt_max_abs
        cycle["prompt"] = {"token": prompt_token, "resident_token": token1, "token_equal": prompt_token == token1, "max_abs_diff": prompt_max, "threshold": prompt_threshold, "logits_pass": prompt_max <= prompt_threshold}
        del prompt_ids, prompt_logits, prompt_delta
        cycle["snapshots"]["before_block1"] = __stretch040_snapshot()
        target_started = time.perf_counter(); previous = None
        for index in range(2):
            start = index * ORACLE_BLOCK_SIZE; draft = oracle_sequence[start:start + ORACLE_BLOCK_SIZE]
            ids = make_ids([draft])
            __stretch038_cleanup_enabled = index == 1
            __stretch040_current_cycle = cycle if index == 1 else None
            __stretch038_before_cleanup = (lambda: cycle["snapshots"].__setitem__("after_block2_before_mx_clear", __stretch040_snapshot())) if index == 1 else None
            pass_started = time.perf_counter(); logits, passed = run_streamed_pass(ids, caches, f"stretch040_{phase}_{ordinal}_block{index + 1}"); pass_finished = time.perf_counter()
            rows, previous = __stretch040_rows(logits, start, prompt_token, previous, draft)
            cleanup = passed["stages"]["shared_stage_cleanup"]
            cycle["blocks"].append({"block": index + 1, "outer_pass_wall_seconds": pass_finished - pass_started, "pass_wall_seconds": passed["total_pass_wall_seconds"], "compute_wall_seconds": passed["total_pass_wall_seconds"] - cleanup["wall_seconds"], "source_cleanup": cleanup, "positions": rows})
            del ids, logits
            if index == 0:
                cycle["snapshots"]["after_block1_before_block2"] = __stretch040_snapshot()
        target_finished = time.perf_counter()
        cycle["total_10_token_target_wall_seconds"] = target_finished - target_started
        cycle["snapshots"]["after_mx_clear"] = __stretch040_snapshot()
        cycle["snapshots"]["before_next_cycle"] = __stretch040_snapshot()
        all_rows = [row for block in cycle["blocks"] for row in block["positions"]]
        cycle["accepted_tokens"] = sum(1 for row in all_rows if row["accepted"])
        cycle["generated_sequence_equal"] = [row["oracle_token"] for row in all_rows] == resident_generated_tokens
        cycle["correctness_pass"] = bool(cycle["prompt"]["token_equal"] and cycle["prompt"]["logits_pass"] and len(all_rows) == 10 and all(row["accepted"] and row["logits_pass"] and row["top1_equal"] for row in all_rows))
        cycle["full_weight_persistence_bytes"] = hotset_record["materialized_delta_bytes"] + shared_persistence_record["materialized_delta_bytes"]
        cycle["cleanup"] = cycle.get("cleanup", {})
        cycle["usable"] = bool(cycle["correctness_pass"] and cycle["generated_sequence_equal"] and cycle["accepted_tokens"] == 10 and cycle["full_weight_persistence_bytes"] == 3583928320 and len(cycle["blocks"]) == 2 and cycle["cleanup_cadence"] == {"block1_executed": False, "block2_executed": True} and cycle["cleanup"].get("composition") == composition)
        if not cycle["usable"]:
            raise RuntimeError(f"STRETCH040_CYCLE_GATE_FAIL {cycle}")
        __stretch040_result["cycles"].append(cycle)
        __stretch038_cleanup_enabled = True; __stretch038_before_cleanup = None; __stretch040_current_cycle = None
        return cycle

    # First, component attribution on eight canonical (CONTROL) cycles.  The
    # resulting ideal-elimination arithmetic determines whether a treatment is
    # even admissible for this feasibility run.
    for ordinal in range(1, 9):
        __stretch040_cycle("CONTROL", "DIAGNOSTIC_CONTROL", ordinal)
    diagnostic = __stretch040_result["cycles"]
    control_total = [x["total_10_token_target_wall_seconds"] for x in diagnostic]
    first_gc = [x["cleanup"]["first_gc_collect_wall_seconds"] for x in diagnostic]
    clear = [x["cleanup"]["mx_clear_cache_wall_seconds"] for x in diagnostic]
    second_gc = [x["cleanup"]["second_gc_collect_wall_seconds"] for x in diagnostic]
    gc_sum = [a + b for a, b in zip(first_gc, second_gc)]
    pooled_control = sum(control_total); pooled_gc = sum(gc_sum)
    ideal_treatment_wall = pooled_control - pooled_gc
    max_ratio = pooled_control / ideal_treatment_wall if ideal_treatment_wall > 0 else float("inf")
    __stretch040_result["component_attribution"] = {"control_cycles": len(diagnostic), "control_total_wall_seconds": control_total, "first_gc_collect_walls_seconds": first_gc, "mx_clear_cache_walls_seconds": clear, "second_gc_collect_walls_seconds": second_gc, "combined_explicit_gc_walls_seconds": gc_sum, "first_gc_collected_objects": [x["cleanup"]["first_gc_collected_objects"] for x in diagnostic], "second_gc_collected_objects": [x["cleanup"]["second_gc_collected_objects"] for x in diagnostic], "means_seconds": {"first_gc_collect": __stretch040_statistics.fmean(first_gc), "mx_clear_cache": __stretch040_statistics.fmean(clear), "second_gc_collect": __stretch040_statistics.fmean(second_gc), "combined_explicit_gc": __stretch040_statistics.fmean(gc_sum), "control_10_token_wall": __stretch040_statistics.fmean(control_total)}, "medians_seconds": {"first_gc_collect": __stretch040_statistics.median(first_gc), "mx_clear_cache": __stretch040_statistics.median(clear), "second_gc_collect": __stretch040_statistics.median(second_gc), "combined_explicit_gc": __stretch040_statistics.median(gc_sum), "control_10_token_wall": __stretch040_statistics.median(control_total)}, "ideal_removal_arithmetic": {"pooled_control_10_token_wall_seconds": pooled_control, "pooled_explicit_gc_wall_seconds": pooled_gc, "perfect_elimination_treatment_wall_seconds": ideal_treatment_wall, "maximum_throughput_equivalent_ratio": max_ratio, "maximum_throughput_equivalent_gain_percent": (max_ratio - 1) * 100}}
    if max_ratio < 1.05:
        __stretch040_result.update({"classification": "STRETCH_040_GC_COMPOSITION_UPSIDE_BELOW_GATE", "decision": "INVESTIGATION_ONLY", "treatment_created": False, "reason": "Combined explicit Python GC wall cannot yield >=5% throughput even under perfect elimination."})
    else:
        for ordinal, composition in enumerate(["CONTROL", "TREATMENT", "TREATMENT"] * 6, 1):
            __stretch040_cycle(composition, "PRIMARY_BALANCED", ordinal)
        primary_treatments = [x for x in __stretch040_result["cycles"] if x["phase"] == "PRIMARY_BALANCED" and x["composition"] == "TREATMENT"]
        stable12 = len(primary_treatments) == 12 and all(x["usable"] for x in primary_treatments)
        if stable12:
            for ordinal in range(1, 13):
                __stretch040_cycle("TREATMENT", "EXTENDED_STABILITY", ordinal)
        primary_control = [x for x in __stretch040_result["cycles"] if x["phase"] == "PRIMARY_BALANCED" and x["composition"] == "CONTROL"]
        primary_treatment = [x for x in __stretch040_result["cycles"] if x["phase"] == "PRIMARY_BALANCED" and x["composition"] == "TREATMENT"]
        control_wall = sum(x["total_10_token_target_wall_seconds"] for x in primary_control)
        treatment_wall = sum(x["total_10_token_target_wall_seconds"] for x in primary_treatment)
        # The C,T,T schedule intentionally has twice as many T cycles; compare
        # equal-cycle mean walls, not unequal raw wall totals.
        control_mean_wall = control_wall / len(primary_control)
        treatment_mean_wall = treatment_wall / len(primary_treatment)
        ratio = control_mean_wall / treatment_mean_wall
        treatment_all = [x for x in __stretch040_result["cycles"] if x["composition"] == "TREATMENT"]
        # Recovery requires active/cache return to a stable non-increasing band
        # after every retained mx.clear_cache; Python counts/objects are retained
        # for inspection rather than treated as an MLX-only proxy.
        recovery = [x["snapshots"]["after_mx_clear"]["mlx_active_bytes"] <= x["snapshots"]["after_block2_before_mx_clear"]["mlx_active_bytes"] for x in treatment_all]
        free = [x["snapshots"]["after_mx_clear"]["free_memory_percent"] for x in treatment_all]
        swap = [x["snapshots"]["after_mx_clear"]["swap_used_mb"] for x in treatment_all]
        tracked = [x["snapshots"]["after_mx_clear"]["python_tracked_objects"] for x in treatment_all]
        gc_counts = [x["snapshots"]["after_mx_clear"]["python_gc_count"] for x in treatment_all]
        # A pathological trajectory is a strict monotonic increase across the
        # complete bounded treatment sequence; report raw values regardless.
        pathological = len(tracked) >= 4 and all(b > a for a, b in zip(tracked, tracked[1:]))
        extended = [x for x in treatment_all if x["phase"] == "EXTENDED_STABILITY"]
        resources_safe = min(free) >= 5 and max(swap) <= 5600
        go = bool(ratio >= 1.05 and stable12 and len(extended) == 12 and all(x["usable"] for x in treatment_all) and all(recovery) and resources_safe and not pathological)
        __stretch040_result.update({"classification": "STRETCH_040_GC_COMPOSITION_FEASIBILITY_GO" if go else "STRETCH_040_GC_COMPOSITION_FEASIBILITY_NO_GO", "decision": "GO_FOR_PREREGISTRATION_ONLY" if go else "NO_GO", "treatment_created": True, "primary_comparison": {"control_cycles": len(primary_control), "treatment_cycles": len(primary_treatment), "control_total_10_token_wall_seconds": control_wall, "treatment_total_10_token_wall_seconds": treatment_wall, "control_mean_10_token_wall_seconds": control_mean_wall, "treatment_mean_10_token_wall_seconds": treatment_mean_wall, "control_median_10_token_wall_seconds": __stretch040_statistics.median([x["total_10_token_target_wall_seconds"] for x in primary_control]), "treatment_median_10_token_wall_seconds": __stretch040_statistics.median([x["total_10_token_target_wall_seconds"] for x in primary_treatment]), "wall_ratio_treatment_over_control": treatment_mean_wall / control_mean_wall, "throughput_equivalent_ratio_treatment_over_control": ratio, "throughput_equivalent_gain_percent": (ratio - 1) * 100}, "treatment_resource_stability": {"treatment_cycles_total": len(treatment_all), "extended_cycles": len(extended), "all_mlx_active_recoveries": all(recovery), "minimum_free_memory_percent": min(free), "peak_swap_mb": max(swap), "python_tracked_objects_after_mx_clear": tracked, "python_gc_counts_after_mx_clear": gc_counts, "strict_monotonic_tracked_object_growth": pathological, "resources_safe": resources_safe, "stability_pass": bool(stable12 and len(extended) == 12 and all(x["usable"] for x in treatment_all) and all(recovery) and resources_safe and not pathological)}})

    __stretch040_result["promoted_frozen_invariants"] = {"m5": 5, "h36": 36, "full_raw_weight_persistence_bytes": hotset_record["materialized_delta_bytes"] + shared_persistence_record["materialized_delta_bytes"], "bf16_kv": True, "s1_r8": True, "cleanup_cadence": "one explicit cleanup event after two M5 blocks / 10 accepted tokens", "python_gc_enabled_final": bool(gc.isenabled())}
    if __stretch040_result["promoted_frozen_invariants"]["full_raw_weight_persistence_bytes"] != 3583928320:
        raise RuntimeError("STRETCH040_FULL_PERSISTENCE_FAIL")

    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens
    stream_peak = int(mx.get_peak_memory())
'''


def render_final(repo: Path) -> tuple[str, dict]:
    """Reuse the promoted Stretch-038 renderer, then replace only its extension."""
    sys.path.insert(0, str(repo / "scripts"))
    import stretch_s1r8_deferred_cleanup_comparison_038 as stretch038

    source, info = stretch038.render_final(repo, "TREATMENT")
    provenance = info["promoted_s1_r8"]
    if (provenance.get("control_sha256") != PROMOTED_CONTROL_SHA256 or
            provenance.get("treatment_sha256") != PROMOTED_S1_R8_SHA256 or
            provenance.get("injection_sha256") != PROMOTED_S1_R8_INJECTION_SHA256 or
            not provenance.get("normalized_equal")):
        raise RuntimeError(f"STRETCH040_PROMOTED_S1_R8_CHANGED: {provenance}")
    old_cleanup = '''        if __stretch038_cleanup_enabled:
            if __stretch038_before_cleanup is not None:
                __stretch038_before_cleanup()
            gc.collect()
            mx.clear_cache()
            gc.collect()
'''
    new_cleanup = '''        if __stretch038_cleanup_enabled:
            if __stretch038_before_cleanup is not None:
                __stretch038_before_cleanup()
            if __stretch040_cleanup_callback is None:
                gc.collect()
                mx.clear_cache()
                gc.collect()
            else:
                __stretch040_cleanup_callback()
'''
    source = patch_once(source, old_cleanup, new_cleanup, "FINAL_CLEANUP")
    source = patch_once(source, "__stretch038_before_cleanup = None\n", "__stretch038_before_cleanup = None\n__stretch040_cleanup_callback = None\n", "CLEANUP_GLOBAL")
    start = source.index("    # Stretch 038 scientific constituent.")
    end = source.index("    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens\n    stream_peak = int(mx.get_peak_memory())\n", start)
    source = source[:start] + extension_source() + source[end + len("    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens\n    stream_peak = int(mx.get_peak_memory())\n"):]
    # The borrowed renderer has a Stretch-038 payload slot; its extension was
    # replaced above, so remove that now-undefined field before adding ours.
    source = patch_once(source, '        "stretch038": __stretch038_result,\n', "", "OBSOLETE_STRETCH038_PAYLOAD")
    source = patch_once(source, '        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,\n', '        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,\n        "stretch040": __stretch040_result,\n', "RESULT_PAYLOAD")
    return source, {"promoted_s1_r8": provenance, "rendered_sha256": sha256_text(source), "cleanup_snippet_sha256": sha256_text(CLEANUP_SNIPPET)}


def parse_child_summary(stdout: str) -> Path | None:
    found = re.findall(r"^Summary:\s*(.+summary\.json)\s*$", stdout, re.M)
    return Path(found[-1]) if found else None


def main() -> int:
    repo = Path(__file__).parent.parent
    root = repo / "results-local/stretch/s1r8-gc-cleanup-composition-040-feasibility" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    root.mkdir(parents=True, exist_ok=False)
    summary = {"classification": "RUNNING", "harness_revision": HARNESS_REVISION, "scientific_abba_started": False, "deliberate_cache_purge": False, "source_identity": {"stretch038_runner": STRETCH038_RUNNER, "stretch038_runner_git_blob": git_blob(repo, STRETCH038_RUNNER), "promoted_s1_r8_render_sha256": PROMOTED_S1_R8_SHA256, "canonical_cleanup_exact": CLEANUP_SNIPPET.rstrip().splitlines(), "canonical_cleanup_snippet_sha256": sha256_text(CLEANUP_SNIPPET), "cadence": "once after two M5 blocks / 10 accepted tokens"}}
    try:
        py_compile.compile(str(Path(__file__)), doraise=True)
        readiness = host_sample(abort=False)
        summary["passive_host_readiness"] = readiness
        if readiness["free_memory_percent"] < 60 or readiness["swap_used_mb"] > 5600:
            summary.update({"classification": "NOT_STARTED_HOST_NOT_READY", "decision": "INVESTIGATION_ONLY", "reason": "inherited passive launch gate"})
            (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(f"Classification: {summary['classification']}\nSummary: {root/'summary.json'}")
            return 0
        source, render_info = render_final(repo)
        generated = root / "stretch040-final.py"
        generated.write_text(source)
        compile(source, str(generated), "exec")
        summary["source_identity"].update(render_info)
        literal = literal_launcher(repo)
        env = {**os.environ, "LOOM_REPO": str(repo), "STRETCH038_RUN_DIR": str(root)}
        proc = subprocess.run([str(literal), str(generated)], cwd=repo, env=env, text=True, capture_output=True, check=False)
        (root / "stdout.txt").write_text(proc.stdout)
        (root / "stderr.txt").write_text(proc.stderr)
        child_summary_path = parse_child_summary(proc.stdout)
        child_final = root / "child-final.json"
        summary.update({"child_returncode": proc.returncode, "child_summary": str(child_summary_path) if child_summary_path else None, "child_final": str(child_final) if child_final.is_file() else None})
        if child_summary_path and child_summary_path.is_file():
            shutil.copy2(child_summary_path, root / "child-summary.json")
        if proc.returncode or not child_final.is_file():
            summary.update({"classification": "STRETCH_040_GC_COMPOSITION_INCOMPLETE", "decision": "INVESTIGATION_ONLY", "failure_reason": "child failed or child-final payload missing"})
        else:
            payload = json.loads(child_final.read_text())
            outcome = payload.get("stretch040")
            if not outcome:
                summary.update({"classification": "STRETCH_040_GC_COMPOSITION_INCOMPLETE", "decision": "INVESTIGATION_ONLY", "failure_reason": "stretch040 payload missing"})
            else:
                summary.update(outcome)
                summary["child_classification"] = payload.get("classification")
                summary["custom_qmv"] = payload.get("custom_qmv")
                if (payload.get("custom_qmv", {}).get("kernel_count") != 4 or
                        payload.get("custom_qmv", {}).get("recompilation_count_during_target") != 0):
                    summary.update({"classification": "STRETCH_040_GC_COMPOSITION_INCOMPLETE", "decision": "INVESTIGATION_ONLY", "failure_reason": "S1_R8 kernel provenance changed"})
    except Exception as exc:
        summary.update({"classification": "STRETCH_040_GC_COMPOSITION_INCOMPLETE", "decision": "INVESTIGATION_ONLY", "failure_reason": f"{type(exc).__name__}: {exc}"})
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Classification: {summary['classification']}\nSummary: {root/'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
