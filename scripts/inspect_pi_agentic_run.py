#!/usr/bin/env python3
"""Inspect an existing LOOM Pi agentic run without rerunning the model.

Reads the saved Pi JSONL event streams, reports tool arguments/path safety, and
extracts provider-reported usage snapshots. This is intended to validate the
preregistered workspace-isolation rule and recover usage telemetry that the first
agentic adapter did not summarize.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TASK_IDS = ["T01", "T02", "T03", "T04", "T05", "T06"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Existing results-local/coding-agentic-pi/<run-id> directory",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    events: list[dict] = []
    errors: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:
            errors.append(f"line {line_no}: {type(exc).__name__}: {exc}")
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events, errors


def path_is_safe(value: str) -> bool:
    p = Path(value)
    if p.is_absolute():
        return False
    return ".." not in p.parts


def usage_is_nonzero(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, dict):
        return any(usage_is_nonzero(v) for v in value.values())
    if isinstance(value, list):
        return any(usage_is_nonzero(v) for v in value)
    return False


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    raw_dir = run_dir / "raw"
    if not raw_dir.exists():
        raise SystemExit(f"raw directory not found: {raw_dir}")

    overall_safe = True
    any_usage = False

    print(f"LOOM Pi agentic raw-run inspection: {run_dir.name}")

    for task_id in TASK_IDS:
        path = raw_dir / f"{task_id}-pi.jsonl"
        if not path.exists():
            print(f"\n--- {task_id} ---")
            print(f"ERROR: missing {path}")
            overall_safe = False
            continue

        events, parse_errors = load_jsonl(path)
        session_cwd = None
        tool_rows: list[dict] = []
        unsafe_paths: list[str] = []
        usage_snapshots: list[dict] = []

        for event in events:
            if event.get("type") == "session" and isinstance(event.get("cwd"), str):
                session_cwd = event["cwd"]

            if event.get("type") == "tool_execution_start":
                name = event.get("toolName")
                raw_args = event.get("args")
                args_obj = raw_args if isinstance(raw_args, dict) else {}
                tool_path = args_obj.get("path")
                safe = True
                if isinstance(tool_path, str):
                    safe = path_is_safe(tool_path)
                    if not safe:
                        unsafe_paths.append(tool_path)
                tool_rows.append({
                    "tool": name,
                    "path": tool_path,
                    "path_safe": safe,
                    "args_keys": sorted(args_obj.keys()),
                })

            if event.get("type") == "message_update" and isinstance(event.get("usage"), dict):
                usage = event["usage"]
                if usage_is_nonzero(usage):
                    usage_snapshots.append(usage)

        task_safe = not parse_errors and not unsafe_paths
        overall_safe = overall_safe and task_safe
        if usage_snapshots:
            any_usage = True

        print(f"\n--- {task_id} ---")
        print(f"session_cwd: {session_cwd}")
        print(f"jsonl_parse_errors: {parse_errors}")
        print("tool_calls:")
        for row in tool_rows:
            print(
                f"  - tool={row['tool']!r} path={row['path']!r} "
                f"path_safe={row['path_safe']} args_keys={row['args_keys']}"
            )
        print(f"path_safety: {'PASS' if task_safe else 'FAIL'}")
        if unsafe_paths:
            print(f"unsafe_paths: {unsafe_paths}")
        if usage_snapshots:
            print(f"usage_snapshots_nonzero: {len(usage_snapshots)}")
            print("last_nonzero_usage:")
            print(json.dumps(usage_snapshots[-1], indent=2, ensure_ascii=False))
        else:
            print("usage_snapshots_nonzero: 0")

    print("\n=== OVERALL ===")
    print(f"workspace_path_safety: {'PASS' if overall_safe else 'FAIL'}")
    print(f"provider_usage_detected: {any_usage}")
    return 0 if overall_safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
