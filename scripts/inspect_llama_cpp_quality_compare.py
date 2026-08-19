#!/usr/bin/env python3
"""Inspect a persisted LOOM llama.cpp Coding Quality Compare run without rerunning models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "run_dir",
        nargs="?",
        type=Path,
        help="comparison run directory; defaults to latest under results-local/llama-cpp/coding-quality-compare-001",
    )
    return p.parse_args()


def latest_run(repo_root: Path) -> Path:
    base = repo_root / "results-local" / "llama-cpp" / "coding-quality-compare-001"
    runs = sorted([p for p in base.iterdir() if p.is_dir()]) if base.exists() else []
    if not runs:
        raise SystemExit(f"No comparison runs found under {base}")
    return runs[-1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_shape(text: str) -> str:
    try:
        obj = json.loads(text)
    except Exception as exc:
        return f"NOT_JSON ({type(exc).__name__}: {exc})"
    if isinstance(obj, dict):
        return f"dict keys={sorted(obj.keys())}"
    if isinstance(obj, list):
        return f"list len={len(obj)}"
    return type(obj).__name__


def compact_prefix(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    return text[:limit] + ("..." if len(text) > limit else "")


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    run_dir = args.run_dir.resolve() if args.run_dir else latest_run(repo_root)
    summary_path = run_dir / "comparison-summary.json"
    if not summary_path.exists():
        raise SystemExit(f"Missing comparison summary: {summary_path}")

    summary = load_json(summary_path)
    print(f"Run: {run_dir}")
    print(f"Classification: {summary.get('classification')}")
    print(f"Quality relation: {summary.get('quality_relation')}")
    print(f"Delta 8B-4B: {summary.get('delivery_delta_8b_minus_4b')}")

    profiles = summary.get("profiles", [])
    for profile in profiles:
        pinfo = profile.get("profile", {})
        label = pinfo.get("label") or pinfo.get("key") or "unknown"
        print("\n" + "=" * 72)
        print(label)
        print("=" * 72)
        print(f"classification: {profile.get('classification')}")
        print(f"artifact_score: {profile.get('artifact_score')}")
        print(f"delivery_adjusted_score: {profile.get('delivery_adjusted_score')}")
        print(f"server_ready: {profile.get('server_ready')}")
        print(f"guardrail_abort_reason: {profile.get('guardrail_abort_reason')}")
        print(f"execution_failure: {profile.get('execution_failure')}")
        print(f"telemetry: {profile.get('telemetry')}")

        for task in profile.get("tasks", []):
            req = task.get("request") if isinstance(task.get("request"), dict) else {}
            resp = req.get("response") if isinstance(req.get("response"), dict) else {}
            content = resp.get("content") if isinstance(resp.get("content"), str) else None
            print(f"\n{task.get('id')} status={task.get('adapter_status')}")
            print(f"  error: {task.get('error')}")
            print(f"  http_status: {req.get('http_status')}")
            print(f"  wall_seconds: {req.get('wall_seconds')}")
            print(f"  stop_type: {task.get('stop_type')}")
            print(f"  tokens_evaluated: {task.get('tokens_evaluated')}")
            print(f"  tokens_predicted: {task.get('tokens_predicted')}")
            print(f"  content_present: {content is not None}")
            if content is not None:
                print(f"  content_chars: {len(content)}")
                print(f"  json_shape: {json_shape(content)}")
                print(f"  prefix: {compact_prefix(content)!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
