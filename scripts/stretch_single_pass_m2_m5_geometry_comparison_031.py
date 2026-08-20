#!/usr/bin/env python3
"""LOOM Stretch 031 — balanced M2 vs M5 SINGLE_PASS geometry comparison."""
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

SOURCE_M5_PATH = Path("scripts/stretch_single_pass_m5_ten_token_control_031.py")
SOURCE_M5_BLOB = "5f047b9e5f42bed959ced59e9329a8c8d7e3fc25"
SOURCE_M2_PATH = Path("scripts/stretch_single_pass_m2_ten_token_variant_031.py")
SOURCE_M2_BLOB = "6005ff3a285760457d3255bc6505f2987c1fa4e8"
EXPECTED_CLASSIFICATION = {
    "M5": "SINGLE_PASS_M5_TEN_TOKEN_GEOMETRY_PASS",
    "M2": "SINGLE_PASS_M2_TEN_TOKEN_GEOMETRY_PASS",
}
EXPECTED_BLOCK_SIZE = {"M5": 5, "M2": 2}
EXPECTED_BLOCK_COUNT = {"M5": 2, "M2": 5}
EXPECTED_ACCEPTED_TOKENS = 10
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
RUN_ORDER = ["M5", "M2", "M2", "M5"]

SCIENTIFIC_FAIL_CLASSES = {
    "PROMPT_KV_NUMERICAL_PARITY_FAIL",
    "GENERATED_TOKEN_MISMATCH",
    "ORACLE_SEQUENCE_PROVENANCE_FAIL",
    "ORACLE_BLOCK_NUMERICAL_PARITY_FAIL",
    "ORACLE_BLOCK_TOP1_MISMATCH",
    "ORACLE_TOKEN_REJECTED",
    "GENERATED_SEQUENCE_MISMATCH",
}


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
    return num / den if den else None


