#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q2 Stage B 001.

Runs only the preregistered llama-bench throughput continuation after Q2
Capability 003 supplied recovered-valid Stage A launch/memory evidence.
No llama-cli smoke is repeated.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PINNED_COMMIT = "60addddf3c567c43ec3caf70fc953fba3572d96f"
Q4_TEMPLATE_BLOB_SHA = "83e01eae5ed12d13396f003d5291ba786a668ffd"
MODEL_REPO = "unsloth/Qwen3-8B-GGUF"
MODEL_FILE = "Qwen3-8B-Q2_K.gguf"
MODEL_QUANT = "Q2_K"
MODEL_SHA256 = "7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf"
OLLAMA_MODEL = "qwen3.5:4b-mlx"
STAGE_A_SOURCE_RUN = "20260819-103347"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_frozen_helpers(repo_root: Path):
    template = repo_root / "scripts" / "llama_cpp_8b_q4.py"
    blob = subprocess.run(
        ["git", "hash-object", str(template)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if blob != Q4_TEMPLATE_BLOB_SHA:
        raise RuntimeError(
            f"Q4 helper template blob mismatch: observed={blob or 'N/A'} expected={Q4_TEMPLATE_BLOB_SHA}"
        )

    spec = importlib.util.spec_from_file_location("loom_q4_frozen_helpers", template)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen Q4 helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        q4 = load_frozen_helpers(repo_root)
    except Exception as exc:
        print("LOOM llama.cpp 8B Q2 Stage B 001")
        print(f"Helper verification: FAIL — {type(exc).__name__}: {exc}")
        return 2

    llama_root = repo_root / "results-local" / "llama-cpp"
    source = llama_root / f"source-{PINNED_COMMIT[:12]}"
    build = source / "build-loom-metal"
    bench = build / "bin" / "llama-bench"
    model_path = repo_root / "results-local" / "models" / "Qwen3-8B-GGUF" / MODEL_FILE

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = llama_root / "8b-q2-stage-b" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    disk_before = q4.disk_snapshot(repo_root)
    source_sha = q4.run(["git", "rev-parse", "HEAD"], source).get("stdout", "").strip() if source.exists() else ""
    missing = [x for x in ["sysctl", "ps", "memory_pressure"] if shutil.which(x) is None]

    summary: dict = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "llama.cpp 8B Q2 Stage B 001",
        "stage_a_source_run": STAGE_A_SOURCE_RUN,
        "stage_a_status": "RECOVERED_PASS",
        "classification": None,
        "pinned_commit": PINNED_COMMIT,
        "source_commit_actual": source_sha,
        "model": {
            "repo": MODEL_REPO,
            "file": MODEL_FILE,
            "quantization": MODEL_QUANT,
            "expected_sha256": MODEL_SHA256,
            "path": str(model_path),
        },
        "guardrails": {
            "abort_below_memory_free_percent": q4.FREE_MEMORY_ABORT_PERCENT,
            "abort_above_swap_mb": q4.SWAP_ABORT_MB,
        },
        "disk_before": disk_before,
        "memory_before": q4.memory_snapshot(repo_root),
        "missing_prerequisites": missing,
    }

    print("LOOM llama.cpp 8B Q2 Stage B 001")
    print(f"Stage A source: {STAGE_A_SOURCE_RUN} (RECOVERED_PASS)")
    print(f"Disk free before: {disk_before['free_gib']:.3f} GiB")

    if missing or source_sha != PINNED_COMMIT or not bench.exists() or not model_path.exists():
        summary["classification"] = "BENCH_FAIL"
        summary["failure_reason"] = "preflight/build/model verification failed"
        path = out_dir / "stage-b-summary.json"
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print("Preflight: FAIL")
        print(f"Summary: {path}")
        return 2

    digest = q4.sha256_file(model_path)
    hash_ok = digest == MODEL_SHA256
    summary["model"].update({
        "sha256": digest,
        "sha256_ok": hash_ok,
        "size_bytes": model_path.stat().st_size,
        "size_gib": round(model_path.stat().st_size / (1024 ** 3), 3),
    })
    print(f"Model SHA256: {'PASS' if hash_ok else 'FAIL'}")
    if not hash_ok:
        summary["classification"] = "BENCH_FAIL"
        summary["failure_reason"] = "model SHA256 mismatch"
        path = out_dir / "stage-b-summary.json"
        path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Summary: {path}")
        return 1

    if shutil.which("ollama"):
        summary["ollama_stop"] = q4.run(["ollama", "stop", OLLAMA_MODEL], repo_root, timeout=30)

    devices = q4.run([str(bench), "--list-devices"], source, timeout=60)
    summary["device_list"] = devices
    print("=== DEVICES ===")
    print((devices.get("stdout", "") + devices.get("stderr", "")).strip())

    bench_cmd = [
        str(bench),
        "-m", str(model_path),
        "-ngl", "-1",
        "-fa", "auto",
        "-p", "512",
        "-n", "128",
        "-r", "3",
        "-o", "json",
    ]

    print("=== STAGE B — BENCHMARK ===", flush=True)
    benchmark = q4.monitor_command(bench_cmd, source, timeout=1800)
    q4.save_monitored(out_dir, "stage-b-benchmark", benchmark)
    (out_dir / "stage-b-benchmark-stdout.json").write_text(benchmark.get("stdout", ""), encoding="utf-8")

    parsed = None
    parse_error = None
    try:
        parsed = json.loads(benchmark.get("stdout", ""))
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"

    rows = parsed if isinstance(parsed, list) else []
    pp_rows = [r for r in rows if isinstance(r, dict) and (r.get("n_prompt") or 0) > 0 and (r.get("n_gen") or 0) == 0]
    tg_rows = [r for r in rows if isinstance(r, dict) and (r.get("n_gen") or 0) > 0 and (r.get("n_prompt") or 0) == 0]
    positive = bool(pp_rows and tg_rows) and all(float(r.get("avg_ts", 0) or 0) > 0 for r in pp_rows + tg_rows)

    evidence_text = (
        devices.get("stdout", "")
        + devices.get("stderr", "")
        + benchmark.get("stderr", "")
        + json.dumps(rows)
    ).lower()
    metal_evidence = "metal" in evidence_text or "mtl" in evidence_text

    bench_pass = (
        benchmark.get("exit_code") == 0
        and not benchmark.get("timed_out")
        and not benchmark.get("guardrail_abort")
        and parse_error is None
        and positive
        and metal_evidence
    )

    summary["stage_b"] = {
        **{k: v for k, v in benchmark.items() if k != "samples"},
        "parse_error": parse_error,
        "rows": rows,
        "pp_row_count": len(pp_rows),
        "tg_row_count": len(tg_rows),
        "positive_throughput": positive,
        "metal_evidence": metal_evidence,
        "pass": bench_pass,
    }

    for row in pp_rows + tg_rows:
        test = f"pp{row.get('n_prompt')}" if (row.get("n_prompt") or 0) else f"tg{row.get('n_gen')}"
        print(
            f"{test}: {float(row.get('avg_ts', 0) or 0):.2f} t/s ± "
            f"{float(row.get('stddev_ts', 0) or 0):.2f} | "
            f"backend={row.get('backends')} ngl={row.get('n_gpu_layers')}"
        )

    print(f"Stage B: {'PASS' if bench_pass else 'FAIL'}")
    print(
        f"  wall={benchmark.get('wall_seconds')}s "
        f"peak_rss={benchmark.get('peak_rss_mb')} MB "
        f"peak_swap={benchmark.get('peak_swap_used_mb')} MB "
        f"min_free={benchmark.get('min_memory_free_percent')}%"
    )
    if benchmark.get("guardrail_reason"):
        print(f"  guardrail={benchmark.get('guardrail_reason')}")

    summary["classification"] = "FULL_PASS" if bench_pass else "BENCH_FAIL"
    summary["memory_after"] = q4.memory_snapshot(repo_root)
    summary["disk_after"] = q4.disk_snapshot(repo_root)
    summary["finished_at_utc"] = utc_now()

    path = out_dir / "stage-b-summary.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Classification: {summary['classification']}")
    print(f"Disk free after: {summary['disk_after']['free_gib']:.3f} GiB")
    print(f"Run directory: {out_dir}")
    print(f"Summary: {path}")
    return 0 if bench_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
