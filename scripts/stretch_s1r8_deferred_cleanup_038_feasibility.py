#!/usr/bin/env python3
"""Stretch 038 feasibility: defer the frozen final cleanup across two M5 blocks.

This is a distinct, process-local harness.  It renders the promoted Stretch 037
S1_R8 source, changes only the cadence of its existing full-pass cleanup, and
runs a single child/model-load process.  It is deliberately not an ABBA runner.
"""
from __future__ import annotations

import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CANONICAL_LAUNCHER = "results-local/mlx/venv-mlx-lm-0.31.3/bin/python"
RUNTIME = "scripts/stretch_m1_qmv_fast_runtime_037.py"
EXPECTED_PREFIX = "results-local/mlx/venv-mlx-lm-0.31.3"
EXPECTED_VERSIONS = {"mlx": "0.31.2", "mlx-metal": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
TOTAL_WEIGHTS = 3_583_928_320
CYCLES = ("CONTROL", "TREATMENT", "TREATMENT", "CONTROL", "TREATMENT", "TREATMENT", "CONTROL", "TREATMENT", "TREATMENT", "CONTROL", "TREATMENT", "TREATMENT")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def patch_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"Stretch 038 source patch {label!r} expected one anchor, found {source.count(old)}")
    return source.replace(old, new, 1)


