#!/usr/bin/env python3
"""LOOM Stretch 024 — balanced full-persistent compute/kernel attribution.

Runs canonical M5/H36/full-persistent CONTROL and the attribution PROFILED
variant in ABBA order. The profiled path adds explicit evaluation boundaries;
therefore its throughput is used only to quantify instrumentation perturbation.
Component timing is the scientific output.
"""
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

SOURCE_CONTROL_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py")
SOURCE_CONTROL_BLOB = "120ad7be2f275559898bf636ca8e8fe039a56c60"
SOURCE_PROFILED_PATH = Path("scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py")
SOURCE_PROFILED_BLOB = "845b10da26a70455cd40f483cea5d313f9ac12dd"
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


def shared_stage_block_metrics(child: dict) -> tuple[list[float], list[float]]:
    materialize, forward = [], []
    for record in (child.get("stream") or {}).get("tokens") or []:
        stages = (record.get("pass") or {}).get("stages") or {}
        if any(name not in stages for name in SHARED_STAGE_NAMES):
            raise RuntimeError("target block missing shared stage records")
        materialize.append(sum(float(stages[name].get("materialize_wall_seconds", 0.0)) for name in SHARED_STAGE_NAMES))
        forward.append(sum(float(stages[name].get("forward_wall_seconds", 0.0)) for name in SHARED_STAGE_NAMES))
    return materialize, forward


def profiled_cycle_metrics(child: dict) -> tuple[list[float], list[float]]:
    build, cleanup = [], []
    for record in (child.get("stream") or {}).get("tokens") or []:
        cycles = (record.get("pass") or {}).get("cycles") or []
        if len(cycles) != 36:
            raise RuntimeError(f"expected 36 cycles, got {len(cycles)}")
        if any("build_reuse_wall_seconds" not in c or "cleanup_wall_seconds" not in c for c in cycles):
            raise RuntimeError("profiled cycle attribution fields missing")
        build.append(sum(float(c["build_reuse_wall_seconds"]) for c in cycles))
        cleanup.append(sum(float(c["cleanup_wall_seconds"]) for c in cycles))
    return build, cleanup


def aggregate_basic(records: list[dict]) -> dict:
    accepted = sum(int(r["accepted_tokens"]) for r in records)
    wall = sum(float(r["total_block_wall"]) for r in records)
    block_walls = [float(x) for r in records for x in r["block_walls"]]
    min_free = [int(r["min_free"]) for r in records if r.get("min_free") is not None]
    peak_swap = [float(r["peak_swap"]) for r in records if r.get("peak_swap") is not None]
    return {
        "runs": len(records),
        "accepted_tokens": accepted,
        "total_target_block_wall_seconds": wall,
        "pooled_target_verification_tokens_per_second": accepted / wall,
        "mean_block_wall_seconds": statistics.mean(block_walls),
        "median_block_wall_seconds": statistics.median(block_walls),
        "raw_block_walls": block_walls,
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
    }


