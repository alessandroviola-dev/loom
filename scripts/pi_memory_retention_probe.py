#!/usr/bin/env python3
"""LOOM Pi Memory Retention Probe 001.

Runs an identical tiny Pi/read task repeatedly in two preregistered arms:
- warm: separate Pi processes without unloading Ollama between calls;
- cold: unload Ollama before every call.

Captures macOS memory/swap, Ollama reported size/context, Pi JSONL usage and
protocol success. Uses an isolated PI_CODING_AGENT_DIR and never touches the
user's normal Pi configuration.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID = "qwen3.5:4b-mlx"

PI_MODELS = {
    "providers": {
        "ollama": {
            "baseUrl": "http://localhost:11434/v1",
            "api": "openai-completions",
            "apiKey": "ollama",
            "compat": {
                "supportsDeveloperRole": False,
                "supportsReasoningEffort": False,
            },
            "models": [
                {
                    "id": MODEL_ID,
                    "name": "Qwen 3.5 4B MLX (Ollama / LOOM memory probe)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 4096,
                    "maxTokens": 2048,
                    "cost": {
                        "input": 0,
                        "output": 0,
                        "cacheRead": 0,
                        "cacheWrite": 0,
                    },
                }
            ],
        }
    }
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
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return result

    row = lines[1]
    if MODEL_ID not in row:
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
    physmem = ""
    for line in top.get("stdout", "").splitlines():
        if line.startswith("PhysMem:"):
            physmem = line
            break

    pressure = run(["memory_pressure"], repo_root)
    pressure_line = ""
    for line in reversed(pressure.get("stdout", "").splitlines()):
        if line.strip():
            pressure_line = line.strip()
            break

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
        if event.get("type") == "tool_execution_start":
            name = event.get("toolName")
            if isinstance(name, str):
                tools.append(name)

        if event.get("type") == "message_update":
            usage = event.get("usage")
            if isinstance(usage, dict):
                total = usage.get("totalTokens", 0) or 0
                if total:
                    last_usage = usage

            update = event.get("assistantMessageEvent")
            if isinstance(update, dict) and update.get("type") == "text_delta":
                delta = update.get("delta")
                if isinstance(delta, str):
                    text_parts.append(delta)

        if event.get("type") in {"error", "auto_retry_end"}:
            event_errors.append(json.dumps(event, ensure_ascii=False))

    return {
        "tool_names": tools,
        "final_text": "".join(text_parts).strip(),
        "event_errors": event_errors,
        "last_nonzero_usage": last_usage,
    }


def run_probe_call(
    *,
    repo_root: Path,
    workspace: Path,
    pi_env: dict,
    timeout: int,
    label: str,
    raw_dir: Path,
) -> dict:
    before = memory_snapshot(repo_root)
    prompt = (
        "LOOM Memory Retention Probe 001. Work only in the current directory. "
        "Use the read tool to read probe.txt. Do not modify or create any file. "
        "After reading it, reply exactly DONE with no explanation."
    )
    command = [
        "pi",
        "--provider",
        "ollama",
        "--model",
        MODEL_ID,
        "--tools",
        "read",
        "--no-extensions",
        "--no-skills",
        "--no-prompt-templates",
        "--no-themes",
        "--no-context-files",
        "--no-approve",
        "--no-session",
        "--mode",
        "json",
        "-p",
        prompt,
    ]

    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=timeout,
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
    (raw_dir / f"{label}-pi.jsonl").write_text(stdout, encoding="utf-8")
    (raw_dir / f"{label}-stderr.txt").write_text(stderr, encoding="utf-8")

    events, parse_errors = parse_jsonl(stdout)
    event_summary = summarize_events(events)
    after = memory_snapshot(repo_root)

    success = (
        exit_code == 0
        and not timed_out
        and "read" in event_summary["tool_names"]
        and event_summary["final_text"] == "DONE"
        and not parse_errors
        and not event_summary["event_errors"]
    )

    return {
        "label": label,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "wall_seconds": wall_seconds,
        "success": success,
        "tool_names": event_summary["tool_names"],
        "final_text": event_summary["final_text"],
        "event_errors": event_summary["event_errors"],
        "jsonl_parse_errors": parse_errors,
        "last_nonzero_usage": event_summary["last_nonzero_usage"],
        "memory_before": before,
        "memory_after": after,
    }


def guard_triggered(snapshot: dict, min_free_percent: int, max_swap_mb: float) -> tuple[bool, str]:
    free_pct = snapshot.get("memory_free_percent")
    swap_mb = snapshot.get("swap_used_mb")
    if isinstance(free_pct, int) and free_pct < min_free_percent:
        return True, f"memory free {free_pct}% < guard {min_free_percent}%"
    if isinstance(swap_mb, (int, float)) and swap_mb > max_swap_mb:
        return True, f"swap used {swap_mb:.2f} MB > guard {max_swap_mb:.2f} MB"
    return False, ""


def print_iteration(record: dict) -> None:
    after = record["memory_after"]
    ollama = after.get("ollama", {})
    usage = record.get("last_nonzero_usage") or {}
    print(
        f"{record['label']}: success={record['success']} "
        f"wall={record['wall_seconds']}s "
        f"ollama_size={ollama.get('reported_size_gb')}GB "
        f"context={ollama.get('context')} "
        f"swap={after.get('swap_used_mb')}MB "
        f"free={after.get('memory_free_percent')}% "
        f"usage_total={usage.get('totalTokens')}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--warm-count", type=int, default=4)
    parser.add_argument("--cold-count", type=int, default=2)
    parser.add_argument("--task-timeout", type=int, default=180)
    parser.add_argument("--min-free-percent", type=int, default=8)
    parser.add_argument("--max-swap-mb", type=float, default=5600.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if shutil.which("pi") is None:
        raise SystemExit("pi executable not found in PATH")
    if shutil.which("ollama") is None:
        raise SystemExit("ollama executable not found in PATH")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo_root / "results-local" / "memory-retention" / run_id
    raw_dir = run_dir / "raw"
    workspace = run_dir / "workspace"
    pi_agent_dir = run_dir / "pi-agent"
    raw_dir.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)
    pi_agent_dir.mkdir(parents=True, exist_ok=True)

    (workspace / "probe.txt").write_text("LOOM_MEMORY_PROBE\n", encoding="utf-8")
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
        "experiment": "Pi Memory Retention Probe 001",
        "model": MODEL_ID,
        "context": 4096,
        "warm_count_planned": args.warm_count,
        "cold_count_planned": args.cold_count,
        "guardrails": {
            "min_free_percent": args.min_free_percent,
            "max_swap_mb": args.max_swap_mb,
        },
        "initial_memory": memory_snapshot(repo_root),
        "warm": [],
        "cold": [],
        "warm_aborted": False,
        "warm_abort_reason": None,
    }

    print("LOOM Pi Memory Retention Probe 001")
    print("=== WARM ARM ===")
    run(["ollama", "stop", MODEL_ID], repo_root)
    summary["warm_after_initial_stop"] = memory_snapshot(repo_root)

    for index in range(1, args.warm_count + 1):
        label = f"warm-{index:02d}"
        record = run_probe_call(
            repo_root=repo_root,
            workspace=workspace,
            pi_env=pi_env,
            timeout=args.task_timeout,
            label=label,
            raw_dir=raw_dir,
        )
        summary["warm"].append(record)
        print_iteration(record)
        triggered, reason = guard_triggered(record["memory_after"], args.min_free_percent, args.max_swap_mb)
        if triggered:
            summary["warm_aborted"] = True
            summary["warm_abort_reason"] = reason
            print(f"Warm arm guardrail triggered: {reason}")
            run(["ollama", "stop", MODEL_ID], repo_root)
            break

    print("=== COLD ARM ===")
    for index in range(1, args.cold_count + 1):
        run(["ollama", "stop", MODEL_ID], repo_root)
        after_stop = memory_snapshot(repo_root)
        label = f"cold-{index:02d}"
        record = run_probe_call(
            repo_root=repo_root,
            workspace=workspace,
            pi_env=pi_env,
            timeout=args.task_timeout,
            label=label,
            raw_dir=raw_dir,
        )
        record["memory_after_stop_before_call"] = after_stop
        summary["cold"].append(record)
        print_iteration(record)

    run(["ollama", "stop", MODEL_ID], repo_root)
    summary["final_after_stop"] = memory_snapshot(repo_root)
    summary["finished_at_utc"] = utc_now()

    summary_path = run_dir / "probe-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("=== COMPLETE ===")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
