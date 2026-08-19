#!/usr/bin/env python3
"""Read-only diagnostic for a completed LOOM Direct MLX Coding Benchmark 001 run."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_direct_mlx_coding_benchmark_001.py <run-directory>")
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    summary_path = run_dir / "benchmark-summary.json"
    if not summary_path.exists():
        print(f"Missing summary: {summary_path}")
        return 2

    summary = load_json(summary_path)
    benchmark = summary.get("benchmark_result") or {}
    scorer_by_id = {x.get("id"): x for x in benchmark.get("tasks", []) if isinstance(x, dict)}

    print("=" * 80)
    print("DIRECT MLX CODING BENCHMARK 001 — QUALITY DIAGNOSTIC")
    print("=" * 80)
    print(f"run_id: {summary.get('run_id')!r}")
    print(f"classification: {summary.get('classification')!r}")
    print(f"artifact_score: {summary.get('artifact_score')!r}")
    print(f"delivery_adjusted_score: {summary.get('delivery_adjusted_score')!r}")
    print(f"written_tasks: {summary.get('written_tasks')!r}/6")
    print(f"telemetry: {summary.get('telemetry')!r}")

    for rec in summary.get("tasks") or []:
        if not isinstance(rec, dict):
            continue
        task_id = rec.get("id")
        score = scorer_by_id.get(task_id, {})
        print("\n" + "-" * 80)
        print(task_id)
        print("-" * 80)
        print(f"adapter_status: {rec.get('adapter_status')!r}")
        print(f"adapter_error: {rec.get('error')!r}")
        print(f"metrics: {rec.get('metrics')!r}")
        print(f"scorer_points: {score.get('points_earned')!r}/{score.get('points_available')!r}")
        print(f"tests_passed: {score.get('tests_passed')!r}/{score.get('tests_total')!r}")
        if score.get("stderr"):
            print("scorer_failure_tail:")
            print(str(score.get("stderr"))[-1600:])

        raw_path = run_dir / "raw" / f"{task_id}-generation.json"
        if raw_path.exists():
            raw = load_json(raw_path)
            text = raw.get("text") if isinstance(raw, dict) else None
            print(f"raw_finish_reason: {raw.get('finish_reason')!r}")
            print(f"raw_output_chars: {len(text) if isinstance(text, str) else None!r}")
            if isinstance(text, str):
                print(f"raw_output_prefix: {text[:1200]!r}")
                try:
                    parsed = json.loads(text)
                    print(f"raw_json_type: {type(parsed).__name__}")
                    if isinstance(parsed, dict):
                        print(f"raw_top_level_keys: {list(parsed.keys())!r}")
                        files = parsed.get("files")
                        if isinstance(files, dict):
                            print(f"raw_files_keys: {list(files.keys())!r}")
                except Exception as exc:
                    print(f"raw_json_parse: FAIL {type(exc).__name__}: {exc}")
        else:
            print(f"raw generation file missing: {raw_path}")

    print("\n" + "=" * 80)
    print("DELIVERY-ADJUSTED CONTRIBUTIONS")
    print("=" * 80)
    written = {x.get("id"): x.get("adapter_status") == "written" for x in summary.get("tasks") or [] if isinstance(x, dict)}
    adjusted = 0.0
    for task_id in ["T01", "T02", "T03", "T04", "T05", "T06"]:
        item = scorer_by_id.get(task_id, {})
        points = item.get("points_earned", 0) or 0
        contribution = points if written.get(task_id) else 0
        adjusted += contribution
        print(f"{task_id}: scorer={points} written={written.get(task_id)} delivery_contribution={contribution}")
    print(f"recomputed_delivery_adjusted: {round(adjusted, 2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
