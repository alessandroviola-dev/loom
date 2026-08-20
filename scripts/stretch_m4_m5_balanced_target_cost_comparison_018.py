#!/usr/bin/env python3
"""LOOM Stretch 018 — balanced M4 vs M5 target-cost comparison.

Runs the already-frozen Stretch 013 (M=4) and Stretch 017 (M=5) harnesses in
balanced ABBA order and aggregates only their target-block/I-O metrics. No MLX,
model, quantization, KV, hotset, parity, or cache-purge policy is changed here.

This is a performance/I-O attribution experiment, not a new correctness path.
Each inherited run must independently pass its existing correctness and host
state gates before the comparison is considered scientifically complete.
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

SOURCE_M4_PATH = Path("scripts/stretch_four_token_oracle_block_verification_013.py")
SOURCE_M4_BLOB = "deeb0339294162f38cd4522d2890b6a0c728f96e"
SOURCE_M5_PATH = Path("scripts/stretch_five_token_oracle_block_confirmation_017.py")
SOURCE_M5_BLOB = "6171440736badf5150297f9c8945209fe49d0826"

EXPECTED_CLASSIFICATION = {
    "M4": "FOUR_TOKEN_ORACLE_BLOCK_VERIFICATION_PASS",
    "M5": "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS",
}

# Balanced order reduces first/last-run host-cache ordering bias without any
# deliberate cache purge. The inherited host-state gate still decides whether
# each constituent run is scientifically usable.
RUN_ORDER = ["M4", "M5", "M5", "M4"]


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
        "raw_block_full_pass_seconds": full,
        "raw_block_materialize_seconds": materialize,
        "raw_block_forward_seconds": forward,
        "raw_full_pass_disk_read_bytes_per_block": full_reads,
        "raw_materialize_disk_read_bytes_per_block": materialize_reads,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    m4_path = repo / SOURCE_M4_PATH
    m5_path = repo / SOURCE_M5_PATH

    observed_m4 = git_blob(m4_path, repo)
    observed_m5 = git_blob(m5_path, repo)

    print("LOOM Stretch 018 — Balanced M4 vs M5 Target-Cost Comparison")
    print(f"Stretch 013 M4 blob: {observed_m4}")
    print(f"Stretch 017 M5 blob: {observed_m5}")
    if observed_m4 != SOURCE_M4_BLOB or observed_m5 != SOURCE_M5_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Balanced run order: M4 -> M5 -> M5 -> M4")
    print("Deliberate cache purge: NONE")
    print("Runtime/model/quantization/KV/hotset/parity policy: inherited unchanged")
    print("Each constituent run must independently PASS its frozen host/correctness gates")

    root = repo / "results-local" / "stretch" / "m4-m5-balanced-target-cost-comparison-018"
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 018 — Balanced M4 vs M5 Target-Cost Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "source_provenance": {
            "m4_path": str(SOURCE_M4_PATH),
            "m4_expected_blob": SOURCE_M4_BLOB,
            "m4_observed_blob": observed_m4,
            "m5_path": str(SOURCE_M5_PATH),
            "m5_expected_blob": SOURCE_M5_BLOB,
            "m5_observed_blob": observed_m5,
        },
        "run_order": RUN_ORDER,
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    save()

    scripts = {
        "M4": m4_path,
        "M5": m5_path,
    }

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
            summary["classification"] = "CONTROLLED_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = f"attempt {index} {variant}: summary missing"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 3

        child = json.loads(child_summary_path.read_text(encoding="utf-8"))
        classification = child.get("classification")
        attempt["classification"] = classification
        attempt["usable"] = classification == EXPECTED_CLASSIFICATION[variant]
        attempt["telemetry"] = child.get("telemetry")

        ob = child.get("oracle_block_verification") or {}
        ioa = child.get("io_attribution") or {}
        attempt.update({
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_oracle_tokens": ob.get("accepted_oracle_tokens"),
            "total_target_block_wall_seconds": ob.get("total_target_block_wall_seconds"),
            "oracle_target_verification_tokens_per_second": ob.get("oracle_target_verification_tokens_per_second"),
            "block_full_pass_seconds": ob.get("block_full_pass_seconds") or [],
            "block_materialize_seconds": ob.get("block_materialize_seconds") or [],
            "block_forward_seconds": ob.get("block_forward_seconds") or [],
            "full_pass_disk_read_bytes_per_block": ioa.get("full_pass_disk_read_bytes_per_block") or [],
            "materialize_disk_read_bytes_per_block": ioa.get("materialize_disk_read_bytes_per_block") or [],
        })
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            summary["classification"] = "CONTROLLED_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = (
                f"attempt {index} {variant}: expected {EXPECTED_CLASSIFICATION[variant]}, "
                f"got {classification}"
            )
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

    m4_records = [r for r in summary["attempts"] if r["variant"] == "M4"]
    m5_records = [r for r in summary["attempts"] if r["variant"] == "M5"]
    m4 = aggregate_variant(m4_records)
    m5 = aggregate_variant(m5_records)

    comparison = {
        "m4": m4,
        "m5": m5,
        "m5_over_m4_pooled_target_rate_ratio": (
            m5["pooled_target_verification_tokens_per_second"]
            / m4["pooled_target_verification_tokens_per_second"]
        ),
        "m5_over_m4_median_block_wall_ratio": (
            m5["median_block_full_pass_seconds"] / m4["median_block_full_pass_seconds"]
        ),
        "m5_over_m4_median_materialize_ratio": (
            m5["median_block_materialize_seconds"] / m4["median_block_materialize_seconds"]
        ),
        "m5_over_m4_median_forward_ratio": (
            m5["median_block_forward_seconds"] / m4["median_block_forward_seconds"]
        ),
        "m5_over_m4_mean_full_pass_read_bytes_per_block_ratio": (
            m5["mean_full_pass_disk_read_bytes_per_block"]
            / m4["mean_full_pass_disk_read_bytes_per_block"]
        ),
        "m5_over_m4_mean_full_pass_read_bytes_per_token_ratio": (
            m5["mean_full_pass_disk_read_bytes_per_accepted_token"]
            / m4["mean_full_pass_disk_read_bytes_per_accepted_token"]
        ),
    }
    comparison["observed_higher_pooled_target_rate"] = (
        "M5"
        if m5["pooled_target_verification_tokens_per_second"] > m4["pooled_target_verification_tokens_per_second"]
        else "M4"
    )

    summary["comparison"] = comparison
    summary["classification"] = "M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: M4_M5_BALANCED_TARGET_COST_COMPARISON_PASS")
    print(f"M4 pooled target-verification tok/s: {m4['pooled_target_verification_tokens_per_second']}")
    print(f"M5 pooled target-verification tok/s: {m5['pooled_target_verification_tokens_per_second']}")
    print(f"M5/M4 target-rate ratio: {comparison['m5_over_m4_pooled_target_rate_ratio']}")
    print(f"M4 median block wall: {m4['median_block_full_pass_seconds']} s")
    print(f"M5 median block wall: {m5['median_block_full_pass_seconds']} s")
    print(f"M5/M4 median materialize ratio: {comparison['m5_over_m4_median_materialize_ratio']}")
    print(f"M5/M4 median forward ratio: {comparison['m5_over_m4_median_forward_ratio']}")
    print(
        "M5/M4 mean full-pass process-read bytes/block ratio: "
        f"{comparison['m5_over_m4_mean_full_pass_read_bytes_per_block_ratio']}"
    )
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