def aggregate_profiled(records: list[dict]) -> dict:
    component_values = {name: [] for name in COMPONENT_NAMES}
    attention_path, mlp_path, transformer_compute = [], [], []
    build, cleanup, shared_materialize, shared_forward, transformer_materialize, full_wall = ([] for _ in range(6))
    slow_layers: dict[int, list[float]] = {i: [] for i in range(36)}

    for record in records:
        ca = record["compute_attribution"]
        for block in ca["block_totals"]:
            for name in COMPONENT_NAMES:
                component_values[name].append(float(block[name]))
            attention_path.append(float(block["attention_path_seconds"]))
            mlp_path.append(float(block["mlp_path_seconds"]))
            transformer_compute.append(float(block["profiled_transformer_compute_seconds"]))
        build.extend(float(x) for x in record["build_walls"])
        cleanup.extend(float(x) for x in record["cleanup_walls"])
        shared_materialize.extend(float(x) for x in record["shared_materialize"])
        shared_forward.extend(float(x) for x in record["shared_forward"])
        transformer_materialize.extend(float(x) for x in record["transformer_materialize"])
        full_wall.extend(float(x) for x in record["block_walls"])
        for row in ca["all_layer_means"]:
            slow_layers[int(row["layer_id"])].append(float(row["mean_profiled_compute_seconds"]))

    means = {name: statistics.mean(values) for name, values in component_values.items()}
    transformer_mean = statistics.mean(transformer_compute)
    component_share = {name: means[name] / transformer_mean for name in COMPONENT_NAMES}
    ranked_components = sorted(component_share.items(), key=lambda item: item[1], reverse=True)

    accounted, residual = [], []
    for i in range(len(full_wall)):
        value = (
            transformer_compute[i]
            + build[i]
            + cleanup[i]
            + shared_materialize[i]
            + shared_forward[i]
            + transformer_materialize[i]
        )
        accounted.append(value)
        residual.append(full_wall[i] - value)

    layer_means = [
        {"layer_id": layer_id, "mean_profiled_compute_seconds": statistics.mean(values)}
        for layer_id, values in slow_layers.items() if values
    ]
    layer_means.sort(key=lambda row: row["mean_profiled_compute_seconds"], reverse=True)

    return {
        "profiled_block_samples": len(full_wall),
        "mean_component_seconds_per_block": means,
        "component_share_of_profiled_transformer_compute": component_share,
        "ranked_components": ranked_components,
        "mean_attention_path_seconds_per_block": statistics.mean(attention_path),
        "mean_mlp_path_seconds_per_block": statistics.mean(mlp_path),
        "mlp_over_attention_path_ratio": safe_ratio(statistics.mean(mlp_path), statistics.mean(attention_path)),
        "mean_profiled_transformer_compute_seconds_per_block": transformer_mean,
        "mean_transformer_materialize_seconds_per_block": statistics.mean(transformer_materialize),
        "mean_layer_build_reuse_seconds_per_block": statistics.mean(build),
        "mean_layer_cleanup_seconds_per_block": statistics.mean(cleanup),
        "mean_shared_materialize_seconds_per_block": statistics.mean(shared_materialize),
        "mean_shared_forward_seconds_per_block": statistics.mean(shared_forward),
        "mean_accounted_seconds_per_block": statistics.mean(accounted),
        "mean_residual_unattributed_seconds_per_block": statistics.mean(residual),
        "mean_profiled_full_block_wall_seconds": statistics.mean(full_wall),
        "accounted_share_of_profiled_full_wall": safe_ratio(statistics.mean(accounted), statistics.mean(full_wall)),
        "slowest_layers_by_mean_profiled_compute": layer_means[:8],
        "raw_residual_unattributed_seconds": residual,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    control_path = repo / SOURCE_CONTROL_PATH
    profiled_path = repo / SOURCE_PROFILED_PATH
    observed_control = git_blob(control_path, repo)
    observed_profiled = git_blob(profiled_path, repo)

    print("LOOM Stretch 024 — Full-Persistent Compute/Kernel Attribution")
    print(f"Canonical CONTROL blob: {observed_control}")
    print(f"PROFILED attribution blob: {observed_profiled}")
    if observed_control != SOURCE_CONTROL_BLOB or observed_profiled != SOURCE_PROFILED_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Balanced order: CONTROL -> PROFILED -> PROFILED -> CONTROL")
    print("Frozen architecture: M=5 + H36 + full raw-weight persistence")
    print("Scientific change: instrumentation boundaries ONLY")
    print("PROFILED throughput is perturbation telemetry, not a canonical speed claim")
    print("No cache purge / runtime change / drafter / KV change")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "full-persistent-compute-kernel-attribution-024" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"
    summary: dict = {
        "experiment": "Stretch 024 — Full-Persistent Compute/Kernel Attribution",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "source_provenance": {
            "control_path": str(SOURCE_CONTROL_PATH),
            "control_blob": observed_control,
            "profiled_path": str(SOURCE_PROFILED_PATH),
            "profiled_blob": observed_profiled,
        },
        "frozen_architecture": "M5 H36 full raw-weight persistence; MLX 0.31.2",
        "instrumentation_policy": "explicit mx.eval target-component boundaries; throughput perturbation measured separately",
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
        attempt = {
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
            summary["classification"] = "COMPUTE_ATTRIBUTION_INCOMPLETE"
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
            shared_materialize, shared_forward = shared_stage_block_metrics(child)
            if variant == "PROFILED":
                build_walls, cleanup_walls = profiled_cycle_metrics(child)
            else:
                build_walls, cleanup_walls = [], []
        except Exception as exc:
            attempt["usable"] = False
            attempt["failure_reason"] = f"metric extraction failed: {type(exc).__name__}: {exc}"
            summary["attempts"].append(attempt)
            summary["classification"] = "COMPUTE_ATTRIBUTION_INCOMPLETE"
            summary["failure_reason"] = f"attempt {index} {variant}: {attempt['failure_reason']}"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

        ca = child.get("compute_attribution") if variant == "PROFILED" else None
        attempt.update({
            "classification": child.get("classification"),
            "hotset_layer_ids": observed_ids,
            "persistent_total_raw_weight_bytes": persistent_total,
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_tokens": ob.get("accepted_oracle_tokens"),
            "total_block_wall": ob.get("total_target_block_wall_seconds"),
            "block_walls": ob.get("block_full_pass_seconds") or [],
            "transformer_materialize": ob.get("block_materialize_seconds") or [],
            "shared_materialize": shared_materialize,
            "shared_forward": shared_forward,
            "build_walls": build_walls,
            "cleanup_walls": cleanup_walls,
            "compute_attribution": ca,
            "min_free": telemetry.get("min_memory_free_percent"),
            "peak_swap": telemetry.get("peak_swap_used_mb"),
        })
        profile_ok = True
        if variant == "PROFILED":
            profile_ok = (
                isinstance(ca, dict)
                and int(ca.get("profiled_target_layer_records", -1)) == 108
                and len(ca.get("block_totals") or []) == 3
                and len(build_walls) == 3
                and len(cleanup_walls) == 3
            )
        else:
            profile_ok = ca is None

        attempt["usable"] = (
            proc.returncode == 0
            and child.get("classification") == EXPECTED_CHILD_CLASSIFICATION
            and observed_ids == EXPECTED_HOTSET_IDS
            and persistent_total is not None
            and abs(int(persistent_total) - EXPECTED_TOTAL_WEIGHT_BYTES) <= 24 * 1024 * 1024
            and int(ob.get("oracle_block_size", -1)) == 5
            and int(ob.get("accepted_oracle_tokens", -1)) == 15
            and len(ob.get("block_full_pass_seconds") or []) == 3
            and profile_ok
        )
        summary["attempts"].append(attempt)
        save()
        if not attempt["usable"]:
            summary["classification"] = "COMPUTE_ATTRIBUTION_INCOMPLETE"
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
    profiled_attr = aggregate_profiled(profiled_records)

    perturbation = {
        "profiled_over_control_target_rate_ratio": safe_ratio(
            profiled_basic["pooled_target_verification_tokens_per_second"],
            control["pooled_target_verification_tokens_per_second"],
        ),
        "profiled_over_control_median_block_wall_ratio": safe_ratio(
            profiled_basic["median_block_wall_seconds"], control["median_block_wall_seconds"]
        ),
        "interpretation": "instrumentation perturbation only; not a target optimization result",
    }
    summary["control"] = control
    summary["profiled_basic"] = profiled_basic
    summary["instrumentation_perturbation"] = perturbation
    summary["compute_kernel_attribution"] = profiled_attr
    summary["classification"] = "FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS")
    print(f"CONTROL pooled target-verification tok/s: {control['pooled_target_verification_tokens_per_second']}")
    print(f"PROFILED pooled target-verification tok/s: {profiled_basic['pooled_target_verification_tokens_per_second']}")
    print(f"PROFILED/CONTROL target-rate ratio (instrumentation perturbation): {perturbation['profiled_over_control_target_rate_ratio']}")
    print(f"CONTROL median block wall: {control['median_block_wall_seconds']} s")
    print(f"PROFILED median block wall: {profiled_basic['median_block_wall_seconds']} s")
    print(f"Mean profiled transformer compute/block: {profiled_attr['mean_profiled_transformer_compute_seconds_per_block']} s")
    print(f"Mean attention path/block: {profiled_attr['mean_attention_path_seconds_per_block']} s")
    print(f"Mean MLP path/block: {profiled_attr['mean_mlp_path_seconds_per_block']} s")
    print(f"MLP/attention path ratio: {profiled_attr['mlp_over_attention_path_ratio']}")
    print(f"Mean component seconds/block: {profiled_attr['mean_component_seconds_per_block']}")
    print(f"Ranked components: {profiled_attr['ranked_components']}")
    print(f"Mean layer cleanup/block: {profiled_attr['mean_layer_cleanup_seconds_per_block']} s")
    print(f"Mean shared forward/block: {profiled_attr['mean_shared_forward_seconds_per_block']} s")
    print(f"Mean residual unattributed/block: {profiled_attr['mean_residual_unattributed_seconds_per_block']} s")
    print(f"Accounted share of profiled full wall: {profiled_attr['accounted_share_of_profiled_full_wall']}")
    print(f"Slowest profiled layers: {profiled_attr['slowest_layers_by_mean_profiled_compute']}")
    print(f"CONTROL minimum observed free memory: {control['minimum_observed_free_memory_percent']}%")
    print(f"PROFILED minimum observed free memory: {profiled_basic['minimum_observed_free_memory_percent']}%")
    print(f"CONTROL peak swap: {control['peak_observed_swap_mb']} MB")
    print(f"PROFILED peak swap: {profiled_basic['peak_observed_swap_mb']} MB")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
