#!/usr/bin/env python3
"""LOOM Stretch 028 — balanced compute re-attribution on SINGLE_PASS baseline."""
from __future__ import annotations

import json
import re
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SOURCE_CONTROL_PATH = Path("scripts/stretch_full_persistent_single_pass_cleanup_027.py")
SOURCE_CONTROL_BLOB = "6636456df5a773ac6062fdad66b7dc96abe8bd81"
SOURCE_PROFILED_PATH = Path("scripts/stretch_single_pass_compute_reattribution_028_profiled.py")
SOURCE_PROFILED_BLOB = "0858e39a46bf09fe7750691b6dcd95b6753e5c70"
EXPECTED_CHILD_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
RUN_ORDER = ["CONTROL", "PROFILED", "PROFILED", "CONTROL"]
COMPONENT_NAMES = [
    "input_norm_seconds",
    "attention_seconds",
    "residual_1_seconds",
    "post_attention_norm_seconds",
    "gate_proj_seconds",
    "up_proj_seconds",
    "swiglu_seconds",
    "down_proj_seconds",
    "residual_2_seconds",
]
SHARED_STAGE_NAMES = ("embedding", "norm", "head")


def git_blob(path: Path, repo: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)], cwd=repo, capture_output=True,
        text=True, timeout=30, check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def gib_free(path: Path) -> float:
    return shutil.disk_usage(path).free / (1024 ** 3)


def parse_summary_path(stdout_text: str) -> Path | None:
    matches = re.findall(r"^Summary:\s*(.+summary\.json)\s*$", stdout_text, flags=re.MULTILINE)
    return Path(matches[-1].strip()) if matches else None


def safe_ratio(num: float, den: float) -> float | None:
    return num / den if den != 0 else None


def extract_pass_metrics(child: dict) -> tuple[list[float], list[float], list[float]]:
    cleanup, shared_forward, shared_materialize = [], [], []
    for record in (child.get("stream") or {}).get("tokens") or []:
        stages = (record.get("pass") or {}).get("stages") or {}
        final_cleanup = stages.get("shared_stage_cleanup")
        if not isinstance(final_cleanup, dict) or final_cleanup.get("policy") != "single_cleanup_after_full_pass":
            raise RuntimeError("single final cleanup provenance missing")
        cleanup.append(float(final_cleanup.get("wall_seconds", -1.0)))
        if any(name not in stages for name in SHARED_STAGE_NAMES):
            raise RuntimeError("target block missing persistent shared-stage records")
        shared_forward.append(
            sum(float(stages[name].get("forward_wall_seconds", 0.0)) for name in SHARED_STAGE_NAMES)
        )
        shared_materialize.append(
            sum(float(stages[name].get("materialize_wall_seconds", 0.0)) for name in SHARED_STAGE_NAMES)
        )
    return cleanup, shared_forward, shared_materialize


def aggregate_basic(records: list[dict]) -> dict:
    accepted = sum(int(r["accepted_tokens"]) for r in records)
    total_wall = sum(float(r["total_block_wall"]) for r in records)
    block_walls = [float(v) for r in records for v in r["block_walls"]]
    cleanup = [float(v) for r in records for v in r["cleanup_walls"]]
    shared_forward = [float(v) for r in records for v in r["shared_forward"]]
    shared_materialize = [float(v) for r in records for v in r["shared_materialize"]]
    min_free = [int(r["min_free"]) for r in records if r.get("min_free") is not None]
    peak_swap = [float(r["peak_swap"]) for r in records if r.get("peak_swap") is not None]
    return {
        "runs": len(records),
        "accepted_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "mean_block_wall_seconds": statistics.mean(block_walls),
        "median_block_wall_seconds": statistics.median(block_walls),
        "mean_final_cleanup_wall_seconds": statistics.mean(cleanup),
        "mean_shared_forward_seconds": statistics.mean(shared_forward),
        "mean_shared_materialize_seconds": statistics.mean(shared_materialize),
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
        "raw_block_walls": block_walls,
    }


