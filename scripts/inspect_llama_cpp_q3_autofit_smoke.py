#!/usr/bin/env python3
"""Inspect an existing LOOM Q3 auto-fit server smoke run without rerunning inference."""

from __future__ import annotations

import json
import sys
from pathlib import Path

KEYWORDS = (
    "fit",
    "offload",
    "gpu layer",
    "gpu_layers",
    "n_gpu_layers",
    "metal",
    "buffer size",
    "kv",
    "context",
    "n_ctx",
    "load",
)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: inspect_llama_cpp_q3_autofit_smoke.py RUN_DIR")
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    summary_path = run_dir / "autofit-server-smoke-summary.json"
    stderr_path = run_dir / "llama-server-stderr.txt"

    if not summary_path.exists():
        print(f"Missing summary: {summary_path}")
        return 2

    data = json.loads(summary_path.read_text(encoding="utf-8"))

    print("=" * 72)
    print("Q3 AUTO-FIT SERVER SMOKE DIAGNOSTIC")
    print("=" * 72)
    for key in (
        "classification",
        "failure_reason",
        "server_ready",
        "request_pass",
        "guardrail_abort_reason",
        "readiness_wall_seconds",
    ):
        print(f"{key}: {data.get(key)!r}")

    print(f"telemetry: {data.get('telemetry')!r}")
    print(f"fit_policy: {data.get('fit_policy')!r}")
    print(f"server_command: {data.get('server_command')!r}")

    health = data.get("health_history") or []
    print("\nHEALTH HISTORY")
    print(f"count: {len(health)}")
    for item in health[-8:]:
        print(item)

    fit_lines = data.get("fit_offload_log_lines") or []
    print("\nSAVED FIT/OFFLOAD LINES")
    print(f"count: {len(fit_lines)}")
    for line in fit_lines:
        print(line)

    samples = data.get("samples") or []
    print("\nFINAL MEMORY SAMPLES")
    print(f"count: {len(samples)}")
    for item in samples[-10:]:
        print(item)

    print("\nRELEVANT STDERR LINES")
    if stderr_path.exists():
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
        relevant = [
            line.rstrip()
            for line in stderr.splitlines()
            if any(keyword in line.lower() for keyword in KEYWORDS)
        ]
        print(f"count: {len(relevant)}")
        for line in relevant[-80:]:
            print(line)

        print("\nSTDERR TAIL")
        tail = stderr.splitlines()[-80:]
        for line in tail:
            print(line)
    else:
        print(f"Missing stderr log: {stderr_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
