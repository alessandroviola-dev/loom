#!/usr/bin/env python3
"""Read-only diagnostic for a LOOM Capability Amplifier 001 run."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def compact(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def summarize_phase(samples: list[dict]) -> dict:
    frees = [x.get("memory_free_percent") for x in samples if isinstance(x.get("memory_free_percent"), int)]
    swaps = [x.get("swap_used_mb") for x in samples if isinstance(x.get("swap_used_mb"), (int, float))]
    return {
        "samples": len(samples),
        "min_free_percent": min(frees) if frees else None,
        "max_free_percent": max(frees) if frees else None,
        "peak_swap_mb": max(swaps) if swaps else None,
        "last_free_percent": frees[-1] if frees else None,
        "last_swap_mb": swaps[-1] if swaps else None,
    }


def print_task(task: dict) -> None:
    print(f"{task.get('id')}: selected={task.get('selected_candidate')} final_delivery={task.get('final_delivery_success')}")
    initial = task.get("initial") or {}
    print(f"  initial.adapter_status={initial.get('adapter_status')}")
    if initial.get("parser_error"):
        print(f"  initial.parser_error={initial.get('parser_error')}")
    if initial.get("test_result"):
        tr = initial["test_result"]
        print(f"  initial.tests={tr.get('tests_passed')}/{tr.get('tests_total')} points={tr.get('points_earned')}/{tr.get('points_available')}")
    if initial.get("metrics"):
        m = initial["metrics"]
        print(f"  initial.metrics prompt={m.get('prompt_eval_count')} gen={m.get('eval_count')} gen_tps={m.get('generation_tokens_per_second')} wall={m.get('wall_seconds')}")

    repair = task.get("repair") or {}
    print(f"  repair.attempted={repair.get('attempted')}")
    if repair.get("feedback_kind"):
        print(f"  repair.feedback_kind={repair.get('feedback_kind')}")
    if repair.get("adapter_status"):
        print(f"  repair.adapter_status={repair.get('adapter_status')}")
    if repair.get("parser_error"):
        print(f"  repair.parser_error={repair.get('parser_error')}")
    if repair.get("test_result"):
        tr = repair["test_result"]
        print(f"  repair.tests={tr.get('tests_passed')}/{tr.get('tests_total')} points={tr.get('points_earned')}/{tr.get('points_available')}")
    if repair.get("metrics"):
        m = repair["metrics"]
        print(f"  repair.metrics prompt={m.get('prompt_eval_count')} gen={m.get('eval_count')} gen_tps={m.get('generation_tokens_per_second')} wall={m.get('wall_seconds')}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()

    run_dir = args.run_dir.expanduser().resolve()
    summary_path = run_dir / "run-summary.json"
    telemetry_path = run_dir / "telemetry.json"
    if not summary_path.exists():
        raise SystemExit(f"Missing summary: {summary_path}")
    if not telemetry_path.exists():
        raise SystemExit(f"Missing telemetry: {telemetry_path}")

    summary = load_json(summary_path)
    telemetry = load_json(telemetry_path)
    if not isinstance(telemetry, list):
        raise SystemExit("telemetry.json must contain a list")

    print("=" * 80)
    print("CAPABILITY AMPLIFIER 001 — READ-ONLY DIAGNOSTIC")
    print("=" * 80)
    print(f"run_dir: {run_dir}")
    print(f"run_id: {summary.get('run_id')!r}")
    print(f"classification: {summary.get('classification')!r}")
    print(f"failure_reason: {summary.get('failure_reason')!r}")
    print(f"whole_wall_seconds: {summary.get('whole_wall_seconds')!r}")
    print(f"disk_before: {summary.get('disk_before')!r}")
    print(f"disk_after: {summary.get('disk_after')!r}")
    print(f"telemetry_summary: {summary.get('telemetry')!r}")
    print(f"host_gate_samples: {compact(summary.get('host_gate_samples'))}")
    print(f"completed_model_call_records: {len(summary.get('model_calls') or [])}")

    print("\n" + "-" * 80)
    print("TASK RECORDS")
    print("-" * 80)
    for task in summary.get("tasks") or []:
        print_task(task)

    print("\n" + "-" * 80)
    print("MODEL CALL RECORDS")
    print("-" * 80)
    for call in summary.get("model_calls") or []:
        print(compact(call))

    by_phase: dict[tuple[str | None, str | None], list[dict]] = defaultdict(list)
    for sample in telemetry:
        by_phase[(sample.get("task"), sample.get("phase"))].append(sample)

    print("\n" + "-" * 80)
    print("TELEMETRY BY TASK/PHASE")
    print("-" * 80)
    for key, samples in by_phase.items():
        print(f"task={key[0]!r} phase={key[1]!r} {compact(summarize_phase(samples))}")

    frees = [x for x in telemetry if isinstance(x.get("memory_free_percent"), int)]
    swaps = [x for x in telemetry if isinstance(x.get("swap_used_mb"), (int, float))]
    min_free = min(frees, key=lambda x: x["memory_free_percent"]) if frees else None
    max_swap = max(swaps, key=lambda x: x["swap_used_mb"]) if swaps else None

    print("\n" + "-" * 80)
    print("MIN-FREE SAMPLE")
    print("-" * 80)
    print(compact(min_free))
    print("\n" + "-" * 80)
    print("MAX-SWAP SAMPLE")
    print("-" * 80)
    print(compact(max_swap))

    print("\n" + "-" * 80)
    print("LAST 20 TELEMETRY SAMPLES")
    print("-" * 80)
    for sample in telemetry[-20:]:
        print(compact(sample))

    raw_dir = run_dir / "raw"
    if raw_dir.exists():
        print("\n" + "-" * 80)
        print("RAW RESPONSE FILES")
        print("-" * 80)
        for path in sorted(raw_dir.glob("*.json")):
            print(f"{path.name}: {path.stat().st_size} bytes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
