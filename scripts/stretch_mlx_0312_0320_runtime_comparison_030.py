#!/usr/bin/env python3
"""LOOM Stretch 030 — balanced isolated MLX 0.31.2 vs 0.32.0 comparison.

The exact same canonical Stretch 027 workload source is executed under two Python
environments. The treatment venv inherits all canonical site packages and overlays
ONLY mlx==0.32.0. No environment provisioning occurs inside the scientific run.
"""
from __future__ import annotations

import importlib.metadata as md
import json
import re
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SOURCE_PATH = Path("scripts/stretch_full_persistent_single_pass_cleanup_027.py")
SOURCE_BLOB = "6636456df5a773ac6062fdad66b7dc96abe8bd81"
SETUP_PATH = Path("scripts/stretch_mlx_0320_env_setup_030.py")
SETUP_BLOB = "fde39967be02cba81ea14bb043c9fdacd24db861"
TREATMENT_VENV = Path(".venvs/stretch030-mlx0320")
ENV_MARKER = "loom_stretch030_env.json"
EXPECTED_PASS_CLASSIFICATION = "FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS"
EXPECTED_HOTSET_IDS = list(range(36))
EXPECTED_TOTAL_WEIGHT_BYTES = 3_583_928_320
EXPECTED_CONTROL_MLX = "0.31.2"
EXPECTED_TREATMENT_MLX = "0.32.0"
EXPECTED_MLX_LM = "0.31.3"
EXPECTED_TRANSFORMERS = "5.12.1"
RUN_ORDER = ["MLX0312", "MLX0320", "MLX0320", "MLX0312"]

