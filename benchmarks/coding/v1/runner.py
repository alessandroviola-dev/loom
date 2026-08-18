#!/usr/bin/env python3
"""LOOM Coding Benchmark 01 runner.

Runs the benchmark unittest suites and emits a machine-readable result.
Environment variables may be used to annotate a run:
  LOOM_MODEL, LOOM_RUNTIME, LOOM_BACKEND, LOOM_MODE, LOOM_CONTEXT

Scoring rule:
- each top-level unittest.TestCase method counts exactly once;
- a method passes only if it completes without failures, errors,
  unexpected successes, or failing subtests;
- failing subtests do not increase the denominator.

By default the runner scores the benchmark tree containing this file. Use
--benchmark-root to rescore an isolated working copy from an earlier run.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent

TEST_PROBE = r'''
import contextlib
import io
import json
import unittest


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


suite = unittest.defaultTestLoader.discover(".", pattern="test*.py")
records = []

for case in list(flatten(suite)):
    result = unittest.TestResult()
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(captured_stderr):
        case(result)

    failed = bool(result.failures or result.errors or result.unexpectedSuccesses)
    skipped = bool(result.skipped) and not failed
    passed = result.testsRun == 1 and not failed and not skipped

    records.append({
        "id": case.id(),
        "passed": passed,
        "skipped": skipped,
        "failures": [traceback for _, traceback in result.failures],
        "errors": [traceback for _, traceback in result.errors],
        "unexpected_successes": [str(item) for item in result.unexpectedSuccesses],
        "captured_stdout": captured_stdout.getvalue()[-2000:],
        "captured_stderr": captured_stderr.getvalue()[-2000:],
    })

print(json.dumps({"tests": records}))
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--benchmark-root",
        type=Path,
        default=SCRIPT_ROOT,
        help="Benchmark v1 tree to score. Defaults to the tree containing this runner.",
    )
    return parser.parse_args()


def run_task(task: dict, benchmark_root: Path) -> dict:
    task_dir = benchmark_root / task["path"]
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-c", TEST_PROBE],
        cwd=task_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    duration = time.perf_counter() - started

    if proc.returncode != 0:
        return {
            "id": task["id"],
            "skill": task["skill"],
            "points_available": task["points"],
            "points_earned": 0,
            "tests_total": 0,
            "tests_passed": 0,
            "exit_code": proc.returncode,
            "duration_seconds": round(duration, 3),
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
            "runner_probe_error": True,
        }

    try:
        payload = json.loads(proc.stdout)
        tests = payload["tests"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return {
            "id": task["id"],
            "skill": task["skill"],
            "points_available": task["points"],
            "points_earned": 0,
            "tests_total": 0,
            "tests_passed": 0,
            "exit_code": 1,
            "duration_seconds": round(duration, 3),
            "stdout": proc.stdout[-4000:],
            "stderr": (proc.stderr + f"\nProbe parse error: {exc}")[-4000:],
            "runner_probe_error": True,
        }

    total = len(tests)
    passed = sum(1 for test in tests if test.get("passed") is True)
    ratio = (passed / total) if total else 0.0
    earned = round(task["points"] * ratio, 2)

    failure_summaries = []
    for test in tests:
        if test.get("passed"):
            continue
        failure_summaries.append({
            "id": test.get("id"),
            "skipped": test.get("skipped", False),
            "failures": test.get("failures", []),
            "errors": test.get("errors", []),
            "unexpected_successes": test.get("unexpected_successes", []),
        })

    return {
        "id": task["id"],
        "skill": task["skill"],
        "points_available": task["points"],
        "points_earned": earned,
        "tests_total": total,
        "tests_passed": passed,
        "exit_code": 0 if passed == total else 1,
        "duration_seconds": round(duration, 3),
        "stdout": "",
        "stderr": json.dumps(failure_summaries, indent=2)[-4000:] if failure_summaries else "",
    }


def main() -> int:
    args = parse_args()
    benchmark_root = args.benchmark_root.resolve()
    manifest_path = benchmark_root / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Benchmark manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text())
    results = []
    for task in manifest["tasks"]:
        try:
            results.append(run_task(task, benchmark_root))
        except subprocess.TimeoutExpired:
            results.append({
                "id": task["id"],
                "skill": task["skill"],
                "points_available": task["points"],
                "points_earned": 0,
                "tests_total": 0,
                "tests_passed": 0,
                "exit_code": None,
                "duration_seconds": 120,
                "timeout": True,
            })

    score = round(sum(x["points_earned"] for x in results), 2)
    payload = {
        "benchmark": manifest["benchmark"],
        "version": manifest["version"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": os.getenv("LOOM_MODEL", "unknown"),
        "runtime": os.getenv("LOOM_RUNTIME", "unknown"),
        "backend": os.getenv("LOOM_BACKEND", "unknown"),
        "mode": os.getenv("LOOM_MODE", "unknown"),
        "context": os.getenv("LOOM_CONTEXT", "unknown"),
        "score": score,
        "max_score": manifest["total_points"],
        "tasks": results,
    }

    # For an isolated run tree shaped as <run>/benchmarks/coding/v1, parents[2]
    # resolves to <run>. For the canonical tree it resolves to the repository root.
    output_root = benchmark_root.parents[2]
    out_dir = output_root / "results-local"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = out_dir / f"coding-benchmark-01-{stamp}.json"
    out_file.write_text(json.dumps(payload, indent=2) + "\n")

    print(json.dumps(payload, indent=2))
    print(f"\nSaved: {out_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