def aggregate_profiled(records: list[dict]) -> dict:
    rows = []
    slow_layers: dict[int, list[float]] = {}
    for record in records:
        ca = record["compute_attribution"]
        rows.extend(ca["block_totals"])
        for row in ca.get("slowest_layers_by_mean_profiled_compute", []):
            slow_layers.setdefault(int(row["layer_id"]), []).append(
                float(row["mean_profiled_compute_seconds"])
            )

    means = {
        name: statistics.mean(float(row[name]) for row in rows)
        for name in COMPONENT_NAMES
    }
    transformer_mean = sum(means.values())
    attention = means["input_norm_seconds"] + means["attention_seconds"] + means["residual_1_seconds"]
    mlp = (
        means["post_attention_norm_seconds"]
        + means["gate_proj_seconds"]
        + means["up_proj_seconds"]
        + means["swiglu_seconds"]
        + means["down_proj_seconds"]
        + means["residual_2_seconds"]
    )
    ranked = sorted(
        [(name, value, safe_ratio(value, transformer_mean)) for name, value in means.items()],
        key=lambda item: item[1],
        reverse=True,
    )
    layer_candidates = [
        {"layer_id": layer_id, "mean_profiled_compute_seconds": statistics.mean(values)}
        for layer_id, values in slow_layers.items() if values
    ]
    layer_candidates.sort(key=lambda row: row["mean_profiled_compute_seconds"], reverse=True)

    basic = aggregate_basic(records)
    accounted = (
        transformer_mean
        + basic["mean_final_cleanup_wall_seconds"]
        + basic["mean_shared_forward_seconds"]
        + basic["mean_shared_materialize_seconds"]
    )
    residual = basic["mean_block_wall_seconds"] - accounted

    return {
        "profiled_block_samples": len(rows),
        "mean_component_seconds_per_block": means,
        "ranked_components": ranked,
        "mean_profiled_transformer_compute_seconds_per_block": transformer_mean,
        "mean_attention_path_seconds_per_block": attention,
        "mean_mlp_path_seconds_per_block": mlp,
        "mlp_over_attention_path_ratio": safe_ratio(mlp, attention),
        "mean_final_cleanup_wall_seconds": basic["mean_final_cleanup_wall_seconds"],
        "mean_shared_forward_seconds_per_block": basic["mean_shared_forward_seconds"],
        "mean_shared_materialize_seconds_per_block": basic["mean_shared_materialize_seconds"],
        "mean_profiled_full_block_wall_seconds": basic["mean_block_wall_seconds"],
        "mean_accounted_seconds_per_block": accounted,
        "mean_residual_unattributed_seconds_per_block": residual,
        "accounted_share_of_profiled_full_wall": safe_ratio(accounted, basic["mean_block_wall_seconds"]),
        "slowest_layer_candidates": layer_candidates[:8],
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    control_path = repo / SOURCE_CONTROL_PATH
    profiled_path = repo / SOURCE_PROFILED_PATH
    observed_control = git_blob(control_path, repo)
    observed_profiled = git_blob(profiled_path, repo)

    print("LOOM Stretch 028 — Balanced SINGLE_PASS Compute Re-Attribution")
    print(f"Canonical CONTROL blob: {observed_control}")
    print(f"PROFILED attribution blob: {observed_profiled}")
    if observed_control != SOURCE_CONTROL_BLOB or observed_profiled != SOURCE_PROFILED_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Balanced order: CONTROL -> PROFILED -> PROFILED -> CONTROL")
    print("Frozen architecture: M=5 + H36 + full persistence + one final cleanup/pass")
    print("Scientific change: instrumentation boundaries ONLY")
    print("PROFILED throughput is perturbation telemetry, not an optimization result")
    print("Model / runtime / KV / parity / I-O / safety: UNCHANGED")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "single-pass-compute-reattribution-028" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"
    summary: dict = {
        "experiment": "Stretch 028 — Balanced SINGLE_PASS Compute Re-Attribution",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "source_provenance": {
            "control_path": str(SOURCE_CONTROL_PATH),
            "control_blob": observed_control,
            "profiled_path": str(SOURCE_PROFILED_PATH),
            "profiled_blob": observed_profiled,
        },
        "frozen_architecture": "M5 H36 full persistence; one final cleanup/pass; MLX 0.31.2",
        "instrumentation_policy": "explicit mx.eval target-component boundaries; perturbation measured by balanced control",
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    save()
    scripts = {"CONTROL": control_path, "PROFILED": profiled_path}

    for index, variant in enumerate(RUN_ORDER, start=1):
        script = scripts[variant]
        out_path = run_dir / f"attempt-{index}-{variant.lower()}-stdout.txt"
        err_path = run_dir / f"attempt-{index}-{variant.lower()}-stderr.txt"
        print(f"Attempt {index}/4: {variant} via {script.name}")
        started = time.perf_counter()
        with out_path.open("w", encoding="utf-8") as out, err_path.open("w", encoding="utf-8") as err:
            proc = subprocess.run([sys.executable, str(script)], cwd=repo, stdout=out, stderr=err, text=True, check=False)
        wrapper_wall = time.perf_counter() - started
        stdout_text = out_path.read_text(encoding="utf-8", errors="replace")
        child_summary_path = parse_summary_path(stdout_text)
        attempt: dict = {
            "attempt": index,
            "variant": variant,
            "returncode": proc.returncode,
            "wrapper_wall_seconds": wrapper_wall,
            "stdout_path": str(out_path),
            "stderr_path": str(err_path),
            "child_summary_path": str(child_summary_path) if child_summary_path else None,
        }

        if child_summary_path is None or not child_summary_path.is_file():
            attempt["usable"] = False
            summary["attempts"].append(attempt)
            summary["classification"] = "SINGLE_PASS_COMPUTE_REATTRIBUTION_INCOMPLETE"
            summary["failure_reason"] = f"attempt {index} {variant}: summary missing"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 3

        child = json.loads(child_summary_path.read_text(encoding="utf-8"))
        hotset = child.get("hotset") or {}
        full = child.get("full_weight_persistence") or {}
        ob = child.get("oracle_block_verification") or {}
        telemetry = child.get("telemetry") or {}
        observed_ids = [int(x) for x in hotset.get("layer_ids", [])]
        persistent_total = full.get("persistent_total_raw_weight_bytes")
        try:
            cleanup_walls, shared_forward, shared_materialize = extract_pass_metrics(child)
        except Exception as exc:
            attempt["usable"] = False
            attempt["failure_reason"] = f"metric extraction failed: {type(exc).__name__}: {exc}"
            summary["attempts"].append(attempt)
            summary["classification"] = "SINGLE_PASS_COMPUTE_REATTRIBUTION_INCOMPLETE"
            summary["failure_reason"] = f"attempt {index} {variant}: {attempt['failure_reason']}"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

        ca = child.get("single_pass_compute_attribution") if variant == "PROFILED" else None
        profile_ok = True
        if variant == "PROFILED":
            profile_ok = (
                isinstance(ca, dict)
                and int(ca.get("profiled_target_layer_records", -1)) == 108
                and len(ca.get("block_totals") or []) == 3
            )
        else:
            profile_ok = ca is None

        attempt.update({
            "classification": child.get("classification"),
            "hotset_layer_ids": observed_ids,
            "persistent_total_raw_weight_bytes": persistent_total,
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_tokens": ob.get("accepted_oracle_tokens"),
            "total_block_wall": ob.get("total_target_block_wall_seconds"),
            "block_walls": ob.get("block_full_pass_seconds") or [],
            "cleanup_walls": cleanup_walls,
            "shared_forward": shared_forward,
            "shared_materialize": shared_materialize,
            "compute_attribution": ca,
            "profile_ok": profile_ok,
            "min_free": telemetry.get("min_memory_free_percent"),
            "peak_swap": telemetry.get("peak_swap_used_mb"),
        })

        attempt["usable"] = (
            proc.returncode == 0
            and child.get("classification") == EXPECTED_CHILD_CLASSIFICATION
            and observed_ids == EXPECTED_HOTSET_IDS
            and persistent_total is not None
            and abs(int(persistent_total) - EXPECTED_TOTAL_WEIGHT_BYTES) <= 24 * 1024 * 1024
            and int(ob.get("oracle_block_size", -1)) == 5
            and int(ob.get("accepted_oracle_tokens", -1)) == 15
            and len(ob.get("block_full_pass_seconds") or []) == 3
            and len(cleanup_walls) == 3
            and profile_ok
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            summary["classification"] = "SINGLE_PASS_COMPUTE_REATTRIBUTION_INCOMPLETE"
            summary["failure_reason"] = (
                f"attempt {index} {variant} failed inherited/profile gates: "
                f"rc={proc.returncode}, class={child.get('classification')}, profile_ok={profile_ok}"
            )
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 5

    control_records = [r for r in summary["attempts"] if r["variant"] == "CONTROL"]
    profiled_records = [r for r in summary["attempts"] if r["variant"] == "PROFILED"]
    control = aggregate_basic(control_records)
    profiled_basic = aggregate_basic(profiled_records)
    attribution = aggregate_profiled(profiled_records)

    perturbation = {
        "profiled_over_control_target_rate_ratio": safe_ratio(
            profiled_basic["pooled_target_verification_tokens_per_second"],
            control["pooled_target_verification_tokens_per_second"],
        ),
        "profiled_over_control_median_block_wall_ratio": safe_ratio(
            profiled_basic["median_block_wall_seconds"], control["median_block_wall_seconds"]
        ),
        "interpretation": "instrumentation perturbation only; not optimization evidence",
    }

    summary["control"] = control
    summary["profiled_basic"] = profiled_basic
    summary["instrumentation_perturbation"] = perturbation
    summary["single_pass_compute_reattribution"] = attribution
    summary["classification"] = "SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: SINGLE_PASS_COMPUTE_REATTRIBUTION_PASS")
    print(f"CONTROL pooled target-verification tok/s: {control['pooled_target_verification_tokens_per_second']}")
    print(f"PROFILED pooled target-verification tok/s: {profiled_basic['pooled_target_verification_tokens_per_second']}")
    print(f"PROFILED/CONTROL target-rate ratio (instrumentation): {perturbation['profiled_over_control_target_rate_ratio']}")
    print(f"CONTROL median block wall: {control['median_block_wall_seconds']} s")
    print(f"PROFILED median block wall: {profiled_basic['median_block_wall_seconds']} s")
    print(f"Mean profiled transformer compute/block: {attribution['mean_profiled_transformer_compute_seconds_per_block']} s")
    print(f"Mean attention path/block: {attribution['mean_attention_path_seconds_per_block']} s")
    print(f"Mean MLP path/block: {attribution['mean_mlp_path_seconds_per_block']} s")
    print(f"MLP/attention path ratio: {attribution['mlp_over_attention_path_ratio']}")
    print(f"Mean component seconds/block: {attribution['mean_component_seconds_per_block']}")
    print(f"Ranked components: {attribution['ranked_components']}")
    print(f"Mean final cleanup wall: {attribution['mean_final_cleanup_wall_seconds']} s")
    print(f"Mean shared forward wall: {attribution['mean_shared_forward_seconds_per_block']} s")
    print(f"Mean residual unattributed wall: {attribution['mean_residual_unattributed_seconds_per_block']} s")
    print(f"Accounted share of PROFILED wall: {attribution['accounted_share_of_profiled_full_wall']}")
    print(f"Slowest layer candidates: {attribution['slowest_layer_candidates']}")
    print(f"CONTROL minimum free memory: {control['minimum_observed_free_memory_percent']}%")
    print(f"PROFILED minimum free memory: {profiled_basic['minimum_observed_free_memory_percent']}%")
    print(f"CONTROL peak swap: {control['peak_observed_swap_mb']} MB")
    print(f"PROFILED peak swap: {profiled_basic['peak_observed_swap_mb']} MB")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