def aggregate(records: list[dict]) -> dict:
    accepted = sum(int(r["accepted_tokens"]) for r in records)
    total_wall = sum(float(r["total_block_wall"]) for r in records)
    block_walls = [float(v) for r in records for v in r["block_walls"]]
    final_cleanup = [float(v) for r in records for v in r.get("final_cleanup_walls", [])]
    min_free = [int(r["min_free"]) for r in records if r.get("min_free") is not None]
    peak_swap = [float(r["peak_swap"]) for r in records if r.get("peak_swap") is not None]
    return {
        "runs": len(records),
        "oracle_block_size": int(records[0]["oracle_block_size"]),
        "accepted_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "wall_seconds_per_accepted_token": total_wall / accepted,
        "mean_block_wall_seconds": statistics.mean(block_walls),
        "median_block_wall_seconds": statistics.median(block_walls),
        "mean_final_cleanup_wall_seconds_per_block": statistics.mean(final_cleanup) if final_cleanup else None,
        "final_cleanup_wall_seconds_per_accepted_token": (
            sum(final_cleanup) / accepted if final_cleanup else None
        ),
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
        "raw_block_walls": block_walls,
        "raw_final_cleanup_walls": final_cleanup,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    m5_path = repo / SOURCE_M5_PATH
    m2_path = repo / SOURCE_M2_PATH
    observed_m5 = git_blob(m5_path, repo)
    observed_m2 = git_blob(m2_path, repo)

    print("LOOM Stretch 031 — Balanced M2 vs M5 SINGLE_PASS Geometry Comparison")
    print(f"M5 control blob: {observed_m5}")
    print(f"M2 treatment blob: {observed_m2}")
    if observed_m5 != SOURCE_M5_BLOB or observed_m2 != SOURCE_M2_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Balanced run order: M5 -> M2 -> M2 -> M5")
    print("Identical frozen oracle prefix depth: 10 accepted tokens per constituent")
    print("M5 geometry: 2 blocks x 5 tokens")
    print("M2 geometry: 5 blocks x 2 tokens")
    print("Frozen architecture: H36 + full persistence + one final cleanup/pass + MLX 0.31.2")
    print("Scientific factor: target oracle block size M5 -> M2 ONLY")
    print("Model / quantization / KV / exactness / I-O / resource policy: UNCHANGED")
    print("Deliberate cache purge: NONE")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "single-pass-m2-m5-geometry-comparison-031" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"
    summary: dict = {
        "experiment": "Stretch 031 — Balanced M2 vs M5 SINGLE_PASS Geometry Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "scientific_factor": "oracle target block size M5 -> M2 only at common ten-token continuation depth",
        "source_provenance": {
            "m5_path": str(SOURCE_M5_PATH),
            "m5_blob": observed_m5,
            "m2_path": str(SOURCE_M2_PATH),
            "m2_blob": observed_m2,
        },
        "frozen_architecture": "Qwen3-8B 3bit/group64; H36; full raw-weight persistence; one final cleanup/pass; MLX 0.31.2; BF16 KV",
        "common_oracle_tokens_per_constituent": EXPECTED_ACCEPTED_TOKENS,
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    def finish_incomplete(reason: str, code: int) -> int:
        summary["classification"] = "SINGLE_PASS_M2_M5_GEOMETRY_COMPARISON_INCOMPLETE"
        summary["failure_reason"] = reason
        summary["disk_free_after_gib"] = gib_free(repo)
        save()
        print(f"Classification: {summary['classification']}", file=sys.stderr)
        print(f"Failure reason: {reason}", file=sys.stderr)
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    save()
    scripts = {"M5": m5_path, "M2": m2_path}

    for index, variant in enumerate(RUN_ORDER, start=1):
        script = scripts[variant]
        out_path = run_dir / f"attempt-{index}-{variant.lower()}-stdout.txt"
        err_path = run_dir / f"attempt-{index}-{variant.lower()}-stderr.txt"
        print(f"Attempt {index}/4: {variant} via {script.name}")
        started = time.perf_counter()
        with out_path.open("w", encoding="utf-8") as out, err_path.open("w", encoding="utf-8") as err:
            proc = subprocess.run(
                [sys.executable, str(script)], cwd=repo,
                stdout=out, stderr=err, text=True, check=False,
            )
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
            save()
            return finish_incomplete(f"attempt {index} {variant}: summary missing", 3)

        child = json.loads(child_summary_path.read_text(encoding="utf-8"))
        child_class = child.get("classification")
        attempt["classification"] = child_class
        attempt["failure_reason"] = child.get("failure_reason")

        if variant == "M2" and child_class in SCIENTIFIC_FAIL_CLASSES:
            attempt["usable"] = False
            attempt["scientific_geometry_failure"] = True
            attempt["prompt_parity"] = child.get("prompt_parity")
            attempt["step_parities"] = child.get("step_parities")
            summary["attempts"].append(attempt)
            summary["classification"] = "M2_SINGLE_PASS_GEOMETRY_EXACTNESS_FAIL"
            summary["failure_reason"] = (
                f"attempt {index} M2 produced valid frozen-gate failure: "
                f"{child_class}: {child.get('failure_reason')}"
            )
            summary["scientific_result"] = "M2_NOT_ADMISSIBLE_UNDER_FROZEN_EXACTNESS_GATES"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print(f"Classification: {summary['classification']}")
            print(f"Underlying child classification: {child_class}")
            print(f"Failure reason: {child.get('failure_reason')}")
            print("Scientific result: M2 not admissible under frozen gates; no retry/rescue")
            print(f"Run directory: {run_dir}")
            print(f"Summary: {summary_path}")
            return 0

        hotset = child.get("hotset") or {}
        full = child.get("full_weight_persistence") or {}
        ob = child.get("oracle_block_verification") or {}
        telemetry = child.get("telemetry") or {}
        observed_ids = [int(x) for x in hotset.get("layer_ids", [])]
        persistent_total = full.get("persistent_total_raw_weight_bytes")

        final_cleanup_walls: list[float] = []
        cleanup_mode_ok = True
        stream_records = (child.get("stream") or {}).get("tokens") or []
        for record in stream_records:
            stages = (record.get("pass") or {}).get("stages") or {}
            if stages.get("transformer_body_cleanup") is not None:
                cleanup_mode_ok = False
                break
            final = stages.get("shared_stage_cleanup")
            if not isinstance(final, dict) or final.get("policy") != "single_cleanup_after_full_pass":
                cleanup_mode_ok = False
                break
            final_cleanup_walls.append(float(final.get("wall_seconds", -1.0)))

        attempt.update({
            "hotset_layer_ids": observed_ids,
            "persistent_total_raw_weight_bytes": persistent_total,
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_tokens": ob.get("accepted_oracle_tokens"),
            "total_block_wall": ob.get("total_target_block_wall_seconds"),
            "block_walls": ob.get("block_full_pass_seconds") or [],
            "final_cleanup_walls": final_cleanup_walls,
            "cleanup_mode_ok": cleanup_mode_ok,
            "min_free": telemetry.get("min_memory_free_percent"),
            "peak_swap": telemetry.get("peak_swap_used_mb"),
        })

        expected_blocks = EXPECTED_BLOCK_COUNT[variant]
        attempt["usable"] = (
            proc.returncode == 0
            and child_class == EXPECTED_CLASSIFICATION[variant]
            and observed_ids == EXPECTED_HOTSET_IDS
            and persistent_total is not None
            and abs(int(persistent_total) - EXPECTED_TOTAL_WEIGHT_BYTES) <= 24 * 1024 * 1024
            and int(ob.get("oracle_block_size", -1)) == EXPECTED_BLOCK_SIZE[variant]
            and int(ob.get("accepted_oracle_tokens", -1)) == EXPECTED_ACCEPTED_TOKENS
            and len(ob.get("block_full_pass_seconds") or []) == expected_blocks
            and len(stream_records) == expected_blocks
            and cleanup_mode_ok
            and len(final_cleanup_walls) == expected_blocks
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            return finish_incomplete(
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"rc={proc.returncode}, class={child_class}, "
                f"block_size={ob.get('oracle_block_size')}, accepted={ob.get('accepted_oracle_tokens')}, "
                f"cleanup_mode_ok={cleanup_mode_ok}",
                4,
            )

    m5_records = [r for r in summary["attempts"] if r["variant"] == "M5"]
    m2_records = [r for r in summary["attempts"] if r["variant"] == "M2"]
    m5 = aggregate(m5_records)
    m2 = aggregate(m2_records)

    comparison = {
        "m5": m5,
        "m2": m2,
        "m2_over_m5_target_rate_ratio": safe_ratio(
            m2["pooled_target_verification_tokens_per_second"],
            m5["pooled_target_verification_tokens_per_second"],
        ),
        "m2_over_m5_wall_per_token_ratio": safe_ratio(
            m2["wall_seconds_per_accepted_token"], m5["wall_seconds_per_accepted_token"]
        ),
        "m2_over_m5_cleanup_per_token_ratio": safe_ratio(
            m2["final_cleanup_wall_seconds_per_accepted_token"],
            m5["final_cleanup_wall_seconds_per_accepted_token"],
        ),
        "observed_higher_pooled_target_rate": (
            "M2" if m2["pooled_target_verification_tokens_per_second"] > m5["pooled_target_verification_tokens_per_second"] else "M5"
        ),
    }
    summary["comparison"] = comparison
    summary["classification"] = "SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: SINGLE_PASS_M2_M5_BALANCED_GEOMETRY_COMPARISON_PASS")
    print(f"M5 pooled target-verification tok/s: {m5['pooled_target_verification_tokens_per_second']}")
    print(f"M2 pooled target-verification tok/s: {m2['pooled_target_verification_tokens_per_second']}")
    print(f"M2/M5 target-rate ratio: {comparison['m2_over_m5_target_rate_ratio']}")
    print(f"M5 wall seconds/accepted token: {m5['wall_seconds_per_accepted_token']}")
    print(f"M2 wall seconds/accepted token: {m2['wall_seconds_per_accepted_token']}")
    print(f"M2/M5 wall-per-token ratio: {comparison['m2_over_m5_wall_per_token_ratio']}")
    print(f"M5 median block wall: {m5['median_block_wall_seconds']} s")
    print(f"M2 median block wall: {m2['median_block_wall_seconds']} s")
    print(f"M5 final cleanup seconds/accepted token: {m5['final_cleanup_wall_seconds_per_accepted_token']}")
    print(f"M2 final cleanup seconds/accepted token: {m2['final_cleanup_wall_seconds_per_accepted_token']}")
    print(f"M2/M5 cleanup-per-token ratio: {comparison['m2_over_m5_cleanup_per_token_ratio']}")
    print(f"M5 minimum observed free memory: {m5['minimum_observed_free_memory_percent']}%")
    print(f"M2 minimum observed free memory: {m2['minimum_observed_free_memory_percent']}%")
    print(f"M5 peak swap: {m5['peak_observed_swap_mb']} MB")
    print(f"M2 peak swap: {m2['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
