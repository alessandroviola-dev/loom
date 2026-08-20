#!/usr/bin/env python3
"""LOOM Stretch 020 — balanced M5 H16 vs H24 hotset comparison.

Runs the frozen exact M=5 target path with either 16 or 24 persistent
transformer layers in balanced ABBA order. The only intended scientific factor
is hotset residency. No deliberate cache purge is performed.
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

SOURCE_H16_PATH = Path("scripts/stretch_five_token_h16_hotset_variant_019.py")
SOURCE_H16_BLOB = "6a0bd001ad7a5a5bf5646b54a302f7fc372e4367"
SOURCE_H24_PATH = Path("scripts/stretch_five_token_h24_hotset_variant_020.py")
SOURCE_H24_BLOB = "09363f4ce669a7de7b2f16fe4dfb63519c72eb9f"
EXPECTED_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
RUN_ORDER = ["H16", "H24", "H24", "H16"]
EXPECTED_HOTSET_IDS = {
    "H16": list(range(16)),
    "H24": list(range(24)),
}


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
    if not matches:
        return None
    return Path(matches[-1].strip())


def flatten(records: list[dict], key: str) -> list[float]:
    values: list[float] = []
    for record in records:
        values.extend(float(v) for v in record.get(key, []))
    return values


def aggregate_variant(records: list[dict]) -> dict:
    accepted = sum(int(r["accepted_oracle_tokens"]) for r in records)
    total_wall = sum(float(r["total_target_block_wall_seconds"]) for r in records)
    full = flatten(records, "block_full_pass_seconds")
    materialize = flatten(records, "block_materialize_seconds")
    forward = flatten(records, "block_forward_seconds")
    full_reads = flatten(records, "full_pass_disk_read_bytes_per_block")
    materialize_reads = flatten(records, "materialize_disk_read_bytes_per_block")
    min_free_values = [
        int(r["min_memory_free_percent"])
        for r in records
        if r.get("min_memory_free_percent") is not None
    ]
    peak_swap_values = [
        float(r["peak_swap_used_mb"])
        for r in records
        if r.get("peak_swap_used_mb") is not None
    ]
    hotset_bytes = [int(r["persistent_hotset_bytes"]) for r in records]
    hybrid_budgets = [int(r["hybrid_raw_weight_budget_bytes"]) for r in records]
    block_size = int(records[0]["oracle_block_size"])
    return {
        "runs": len(records),
        "oracle_block_size": block_size,
        "accepted_oracle_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "block_samples": len(full),
        "mean_block_full_pass_seconds": statistics.mean(full),
        "median_block_full_pass_seconds": statistics.median(full),
        "mean_block_materialize_seconds": statistics.mean(materialize),
        "median_block_materialize_seconds": statistics.median(materialize),
        "mean_block_forward_seconds": statistics.mean(forward),
        "median_block_forward_seconds": statistics.median(forward),
        "mean_full_pass_disk_read_bytes_per_block": statistics.mean(full_reads),
        "median_full_pass_disk_read_bytes_per_block": statistics.median(full_reads),
        "mean_materialize_disk_read_bytes_per_block": statistics.mean(materialize_reads),
        "mean_full_pass_disk_read_bytes_per_accepted_token": statistics.mean(full_reads) / block_size,
        "mean_materialize_disk_read_bytes_per_accepted_token": statistics.mean(materialize_reads) / block_size,
        "persistent_hotset_bytes": statistics.median(hotset_bytes),
        "hybrid_raw_weight_budget_bytes": statistics.median(hybrid_budgets),
        "minimum_observed_free_memory_percent": min(min_free_values) if min_free_values else None,
        "peak_observed_swap_mb": max(peak_swap_values) if peak_swap_values else None,
        "raw_block_full_pass_seconds": full,
        "raw_block_materialize_seconds": materialize,
        "raw_block_forward_seconds": forward,
        "raw_full_pass_disk_read_bytes_per_block": full_reads,
        "raw_materialize_disk_read_bytes_per_block": materialize_reads,
    }


def safe_ratio(num: float, den: float) -> float | None:
    return num / den if den != 0 else None


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    h16_path = repo / SOURCE_H16_PATH
    h24_path = repo / SOURCE_H24_PATH
    observed_h16 = git_blob(h16_path, repo)
    observed_h24 = git_blob(h24_path, repo)

    print("LOOM Stretch 020 — Balanced M5 H16 vs H24 Hotset Comparison")
    print(f"Stretch 019 H16 helper blob: {observed_h16}")
    print(f"Stretch 020 H24 helper blob: {observed_h24}")
    if observed_h16 != SOURCE_H16_BLOB or observed_h24 != SOURCE_H24_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Balanced run order: H16 -> H24 -> H24 -> H16")
    print("Frozen exact oracle block size: M=5")
    print("Scientific factor: persistent transformer layers 16 -> 24 ONLY")
    print("Deliberate cache purge: NONE")
    print("Runtime/model/quantization/KV/parity/I-O/safety policy: inherited unchanged")
    print("Each constituent run must independently PASS all inherited gates")

    root = repo / "results-local" / "stretch" / "m5-h16-h24-balanced-hotset-comparison-020"
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 020 — Balanced M5 H16 vs H24 Hotset Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "source_provenance": {
            "h16_path": str(SOURCE_H16_PATH),
            "h16_expected_blob": SOURCE_H16_BLOB,
            "h16_observed_blob": observed_h16,
            "h24_path": str(SOURCE_H24_PATH),
            "h24_expected_blob": SOURCE_H24_BLOB,
            "h24_observed_blob": observed_h24,
        },
        "run_order": RUN_ORDER,
        "oracle_block_size": 5,
        "scientific_factor": "persistent transformer hotset H16 -> H24 only",
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    save()
    scripts = {"H16": h16_path, "H24": h24_path}

    for index, variant in enumerate(RUN_ORDER, start=1):
        script = scripts[variant]
        stdout_path = run_dir / f"attempt-{index}-{variant.lower()}-stdout.txt"
        stderr_path = run_dir / f"attempt-{index}-{variant.lower()}-stderr.txt"
        print(f"Attempt {index}/4: {variant} via {script.name}")
        started = time.perf_counter()
        with stdout_path.open("w", encoding="utf-8") as out_handle, stderr_path.open("w", encoding="utf-8") as err_handle:
            proc = subprocess.run(
                [sys.executable, str(script)],
                cwd=repo,
                stdout=out_handle,
                stderr=err_handle,
                text=True,
                check=False,
            )
        wall = time.perf_counter() - started
        stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
        child_summary_path = parse_summary_path(stdout_text)
        attempt: dict = {
            "attempt": index,
            "variant": variant,
            "returncode": proc.returncode,
            "wrapper_wall_seconds": wall,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "child_summary_path": str(child_summary_path) if child_summary_path else None,
        }

        if child_summary_path is None or not child_summary_path.is_file():
            attempt["usable"] = False
            attempt["failure_reason"] = "constituent summary path missing"
            summary["attempts"].append(attempt)
            summary["classification"] = "HOTSET_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = f"attempt {index} {variant}: summary missing"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 3

        child = json.loads(child_summary_path.read_text(encoding="utf-8"))
        classification = child.get("classification")
        hotset = child.get("hotset") or {}
        hybrid = child.get("hybrid_weight_residency") or {}
        ob = child.get("oracle_block_verification") or {}
        ioa = child.get("io_attribution") or {}
        telemetry = child.get("telemetry") or {}
        observed_ids = [int(x) for x in hotset.get("layer_ids", [])]
        expected_ids = EXPECTED_HOTSET_IDS[variant]

        attempt.update({
            "classification": classification,
            "hotset_layer_ids": observed_ids,
            "persistent_hotset_bytes": hybrid.get("persistent_hotset_bytes", hotset.get("materialized_delta_bytes")),
            "hybrid_raw_weight_budget_bytes": hybrid.get("max_simultaneous_raw_weight_budget_bytes"),
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_oracle_tokens": ob.get("accepted_oracle_tokens"),
            "total_target_block_wall_seconds": ob.get("total_target_block_wall_seconds"),
            "oracle_target_verification_tokens_per_second": ob.get("oracle_target_verification_tokens_per_second"),
            "block_full_pass_seconds": ob.get("block_full_pass_seconds") or [],
            "block_materialize_seconds": ob.get("block_materialize_seconds") or [],
            "block_forward_seconds": ob.get("block_forward_seconds") or [],
            "full_pass_disk_read_bytes_per_block": ioa.get("full_pass_disk_read_bytes_per_block") or [],
            "materialize_disk_read_bytes_per_block": ioa.get("materialize_disk_read_bytes_per_block") or [],
            "min_memory_free_percent": telemetry.get("min_memory_free_percent"),
            "peak_swap_used_mb": telemetry.get("peak_swap_used_mb"),
        })

        attempt["usable"] = (
            proc.returncode == 0
            and classification == EXPECTED_CLASSIFICATION
            and observed_ids == expected_ids
            and int(ob.get("oracle_block_size", -1)) == 5
            and int(ob.get("accepted_oracle_tokens", -1)) == 15
            and attempt["persistent_hotset_bytes"] is not None
            and attempt["hybrid_raw_weight_budget_bytes"] is not None
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            summary["classification"] = "HOTSET_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = (
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"returncode={proc.returncode}, classification={classification}, "
                f"hotset_ids={observed_ids}"
            )
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

    h16_records = [r for r in summary["attempts"] if r["variant"] == "H16"]
    h24_records = [r for r in summary["attempts"] if r["variant"] == "H24"]
    h16 = aggregate_variant(h16_records)
    h24 = aggregate_variant(h24_records)

    comparison = {
        "h16": h16,
        "h24": h24,
        "h24_over_h16_pooled_target_rate_ratio": safe_ratio(
            h24["pooled_target_verification_tokens_per_second"],
            h16["pooled_target_verification_tokens_per_second"],
        ),
        "h24_over_h16_median_block_wall_ratio": safe_ratio(
            h24["median_block_full_pass_seconds"], h16["median_block_full_pass_seconds"]
        ),
        "h24_over_h16_median_materialize_ratio": safe_ratio(
            h24["median_block_materialize_seconds"], h16["median_block_materialize_seconds"]
        ),
        "h24_over_h16_median_forward_ratio": safe_ratio(
            h24["median_block_forward_seconds"], h16["median_block_forward_seconds"]
        ),
        "h24_over_h16_mean_full_pass_read_bytes_per_block_ratio": safe_ratio(
            h24["mean_full_pass_disk_read_bytes_per_block"], h16["mean_full_pass_disk_read_bytes_per_block"]
        ),
        "h24_over_h16_mean_materialize_read_bytes_per_block_ratio": safe_ratio(
            h24["mean_materialize_disk_read_bytes_per_block"], h16["mean_materialize_disk_read_bytes_per_block"]
        ),
        "h24_over_h16_hotset_bytes_ratio": safe_ratio(
            h24["persistent_hotset_bytes"], h16["persistent_hotset_bytes"]
        ),
    }
    comparison["observed_higher_pooled_target_rate"] = (
        "H24"
        if h24["pooled_target_verification_tokens_per_second"] > h16["pooled_target_verification_tokens_per_second"]
        else "H16"
    )

    summary["comparison"] = comparison
    summary["classification"] = "M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: M5_H16_H24_BALANCED_HOTSET_COMPARISON_PASS")
    print(f"H16 pooled target-verification tok/s: {h16['pooled_target_verification_tokens_per_second']}")
    print(f"H24 pooled target-verification tok/s: {h24['pooled_target_verification_tokens_per_second']}")
    print(f"H24/H16 target-rate ratio: {comparison['h24_over_h16_pooled_target_rate_ratio']}")
    print(f"H16 median block wall: {h16['median_block_full_pass_seconds']} s")
    print(f"H24 median block wall: {h24['median_block_full_pass_seconds']} s")
    print(f"H24/H16 median materialize ratio: {comparison['h24_over_h16_median_materialize_ratio']}")
    print(f"H24/H16 median forward ratio: {comparison['h24_over_h16_median_forward_ratio']}")
    print(f"H24/H16 mean full-pass process-read bytes/block ratio: {comparison['h24_over_h16_mean_full_pass_read_bytes_per_block_ratio']}")
    print(f"H16 persistent hotset bytes: {h16['persistent_hotset_bytes']}")
    print(f"H24 persistent hotset bytes: {h24['persistent_hotset_bytes']}")
    print(f"H16 hybrid raw-weight budget bytes: {h16['hybrid_raw_weight_budget_bytes']}")
    print(f"H24 hybrid raw-weight budget bytes: {h24['hybrid_raw_weight_budget_bytes']}")
    print(f"H16 minimum observed free memory: {h16['minimum_observed_free_memory_percent']}%")
    print(f"H24 minimum observed free memory: {h24['minimum_observed_free_memory_percent']}%")
    print(f"H16 peak observed swap: {h16['peak_observed_swap_mb']} MB")
    print(f"H24 peak observed swap: {h24['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
