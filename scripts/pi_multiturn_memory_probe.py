#!/usr/bin/env python3
"""LOOM Pi Multi-turn Memory Probe 001.

Forces sequential read-tool chains of different depths inside one Pi session and
measures post-session Ollama SIZE/memory state. The next path is revealed only by
the preceding file content, forcing model->tool->result->model round trips.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

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
                    "name": "Qwen 3.5 4B MLX (Ollama / LOOM multi-turn probe)",
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

    row = next((line for line in lines[1:] if MODEL_ID in line), "")
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


def safe_relative_path(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or not value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts


def summarize_events(events: list[dict]) -> dict:
    tool_calls: list[dict] = []
    text_parts: list[str] = []
    event_errors: list[str] = []
    last_usage = None

    for event in events:
        if event.get("type") == "tool_execution_start":
            name = event.get("toolName")
            args = event.get("args") if isinstance(event.get("args"), dict) else {}
            path = args.get("path")
            tool_calls.append(
                {
                    "tool": name,
                    "path": path,
                    "path_safe": safe_relative_path(path),
                    "args_keys": sorted(args.keys()),
                }
            )

        if event.get("type") == "message_update":
            usage = event.get("usage")
            if isinstance(usage, dict) and (usage.get("totalTokens", 0) or 0):
                last_usage = usage

            update = event.get("assistantMessageEvent")
            if isinstance(update, dict) and update.get("type") == "text_delta":
                delta = update.get("delta")
                if isinstance(delta, str):
                    text_parts.append(delta)

        if event.get("type") in {"error", "auto_retry_end"}:
            event_errors.append(json.dumps(event, ensure_ascii=False))

    return {
        "tool_calls": tool_calls,
        "final_text": "".join(text_parts).strip(),
        "event_errors": event_errors,
        "last_nonzero_usage": last_usage,
    }


def make_chain(workspace: Path, prefix: str, length: int) -> list[str]:
    names = [f"{prefix}-{i:02d}.txt" for i in range(1, length + 1)]
    for index, name in enumerate(names):
        if index + 1 < len(names):
            content = f"CHAIN={prefix}\nSTEP={index + 1}\nNEXT: {names[index + 1]}\n"
        else:
            content = f"CHAIN={prefix}\nSTEP={index + 1}\nSTOP\n"
        (workspace / name).write_text(content, encoding="utf-8")
    return names


def run_condition(
    *,
    label: str,
    expected_paths: list[str],
    repo_root: Path,
    workspace: Path,
    pi_env: dict,
    raw_dir: Path,
    timeout: int,
) -> dict:
    before = memory_snapshot(repo_root)
    start_file = expected_paths[0]
    prompt = (
        "LOOM Pi Multi-turn Memory Probe 001. Work only in the current directory. "
        f"Start by reading {start_file} with the read tool. Each file contains either "
        "a line beginning with NEXT: followed by the exact filename you must read next, "
        "or STOP. You MUST learn each next filename from the preceding read result; follow "
        "the chain exactly until STOP. Do not read any other file. Do not modify or create "
        "files. When STOP is reached, reply exactly DONE with no explanation."
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
    read_calls = [call for call in event_summary["tool_calls"] if call.get("tool") == "read"]
    observed_paths = [call.get("path") for call in read_calls]
    all_paths_safe = all(call.get("path_safe") is True for call in event_summary["tool_calls"])
    expected_exact = observed_paths == expected_paths
    after = memory_snapshot(repo_root)

    success = (
        exit_code == 0
        and not timed_out
        and not parse_errors
        and not event_summary["event_errors"]
        and event_summary["final_text"] == "DONE"
        and expected_exact
        and all_paths_safe
        and len(event_summary["tool_calls"]) == len(expected_paths)
    )

    return {
        "label": label,
        "expected_paths": expected_paths,
        "observed_paths": observed_paths,
        "tool_calls": event_summary["tool_calls"],
        "read_count": len(read_calls),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "wall_seconds": wall_seconds,
        "success": success,
        "final_text": event_summary["final_text"],
        "event_errors": event_summary["event_errors"],
        "jsonl_parse_errors": parse_errors,
        "paths_safe": all_paths_safe,
        "expected_exact": expected_exact,
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


def print_record(record: dict) -> None:
    after = record["memory_after"]
    ollama = after.get("ollama", {})
    usage = record.get("last_nonzero_usage") or {}
    print(
        f"{record['label']}: success={record['success']} reads={record['read_count']} "
        f"wall={record['wall_seconds']}s ollama_size={ollama.get('reported_size_gb')}GB "
        f"context={ollama.get('context')} swap={after.get('swap_used_mb')}MB "
        f"free={after.get('memory_free_percent')}% usage_total={usage.get('totalTokens')}"
    )
    if not record["success"]:
        print(f"  observed_paths={record['observed_paths']}")
        print(f"  expected_paths={record['expected_paths']}")
        print(f"  final_text={record['final_text']!r}")
        print(f"  event_errors={record['event_errors']}")
        print(f"  jsonl_parse_errors={record['jsonl_parse_errors']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--task-timeout", type=int, default=240)
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
    run_dir = repo_root / "results-local" / "pi-multiturn-memory" / run_id
    raw_dir = run_dir / "raw"
    workspace = run_dir / "workspace"
    pi_agent_dir = run_dir / "pi-agent"
    raw_dir.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)
    pi_agent_dir.mkdir(parents=True, exist_ok=True)

    chains = {
        "cold-1turn": make_chain(workspace, "one", 1),
        "cold-4turn": make_chain(workspace, "four", 4),
        "cold-8turn": make_chain(workspace, "eight", 8),
    }
    chains["warm-1turn-after-8"] = chains["cold-1turn"]

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
        "experiment": "Pi Multi-turn Memory Probe 001",
        "model": MODEL_ID,
        "context": 4096,
        "guardrails": {
            "min_free_percent": args.min_free_percent,
            "max_swap_mb": args.max_swap_mb,
        },
        "initial_memory": memory_snapshot(repo_root),
        "conditions": [],
    }

    print("LOOM Pi Multi-turn Memory Probe 001")
    print("=== COLD DEPTH ARM ===")

    warm_allowed = True
    for label in ("cold-1turn", "cold-4turn", "cold-8turn"):
        run(["ollama", "stop", MODEL_ID], repo_root)
        after_stop = memory_snapshot(repo_root)
        pre_guard, pre_reason = guard_triggered(after_stop, args.min_free_percent, args.max_swap_mb)
        if pre_guard:
            print(f"{label}: ABORT before call — {pre_reason}")
            summary["conditions"].append(
                {
                    "label": label,
                    "aborted_before_call": True,
                    "abort_reason": pre_reason,
                    "memory_after_stop": after_stop,
                }
            )
            warm_allowed = False
            break

        record = run_condition(
            label=label,
            expected_paths=chains[label],
            repo_root=repo_root,
            workspace=workspace,
            pi_env=pi_env,
            raw_dir=raw_dir,
            timeout=args.task_timeout,
        )
        record["memory_after_stop_before_call"] = after_stop
        summary["conditions"].append(record)
        print_record(record)

        post_guard, post_reason = guard_triggered(record["memory_after"], args.min_free_percent, args.max_swap_mb)
        if post_guard:
            print(f"Guardrail after {label}: {post_reason}")
            run(["ollama", "stop", MODEL_ID], repo_root)
            warm_allowed = False
            if label != "cold-8turn":
                continue

    print("=== WARM RETENTION ARM ===")
    cold8 = next((r for r in summary["conditions"] if r.get("label") == "cold-8turn"), None)
    if warm_allowed and cold8 and cold8.get("success"):
        record = run_condition(
            label="warm-1turn-after-8",
            expected_paths=chains["warm-1turn-after-8"],
            repo_root=repo_root,
            workspace=workspace,
            pi_env=pi_env,
            raw_dir=raw_dir,
            timeout=args.task_timeout,
        )
        summary["conditions"].append(record)
        print_record(record)
    else:
        reason = "cold-8turn unavailable/invalid or guardrail prevented warm follow-up"
        print(f"warm-1turn-after-8: SKIPPED — {reason}")
        summary["conditions"].append(
            {
                "label": "warm-1turn-after-8",
                "skipped": True,
                "skip_reason": reason,
            }
        )

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
