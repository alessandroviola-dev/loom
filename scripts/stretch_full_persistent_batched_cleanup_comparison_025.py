#!/usr/bin/env python3
"""LOOM Stretch 025 — balanced full-persistent cleanup-schedule comparison."""
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
SOURCE_BATCHED_PATH = Path("scripts/stretch_full_persistent_batched_cleanup_025.py")
SOURCE_BATCHED_BLOB = "5ca3572f3269899e7c3fc23b9e136381ce864d99"
EXPECTED_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
RUN_ORDER = ["CONTROL", "BATCHED", "BATCHED", "CONTROL"]


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
    min_free = [int(r["min_free"]) for r in records if r.get("min_free") is not None]
    peak_swap = [float(r["peak_swap"]) for r in records if r.get("peak_swap") is not None]
    cleanup_walls = [
        float(v) for r in records for v in r.get("body_cleanup_walls", [])
    ]
    return {
        "runs": len(records),
        "accepted_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "mean_block_wall_seconds": statistics.mean(block_walls),
        "median_block_wall_seconds": statistics.median(block_walls),
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
        "mean_batched_body_cleanup_wall_seconds": (
            statistics.mean(cleanup_walls) if cleanup_walls else None
        ),
        "median_batched_body_cleanup_wall_seconds": (
            statistics.median(cleanup_walls) if cleanup_walls else None
        ),
        "raw_block_walls": block_walls,
        "raw_body_cleanup_walls": cleanup_walls,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    control_path = repo / SOURCE_CONTROL_PATH
    batched_path = repo / SOURCE_BATCHED_PATH
    observed_control = git_blob(control_path, repo)
    observed_batched = git_blob(batched_path, repo)

    print("LOOM Stretch 025 — Balanced Full-Persistent Cleanup-Schedule Comparison")
    print(f"Canonical CONTROL blob: {observed_control}")
    print(f"BATCHED treatment blob: {observed_batched}")
    if observed_control != SOURCE_CONTROL_BLOB or observed_batched != SOURCE_BATCHED_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Balanced run order: CONTROL -> BATCHED -> BATCHED -> CONTROL")
    print("Frozen architecture: M=5 + H36 + full raw-weight persistence")
    print("Scientific factor: transformer cleanup 36x per-layer -> 1x post-body ONLY")
    print("Shared-stage cleanup / model / runtime / KV / parity / I-O / safety: UNCHANGED")
    print("Deliberate cache purge: NONE")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = (
        repo
        / "results-local"
        / "stretch"
        / "full-persistent-batched-cleanup-comparison-025"
        / run_id
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 025 — Balanced Full-Persistent Cleanup-Schedule Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "scientific_factor": "transformer cleanup 36x per-layer -> one post-body cleanup",
        "source_provenance": {
            "control_path": str(SOURCE_CONTROL_PATH),
            "control_blob": observed_control,
            "batched_path": str(SOURCE_BATCHED_PATH),
            "batched_blob": observed_batched,
        },
        "frozen_architecture": "M5 H36 full raw-weight persistence; MLX 0.31.2",
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    save()
    scripts = {"CONTROL": control_path, "BATCHED": batched_path}

    for index, variant in enumerate(RUN_ORDER, start=1):
        script = scripts[variant]
        out_path = run_dir / f"attempt-{index}-{variant.lower()}-stdout.txt"
        err_path = run_dir / f"attempt-{index}-{variant.lower()}-stderr.txt"
        print(f"Attempt {index}/4: {variant} via {script.name}")
        started = time.perf_counter()
        with out_path.open("w", encoding="utf-8") as out, err_path.open("w", encoding="utf-8") as err:
            proc = subprocess.run(
                [sys.executable, str(script)],
                cwd=repo,
                stdout=out,
                stderr=err,
                text=True,
                check=False,
            )
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
            summary["classification"] = "CLEANUP_COMPARISON_INCOMPLETE"
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
        cleanup_mode_ok = True
        for record in (child.get("stream") or {}).get("tokens") or []:
            stages = (record.get("pass") or {}).get("stages") or {}
            body = stages.get("transformer_body_cleanup")
            if variant == "BATCHED":
                if not isinstance(body, dict) or body.get("policy") != "batched_once_after_36_layers":
                    cleanup_mode_ok = False
                    break
                body_cleanup_walls.append(float(body.get("wall_seconds", -1.0)))
            else:
                if body is not None:
                    cleanup_mode_ok = False
                    break

        attempt.update(
            {
                "classification": child.get("classification"),
                "hotset_layer_ids": observed_ids,
                "persistent_total_raw_weight_bytes": persistent_total,
                "oracle_block_size": ob.get("oracle_block_size"),
                "accepted_tokens": ob.get("accepted_oracle_tokens"),
                "total_block_wall": ob.get("total_target_block_wall_seconds"),
                "block_walls": ob.get("block_full_pass_seconds") or [],
                "body_cleanup_walls": body_cleanup_walls,
                "cleanup_mode_ok": cleanup_mode_ok,
                "min_free": telemetry.get("min_memory_free_percent"),
                "peak_swap": telemetry.get("peak_swap_used_mb"),
            }
        )

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
            and (variant != "BATCHED" or len(body_cleanup_walls) == 3)
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            summary["classification"] = "CLEANUP_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = (
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"rc={proc.returncode}, class={child.get('classification')}, "
                f"cleanup_mode_ok={cleanup_mode_ok}"
            )
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

    control_records = [r for r in summary["attempts"] if r["variant"] == "CONTROL"]
    batched_records = [r for r in summary["attempts"] if r["variant"] == "BATCHED"]
    control = aggregate(control_records)
    batched = aggregate(batched_records)

    comparison = {
        "control": control,
        "batched": batched,
        "batched_over_control_target_rate_ratio": safe_ratio(
            batched["pooled_target_verification_tokens_per_second"],
            control["pooled_target_verification_tokens_per_second"],
        ),
        "batched_over_control_median_block_wall_ratio": safe_ratio(
            batched["median_block_wall_seconds"],
            control["median_block_wall_seconds"],
        ),
        "observed_higher_pooled_target_rate": (
            "BATCHED"
            if batched["pooled_target_verification_tokens_per_second"]
            > control["pooled_target_verification_tokens_per_second"]
            else "CONTROL"
        ),
    }

    summary["comparison"] = comparison
    summary["classification"] = "FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: FULL_PERSISTENT_BATCHED_CLEANUP_COMPARISON_PASS")
    print(f"CONTROL pooled target-verification tok/s: {control['pooled_target_verification_tokens_per_second']}")
    print(f"BATCHED pooled target-verification tok/s: {batched['pooled_target_verification_tokens_per_second']}")
    print(f"BATCHED/CONTROL target-rate ratio: {comparison['batched_over_control_target_rate_ratio']}")
    print(f"CONTROL median block wall: {control['median_block_wall_seconds']} s")
    print(f"BATCHED median block wall: {batched['median_block_wall_seconds']} s")
    print(f"BATCHED/CONTROL median block-wall ratio: {comparison['batched_over_control_median_block_wall_ratio']}")
    print(f"BATCHED mean one-per-body cleanup wall: {batched['mean_batched_body_cleanup_wall_seconds']} s")
    print(f"CONTROL minimum observed free memory: {control['minimum_observed_free_memory_percent']}%")
    print(f"BATCHED minimum observed free memory: {batched['minimum_observed_free_memory_percent']}%")
    print(f"CONTROL peak swap: {control['peak_observed_swap_mb']} MB")
    print(f"BATCHED peak swap: {batched['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