RUNTIME_SCIENTIFIC_FAIL_CLASSES = {
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


def query_env(python: Path, repo: Path) -> dict:
    code = r'''
import importlib.metadata as md, json, platform, sys
names = ["mlx", "mlx-lm", "transformers", "numpy", "safetensors"]
out = {"python": sys.version.split()[0], "python_executable": sys.executable, "platform": platform.platform()}
for name in names:
    try:
        out[name] = md.version(name)
    except md.PackageNotFoundError:
        out[name] = "MISSING"
print(json.dumps(out, sort_keys=True))
'''
    proc = subprocess.run([str(python), "-c", code], cwd=repo, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"environment query failed for {python}: {proc.stderr.strip()}")
    return json.loads(proc.stdout.strip())


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
    source = repo / SOURCE_PATH
    setup = repo / SETUP_PATH
    treatment_python = repo / TREATMENT_VENV / "bin/python"
    marker_path = repo / TREATMENT_VENV / ENV_MARKER

    observed_source = git_blob(source, repo)
    observed_setup = git_blob(setup, repo)

    print("LOOM Stretch 030 — Balanced MLX 0.31.2 vs 0.32.0 Runtime Comparison")
    print(f"Canonical workload blob: {observed_source}")
    print(f"Environment setup blob: {observed_setup}")
    if observed_source != SOURCE_BLOB or observed_setup != SETUP_BLOB:
        print("Source provenance: FAIL", file=sys.stderr)
        return 2
    if not treatment_python.is_file() or not marker_path.is_file():
        print(
            "Treatment environment missing. Run scripts/stretch_mlx_0320_env_setup_030.py first.",
            file=sys.stderr,
        )
        return 2

    control_python = Path(sys.executable).resolve()
    control_env = query_env(control_python, repo)
    treatment_env = query_env(treatment_python, repo)
    marker = json.loads(marker_path.read_text(encoding="utf-8"))

    env_ok = (
        control_env.get("mlx") == EXPECTED_CONTROL_MLX
        and treatment_env.get("mlx") == EXPECTED_TREATMENT_MLX
        and control_env.get("mlx-lm") == treatment_env.get("mlx-lm") == EXPECTED_MLX_LM
        and control_env.get("transformers") == treatment_env.get("transformers") == EXPECTED_TRANSFORMERS
        and control_env.get("numpy") == treatment_env.get("numpy")
        and control_env.get("safetensors") == treatment_env.get("safetensors")
        and control_env.get("python") == treatment_env.get("python")
        and marker.get("treatment", {}).get("mlx") == EXPECTED_TREATMENT_MLX
    )
    if not env_ok:
        print(f"Environment provenance: FAIL control={control_env} treatment={treatment_env}", file=sys.stderr)
        return 2

    print("Source provenance: PASS")
    print("Environment provenance: PASS")
    print("Balanced order: MLX0312 -> MLX0320 -> MLX0320 -> MLX0312")
    print("Identical workload source in both variants")
    print("Scientific factor: mlx 0.31.2 -> mlx 0.32.0 ONLY")
    print("mlx-lm 0.31.3 / transformers 5.12.1 / M5 / H36 / full persistence / single cleanup / KV / gates: UNCHANGED")
    print("No package install / cache purge occurs inside this scientific runner")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "stretch" / "mlx-0312-0320-runtime-comparison-030" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    summary_path = run_dir / "summary.json"
    summary: dict = {
        "experiment": "Stretch 030 — Balanced MLX 0.31.2 vs 0.32.0 Runtime Comparison",
        "classification": "RUNNING",
        "run_id": run_id,
        "run_order": RUN_ORDER,
        "scientific_factor": "MLX runtime 0.31.2 -> 0.32.0 only",
        "source_provenance": {
            "workload_path": str(SOURCE_PATH),
            "workload_blob": observed_source,
            "setup_path": str(SETUP_PATH),
            "setup_blob": observed_setup,
        },
        "environment_provenance": {
            "control": control_env,
            "treatment": treatment_env,
            "marker": marker,
        },
        "frozen_architecture": "Qwen3-8B 3bit/group64; M5 H36 full persistence; one final cleanup/pass; BF16 KV",
        "scientific_failure_classes": sorted(RUNTIME_SCIENTIFIC_FAIL_CLASSES),
        "deliberate_cache_purge": False,
        "package_install_during_scientific_run": False,
        "disk_free_before_gib": gib_free(repo),
        "attempts": [],
    }

    def save() -> None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    def finish_incomplete(reason: str, code: int) -> int:
        summary["classification"] = "MLX_0312_0320_RUNTIME_COMPARISON_INCOMPLETE"
        summary["failure_reason"] = reason
        summary["disk_free_after_gib"] = gib_free(repo)
        save()
        print(f"Classification: {summary['classification']}", file=sys.stderr)
        print(f"Failure reason: {reason}", file=sys.stderr)
        print(f"Run directory: {run_dir}")
        print(f"Summary: {summary_path}")
        return code

    save()
    executables = {"MLX0312": control_python, "MLX0320": treatment_python}

    for index, variant in enumerate(RUN_ORDER, start=1):
        python = executables[variant]
        out_path = run_dir / f"attempt-{index}-{variant.lower()}-stdout.txt"
        err_path = run_dir / f"attempt-{index}-{variant.lower()}-stderr.txt"
        print(f"Attempt {index}/4: {variant} via {python}")
        started = time.perf_counter()
        with out_path.open("w", encoding="utf-8") as out, err_path.open("w", encoding="utf-8") as err:
            proc = subprocess.run([str(python), str(source)], cwd=repo, stdout=out, stderr=err, text=True, check=False)
        wrapper_wall = time.perf_counter() - started
        stdout_text = out_path.read_text(encoding="utf-8", errors="replace")
        child_summary_path = parse_summary_path(stdout_text)
        attempt: dict = {
            "attempt": index,
            "variant": variant,
            "mlx_version": control_env["mlx"] if variant == "MLX0312" else treatment_env["mlx"],
            "python_executable": str(python),
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

        if variant == "MLX0320" and child_class in RUNTIME_SCIENTIFIC_FAIL_CLASSES:
            attempt["usable"] = False
            attempt["scientific_runtime_failure"] = True
            attempt["prompt_parity"] = child.get("prompt_parity")
            attempt["step_parities"] = child.get("step_parities")
            summary["attempts"].append(attempt)
            summary["classification"] = "MLX_0320_RUNTIME_EXACTNESS_FAIL"
            summary["failure_reason"] = (
                f"attempt {index} MLX0320 produced valid frozen-gate failure: "
                f"{child_class}: {child.get('failure_reason')}"
            )
            summary["scientific_result"] = "MLX_0320_NOT_ADMISSIBLE_UNDER_FROZEN_M5_GATES"
            summary["disk_free_after_gib"] = gib_free(repo)
            save()
            print("Classification: MLX_0320_RUNTIME_EXACTNESS_FAIL")
            print(f"Underlying child classification: {child_class}")
            print(f"Failure reason: {child.get('failure_reason')}")
            print("Scientific result: MLX 0.32.0 is not admissible under frozen M5 gates; no retry/rescue")
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
        )
        summary["attempts"].append(attempt)
        save()

        if not attempt["usable"]:
            return finish_incomplete(
                f"attempt {index} {variant} failed inherited/provenance gates: "
                f"rc={proc.returncode}, class={child_class}, cleanup_mode_ok={cleanup_mode_ok}",
                4,
            )

    control_records = [r for r in summary["attempts"] if r["variant"] == "MLX0312"]
    treatment_records = [r for r in summary["attempts"] if r["variant"] == "MLX0320"]
    control = aggregate(control_records)
    treatment = aggregate(treatment_records)
    comparison = {
        "mlx_0312": control,
        "mlx_0320": treatment,
        "mlx_0320_over_0312_target_rate_ratio": safe_ratio(
            treatment["pooled_target_verification_tokens_per_second"],
            control["pooled_target_verification_tokens_per_second"],
        ),
        "mlx_0320_over_0312_median_block_wall_ratio": safe_ratio(
            treatment["median_block_wall_seconds"], control["median_block_wall_seconds"]
        ),
        "observed_higher_pooled_target_rate": (
            "MLX0320" if treatment["pooled_target_verification_tokens_per_second"] > control["pooled_target_verification_tokens_per_second"] else "MLX0312"
        ),
    }
    summary["comparison"] = comparison
    summary["classification"] = "MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS"
    summary["disk_free_after_gib"] = gib_free(repo)
    save()

    print("Classification: MLX_0312_0320_RUNTIME_BALANCED_COMPARISON_PASS")
    print(f"MLX0312 pooled target-verification tok/s: {control['pooled_target_verification_tokens_per_second']}")
    print(f"MLX0320 pooled target-verification tok/s: {treatment['pooled_target_verification_tokens_per_second']}")
    print(f"MLX0320/MLX0312 target-rate ratio: {comparison['mlx_0320_over_0312_target_rate_ratio']}")
    print(f"MLX0312 median block wall: {control['median_block_wall_seconds']} s")
    print(f"MLX0320 median block wall: {treatment['median_block_wall_seconds']} s")
    print(f"MLX0320/MLX0312 median block-wall ratio: {comparison['mlx_0320_over_0312_median_block_wall_ratio']}")
    print(f"MLX0312 mean final cleanup wall: {control['mean_final_cleanup_wall_seconds']} s")
    print(f"MLX0320 mean final cleanup wall: {treatment['mean_final_cleanup_wall_seconds']} s")
    print(f"MLX0312 minimum free memory: {control['minimum_observed_free_memory_percent']}%")
    print(f"MLX0320 minimum free memory: {treatment['minimum_observed_free_memory_percent']}%")
    print(f"MLX0312 peak swap: {control['peak_observed_swap_mb']} MB")
    print(f"MLX0320 peak swap: {treatment['peak_observed_swap_mb']} MB")
    print(f"Observed higher pooled target rate: {comparison['observed_higher_pooled_target_rate']}")
    print(f"Disk free after: {summary['disk_free_after_gib']:.3f} GiB")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
