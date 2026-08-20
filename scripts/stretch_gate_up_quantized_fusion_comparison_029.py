#!/usr/bin/env python3
"""LOOM Stretch 029 — balanced gate+up quantized fusion comparison."""
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
SOURCE_FUSED_PATH = Path("scripts/stretch_gate_up_quantized_fusion_029.py")
SOURCE_FUSED_BLOB = "c37ff6313106807c1e2e5070b7fb8f19e97abea6"
EXPECTED_PASS_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
RUN_ORDER = ["CONTROL", "FUSED", "FUSED", "CONTROL"]

# These are valid scientific outcomes for the FUSED treatment: they directly
# indicate that changing the quantized output geometry changed frozen target
# numerics/top-1/acceptance. They are not harness failures and are not retried.
FUSION_SCIENTIFIC_FAIL_CLASSES = {
    "PROMPT_KV_NUMERICAL_PARITY_FAIL",
    "GENERATED_TOKEN_MISMATCH",
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
        "accepted_tokens": accepted,
        "total_target_block_wall_seconds": total_wall,
        "pooled_target_verification_tokens_per_second": accepted / total_wall,
        "mean_block_wall_seconds": statistics.mean(block_walls),
        "median_block_wall_seconds": statistics.median(block_walls),
        "mean_final_cleanup_wall_seconds": statistics.mean(final_cleanup) if final_cleanup else None,
        "minimum_observed_free_memory_percent": min(min_free) if min_free else None,
        "peak_observed_swap_mb": max(peak_swap) if peak_swap else None,
        "raw_block_walls": block_walls,
        "raw_final_cleanup_walls": final_cleanup,
    }


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    control_path = repo / SOURCE_CONTROL_PATH
    fused_path = repo / SOURCE_FUSED_PATH
    observed_control = git_blob(control_path, repo)
    observed_fused = git_blob(fused_path, repo)

    print("LOOM Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison")
    print(f"CONTROL blob: {observed_control}")
    print(f"FUSED blob: {observed_fused}")
    if observed_control != SOURCE_CONTROL_BLOB or observed_fused != SOURCE_FUSED_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Balanced order: CONTROL -> FUSED -> FUSED -> CONTROL")
    print("Frozen architecture: M=5 + H36 + full persistence + one final cleanup/pass")
    print("Scientific factor: MLP gate+up 2 quantized matmuls -> 1 fused quantized matmul ONLY")
    print("First FUSED numerical/top1/acceptance failure is a valid scientific FAIL; no retry")
    print("Model / runtime / KV / parity thresholds / I-O / safety: UNCHANGED")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "gate-up-quantized-fusion-comparison-029" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"
    summary: dict = {
        "experiment": "Stretch 029 — Balanced Gate+Up Quantized Fusion Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "scientific_factor": "gate_proj + up_proj two quantized matmuls -> one fused quantized matmul",
        "source_provenance": {
            "control_path": str(SOURCE_CONTROL_PATH),
            "control_blob": observed_control,
            "fused_path": str(SOURCE_FUSED_PATH),
            "fused_blob": observed_fused,
        },
        "frozen_architecture": "M5 H36 full raw-weight persistence; single final cleanup; MLX 0.31.2",
        "scientific_failure_classes": sorted(FUSION_SCIENTIFIC_FAIL_CLASSES),
        "deliberate_cache_purge": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    def finish_incomplete(reason: str, code: int) -> int:
        summary["classification"] = "GATE_UP_QUANTIZED_FUSION_COMPARISON_INCOMPLETE"
        summary["failure_reason"] = reason
        summary["disk_free_after_gib"] = gib_free(repo)
        save()
        print(f"Classification: {summary['classification']}", file=sys.stderr)
        print(f"Failure reason: {reason}", file=sys.stderr)
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    save()
    scripts = {"CONTROL": control_path, "FUSED": fused_path}

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
            save()
            return finish_incomplete(f"attempt {index} {variant}: summary missing", 3)

        child = json.loads(child_summary_path.read_text(encoding="utf-8"))
        child_class = child.get("classification")
        attempt["classification"] = child_class
        attempt["failure_reason"] = child.get("failure_reason")

        # A FUSED numerical/top1/acceptance failure consumes the scientific test
        # and ends the experiment without rescue or completion of ABBA.
        if variant == "FUSED" and child_class in FUSION_SCIENTIFIC_FAIL_CLASSES:
            attempt["usable"] = False
            attempt["scientific_fusion_failure"] = True
            attempt["prompt_parity"] = child.get("prompt_parity")
            attempt["step_parities"] = child.get("step_parities")
            summary["attempts"].append(attempt)
            summary["classification"] = "GATE_UP_QUANTIZED_FUSION_NUMERICAL_PARITY_FAIL"
            summary["failure_reason"] = (
                f"attempt {index} FUSED produced valid scientific exactness failure: "
                f"{child_class}: {child.get('failure_reason')}"
            )
            summary["scientific_result"] = "FUSED_NOT_EXACT_UNDER_FROZEN_M5_GATES"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print("Classification: GATE_UP_QUANTIZED_FUSION_NUMERICAL_PARITY_FAIL")
            print(f"Underlying child classification: {child_class}")
            print(f"Failure reason: {child.get('failure_reason')}")
            print("Scientific result: FUSED is not exact under frozen M5 gates; no rescue variant")
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
        for record in (child.get("stream") or {}).get("tokens") or []:
            stages = (record.get("pass") or {}).get("stages") or {}
            if stages.get("transformer_body_cleanup") is not None:
                cleanup_mode_ok = False
                break
            final = stages.get("shared_stage_cleanup")
            if not isinstance(final, dict) or final.get("policy") != "single_cleanup_after_full_pass":
                cleanup_mode_ok = False
                break
            final_cleanup_walls.append(float(final.get("wall_seconds", -1.0)))

        fusion = child.get("gate_up_fusion") if variant == "FUSED" else None
        fusion_ok = True
        if variant == "FUSED":
            fusion = fusion or {}
            fusion_ids = [int(x) for x in fusion.get("layer_ids", [])]
            fusion_ok = (
                fusion.get("policy") == "single_quantized_matmul_gate_up"
                and fusion_ids == EXPECTED_HOTSET_IDS
                and int(fusion.get("layer_count", -1)) == 36
                and bool(fusion.get("all_payloads_equal"))
                and fusion.get("steady_state_duplicate_gate_up_modules") is False
                and int(fusion.get("group_size", -1)) == 64
                and int(fusion.get("bits", -1)) == 3
            )
        else:
            fusion_ok = fusion is None

        attempt.update({
            "hotset_layer_ids": observed_ids,
            "persistent_total_raw_weight_bytes": persistent_total,
            "oracle_block_size": ob.get("oracle_block_size"),
            "accepted_tokens": ob.get("accepted_oracle_tokens"),
            "total_block_wall": ob.get("total_target_block_wall_seconds"),
            "block_walls": ob.get("block_full_pass_seconds") or [],
            "final_cleanup_walls": final_cleanup_walls,
            "cleanup_mode_ok": cleanup_mode_ok,
            "gate_up_fusion": fusion,
            "fusion_ok": fusion_ok,
            "min_free": telemetry.get("min_memory_free_percent"),
            "peak_swap": telemetry.get("peak_swap_used_mb"),
        })

        attempt["usable"] = (
            proc.returncode == 0
            and child_class == EXPECTED_PASS_CLASSIFICATION
            and observed_ids == EXPECTED_HOTSET_IDS
            and persistent_total is not None
            and abs(int(persistent_total) - EXPECTED_TOTAL_WEIGHT_BYTES) <= 24 * 1024 * 1024
            and int(ob.get("oracle_block_size", -1)) == 5
            and int(ob.get("accepted_oracle_tokens", -1)) == 15
            and len(ob.get("block_full_pass_seconds") or []) == 3
            and cleanup_mode_ok
            and len(final_cleanup_walls) == 3
            and fusion_ok
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            return finish_incomplete(
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"rc={proc.returncode}, class={child_class}, cleanup_ok={cleanup_mode_ok}, fusion_ok={fusion_ok}",
                4,
            )

    control_records = [r for r in summary["attempts"] if r["variant"] == "CONTROL"]
    fused_records = [r for r in summary["attempts"] if r["variant"] == "FUSED"]
    control = aggregate(control_records)
    fused = aggregate(fused_records)
    comparison = {
        "control": control,
        "fused": fused,
        "fused_over_control_target_rate_ratio": safe_ratio(
            fused["pooled_target_verification_tokens_per_second"],
            control["pooled_target_verification_tokens_per_second"],
        ),
        "fused_over_control_median_block_wall_ratio": safe_ratio(
            fused["median_block_wall_seconds"], control["median_block_wall_seconds"]
        ),
        "observed_higher_pooled_target_rate": (
            "FUSED" if fused["pooled_target_verification_tokens_per_second"] > control["pooled_target_verification_tokens_per_second"] else "CONTROL"
        ),
    }
    summary["comparison"] = comparison
    summary["classification"] = "GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: GATE_UP_QUANTIZED_FUSION_BALANCED_COMPARISON_PASS")
    print(f"CONTROL pooled target-verification tok/s: {control['pooled_target_verification_tokens_per_second']}")
    print(f"FUSED pooled target-verification tok/s: {fused['pooled_target_verification_tokens_per_second']}")
    print(f"FUSED/CONTROL target-rate ratio: {comparison['fused_over_control_target_rate_ratio']}")
    print(f"CONTROL median block wall: {control['median_block_wall_seconds']} s")
    print(f"FUSED median block wall: {fused['median_block_wall_seconds']} s")
    print(f"FUSED/CONTROL median block-wall ratio: {comparison['fused_over_control_median_block_wall_ratio']}")
    print(f"CONTROL mean final cleanup wall: {control['mean_final_cleanup_wall_seconds']} s")
    print(f"FUSED mean final cleanup wall: {fused['mean_final_cleanup_wall_seconds']} s")
    print(f"CONTROL minimum free memory: {control['minimum_observed_free_memory_percent']}%")
    print(f"FUSED minimum free memory: {fused['minimum_observed_free_memory_percent']}%")
    print(f"CONTROL peak swap: {control['peak_observed_swap_mb']} MB")
    print(f"FUSED peak swap: {fused['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
