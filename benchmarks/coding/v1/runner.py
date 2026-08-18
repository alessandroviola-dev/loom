#!/usr/bin/env python3
"""LOOM Coding Benchmark 01 runner.

Runs the frozen unittest suites and emits a machine-readable result.
Environment variables may be used to annotate a run:
  LOOM_MODEL, LOOM_RUNTIME, LOOM_BACKEND, LOOM_MODE, LOOM_CONTEXT
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
MANIFEST = json.loads((HERE / "manifest.json").read_text())

TEST_LINE = re.compile(r"^test.*\.\.\. (ok|FAIL|ERROR|skipped.*)$")


def run_task(task: dict) -> dict:
    task_dir = HERE / task["path"]
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-v"],
        cwd=task_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    duration = time.perf_counter() - started
    combined = "\n".join([proc.stdout, proc.stderr])
    outcomes = []
    for line in combined.splitlines():
        match = TEST_LINE.match(line.strip())
        if match:
            outcomes.append(match.group(1))

    total = len(outcomes)
    passed = sum(1 for x in outcomes if x == "ok")
    ratio = (passed / total) if total else 0.0
    earned = round(task["points"] * ratio, 2)

    return {
        "id": task["id"],
        "skill": task["skill"],
        "points_available": task["points"],
        "points_earned": earned,
        "tests_total": total,
        "tests_passed": passed,
        "exit_code": proc.returncode,
        "duration_seconds": round(duration, 3),
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def main() -> int:
    results = []
    for task in MANIFEST["tasks"]:
        try:
            results.append(run_task(task))
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
        "benchmark": MANIFEST["benchmark"],
        "version": MANIFEST["version"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": os.getenv("LOOM_MODEL", "unknown"),
        "runtime": os.getenv("LOOM_RUNTIME", "unknown"),
        "backend": os.getenv("LOOM_BACKEND", "unknown"),
        "mode": os.getenv("LOOM_MODE", "unknown"),
        "context": os.getenv("LOOM_CONTEXT", "unknown"),
        "score": score,
        "max_score": MANIFEST["total_points"],
        "tasks": results,
    }

    out_dir = REPO_ROOT / "results-local"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = out_dir / f"coding-benchmark-01-{stamp}.json"
    out_file.write_text(json.dumps(payload, indent=2) + "\n")

    print(json.dumps(payload, indent=2))
    print(f"\nSaved: {out_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
