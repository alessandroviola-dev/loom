#!/usr/bin/env python3
"""Stretch 038 scientific ABBA: promoted S1_R8 cleanup cadence only.

This source is deliberately independent of the Stretch 038 feasibility harness.
It renders two otherwise byte-normalized final S1_R8 children and executes the
approved fresh CONTROL -> TREATMENT -> TREATMENT -> CONTROL comparison.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
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
PROMOTED_CONTROL_SHA256 = "9f94787f7a002a8da95e8352f134eac11f1b072b9363fe600dcac1122080a54c"
PROMOTED_S1_R8_SHA256 = "82888b134a6c4e0ba56bb24896bce2fd37c9d78c899380af35e0e823ad5fcbe3"
PROMOTED_S1_R8_INJECTION_SHA256 = "a086806a314d387770dac54e9140b9526bf7fe9097819f449bba17b7fc1f3ad4"
TOTAL_WEIGHTS = 3_583_928_320
RUN_ORDER = ("CONTROL", "TREATMENT", "TREATMENT", "CONTROL")
HARNESS_REVISION = "STRETCH_038_CLEANUP_CADENCE_SCIENTIFIC_ABBA"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def patch_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Stretch 038 {label} anchor expected once, found {count}")
    return source.replace(old, new, 1)


def host_sample(abort: bool) -> dict:
    pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
    free_match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
    swap_match = re.search(r"used = ([0-9.,]+)([MG])", swap_text)
    if not free_match or not swap_match:
        raise RuntimeError("STRETCH038_TELEMETRY_UNAVAILABLE")
    free = int(free_match.group(1))
    swap = float(swap_match.group(1).replace(",", ".")) * (1024.0 if swap_match.group(2) == "G" else 1.0)
    sample = {"free_memory_percent": free, "swap_used_mb": swap, "sampled_at_utc": utc_now()}
    if abort and (free < 5 or swap > 5600):
        raise RuntimeError(f"STRETCH038_RESOURCE_ABORT free={free}% swap={swap:.2f}MB")
    return sample


def render_final(repo: Path, kind: str) -> tuple[str, dict]:
    """Render promoted S1_R8 plus the sole cadence switch.

    The final source differs between CONTROL/TREATMENT only at the literal
    boolean controlling cleanup after block 1.  Both always restore cleanup
    before block 2, so the final cleanup is identical.
    """
    if kind not in ("CONTROL", "TREATMENT"):
        raise ValueError(kind)
    sys.path.insert(0, str(repo / "scripts"))
    import stretch_m1_qmv_fast_runtime_037 as runtime

    promoted, provenance = runtime.render(repo, "treatment")
    if (provenance.get("control_sha256") != PROMOTED_CONTROL_SHA256 or
            provenance.get("treatment_sha256") != PROMOTED_S1_R8_SHA256 or
            provenance.get("injection_sha256") != PROMOTED_S1_R8_INJECTION_SHA256 or
            not provenance.get("normalized_equal")):
        raise RuntimeError(f"STRETCH038_PROMOTED_S1_R8_CHANGED: {provenance}")
    enabled = "True" if kind == "CONTROL" else "False"
    source = patch_once(
        promoted, "import traceback\n",
        "import traceback\n\n# Stretch 038 sole scientific factor: cleanup after M5 block 1.\n__stretch038_cleanup_after_block1 = " + enabled + "\n__stretch038_cleanup_enabled = True\n__stretch038_before_cleanup = None\n",
        "cadence module controls",
    )
    source = patch_once(source, "def child_main(argv: list[str]) -> int:\n", "def child_main(argv: list[str]) -> int:\n    global __stretch038_cleanup_enabled, __stretch038_before_cleanup\n", "child globals")
    source = patch_once(
        source,
        "        shared_cleanup_pre_active = int(mx.get_active_memory())\n        shared_cleanup_started = time.perf_counter()\n        gc.collect()\n        mx.clear_cache()\n        gc.collect()\n        shared_cleanup_wall = time.perf_counter() - shared_cleanup_started\n        shared_cleanup_post_active = int(mx.get_active_memory())\n        stage_records[\"shared_stage_cleanup\"] = {\n            \"policy\": \"single_cleanup_after_full_pass\",\n            \"pre_active_bytes\": shared_cleanup_pre_active,\n            \"post_active_bytes\": shared_cleanup_post_active,\n            \"active_delta_bytes\": shared_cleanup_post_active - shared_cleanup_pre_active,\n            \"wall_seconds\": round(shared_cleanup_wall, 6),\n        }\n",
        "        shared_cleanup_pre_active = int(mx.get_active_memory())\n        shared_cleanup_started = time.perf_counter()\n        if __stretch038_cleanup_enabled:\n            if __stretch038_before_cleanup is not None:\n                __stretch038_before_cleanup()\n            gc.collect()\n            mx.clear_cache()\n            gc.collect()\n        shared_cleanup_wall = time.perf_counter() - shared_cleanup_started\n        shared_cleanup_post_active = int(mx.get_active_memory())\n        stage_records[\"shared_stage_cleanup\"] = {\n            \"policy\": \"single_cleanup_after_full_pass\" if __stretch038_cleanup_enabled else \"deferred_to_second_m5_block\",\n            \"executed\": bool(__stretch038_cleanup_enabled),\n            \"pre_active_bytes\": shared_cleanup_pre_active,\n            \"post_active_bytes\": shared_cleanup_post_active,\n            \"active_delta_bytes\": shared_cleanup_post_active - shared_cleanup_pre_active,\n            \"wall_seconds\": round(shared_cleanup_wall, 6),\n        }\n",
        "final cleanup guard",
    )
    source = patch_once(source, "        for global_step in range(start_index + 1, end_index + 1):\n            resident_step_logits[global_step - 1] = None\n", "        # Retain resident logits for the separately timed ABBA constituents.\n        for global_step in range(start_index + 1, end_index + 1):\n            pass\n", "resident logits")
    anchor = "    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens\n    stream_peak = int(mx.get_peak_memory())\n"
    extension = '''    # Stretch 038 scientific constituent.  The inherited target above is an
    # excluded warmup; this fresh cycle is the only timed scientific evidence.
    __stretch038_result = {"warmup_excluded": True}

    def __stretch038_mem():
        return {"mlx_active_bytes": int(mx.get_active_memory()), "mlx_peak_bytes": int(mx.get_peak_memory()), "mlx_cache_bytes": int(mx.get_cache_memory()) if hasattr(mx, "get_cache_memory") else None}

    def __stretch038_sample():
        pressure = subprocess.run(["memory_pressure"], text=True, capture_output=True, check=False).stdout
        match = __import__("re").search(r"System-wide memory free percentage:\\s*(\\d+)%%", pressure)
        swap_text = subprocess.run(["sysctl", "-n", "vm.swapusage"], text=True, capture_output=True, check=False).stdout
        swap_match = __import__("re").search(r"used = ([0-9.,]+)([MG])", swap_text)
        if not match or not swap_match: raise RuntimeError("STRETCH038_TELEMETRY_UNAVAILABLE")
        free = int(match.group(1)); swap = float(swap_match.group(1).replace(",", ".")) * (1024.0 if swap_match.group(2) == "G" else 1.0)
        if free < 5 or swap > 5600: raise RuntimeError(f"STRETCH038_RESOURCE_ABORT free={free}%% swap={swap:.2f}MB")
        return {"free_memory_percent": free, "swap_used_mb": swap, **__stretch038_mem()}

    def __stretch038_rows(logits, start, prompt_prediction, previous_prediction, draft):
        predictions = [prompt_prediction if start == 0 else previous_prediction] + [token_value(logits[:, pos:pos+1, :]) for pos in range(ORACLE_BLOCK_SIZE - 1)]
        rows = []
        for pos, expected in enumerate(draft):
            resident_logits = resident_step_logits[start + pos]; target_logits = logits[:, pos:pos+1, :]
            diff = mx.abs(resident_logits.astype(mx.float32) - target_logits.astype(mx.float32)); mx.eval(diff)
            maximum, mean = float(mx.max(diff).item()), float(mx.mean(diff).item())
            threshold = 1e-5 + 1e-5 * float(mx.max(mx.abs(resident_logits.astype(mx.float32))).item())
            resident_top1, target_top1 = resident_steps[start + pos]["predicted_top1"], token_value(target_logits)
            rows.append({"step": start + pos + 1, "oracle_token": int(expected), "prediction": int(predictions[pos]), "accepted": int(predictions[pos]) == int(expected), "max_abs_diff": maximum, "mean_abs_diff": mean, "threshold": threshold, "logits_pass": maximum <= threshold, "resident_top1": int(resident_top1), "target_top1": int(target_top1), "top1_equal": int(resident_top1) == int(target_top1)})
            del diff
        return rows, token_value(logits[:, ORACLE_BLOCK_SIZE-1:ORACLE_BLOCK_SIZE, :])

    caches = [KVCache() for _ in range(args.num_hidden_layers)]
    prompt_ids = make_ids(prompt_token_ids); prompt_logits, _ = run_streamed_pass(prompt_ids, caches, "stretch038_prompt")
    prompt_token = token_value(prompt_logits); prompt_diff = mx.abs(resident_prompt_logits.astype(mx.float32) - prompt_logits.astype(mx.float32)); mx.eval(prompt_diff)
    prompt_max = float(mx.max(prompt_diff).item()); prompt_threshold = 1e-5 + 1e-5 * resident_prompt_max_abs
    del prompt_ids, prompt_logits, prompt_diff
    # The explicit prompt cleanup is outside the target constituent and is
    # identical on both sides; no cleanup is performed between target blocks.
    gc.collect(); mx.clear_cache(); gc.collect()
    __stretch038_result.update({"prompt": {"token": prompt_token, "resident_token": token1, "token_equal": prompt_token == token1, "max_abs_diff": prompt_max, "threshold": prompt_threshold, "logits_pass": prompt_max <= prompt_threshold}, "snapshots": {"before_block1": __stretch038_sample()}, "blocks": []})
    __stretch038_started = time.perf_counter(); __stretch038_previous = None
    for __stretch038_index in range(2):
        __stretch038_start = __stretch038_index * ORACLE_BLOCK_SIZE; __stretch038_draft = oracle_sequence[__stretch038_start:__stretch038_start + ORACLE_BLOCK_SIZE]
        __stretch038_ids = make_ids([__stretch038_draft])
        __stretch038_cleanup_enabled = __stretch038_cleanup_after_block1 if __stretch038_index == 0 else True
        __stretch038_before_cleanup = lambda: __stretch038_result["snapshots"].__setitem__("after_block2_before_final_cleanup" if __stretch038_index == 1 else "after_cleanup1", __stretch038_sample())
        if __stretch038_index == 1: __stretch038_block2_started = time.perf_counter()
        __stretch038_pass_started = time.perf_counter()
        __stretch038_logits, __stretch038_pass = run_streamed_pass(__stretch038_ids, caches, f"stretch038_block{__stretch038_index + 1}")
        __stretch038_pass_returned = time.perf_counter()
        __stretch038_rows_value, __stretch038_previous = __stretch038_rows(__stretch038_logits, __stretch038_start, prompt_token, __stretch038_previous, __stretch038_draft)
        __stretch038_cleanup = __stretch038_pass["stages"]["shared_stage_cleanup"]
        __stretch038_result["blocks"].append({"block": __stretch038_index + 1, "pass_wall_seconds": __stretch038_pass["total_pass_wall_seconds"], "outer_pass_wall_seconds": __stretch038_pass_returned - __stretch038_pass_started, "compute_wall_seconds": __stretch038_pass["total_pass_wall_seconds"] - __stretch038_cleanup["wall_seconds"], "cleanup": __stretch038_cleanup, "positions": __stretch038_rows_value})
        del __stretch038_ids, __stretch038_logits
        if __stretch038_index == 0:
            __stretch038_block1_finished = __stretch038_pass_returned
            __stretch038_result["snapshots"].setdefault("after_block1_before_block2", __stretch038_sample())
        else:
            __stretch038_result["snapshots"].setdefault("after_final_cleanup", __stretch038_sample())
    __stretch038_finished = time.perf_counter(); __stretch038_before_cleanup = None; __stretch038_cleanup_enabled = True
    __stretch038_result["block1_to_block2_transition_seconds"] = __stretch038_block2_started - __stretch038_block1_finished
    # The next field is a direct boundary-to-boundary measurement, rather than
    # a derived sum; target wall begins at block1 and ends after cleanup2.
    __stretch038_result["total_constituent_target_wall_seconds"] = __stretch038_finished - __stretch038_started
    __stretch038_result["accepted_tokens"] = sum(1 for b in __stretch038_result["blocks"] for r in b["positions"] if r["accepted"])
    __stretch038_rows_all = [r for b in __stretch038_result["blocks"] for r in b["positions"]]
    __stretch038_result["generated_sequence_equal"] = [r["oracle_token"] for r in __stretch038_rows_all] == resident_generated_tokens
    __stretch038_result["correctness_pass"] = bool(__stretch038_result["prompt"]["token_equal"] and __stretch038_result["prompt"]["logits_pass"] and len(__stretch038_rows_all) == 10 and all(r["accepted"] and r["logits_pass"] and r["top1_equal"] for r in __stretch038_rows_all))
    __stretch038_result["full_weight_persistence_bytes"] = hotset_record["materialized_delta_bytes"] + shared_persistence_record["materialized_delta_bytes"]
    __stretch038_result["final_cleanup_executed"] = bool(__stretch038_result["blocks"][1]["cleanup"]["executed"])
    __stretch038_result["cleanup_cadence"] = {"block1_executed": bool(__stretch038_result["blocks"][0]["cleanup"]["executed"]), "block2_executed": bool(__stretch038_result["blocks"][1]["cleanup"]["executed"])}
    if not (__stretch038_result["correctness_pass"] and __stretch038_result["generated_sequence_equal"] and __stretch038_result["accepted_tokens"] == 10 and __stretch038_result["full_weight_persistence_bytes"] == 3583928320 and __stretch038_result["final_cleanup_executed"]): raise RuntimeError(f"STRETCH038_CORRECTNESS_FAIL {__stretch038_result}")

    generated_sequence_equal = resident_generated_tokens == stream_generated_tokens
    stream_peak = int(mx.get_peak_memory())
''' % ()
    source = patch_once(source, anchor, extension, "scientific extension")
    source = patch_once(source, '        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,\n', '        "expected_kv_total_bytes": EXPECTED_KV_TOTAL_BYTES,\n        "stretch038": __stretch038_result,\n', "result payload")
    source = source.replace("    repo = Path(__file__).resolve().parents[1]\n    script_path = Path(__file__).resolve()\n", "    repo = Path(os.environ[\"LOOM_REPO\"])\n    script_path = Path(__file__).resolve()\n", 1)
    source = patch_once(source, '    run_dir = repo / "results-local" / "stretch" / "m5-ten-token-single-pass-control-031-fix3" / run_id\n', '    run_dir = Path(os.environ["STRETCH038_RUN_DIR"])\n', "evidence root")
    source = patch_once(source, "import traceback\n", "import traceback\n\nsys.path.insert(0, str(__import__(\"pathlib\").Path(os.environ.get(\"LOOM_REPO\", \".\")) / \"scripts\"))\n", "source import path")
    return source, {"promoted_s1_r8": provenance, "cadence_kind": kind, "rendered_sha256": sha256(source)}


def normalized_cadence_diff(control: str, treatment: str) -> dict:
    normalized_control = control.replace("__stretch038_cleanup_after_block1 = True", "__stretch038_cleanup_after_block1 = FACTOR")
    normalized_treatment = treatment.replace("__stretch038_cleanup_after_block1 = False", "__stretch038_cleanup_after_block1 = FACTOR")
    if normalized_control != normalized_treatment:
        raise RuntimeError("STRETCH038_NORMALIZED_SCIENTIFIC_DIFF_FAIL")
    if "__stretch038_cleanup_enabled = __stretch038_cleanup_after_block1 if __stretch038_index == 0 else True" not in control:
        raise RuntimeError("STRETCH038_FINAL_CLEANUP_NOT_IDENTICAL")
    return {"status": "PASS", "only_difference": "cleanup after block1: CONTROL present, TREATMENT absent", "final_cleanup_after_block2": "identical and enabled"}


def launcher(repo: Path) -> Path:
    literal = repo / CANONICAL_LAUNCHER
    if not literal.is_symlink():
        raise RuntimeError("STRETCH038_LITERAL_CANONICAL_VENV_LAUNCHER_FAIL")
    return literal


def no_model_child(repo: Path, literal: Path, kind: str, output: Path) -> dict:
    proc = subprocess.run([str(literal), str(Path(__file__)), "--child-no-model", kind, str(output)], cwd=repo, env={**os.environ, "LOOM_REPO": str(repo)}, capture_output=True, text=True, check=False)
    if proc.returncode or not output.is_file():
        raise RuntimeError(f"STRETCH038_{kind}_NO_MODEL_CHILD_FAIL: {proc.stderr}")
    record = json.loads(output.read_text())
    if record.get("model_loaded") or record.get("target_compute_executed") or record.get("classification") != "STRETCH_038_NO_MODEL_PASS":
        raise RuntimeError(f"STRETCH038_{kind}_NO_MODEL_MARKER_FAIL")
    return record


def runtime_provenance(repo: Path, literal: Path, root: Path) -> dict:
    output = root / "s1r8-kernel-preflight.json"
    env = {**os.environ, "STRETCH037_MODE": "treatment"}
    proc = subprocess.run([str(literal), str(repo / RUNTIME), "--jit-preflight", str(output)], cwd=repo, env=env, capture_output=True, text=True, check=False)
    if proc.returncode or not output.is_file():
        raise RuntimeError(f"STRETCH038_KERNEL_PREFLIGHT_FAIL: {proc.stderr}")
    kernel = json.loads(output.read_text())
    observed = subprocess.run([str(literal), "-c", "import importlib.metadata as m, json; print(json.dumps({x:m.version(x) for x in ('mlx','mlx-metal','mlx-lm','transformers')}))"], capture_output=True, text=True, check=True)
    versions = json.loads(observed.stdout)
    if versions != EXPECTED_VERSIONS or kernel.get("kernel_count") != 4 or not all(x.get("exact_equal") for x in kernel.get("real_weight_parity", [])):
        raise RuntimeError("STRETCH038_RUNTIME_PROVENANCE_FAIL")
    return {"status": "PASS", "versions": versions, "kernel_preflight": kernel}


def preflight(repo: Path, root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=False)
    py_compile.compile(str(Path(__file__)), doraise=True)
    py_compile.compile(str(repo / RUNTIME), doraise=True)
    literal = launcher(repo)
    control, control_info = render_final(repo, "CONTROL")
    treatment, treatment_info = render_final(repo, "TREATMENT")
    control_path, treatment_path = root / "control-final.py", root / "treatment-final.py"
    control_path.write_text(control); treatment_path.write_text(treatment)
    compile(control, str(control_path), "exec"); compile(treatment, str(treatment_path), "exec")
    diff = normalized_cadence_diff(control, treatment)
    no_model = {kind: no_model_child(repo, literal, kind, root / f"{kind.lower()}-no-model.json") for kind in ("CONTROL", "TREATMENT")}
    provenance = runtime_provenance(repo, literal, root)
    semantics = {"status": "PASS", "canonical_target_block_wall_includes_cleanup": True, "source_evidence": "run_streamed_pass starts total_pass_wall before compute and executes shared_stage_cleanup before returning; constituent wall starts before block1 and ends after block2 final cleanup", "primary_definition": "20 pooled accepted tokens / pooled total constituent target wall"}
    return {"classification": "STRETCH_038_PREFLIGHT_PASS", "scientific_run": False, "harness_revision": HARNESS_REVISION, "py_compile": "PASS", "rendered_sources": {"control": {"path": str(control_path), **control_info}, "treatment": {"path": str(treatment_path), **treatment_info}}, "normalized_scientific_diff": diff, "literal_canonical_launcher": str(literal), "no_model_parent_child": no_model, "runtime_provenance": provenance, "metric_semantics_audit": semantics}


def parse_child_summary(stdout: str) -> Path | None:
    found = re.findall(r"^Summary:\s*(.+summary\.json)\s*$", stdout, re.M)
    return Path(found[-1]) if found else None


def aggregate(records: list[dict]) -> dict:
    accepted = sum(r["accepted_tokens"] for r in records)
    wall = sum(r["total_wall"] for r in records)
    return {"constituents": len(records), "accepted_tokens": accepted, "total_constituent_target_wall_seconds": wall, "pooled_tokens_per_second": accepted / wall, "wall_seconds_per_accepted_token": wall / accepted, "block1_compute_walls": [r["block1_compute_wall"] for r in records], "block2_compute_walls": [r["block2_compute_wall"] for r in records], "cleanup1_walls": [r["cleanup1_wall"] for r in records], "final_cleanup_walls": [r["final_cleanup_wall"] for r in records], "transitions": [r["transition_wall"] for r in records], "minimum_free_memory_percent": min(r["min_free"] for r in records), "peak_swap_mb": max(r["peak_swap"] for r in records)}


def child_no_model(kind: str, output: Path) -> int:
    repo = Path(os.environ["LOOM_REPO"])
    source, info = render_final(repo, kind)
    compile(source, str(output), "exec")
    output.write_text(json.dumps({"classification": "STRETCH_038_NO_MODEL_PASS", "kind": kind, "model_loaded": False, "target_compute_executed": False, "rendered_sha256": info["rendered_sha256"], "prefix": sys.prefix}, indent=2) + "\n")
    return 0


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "--child-no-model":
        return child_no_model(sys.argv[2], Path(sys.argv[3]))
    repo = Path(__file__).parent.parent
    if sys.argv[1:] == ["--preflight"]:
        root = repo / "results-local/stretch/s1r8-deferred-cleanup-038-comparison/preflight" / datetime.now().strftime("%Y%m%d-%H%M%S")
        try:
            result = preflight(repo, root)
            (root / "preflight-summary.json").write_text(json.dumps(result, indent=2) + "\n")
            print(f"Classification: {result['classification']}\nPreflight summary: {root/'preflight-summary.json'}")
            return 0
        except Exception as exc:
            root.mkdir(parents=True, exist_ok=True); (root / "preflight-summary.json").write_text(json.dumps({"classification": "STRETCH_038_PREFLIGHT_FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2) + "\n")
            print(f"Classification: STRETCH_038_PREFLIGHT_FAIL\nError: {exc}", file=sys.stderr); return 2
    if sys.argv[1:]:
        print("usage: stretch_s1r8_deferred_cleanup_comparison_038.py [--preflight]", file=sys.stderr); return 2
    root = repo / "results-local/stretch/s1r8-deferred-cleanup-038-comparison" / datetime.now().strftime("%Y%m%d-%H%M%S")
    preflight_dir = root / "preflight"
    try:
        pre = preflight(repo, preflight_dir)
        (preflight_dir / "preflight-summary.json").write_text(json.dumps(pre, indent=2) + "\n")
    except Exception as exc:
        root.mkdir(parents=True, exist_ok=True); (root / "summary.json").write_text(json.dumps({"classification": "STRETCH_038_CLEANUP_CADENCE_INCOMPLETE", "scientific_result": "NONE", "failure_reason": f"fresh in-harness preflight: {type(exc).__name__}: {exc}"}, indent=2) + "\n")
        print(f"Classification: STRETCH_038_CLEANUP_CADENCE_INCOMPLETE\nSummary: {root/'summary.json'}"); return 2
    ready = host_sample(abort=False)
    if ready["free_memory_percent"] < 60 or ready["swap_used_mb"] > 5600:
        (root / "summary.json").write_text(json.dumps({"classification": "NOT_STARTED_HOST_NOT_READY", "scientific_result": "NONE", "host_readiness": ready, "preflight": pre}, indent=2) + "\n")
        print(f"Classification: NOT_STARTED_HOST_NOT_READY\nSummary: {root/'summary.json'}"); return 0
    summary = {"classification": "RUNNING", "scientific_result": "NONE", "harness_revision": HARNESS_REVISION, "run_order": RUN_ORDER, "preflight": pre, "passive_host_readiness": ready, "attempts": [], "deliberate_cache_purge": False, "host_manipulation": False}
    def save() -> None: (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    save(); literal = launcher(repo)
    for number, kind in enumerate(RUN_ORDER, 1):
        launch = host_sample(abort=False)
        if launch["free_memory_percent"] < 60 or launch["swap_used_mb"] > 5600:
            summary.update({"classification": "NOT_STARTED_HOST_NOT_READY", "scientific_result": "NONE", "failure_reason": f"constituent {number} launch gate", "attempts": summary["attempts"]}); save(); return 0
        rendered, _ = render_final(repo, kind); generated = root / f"attempt-{number}-{kind.lower()}-final.py"; generated.write_text(rendered); compile(rendered, str(generated), "exec")
        out, err = root / f"attempt-{number}-{kind.lower()}-stdout.txt", root / f"attempt-{number}-{kind.lower()}-stderr.txt"
        env = {**os.environ, "LOOM_REPO": str(repo), "STRETCH038_RUN_DIR": str(root)}
        started = time.perf_counter()
        with out.open("w") as stdout, err.open("w") as stderr:
            proc = subprocess.run([str(literal), str(generated)], cwd=repo, env=env, stdout=stdout, stderr=stderr, check=False)
        child_path = parse_child_summary(out.read_text(errors="replace"))
        attempt = {"constituent": number, "kind": kind, "launch_sample": launch, "returncode": proc.returncode, "stdout": str(out), "stderr": str(err), "wrapper_wall_seconds": time.perf_counter() - started, "child_summary": str(child_path) if child_path else None}
        if not child_path or not child_path.is_file():
            summary["attempts"].append(attempt); summary.update({"classification": "STRETCH_038_CLEANUP_CADENCE_INCOMPLETE", "failure_reason": f"constituent {number} child summary missing"}); save(); return 3
        child = json.loads(child_path.read_text())
        saved_child = root / f"attempt-{number}-{kind.lower()}-child-summary.json"
        shutil.copy2(child_path, saved_child)
        child_final = root / "child-final.json"
        saved_final = root / f"attempt-{number}-{kind.lower()}-child-final.json"
        if child_final.is_file(): shutil.copy2(child_final, saved_final)
        attempt["child_summary"] = str(saved_child)
        attempt["child_final"] = str(saved_final) if saved_final.is_file() else None
        result = child.get("stretch038")
        if not result:
            summary["attempts"].append(attempt); summary.update({"classification": "STRETCH_038_CLEANUP_CADENCE_INCOMPLETE", "failure_reason": f"constituent {number} stretch038 payload missing"}); save(); return 3
        blocks, snapshots = result.get("blocks", []), result.get("snapshots", {})
        custom = child.get("custom_qmv", {})
        before, after = snapshots.get("before_block1", {}), snapshots.get("after_final_cleanup", {})
        recovery = bool(before and after and after.get("mlx_active_bytes", -1) <= before.get("mlx_active_bytes", -1))
        attempt.update({"child_classification": child.get("classification"), "accepted_tokens": result.get("accepted_tokens"), "total_wall": result.get("total_constituent_target_wall_seconds"), "block1_compute_wall": blocks[0]["compute_wall_seconds"] if len(blocks) == 2 else None, "block2_compute_wall": blocks[1]["compute_wall_seconds"] if len(blocks) == 2 else None, "cleanup1_wall": blocks[0]["cleanup"]["wall_seconds"] if len(blocks) == 2 else None, "final_cleanup_wall": blocks[1]["cleanup"]["wall_seconds"] if len(blocks) == 2 else None, "transition_wall": result.get("block1_to_block2_transition_seconds"), "snapshots": snapshots, "min_free": min(x["free_memory_percent"] for x in snapshots.values()), "peak_swap": max(x["swap_used_mb"] for x in snapshots.values()), "full_weight_persistence_bytes": result.get("full_weight_persistence_bytes"), "correctness_pass": result.get("correctness_pass"), "generated_sequence_equal": result.get("generated_sequence_equal"), "cleanup_cadence": result.get("cleanup_cadence"), "custom_qmv": custom, "final_cleanup_recovery": recovery})
        expected_cadence = {"block1_executed": kind == "CONTROL", "block2_executed": True}
        usable = (proc.returncode == 0 and child.get("classification") == "SINGLE_PASS_M5_TEN_TOKEN_GEOMETRY_PASS" and attempt["accepted_tokens"] == 10 and attempt["correctness_pass"] and attempt["generated_sequence_equal"] and attempt["full_weight_persistence_bytes"] == TOTAL_WEIGHTS and attempt["cleanup_cadence"] == expected_cadence and custom.get("kernel_count") == 4 and custom.get("recompilation_count_during_target") == 0 and len(blocks) == 2 and all(x["free_memory_percent"] >= 5 and x["swap_used_mb"] <= 5600 for x in snapshots.values()))
        attempt["usable"] = usable; summary["attempts"].append(attempt); save()
        if not usable:
            if kind == "TREATMENT" and (not attempt["correctness_pass"] or not attempt["generated_sequence_equal"] or attempt["accepted_tokens"] != 10):
                summary.update({"classification": "STRETCH_038_CLEANUP_CADENCE_VALID_SCIENTIFIC_FAIL", "scientific_result": "VALID_SCIENTIFIC_FAIL", "failure_reason": f"treatment correctness failure constituent {number}"})
            else:
                summary.update({"classification": "STRETCH_038_CLEANUP_CADENCE_INCOMPLETE", "scientific_result": "NONE", "failure_reason": f"constituent {number} gate failure"})
            save(); return 0
    control, treatment = aggregate([x for x in summary["attempts"] if x["kind"] == "CONTROL"]), aggregate([x for x in summary["attempts"] if x["kind"] == "TREATMENT"])
    ratio = treatment["pooled_tokens_per_second"] / control["pooled_tokens_per_second"]
    wall_ratio = treatment["total_constituent_target_wall_seconds"] / control["total_constituent_target_wall_seconds"]
    stable = all(a["final_cleanup_recovery"] for a in summary["attempts"])
    classification = "STRETCH_038_CLEANUP_CADENCE_PASS" if stable and ratio >= 1.05 else "STRETCH_038_CLEANUP_CADENCE_RETAIN_CONTROL"
    summary.update({"classification": classification, "scientific_result": "VALID_ABBA", "comparison": {"control": control, "treatment": treatment, "treatment_over_control_ratio": ratio, "percentage_throughput_gain": (ratio - 1) * 100, "total_wall_ratio": wall_ratio, "percentage_wall_reduction": (1 - wall_ratio) * 100, "decision": "PROMOTE_DEFERRED_CADENCE" if classification.endswith("PASS") else "RETAIN_TWO_CLEANUP_CANONICAL"}}); save()
    print(f"Classification: {classification}\nCONTROL tok/s: {control['pooled_tokens_per_second']}\nTREATMENT tok/s: {treatment['pooled_tokens_per_second']}\nSummary: {root/'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
