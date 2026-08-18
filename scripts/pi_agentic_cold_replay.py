#!/usr/bin/env python3
"""LOOM Pi Agentic Cold Replay 001.

Replays the exact Coding Benchmark 01 v1.0.1 Pi task prompts/fixtures with an
explicit `ollama stop` before every task. This is a memory/workload probe, not a
benchmark rescore: hidden tests are never copied into agent workspaces and no
test feedback is provided.

The script reuses the frozen task definitions and prompt wrapper from
`pi_agentic_benchmark.py` so the agent-facing workload matches Agentic 001 as
closely as possible while removing cross-task warm retention.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from pi_agentic_benchmark import MODEL_ID, PI_MODELS, TASKS, task_prompt


HISTORICAL = {
    "T01": {"warm_size_gb": 4.4, "tool_count": 2, "usage_total": 2474},
    "T02": {"warm_size_gb": 5.2, "tool_count": 8, "usage_total": 4240},
    "T03": {"warm_size_gb": 5.6, "tool_count": 2, "usage_total": 2923},
    "T04": {"warm_size_gb": 6.4, "tool_count": 5, "usage_total": 4213},
    "T05": {"warm_size_gb": 6.8, "tool_count": 3, "usage_total": 2581},
    "T06": {"warm_size_gb": 7.2, "tool_count": 2, "usage_total": 3778},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 30, env: dict | None = None) -> dict:
    try:
        proc = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "error": f"{type(exc).__name__}: {exc}"}


def parse_swap_mb(text: str) -> float | None:
    match = re.search(r"used\s*=\s*([0-9.,]+)M", text)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


def parse_free_percent(text: str) -> int | None:
    match = re.search(r"([0-9]+)%", text)
    return int(match.group(1)) if match else None


def parse_ollama_ps(text: str) -> dict:
    result = {
        "loaded": False,
        "reported_size_gb": None,
        "context": None,
        "processor": None,
    }
    row = next((line.strip() for line in text.splitlines() if MODEL_ID in line), "")
    if not row:
        return result

    result["loaded"] = True
    size = re.search(r"\s([0-9]+(?:\.[0-9]+)?)\s+GB\s", row)
    if size:
        result["reported_size_gb"] = float(size.group(1))

    processor = re.search(r"(\d+%\s+(?:GPU|CPU))", row)
    if processor:
        result["processor"] = processor.group(1)

    context = re.search(r"(?:GPU|CPU)\s+(\d+)\s+", row)
    if context:
        result["context"] = int(context.group(1))

    return result


def memory_snapshot(repo_root: Path) -> dict:
    top = run(["top", "-l", "1", "-n", "0"], repo_root)
    physmem = next(
        (line for line in top.get("stdout", "").splitlines() if line.startswith("PhysMem:")),
        "",
    )

    pressure = run(["memory_pressure"], repo_root)
    pressure_line = next(
        (line.strip() for line in reversed(pressure.get("stdout", "").splitlines()) if line.strip()),
        "",
    )

    swap = run(["sysctl", "vm.swapusage"], repo_root).get("stdout", "").strip()
    ollama_ps = run(["ollama", "ps"], repo_root).get("stdout", "").strip()

    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "memory_free_percent": parse_free_percent(pressure_line),
        "swap": swap,
        "swap_used_mb": parse_swap_mb(swap),
        "ollama_ps": ollama_ps,
        "ollama": parse_ollama_ps(ollama_ps),
    }


def parse_jsonl(text: str) -> tuple[list[dict], list[str]]:
    events: list[dict] = []
    errors: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception as exc:
            errors.append(f"line {index}: {type(exc).__name__}: {exc}")
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events, errors


def summarize_events(events: list[dict]) -> dict:
    tools: list[str] = []
    text_parts: list[str] = []
    event_errors: list[str] = []
    last_usage = None

    for event in events:
        typ = event.get("type")
        if typ == "tool_execution_start":
            name = event.get("toolName")
            if isinstance(name, str):
                tools.append(name)

        if typ == "message_update":
            usage = event.get("usage")
            if isinstance(usage, dict) and (usage.get("totalTokens", 0) or 0):
                last_usage = usage

            update = event.get("assistantMessageEvent")
            if isinstance(update, dict) and update.get("type") == "text_delta":
                delta = update.get("delta")
                if isinstance(delta, str):
                    text_parts.append(delta)

        if typ in {"error", "auto_retry_end"}:
            event_errors.append(json.dumps(event, ensure_ascii=False))

    return {
        "tool_names": tools,
        "final_text": "".join(text_parts).strip(),
        "event_errors": event_errors,
        "last_nonzero_usage": last_usage,
    }


def guard_triggered(snapshot: dict, min_free_percent: int, max_swap_mb: float) -> tuple[bool, str]:
    free = snapshot.get("memory_free_percent")
    swap = snapshot.get("swap_used_mb")
    if isinstance(free, int) and free < min_free_percent:
        return True, f"memory free {free}% < guard {min_free_percent}%"
    if isinstance(swap, (int, float)) and swap > max_swap_mb:
        return True, f"swap used {swap:.2f} MB > guard {max_swap_mb:.2f} MB"
    return False, ""


def print_record(record: dict) -> None:
    after = record["memory_after"]
    ollama = after.get("ollama", {})
    usage = record.get("last_nonzero_usage") or {}
    hist = record["historical_reference"]
    print(
        f"{record['id']}: process_ok={record['process_ok']} "
        f"tools={record['tool_count']} (hist={hist['tool_count']}) "
        f"usage={usage.get('totalTokens')} (hist={hist['usage_total']}) "
        f"wall={record['wall_seconds']}s "
        f"cold_size={ollama.get('reported_size_gb')}GB "
        f"warm_hist={hist['warm_size_gb']}GB "
        f"context={ollama.get('context')} "
        f"swap={after.get('swap_used_mb')}MB "
        f"free={after.get('memory_free_percent')}%"
    )
    if not record["process_ok"]:
        print(f"  final_text={record['final_text']!r}")
        print(f"  event_errors={record['event_errors']}")
        print(f"  jsonl_parse_errors={record['jsonl_parse_errors']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--task-timeout", type=int, default=300)
    parser.add_argument("--min-free-percent", type=int, default=8)
    parser.add_argument("--max-swap-mb", type=float, default=5600.0)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    frozen = repo_root / "benchmarks" / "coding" / "v1"
    if not frozen.exists():
        raise SystemExit(f"Frozen benchmark not found: {frozen}")
    manifest = json.loads((frozen / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "1.0.1":
        raise SystemExit(f"Expected benchmark v1.0.1, found {manifest.get('version')}")
    if shutil.which("pi") is None or shutil.which("ollama") is None:
        raise SystemExit("pi and ollama must be in PATH")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo_root / "results-local" / "pi-agentic-cold-replay" / run_id
    raw_dir = run_dir / "raw"
    archive_dir = run_dir / "workspaces"
    pi_agent_dir = run_dir / "pi-agent"
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    pi_agent_dir.mkdir(parents=True, exist_ok=True)
    (pi_agent_dir / "models.json").write_text(
        json.dumps(PI_MODELS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    pi_env = os.environ.copy()
    pi_env.update(
        {
            "PI_CODING_AGENT_DIR": str(pi_agent_dir),
            "PI_OFFLINE": "1",
            "PI_SKIP_VERSION_CHECK": "1",
            "PI_TELEMETRY": "0",
        }
    )

    summary = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "Pi Agentic Cold Replay 001",
        "benchmark": manifest.get("benchmark"),
        "benchmark_version": manifest.get("version"),
        "model": MODEL_ID,
        "context": 4096,
        "historical_reference_run": "20260818-214848",
        "guardrails": {
            "min_free_percent": args.min_free_percent,
            "max_swap_mb": args.max_swap_mb,
        },
        "initial_memory": memory_snapshot(repo_root),
        "tasks": [],
        "aborted": False,
        "abort_reason": None,
    }

    print("LOOM Pi Agentic Cold Replay 001")
    print("=== COLD TASK REPLAY ===")

    with tempfile.TemporaryDirectory(prefix=f"loom-pi-cold-replay-{run_id}-") as tmp:
        temp_root = Path(tmp)

        for index, task in enumerate(TASKS, start=1):
            run(["ollama", "stop", MODEL_ID], repo_root)
            after_stop = memory_snapshot(repo_root)
            triggered, reason = guard_triggered(after_stop, args.min_free_percent, args.max_swap_mb)
            if triggered:
                summary["aborted"] = True
                summary["abort_reason"] = f"before {task['id']}: {reason}"
                print(f"ABORT before {task['id']}: {reason}")
                break

            frozen_task = frozen / task["path"]
            workspace = temp_root / task["id"]
            workspace.mkdir(parents=True, exist_ok=True)

            copied = set(task["context"])
            for name in task["editable"]:
                if (frozen_task / name).exists():
                    copied.add(name)
            for name in sorted(copied):
                src = frozen_task / name
                if not src.exists():
                    raise RuntimeError(f"Missing benchmark input {task['id']}/{name}")
                shutil.copy2(src, workspace / name)

            prompt = task_prompt(frozen_task, task)
            command = [
                "pi",
                "--provider", "ollama",
                "--model", MODEL_ID,
                "--tools", "read,write,edit",
                "--no-extensions",
                "--no-skills",
                "--no-prompt-templates",
                "--no-themes",
                "--no-context-files",
                "--no-approve",
                "--no-session",
                "--mode", "json",
                "-p", prompt,
            ]

            started = time.perf_counter()
            try:
                proc = subprocess.run(
                    command,
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    timeout=args.task_timeout,
                    env=pi_env,
                )
                exit_code = proc.returncode
                stdout = proc.stdout
                stderr = proc.stderr
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                exit_code = None
                stdout = exc.stdout if isinstance(exc.stdout, str) else ""
                stderr = exc.stderr if isinstance(exc.stderr, str) else ""
                timed_out = True

            wall_seconds = round(time.perf_counter() - started, 3)
            (raw_dir / f"{task['id']}-pi.jsonl").write_text(stdout, encoding="utf-8")
            (raw_dir / f"{task['id']}-stderr.txt").write_text(stderr, encoding="utf-8")
            events, parse_errors = parse_jsonl(stdout)
            event_summary = summarize_events(events)
            after = memory_snapshot(repo_root)

            archive = archive_dir / task["id"]
            shutil.copytree(workspace, archive)

            process_ok = (
                exit_code == 0
                and not timed_out
                and not parse_errors
                and not event_summary["event_errors"]
            )
            hist = HISTORICAL[task["id"]]
            record = {
                "id": task["id"],
                "index": index,
                "command": command,
                "exit_code": exit_code,
                "timed_out": timed_out,
                "process_ok": process_ok,
                "wall_seconds": wall_seconds,
                "tool_names": event_summary["tool_names"],
                "tool_count": len(event_summary["tool_names"]),
                "final_text": event_summary["final_text"],
                "event_errors": event_summary["event_errors"],
                "jsonl_parse_errors": parse_errors,
                "last_nonzero_usage": event_summary["last_nonzero_usage"],
                "memory_after_stop_before_task": after_stop,
                "memory_after": after,
                "historical_reference": hist,
            }
            summary["tasks"].append(record)
            print_record(record)

    run(["ollama", "stop", MODEL_ID], repo_root)
    summary["final_after_stop"] = memory_snapshot(repo_root)
    summary["finished_at_utc"] = utc_now()

    summary_path = run_dir / "replay-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("=== COMPLETE ===")
    print(f"aborted={summary['aborted']} reason={summary['abort_reason']}")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
