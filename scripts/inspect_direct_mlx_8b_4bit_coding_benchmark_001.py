#!/usr/bin/env python3
"""Read-only inspector for Direct MLX 8B 4-bit Coding Benchmark 001 partial runs."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"READ_FAIL {path}: {type(exc).__name__}: {exc}")
        return None


def short(value, limit: int = 1600) -> str:
    if value is None:
        return "None"
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return text if len(text) <= limit else text[:limit] + "...<truncated>"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_direct_mlx_8b_4bit_coding_benchmark_001.py RUN_DIR")
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    summary_path = run_dir / "benchmark-summary.json"
    summary = load_json(summary_path)
    if not isinstance(summary, dict):
        return 2

    print("=" * 80)
    print("DIRECT MLX 8B 4-BIT CODING BENCHMARK 001 — RESOURCE DIAGNOSTIC")
    print("=" * 80)
    print(f"run_dir: {run_dir}")
    print(f"run_id: {summary.get('run_id')!r}")
    print(f"classification: {summary.get('classification')!r}")
    print(f"failure_reason: {summary.get('failure_reason')!r}")
    print(f"generated_task_count: {summary.get('generated_task_count')!r}")
    print(f"written_tasks: {summary.get('written_tasks')!r}")
    print(f"artifact_score: {summary.get('artifact_score')!r}")
    print(f"delivery_adjusted_score: {summary.get('delivery_adjusted_score')!r}")
    print(f"preflight_system: {summary.get('preflight_system')!r}")
    print(f"telemetry: {summary.get('telemetry')!r}")
    print(f"disk_before: {summary.get('disk_before')!r}")
    print(f"disk_after: {summary.get('disk_after')!r}")

    print("\n" + "-" * 80)
    print("CHILD RESULT")
    print("-" * 80)
    child = summary.get("child_result") or {}
    for key in ["exit_code", "wall_seconds", "guardrail_abort_reason", "telemetry_abort_reason"]:
        print(f"{key}: {child.get(key)!r}")
    print(f"stdout_tail: {short(child.get('stdout_tail'))}")
    print(f"stderr_tail: {short(child.get('stderr_tail'))}")

    print("\n" + "-" * 80)
    print("PROGRESS")
    print("-" * 80)
    progress = load_json(run_dir / "progress.json")
    print(short(progress, 3000))

    print("\n" + "-" * 80)
    print("PERSISTED TASK RESULTS")
    print("-" * 80)
    task_results = run_dir / "task-results"
    any_task = False
    if task_results.exists():
        for path in sorted(task_results.glob("T*.json")):
            any_task = True
            data = load_json(path)
            print(f"\n{path.name}: {short(data, 4000)}")
    if not any_task:
        print("none")

    print("\n" + "-" * 80)
    print("SUMMARY TASK RECORDS")
    print("-" * 80)
    tasks = summary.get("tasks") or []
    if tasks:
        for item in tasks:
            print(short(item, 3000))
    else:
        print("none")

    samples = summary.get("memory_samples") or []
    print("\n" + "-" * 80)
    print(f"MEMORY SAMPLES: {len(samples)} total")
    print("-" * 80)
    if samples:
        # First samples show cold-load transition; final samples show the breach.
        show = samples[:8]
        if len(samples) > 20:
            show += [{"separator": "..."}]
            show += samples[-20:]
        else:
            show = samples
        for sample in show:
            if "separator" in sample:
                print("...")
                continue
            print(
                "t={t!r}s free={free!r}% swap={swap!r}MB rss={rss!r}MB "
                "phase={phase!r} task={task!r} index={index!r} completed={completed!r}".format(
                    t=sample.get("elapsed_seconds"),
                    free=sample.get("memory_free_percent"),
                    swap=sample.get("swap_used_mb"),
                    rss=sample.get("rss_mb"),
                    phase=sample.get("phase") or (sample.get("progress") or {}).get("phase"),
                    task=sample.get("current_task") or (sample.get("progress") or {}).get("current_task"),
                    index=sample.get("index") or (sample.get("progress") or {}).get("index"),
                    completed=sample.get("completed") or (sample.get("progress") or {}).get("completed"),
                )
            )

        free_numeric = [s for s in samples if isinstance(s.get("memory_free_percent"), int)]
        if free_numeric:
            min_sample = min(free_numeric, key=lambda s: s["memory_free_percent"])
            print("\nMIN-FREE SAMPLE")
            print(short(min_sample, 4000))
        swap_numeric = [s for s in samples if isinstance(s.get("swap_used_mb"), (int, float))]
        if swap_numeric:
            max_swap = max(swap_numeric, key=lambda s: s["swap_used_mb"])
            print("\nMAX-SWAP SAMPLE")
            print(short(max_swap, 4000))
    else:
        print("none")

    print("\n" + "-" * 80)
    print("RAW CHILD LOG FILE TAILS")
    print("-" * 80)
    for name in ["mlx-child-stdout.txt", "mlx-child-stderr.txt"]:
        path = run_dir / name
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            print(f"\n{name} ({len(text)} chars):")
            print(text[-5000:] if text else "<empty>")
        else:
            print(f"{name}: MISSING")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
