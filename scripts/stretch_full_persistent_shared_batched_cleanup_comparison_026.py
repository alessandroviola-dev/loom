#!/usr/bin/env python3
"""LOOM Stretch 026 — balanced shared-stage cleanup consolidation comparison."""
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

SOURCE_BATCHED_PATH = Path("scripts/stretch_full_persistent_batched_cleanup_025.py")
SOURCE_BATCHED_BLOB = "5ca3572f3269899e7c3fc23b9e136381ce864d99"
SOURCE_SHARED_BATCHED_PATH = Path("scripts/stretch_full_persistent_shared_batched_cleanup_026.py")
SOURCE_SHARED_BATCHED_BLOB = "6926e1b1b9a851f23d88ba6b1f1023e13336098a"
EXPECTED_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
RUN_ORDER = ["BATCHED", "SHARED_BATCHED", "SHARED_BATCHED", "BATCHED"]


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


def aggregate(records: list[dict]) -> dict:
    accepted = sum(int(r["accepted_tokens"]) for r in records)
    total_wall = sum(float(r["total_block_wall"]) for r in records)
    block_walls = [float(v) for r in records for v in r["block_walls"]]
    body_cleanup = [float(v) for r in records for v in r.get("body_cleanup_walls", [])]
    shared_cleanup = [float(v) for r in records for v in r.get("shared_cleanup_walls", [])]
    min_free = [int(r["min_free"]) for r in records if r.get("min_free") is not None]
    peak_swap = [float(r["peak_swap"]) for r in records if r.get("peak_swap") is not None]
    return {
        "runs": len(records),
        "accepted_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "mean_block_wall_seconds": statistics.mean(block_walls),
        "median_block_wall_seconds": statistics.median(block_walls),
        "mean_body_cleanup_wall_seconds": statistics.mean(body_cleanup) if body_cleanup else None,
        "mean_shared_cleanup_wall_seconds": statistics.mean(shared_cleanup) if shared_cleanup else None,
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
        "raw_block_walls": block_walls,
        "raw_body_cleanup_walls": body_cleanup,
        "raw_shared_cleanup_walls": shared_cleanup,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    batched_path = repo / SOURCE_BATCHED_PATH
    shared_path = repo / SOURCE_SHARED_BATCHED_PATH
    observed_batched = git_blob(batched_path, repo)
    observed_shared = git_blob(shared_path, repo)

    print("LOOM Stretch 026 — Balanced Shared-Stage Cleanup Consolidation")
    print(f"BATCHED baseline blob: {observed_batched}")
    print(f"SHARED_BATCHED treatment blob: {observed_shared}")
    if observed_batched != SOURCE_BATCHED_BLOB or observed_shared != SOURCE_SHARED_BATCHED_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Balanced run order: BATCHED -> SHARED_BATCHED -> SHARED_BATCHED -> BATCHED")
    print("Frozen architecture: M=5 + H36 + full raw-weight persistence")
    print("Transformer cleanup: one per body in BOTH variants")
    print("Scientific factor: shared-stage cleanup 3x -> 1x post-head ONLY")
    print("Model / runtime / KV / parity / I-O / safety: UNCHANGED")
    print("Deliberate cache purge: NONE")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "full-persistent-shared-batched-cleanup-comparison-026" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 026 — Balanced Shared-Stage Cleanup Consolidation",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "scientific_factor": "shared persistent-stage cleanup embedding/norm/head 3x -> one post-head cleanup",
        "source_provenance": {
            "batched_path": str(SOURCE_BATCHED_PATH),
            "batched_blob": observed_batched,
            "shared_batched_path": str(SOURCE_SHARED_BATCHED_PATH),
            "shared_batched_blob": observed_shared,
        },
        "frozen_architecture": "M5 H36 full raw-weight persistence; one transformer-body cleanup; MLX 0.31.2",
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    save()
    scripts = {"BATCHED": batched_path, "SHARED_BATCHED": shared_path}

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
            summary["classification"] = "SHARED_CLEANUP_COMPARISON_INCOMPLETE"
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

        body_cleanup_walls: list[float] = []
        shared_cleanup_walls: list[float] = []
        cleanup_mode_ok = True
        for record in (child.get("stream") or {}).get("tokens") or []:
            stages = (record.get("pass") or {}).get("stages") or {}
            body = stages.get("transformer_body_cleanup")
            if not isinstance(body, dict) or body.get("policy") != "batched_once_after_36_layers":
                cleanup_mode_ok = False
                break
            body_cleanup_walls.append(float(body.get("wall_seconds", -1.0)))

            shared = stages.get("shared_stage_cleanup")
            if variant == "SHARED_BATCHED":
                if not isinstance(shared, dict) or shared.get("policy") != "batched_once_after_embedding_norm_head":
                    cleanup_mode_ok = False
                    break
                shared_cleanup_walls.append(float(shared.get("wall_seconds", -1.0)))
            else:
                if shared is not None:
                    cleanup_mode_ok = False
                    break

        attempt.update({
            "classification": child.get("classification"),
            "hotset_layer_ids": observed_ids,
            "persistent_total_raw_weight_bytes": persistent_total,
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_tokens": ob.get("accepted_oracle_tokens"),
            "total_block_wall": ob.get("total_target_block_wall_seconds"),
            "block_walls": ob.get("block_full_pass_seconds") or [],
            "body_cleanup_walls": body_cleanup_walls,
            "shared_cleanup_walls": shared_cleanup_walls,
            "cleanup_mode_ok": cleanup_mode_ok,
            "min_free": telemetry.get("min_memory_free_percent"),
            "peak_swap": telemetry.get("peak_swap_used_mb"),
        })

        attempt["usable"] = (
            proc.returncode == 0
            and child.get("classification") == EXPECTED_CLASSIFICATION
            and observed_ids == EXPECTED_HOTSET_IDS
            and persistent_total is not None
            and abs(int(persistent_total) - EXPECTED_TOTAL_WEIGHT_BYTES) <= 24 * 1024 * 1024
            and int(ob.get("oracle_block_size", -1)) == 5
            and int(ob.get("accepted_oracle_tokens", -1)) == 15
            and len(ob.get("block_full_pass_seconds") or []) == 3
            and cleanup_mode_ok
            and len(body_cleanup_walls) == 3
            and (variant != "SHARED_BATCHED" or len(shared_cleanup_walls) == 3)
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            summary["classification"] = "SHARED_CLEANUP_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = (
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"rc={proc.returncode}, class={child.get('classification')}, cleanup_mode_ok={cleanup_mode_ok}"
            )
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

    baseline_records = [r for r in summary["attempts"] if r["variant"] == "BATCHED"]
    treatment_records = [r for r in summary["attempts"] if r["variant"] == "SHARED_BATCHED"]
    baseline = aggregate(baseline_records)
    treatment = aggregate(treatment_records)

    comparison = {
        "batched": baseline,
        "shared_batched": treatment,
        "shared_batched_over_batched_target_rate_ratio": safe_ratio(
            treatment["pooled_target_verification_tokens_per_second"],
            baseline["pooled_target_verification_tokens_per_second"],
        ),
        "shared_batched_over_batched_median_block_wall_ratio": safe_ratio(
            treatment["median_block_wall_seconds"], baseline["median_block_wall_seconds"]
        ),
        "observed_higher_pooled_target_rate": (
            "SHARED_BATCHED"
            if treatment["pooled_target_verification_tokens_per_second"] > baseline["pooled_target_verification_tokens_per_second"]
            else "BATCHED"
        ),
    }

    summary["comparison"] = comparison
    summary["classification"] = "FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: FULL_PERSISTENT_SHARED_BATCHED_CLEANUP_COMPARISON_PASS")
    print(f"BATCHED pooled target-verification tok/s: {baseline['pooled_target_verification_tokens_per_second']}")
    print(f"SHARED_BATCHED pooled target-verification tok/s: {treatment['pooled_target_verification_tokens_per_second']}")
    print(f"SHARED_BATCHED/BATCHED target-rate ratio: {comparison['shared_batched_over_batched_target_rate_ratio']}")
    print(f"BATCHED median block wall: {baseline['median_block_wall_seconds']} s")
    print(f"SHARED_BATCHED median block wall: {treatment['median_block_wall_seconds']} s")
    print(f"SHARED_BATCHED/BATCHED median block-wall ratio: {comparison['shared_batched_over_batched_median_block_wall_ratio']}")
    print(f"BATCHED mean body cleanup wall: {baseline['mean_body_cleanup_wall_seconds']} s")
    print(f"SHARED_BATCHED mean body cleanup wall: {treatment['mean_body_cleanup_wall_seconds']} s")
    print(f"SHARED_BATCHED mean one-per-shared-path cleanup wall: {treatment['mean_shared_cleanup_wall_seconds']} s")
    print(f"BATCHED minimum observed free memory: {baseline['minimum_observed_free_memory_percent']}%")
    print(f"SHARED_BATCHED minimum observed free memory: {treatment['minimum_observed_free_memory_percent']}%")
    print(f"BATCHED peak swap: {baseline['peak_observed_swap_mb']} MB")
    print(f"SHARED_BATCHED peak swap: {treatment['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
