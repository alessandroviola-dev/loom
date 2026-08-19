#!/usr/bin/env python3
"""Read-only diagnostic for a LOOM llama.cpp Coding Quality Compare 002 run."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: inspect_llama_cpp_quality_compare_002.py <run-directory>")
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    summary_path = run_dir / "comparison-summary.json"
    if not summary_path.exists():
        print(f"Missing summary: {summary_path}")
        return 2

    summary = load_json(summary_path)
    print("=" * 72)
    print("CODING QUALITY COMPARE 002 — RESOURCE DIAGNOSTIC")
    print("=" * 72)
    print(f"run_id: {summary.get('run_id')!r}")
    print(f"classification: {summary.get('classification')!r}")
    print(f"quality_relation_printed: {summary.get('quality_relation')!r}")
    print(f"delta_printed: {summary.get('delivery_score_delta_8b_minus_4b')!r}")

    profiles = summary.get("profiles") or []
    for rec in profiles:
        profile = rec.get("profile") or {}
        label = profile.get("label") or profile.get("key") or "UNKNOWN"
        print("\n" + "-" * 72)
        print(label)
        print("-" * 72)
        print(f"classification: {rec.get('classification')!r}")
        print(f"server_ready: {rec.get('server_ready')!r}")
        print(f"guardrail_abort_reason: {rec.get('guardrail_abort_reason')!r}")
        print(f"execution_failure: {rec.get('execution_failure')!r}")
        print(f"telemetry: {rec.get('telemetry')!r}")
        print(f"artifact_score: {rec.get('artifact_score')!r}")
        print(f"delivery_adjusted_score: {rec.get('delivery_adjusted_score')!r}")
        print(f"attempted_tasks: {rec.get('attempted_tasks')!r}")
        print(f"written_tasks: {rec.get('written_tasks')!r}")
        print(f"server_command: {rec.get('server_command')!r}")

        tasks = rec.get("tasks") or []
        for task in tasks:
            print(f"\n{task.get('id')} status={task.get('adapter_status')}")
            if task.get("error") is not None:
                print(f"  error: {task.get('error')}")
            req = task.get("request")
            if isinstance(req, dict):
                print(f"  http_status: {req.get('http_status')!r}")
                print(f"  wall_seconds: {req.get('wall_seconds')!r}")
                if req.get("error") is not None:
                    print(f"  request_error: {req.get('error')}")
                response = req.get("response")
                if isinstance(response, dict):
                    content = response.get("content")
                    print(f"  stop_type: {response.get('stop_type')!r}")
                    print(f"  tokens_evaluated: {response.get('tokens_evaluated')!r}")
                    print(f"  tokens_predicted: {response.get('tokens_predicted')!r}")
                    print(f"  content_present: {isinstance(content, str)}")
                    if isinstance(content, str):
                        print(f"  content_chars: {len(content)}")
                        print(f"  content_prefix: {content[:240]!r}")

        samples = rec.get("samples") or []
        if samples:
            print("\nFINAL MEMORY SAMPLES")
            for sample in samples[-12:]:
                print(sample)

        profile_dir = run_dir / str(profile.get("key", ""))
        stderr_path = profile_dir / "llama-server-stderr.txt"
        if stderr_path.exists():
            lines = stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()
            relevant = []
            needles = (
                "n_slots", "n_ctx_slot", "kv", "cache", "model loaded", "listening",
                "prompt eval", "eval time", "offload", "fit", "metal", "slot",
            )
            for line in lines:
                low = line.lower()
                if any(n in low for n in needles):
                    relevant.append(line)
            print("\nRELEVANT STDERR TAIL")
            for line in relevant[-40:]:
                print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
