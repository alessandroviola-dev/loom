#!/usr/bin/env python3
"""LOOM Stretch 023 — balanced H36 shared-streamed vs shared-persistent comparison.

Runs the frozen exact M=5/H36 target path in balanced ABBA order. The only
scientific factor is whether embedding, final RMSNorm, and LM head remain
streamed per pass or are materialized once and retained persistently.
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

SOURCE_STREAMED_PATH = Path("scripts/stretch_five_token_h36_hotset_variant_022.py")
SOURCE_STREAMED_BLOB = "9111dde483206a774a9fe5426522dab6e77cecca"
SOURCE_PERSISTENT_PATH = Path("scripts/stretch_five_token_h36_full_weight_persistent_variant_023.py")
SOURCE_PERSISTENT_BLOB = "8c263e7be15441581e481e6f41cbd16f87d4df4b"
EXPECTED_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_HOTSET_BYTES = 3_039_381_504
EXPECTED_SHARED_BYTES = 544_546_816
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
RUN_ORDER = ["STREAMED", "PERSISTENT", "PERSISTENT", "STREAMED"]
SHARED_STAGE_NAMES = ("embedding", "norm", "head")


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


def flatten(records: list[dict], key: str) -> list[float]:
    values: list[float] = []
    for record in records:
        values.extend(float(v) for v in record.get(key, []))
    return values


def extract_shared_pass_metrics(child: dict) -> tuple[list[float], list[float], list[float]]:
    stream = child.get("stream") or {}
    block_records = stream.get("tokens") or []
    shared_materialize: list[float] = []
    shared_forward: list[float] = []
    shared_materialize_reads: list[float] = []
    for record in block_records:
        pass_record = record.get("pass") or {}
        stages = pass_record.get("stages") or {}
        if any(name not in stages for name in SHARED_STAGE_NAMES):
            raise RuntimeError(f"missing shared stage record in target block: {sorted(stages)}")
        shared_materialize.append(
            sum(float(stages[name].get("materialize_wall_seconds", 0.0)) for name in SHARED_STAGE_NAMES)
        )
        shared_forward.append(
            sum(float(stages[name].get("forward_wall_seconds", 0.0)) for name in SHARED_STAGE_NAMES)
        )
        shared_materialize_reads.append(
            sum(
                float((stages[name].get("io_materialize_delta") or {}).get("disk_read_bytes", 0.0))
                for name in SHARED_STAGE_NAMES
            )
        )
    return shared_materialize, shared_forward, shared_materialize_reads


def aggregate(records: list[dict]) -> dict:
    accepted = sum(int(r["accepted_oracle_tokens"]) for r in records)
    total_wall = sum(float(r["total_target_block_wall_seconds"]) for r in records)
    full = flatten(records, "block_full_pass_seconds")
    transformer_materialize = flatten(records, "block_transformer_materialize_seconds")
    transformer_forward = flatten(records, "block_transformer_forward_seconds")
    shared_materialize = flatten(records, "block_shared_materialize_seconds")
    shared_forward = flatten(records, "block_shared_forward_seconds")
    full_reads = flatten(records, "full_pass_disk_read_bytes_per_block")
    shared_materialize_reads = flatten(records, "shared_materialize_disk_read_bytes_per_block")
    persistent_raw = [int(r["persistent_raw_weight_bytes"]) for r in records]
    min_free = [
        int(r["min_memory_free_percent"])
        for r in records
        if r.get("min_memory_free_percent") is not None
    ]
    peak_swap = [
        float(r["peak_swap_used_mb"])
        for r in records
        if r.get("peak_swap_used_mb") is not None
    ]
    setup_walls = [
        float(r["one_time_shared_setup_wall_seconds"])
        for r in records
        if r.get("one_time_shared_setup_wall_seconds") is not None
    ]
    return {
        "runs": len(records),
        "accepted_oracle_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "block_samples": len(full),
        "mean_block_full_pass_seconds": statistics.mean(full),
        "median_block_full_pass_seconds": statistics.median(full),
        "mean_block_transformer_materialize_seconds": statistics.mean(transformer_materialize),
        "median_block_transformer_materialize_seconds": statistics.median(transformer_materialize),
        "mean_block_transformer_forward_seconds": statistics.mean(transformer_forward),
        "median_block_transformer_forward_seconds": statistics.median(transformer_forward),
        "mean_block_shared_materialize_seconds": statistics.mean(shared_materialize),
        "median_block_shared_materialize_seconds": statistics.median(shared_materialize),
        "mean_block_shared_forward_seconds": statistics.mean(shared_forward),
        "median_block_shared_forward_seconds": statistics.median(shared_forward),
        "mean_full_pass_disk_read_bytes_per_block": statistics.mean(full_reads),
        "mean_shared_materialize_disk_read_bytes_per_block": statistics.mean(shared_materialize_reads),
        "persistent_raw_weight_bytes": statistics.median(persistent_raw),
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
        "mean_one_time_shared_setup_wall_seconds": statistics.mean(setup_walls) if setup_walls else None,
        "raw_block_full_pass_seconds": full,
        "raw_block_transformer_materialize_seconds": transformer_materialize,
        "raw_block_transformer_forward_seconds": transformer_forward,
        "raw_block_shared_materialize_seconds": shared_materialize,
        "raw_block_shared_forward_seconds": shared_forward,
        "raw_full_pass_disk_read_bytes_per_block": full_reads,
        "raw_shared_materialize_disk_read_bytes_per_block": shared_materialize_reads,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    streamed_path = repo / SOURCE_STREAMED_PATH
    persistent_path = repo / SOURCE_PERSISTENT_PATH
    observed_streamed = git_blob(streamed_path, repo)
    observed_persistent = git_blob(persistent_path, repo)

    print("LOOM Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison")
    print(f"H36 shared-streamed blob: {observed_streamed}")
    print(f"H36 shared-persistent blob: {observed_persistent}")
    if observed_streamed != SOURCE_STREAMED_BLOB or observed_persistent != SOURCE_PERSISTENT_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    print("Source provenance: PASS")
    print("Balanced run order: STREAMED -> PERSISTENT -> PERSISTENT -> STREAMED")
    print("Frozen exact oracle block size: M=5")
    print("Frozen transformer residency: H36")
    print("Scientific factor: embedding + final norm + LM head streamed -> persistent ONLY")
    print("Persistent one-time shared setup is reported separately from steady-state target rate")
    print("Deliberate cache purge: NONE")
    print("Runtime/model/quantization/KV/parity/I-O/safety policy: inherited unchanged")

    root = repo / "results-local" / "stretch" / "m5-h36-shared-stage-persistence-023"
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"

    summary: dict = {
        "experiment": "Stretch 023 — Balanced H36 Shared-Stage Persistence Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "source_provenance": {
            "streamed_path": str(SOURCE_STREAMED_PATH),
            "streamed_expected_blob": SOURCE_STREAMED_BLOB,
            "streamed_observed_blob": observed_streamed,
            "persistent_path": str(SOURCE_PERSISTENT_PATH),
            "persistent_expected_blob": SOURCE_PERSISTENT_BLOB,
            "persistent_observed_blob": observed_persistent,
        },
        "run_order": RUN_ORDER,
        "oracle_block_size": 5,
        "transformer_hotset": "H36 layers 0..35",
        "scientific_factor": "shared embedding/norm/head streamed per pass -> persistent once",
        "steady_state_rate_excludes_one_time_shared_setup": True,
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    save()
    scripts = {"STREAMED": streamed_path, "PERSISTENT": persistent_path}

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
        wrapper_wall = time.perf_counter() - started
        stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
        child_summary_path = parse_summary_path(stdout_text)
        attempt: dict = {
            "attempt": index,
            "variant": variant,
            "returncode": proc.returncode,
            "wrapper_wall_seconds": wrapper_wall,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "child_summary_path": str(child_summary_path) if child_summary_path else None,
        }

        if child_summary_path is None or not child_summary_path.is_file():
            attempt["usable"] = False
            attempt["failure_reason"] = "constituent summary path missing"
            summary["attempts"].append(attempt)
            summary["classification"] = "SHARED_STAGE_COMPARISON_INCOMPLETE"
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
        full_weight = child.get("full_weight_persistence") or {}
        ob = child.get("oracle_block_verification") or {}
        ioa = child.get("io_attribution") or {}
        telemetry = child.get("telemetry") or {}
        observed_ids = [int(x) for x in hotset.get("layer_ids", [])]

        try:
            shared_materialize, shared_forward, shared_reads = extract_shared_pass_metrics(child)
        except Exception as exc:
            attempt["usable"] = False
            attempt["failure_reason"] = f"shared-stage metric extraction failed: {type(exc).__name__}: {exc}"
            summary["attempts"].append(attempt)
            summary["classification"] = "SHARED_STAGE_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = f"attempt {index} {variant}: {attempt['failure_reason']}"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 4

        if variant == "STREAMED":
            persistent_raw = hybrid.get("persistent_hotset_bytes", hotset.get("materialized_delta_bytes"))
            shared_mode_ok = not bool(child.get("shared_persistence")) and not bool(full_weight)
            one_time_setup = None
        else:
            persistent_raw = full_weight.get("persistent_total_raw_weight_bytes")
            shared = child.get("shared_persistence") or {}
            shared_mode_ok = (
                list(shared.get("stage_names", [])) == list(SHARED_STAGE_NAMES)
                and int(shared.get("expected_payload_bytes", -1)) == EXPECTED_SHARED_BYTES
                and int(full_weight.get("expected_total_weight_bytes", -1)) == EXPECTED_TOTAL_WEIGHT_BYTES
                and persistent_raw is not None
                and abs(int(persistent_raw) - EXPECTED_TOTAL_WEIGHT_BYTES) <= 24 * 1024 * 1024
            )
            one_time_setup = full_weight.get("one_time_shared_setup_wall_seconds")

        attempt.update({
            "classification": classification,
            "hotset_layer_ids": observed_ids,
            "persistent_raw_weight_bytes": persistent_raw,
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_oracle_tokens": ob.get("accepted_oracle_tokens"),
            "total_target_block_wall_seconds": ob.get("total_target_block_wall_seconds"),
            "oracle_target_verification_tokens_per_second": ob.get("oracle_target_verification_tokens_per_second"),
            "block_full_pass_seconds": ob.get("block_full_pass_seconds") or [],
            "block_transformer_materialize_seconds": ob.get("block_materialize_seconds") or [],
            "block_transformer_forward_seconds": ob.get("block_forward_seconds") or [],
            "block_shared_materialize_seconds": shared_materialize,
            "block_shared_forward_seconds": shared_forward,
            "full_pass_disk_read_bytes_per_block": ioa.get("full_pass_disk_read_bytes_per_block") or [],
            "shared_materialize_disk_read_bytes_per_block": shared_reads,
            "one_time_shared_setup_wall_seconds": one_time_setup,
            "min_memory_free_percent": telemetry.get("min_memory_free_percent"),
            "peak_swap_used_mb": telemetry.get("peak_swap_used_mb"),
            "shared_mode_ok": shared_mode_ok,
        })

        attempt["usable"] = (
            proc.returncode == 0
            and classification == EXPECTED_CLASSIFICATION
            and observed_ids == EXPECTED_HOTSET_IDS
            and int(ob.get("oracle_block_size", -1)) == 5
            and int(ob.get("accepted_oracle_tokens", -1)) == 15
            and persistent_raw is not None
            and shared_mode_ok
            and len(shared_materialize) == 3
            and len(shared_forward) == 3
            and len(shared_reads) == 3
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            summary["classification"] = "SHARED_STAGE_COMPARISON_INCOMPLETE"
            summary["failure_reason"] = (
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"returncode={proc.returncode}, classification={classification}, "
                f"hotset_ids={observed_ids}, shared_mode_ok={shared_mode_ok}"
            )
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(summary["failure_reason"], file=sys.stderr)
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 5

    streamed_records = [r for r in summary["attempts"] if r["variant"] == "STREAMED"]
    persistent_records = [r for r in summary["attempts"] if r["variant"] == "PERSISTENT"]
    streamed = aggregate(streamed_records)
    persistent = aggregate(persistent_records)

    comparison = {
        "streamed": streamed,
        "persistent": persistent,
        "persistent_over_streamed_pooled_target_rate_ratio": safe_ratio(
            persistent["pooled_target_verification_tokens_per_second"],
            streamed["pooled_target_verification_tokens_per_second"],
        ),
        "persistent_over_streamed_median_block_wall_ratio": safe_ratio(
            persistent["median_block_full_pass_seconds"], streamed["median_block_full_pass_seconds"]
        ),
        "persistent_over_streamed_median_shared_materialize_ratio": safe_ratio(
            persistent["median_block_shared_materialize_seconds"],
            streamed["median_block_shared_materialize_seconds"],
        ),
        "persistent_over_streamed_median_shared_forward_ratio": safe_ratio(
            persistent["median_block_shared_forward_seconds"],
            streamed["median_block_shared_forward_seconds"],
        ),
        "persistent_over_streamed_mean_full_pass_read_bytes_per_block_ratio": safe_ratio(
            persistent["mean_full_pass_disk_read_bytes_per_block"],
            streamed["mean_full_pass_disk_read_bytes_per_block"],
        ),
        "persistent_over_streamed_mean_shared_materialize_read_bytes_per_block_ratio": safe_ratio(
            persistent["mean_shared_materialize_disk_read_bytes_per_block"],
            streamed["mean_shared_materialize_disk_read_bytes_per_block"],
        ),
        "persistent_raw_weight_bytes_ratio": safe_ratio(
            persistent["persistent_raw_weight_bytes"], streamed["persistent_raw_weight_bytes"]
        ),
    }
    mean_saved_block_wall = (
        streamed["mean_block_full_pass_seconds"] - persistent["mean_block_full_pass_seconds"]
    )
    setup = persistent.get("mean_one_time_shared_setup_wall_seconds")
    comparison["estimated_shared_setup_break_even_target_blocks"] = (
        setup / mean_saved_block_wall
        if setup is not None and mean_saved_block_wall > 0
        else None
    )
    comparison["observed_higher_pooled_target_rate"] = (
        "PERSISTENT"
        if persistent["pooled_target_verification_tokens_per_second"]
        > streamed["pooled_target_verification_tokens_per_second"]
        else "STREAMED"
    )

    summary["comparison"] = comparison
    summary["classification"] = "M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: M5_H36_SHARED_STAGE_BALANCED_COMPARISON_PASS")
    print(f"STREAMED pooled target-verification tok/s: {streamed['pooled_target_verification_tokens_per_second']}")
    print(f"PERSISTENT pooled target-verification tok/s: {persistent['pooled_target_verification_tokens_per_second']}")
    print(f"PERSISTENT/STREAMED target-rate ratio: {comparison['persistent_over_streamed_pooled_target_rate_ratio']}")
    print(f"STREAMED median block wall: {streamed['median_block_full_pass_seconds']} s")
    print(f"PERSISTENT median block wall: {persistent['median_block_full_pass_seconds']} s")
    print(f"PERSISTENT/STREAMED median shared-materialize ratio: {comparison['persistent_over_streamed_median_shared_materialize_ratio']}")
    print(f"PERSISTENT/STREAMED median shared-forward ratio: {comparison['persistent_over_streamed_median_shared_forward_ratio']}")
    print(f"PERSISTENT/STREAMED mean full-pass process-read bytes/block ratio: {comparison['persistent_over_streamed_mean_full_pass_read_bytes_per_block_ratio']}")
    print(f"PERSISTENT/STREAMED shared-materialize process-read ratio: {comparison['persistent_over_streamed_mean_shared_materialize_read_bytes_per_block_ratio']}")
    print(f"STREAMED persistent raw-weight bytes: {streamed['persistent_raw_weight_bytes']}")
    print(f"PERSISTENT persistent raw-weight bytes: {persistent['persistent_raw_weight_bytes']}")
    print(f"PERSISTENT one-time shared setup wall mean: {persistent['mean_one_time_shared_setup_wall_seconds']} s")
    print(f"Estimated shared-setup break-even target blocks: {comparison['estimated_shared_setup_break_even_target_blocks']}")
    print(f"STREAMED minimum observed free memory: {streamed['minimum_observed_free_memory_percent']}%")
    print(f"PERSISTENT minimum observed free memory: {persistent['minimum_observed_free_memory_percent']}%")
    print(f"STREAMED peak observed swap: {streamed['peak_observed_swap_mb']} MB")
    print(f"PERSISTENT peak observed swap: {persistent['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