def patched_source(repo: Path) -> str:
    sys.path.insert(0, str(repo / "scripts"))
    import stretch_m1_qmv_fast_runtime_037 as runtime

    source, provenance = runtime.render(repo, "treatment")
    if not provenance.get("normalized_equal"):
        raise RuntimeError("Stretch 037 S1_R8 rendered source is not a normalized single-factor transform")
    source = patch_once(
        source,
        "import traceback\n",
        "import traceback\n\n# Stretch 038 process-local cadence controls; no kernel modification.\n__stretch038_cleanup_enabled = True\n__stretch038_pre_cleanup_hook = None\n",
        "module cadence controls",
    )
    source = patch_once(
        source,
        "def child_main(argv: list[str]) -> int:\n",
        "def child_main(argv: list[str]) -> int:\n    global __stretch038_cleanup_enabled, __stretch038_pre_cleanup_hook\n",
        "child cadence global scope",
    )
    source = patch_once(
        source,
        "        shared_cleanup_pre_active = int(mx.get_active_memory())\n        shared_cleanup_started = time.perf_counter()\n        gc.collect()\n        mx.clear_cache()\n        gc.collect()\n        shared_cleanup_wall = time.perf_counter() - shared_cleanup_started\n        shared_cleanup_post_active = int(mx.get_active_memory())\n        stage_records[\"shared_stage_cleanup\"] = {\n            \"policy\": \"single_cleanup_after_full_pass\",\n            \"pre_active_bytes\": shared_cleanup_pre_active,\n            \"post_active_bytes\": shared_cleanup_post_active,\n            \"active_delta_bytes\": shared_cleanup_post_active - shared_cleanup_pre_active,\n            \"wall_seconds\": round(shared_cleanup_wall, 6),\n        }\n",
        "        shared_cleanup_pre_active = int(mx.get_active_memory())\n        shared_cleanup_started = time.perf_counter()\n        if __stretch038_cleanup_enabled:\n            if __stretch038_pre_cleanup_hook is not None:\n                __stretch038_pre_cleanup_hook()\n            gc.collect()\n            mx.clear_cache()\n            gc.collect()\n        shared_cleanup_wall = time.perf_counter() - shared_cleanup_started\n        shared_cleanup_post_active = int(mx.get_active_memory())\n        stage_records[\"shared_stage_cleanup\"] = {\n            \"policy\": \"single_cleanup_after_full_pass\" if __stretch038_cleanup_enabled else \"deferred_to_second_m5_block\",\n            \"executed\": bool(__stretch038_cleanup_enabled),\n            \"pre_active_bytes\": shared_cleanup_pre_active,\n            \"post_active_bytes\": shared_cleanup_post_active,\n            \"active_delta_bytes\": shared_cleanup_post_active - shared_cleanup_pre_active,\n            \"wall_seconds\": round(shared_cleanup_wall, 6),\n        }\n",
        "final cleanup guard",
    )
    source = patch_once(
        source,
        "        for global_step in range(start_index + 1, end_index + 1):\n            resident_step_logits[global_step - 1] = None\n",
        "        # Stretch 038 retains resident logits for a same-load treatment comparison.\n        for global_step in range(start_index + 1, end_index + 1):\n            pass\n",
        "retain resident logits",
    )
    extension_anchor = "    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens\n    stream_peak = int(mx.get_peak_memory())\n"
    extension = '''    # Stretch 038: one-load cadence feasibility diagnostic.  The inherited
    # target above is separate warmup/control evidence.  Every cycle below ends
    # with the frozen explicit cleanup; treatment alone skips it after block 1.
    __stretch038_results = {"warmup": {"classification": "INHERITED_CONTROL"}, "cycles": []}

    def __stretch038_host_sample():
        pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
        match = __import__("re").search(r"System-wide memory free percentage:\\s*(\\d+)%%", pressure)
        swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
        swap_match = __import__("re").search(r"used = ([0-9.]+)([MG])", swap_text)
        free = int(match.group(1)) if match else None
        swap = float(swap_match.group(1)) * (1024.0 if swap_match and swap_match.group(2) == "G" else 1.0) if swap_match else None
        if free is None or swap is None:
            raise RuntimeError("STRETCH038_TELEMETRY_UNAVAILABLE")
        if free < 5 or swap > 5600:
            raise RuntimeError(f"STRETCH038_RESOURCE_ABORT free={free}%% swap={swap:.2f}MB")
        return {"free_memory_percent": free, "swap_used_mb": swap, **mem()}

    def __stretch038_positions(logits, start_index, prompt_prediction, previous_prediction, draft_tokens):
        predictions = [prompt_prediction if start_index == 0 else previous_prediction]
        predictions += [token_value(logits[:, pos:pos + 1, :]) for pos in range(ORACLE_BLOCK_SIZE - 1)]
        rows = []
        for pos, draft in enumerate(draft_tokens):
            resident_logits = resident_step_logits[start_index + pos]
            target_logits = logits[:, pos:pos + 1, :]
            diff = mx.abs(resident_logits.astype(mx.float32) - target_logits.astype(mx.float32))
            mx.eval(diff)
            maximum, mean = float(mx.max(diff).item()), float(mx.mean(diff).item())
            resident_top1, target_top1 = resident_steps[start_index + pos]["predicted_top1"], token_value(target_logits)
            threshold = 1e-5 + 1e-5 * float(mx.max(mx.abs(resident_logits.astype(mx.float32))).item())
            rows.append({"step": start_index + pos + 1, "oracle_token": int(draft), "prediction": int(predictions[pos]), "accepted": int(predictions[pos]) == int(draft), "max_abs_diff": maximum, "mean_abs_diff": mean, "threshold": threshold, "logits_pass": maximum <= threshold, "resident_top1": int(resident_top1), "target_top1": int(target_top1), "top1_equal": int(resident_top1) == int(target_top1)})
            del diff
        return rows, token_value(logits[:, ORACLE_BLOCK_SIZE - 1:ORACLE_BLOCK_SIZE, :])

    def __stretch038_cycle(kind, cycle_number):
        global __stretch038_cleanup_enabled, __stretch038_pre_cleanup_hook
        caches = [KVCache() for _ in range(args.num_hidden_layers)]
        prompt_ids = make_ids(prompt_token_ids)
        prompt_logits, prompt_record = run_streamed_pass(prompt_ids, caches, f"stretch038_{kind.lower()}_{cycle_number}_prompt")
        prompt_token = token_value(prompt_logits)
        prompt_diff = mx.abs(resident_prompt_logits.astype(mx.float32) - prompt_logits.astype(mx.float32))
        mx.eval(prompt_diff)
        prompt_max = float(mx.max(prompt_diff).item())
        prompt_threshold = 1e-5 + 1e-5 * resident_prompt_max_abs
        del prompt_ids, prompt_logits, prompt_diff
        gc.collect(); mx.clear_cache(); gc.collect()
        record = {"cycle": cycle_number, "kind": kind, "prompt": {"token": prompt_token, "resident_token": token1, "token_equal": prompt_token == token1, "max_abs_diff": prompt_max, "threshold": prompt_threshold, "logits_pass": prompt_max <= prompt_threshold}, "snapshots": {"before_block1": __stretch038_host_sample()}, "blocks": []}
        previous = None
        for block_index in range(2):
            start = block_index * ORACLE_BLOCK_SIZE
            draft = oracle_sequence[start:start + ORACLE_BLOCK_SIZE]
            ids = make_ids([draft])
            __stretch038_cleanup_enabled = not (kind == "TREATMENT" and block_index == 0)
            __stretch038_pre_cleanup_hook = lambda: record.__setitem__("before_final_cleanup", __stretch038_host_sample())
            started = time.perf_counter()
            logits, pass_record = run_streamed_pass(ids, caches, f"stretch038_{kind.lower()}_{cycle_number}_block{block_index + 1}")
            outer_wall = time.perf_counter() - started
            positions, previous = __stretch038_positions(logits, start, prompt_token, previous, draft)
            cleanup = pass_record["stages"]["shared_stage_cleanup"]
            block = {"block": block_index + 1, "wall_seconds": pass_record["total_pass_wall_seconds"], "outer_wall_seconds": outer_wall, "compute_wall_seconds": pass_record["total_pass_wall_seconds"] - cleanup["wall_seconds"], "cleanup": cleanup, "positions": positions}
            record["blocks"].append(block)
            del ids, logits
            gc.collect()
            if block_index == 0:
                record["snapshots"]["after_block1_before_block2"] = __stretch038_host_sample()
                transition_started = time.perf_counter(); record["no_cleanup_transition_wall_seconds"] = time.perf_counter() - transition_started
            else:
                record["snapshots"]["after_cleanup"] = __stretch038_host_sample()
        __stretch038_pre_cleanup_hook = None
        all_rows = [row for block in record["blocks"] for row in block["positions"]]
        record["accepted_tokens"] = sum(1 for row in all_rows if row["accepted"])
        record["correctness_pass"] = bool(record["prompt"]["token_equal"] and record["prompt"]["logits_pass"] and len(all_rows) == 10 and all(row["accepted"] and row["logits_pass"] and row["top1_equal"] for row in all_rows))
        record["generated_sequence_equal"] = [row["oracle_token"] for row in all_rows] == resident_generated_tokens
        record["total_10_token_wall_seconds"] = sum(block["wall_seconds"] for block in record["blocks"])
        record["total_cleanup_wall_seconds"] = sum(block["cleanup"]["wall_seconds"] for block in record["blocks"])
        record["final_cleanup_executed"] = bool(record["blocks"][-1]["cleanup"]["executed"])
        if not record["correctness_pass"] or not record["generated_sequence_equal"] or record["accepted_tokens"] != 10 or not record["final_cleanup_executed"]:
            raise RuntimeError(f"STRETCH038_CORRECTNESS_FAIL {record}")
        return record

    __stretch038_results["warmup"].update({"correctness_pass": bool(prompt_parity["pass"] and prompt_parity["token_equal"] and all(p["pass"] and p["top1_equal"] for p in step_parities) and resident_generated_tokens == stream_generated_tokens), "accepted_tokens": sum(record["accepted_count"] for record in stream_token_records), "full_weight_persistence_bytes": hotset_record["materialized_delta_bytes"] + shared_persistence_record["materialized_delta_bytes"], "cleanup_walls": [record["pass"]["stages"]["shared_stage_cleanup"]["wall_seconds"] for record in stream_token_records]})
    for __stretch038_cycle_number, __stretch038_kind in enumerate(%s, 1):
        __stretch038_results["cycles"].append(__stretch038_cycle(__stretch038_kind, __stretch038_cycle_number))
    __stretch038_cleanup_enabled = True

    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens
    stream_peak = int(mx.get_peak_memory())
''' % (repr(CYCLES),)
    source = patch_once(source, extension_anchor, extension, "one-load diagnostic extension")
    source = patch_once(
        source,
        '        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,\n',
        '        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,\n        "stretch038": __stretch038_results,\n',
        "final extension payload",
    )
    source = source.replace(
        "    repo = Path(__file__).resolve().parents[1]\n    script_path = Path(__file__).resolve()\n",
        "    repo = Path(os.environ[\"LOOM_REPO\"])\n    script_path = Path(__file__).resolve()\n",
        1,
    )
    run_dir_old = '    run_dir = repo / "results-local" / "stretch" / "m5-ten-token-single-pass-control-031-fix3" / run_id\n'
    source = patch_once(source, run_dir_old, '    run_dir = Path(os.environ["STRETCH038_RUN_DIR"])\n', "evidence directory")
    source = patch_once(source, "import traceback\n", "import traceback\n\nsys.path.insert(0, str(__import__(\"pathlib\").Path(os.environ.get(\"LOOM_REPO\", \".\")) / \"scripts\"))\n", "scripts import path")
    return source


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    if Path(sys.prefix) == repo / EXPECTED_PREFIX:
        raise RuntimeError("run this parent harness with system Python, not the MLX child launcher")
    launcher = repo / CANONICAL_LAUNCHER
    if not launcher.is_symlink():
        raise RuntimeError("canonical literal venv launcher unavailable")
    py_compile.compile(str(repo / RUNTIME), doraise=True)
    root = repo / "results-local/stretch/s1r8-deferred-cleanup-038-feasibility" / datetime.now().strftime("%Y%m%d-%H%M%S")
    root.mkdir(parents=True)
    generated = root / "rendered-s1r8-deferred-cleanup.py"
    source = patched_source(repo)
    compile(source, str(generated), "exec")
    generated.write_text(source, encoding="utf-8")
    preflight = {"classification": "STRETCH_038_PREFLIGHT_PASS", "single_factor": "final cleanup after every M5 block -> only after second M5 block", "mode": "promoted_S1_R8", "cycles": list(CYCLES), "minimum_treatment_cycles": 8, "canonical_launcher": str(launcher), "expected_versions": EXPECTED_VERSIONS, "rendered_source": str(generated), "source_compiles": True, "no_qmv_change": True}
    (root / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    started = time.perf_counter()
    process = subprocess.run([str(launcher), str(generated)], cwd=repo, env={**os.environ, "LOOM_REPO": str(repo), "STRETCH038_RUN_DIR": str(root)}, text=True, capture_output=True, check=False)
    (root / "stdout.txt").write_text(process.stdout, encoding="utf-8")
    (root / "stderr.txt").write_text(process.stderr, encoding="utf-8")
    summary_path = root / "summary.json"
    summary = {"classification": "STRETCH_038_CLEANUP_CADENCE_FEASIBILITY_INCOMPLETE", "started_at_utc": utc_now(), "root": str(root), "preflight": preflight, "returncode": process.returncode, "wrapper_wall_seconds": time.perf_counter() - started}
    child_final = root / "child-final.json"
    parent_summary = root / "summary.json"
    # The rendered parent uses summary.json; preserve it before writing this wrapper summary.
    if parent_summary.is_file():
        shutil.copy2(parent_summary, root / "inherited-parent-summary.json")
    if child_final.is_file():
        child = json.loads(child_final.read_text())
        summary["child"] = child.get("stretch038")
        summary["inherited_classification"] = (json.loads((root / "inherited-parent-summary.json").read_text()).get("classification") if (root / "inherited-parent-summary.json").is_file() else None)
        if process.returncode == 0 and child.get("ok") and child.get("stretch038"):
            summary["classification"] = "STRETCH_038_CLEANUP_CADENCE_FEASIBILITY_COMPLETE"
    else:
        summary["failure_reason"] = "child final payload missing"
    summary["finished_at_utc"] = utc_now()
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Classification: {summary['classification']}\nSummary: {summary_path}")
    return 0 if summary["classification"] == "STRETCH_038_CLEANUP_CADENCE_FEASIBILITY_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
