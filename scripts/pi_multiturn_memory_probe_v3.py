#!/usr/bin/env python3
"""LOOM Pi Multi-turn Memory Probe 003.

Measures true model->tool->result->model depth with a run-local custom Pi tool.
The tool takes no arguments. The extension allows at most one probe_step call per
LLM turn and advances one internal step per successful call. The runner validates
that the requested number of successful tool calls occurred in distinct Pi turns.

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
                    "name": "Qwen 3.5 4B MLX (Ollama / LOOM turn-gated probe)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 4096,
                    "maxTokens": 2048,
                    "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                }
            ],
        }
    }
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 30, env: dict | None = None) -> dict:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return {"command": args, "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "error": f"{type(exc).__name__}: {exc}"}


def parse_swap_mb(text: str) -> float | None:
    m = re.search(r"used\s*=\s*([0-9.,]+)M", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def parse_free_percent(text: str) -> int | None:
    m = re.search(r"([0-9]+)%", text)
    return int(m.group(1)) if m else None


def parse_ollama_ps(text: str) -> dict:
    result = {"loaded": False, "reported_size_gb": None, "context": None, "processor": None}
    row = next((line.strip() for line in text.splitlines() if MODEL_ID in line), "")
    if not row:
        return result
    result["loaded"] = True
    m = re.search(r"\s([0-9]+(?:\.[0-9]+)?)\s+GB\s", row)
    if m:
        result["reported_size_gb"] = float(m.group(1))
    m = re.search(r"(\d+%\s+(?:GPU|CPU))", row)
    if m:
        result["processor"] = m.group(1)
    m = re.search(r"(?:GPU|CPU)\s+(\d+)\s+", row)
    if m:
        result["context"] = int(m.group(1))
    return result


def memory_snapshot(repo_root: Path) -> dict:
    top = run(["top", "-l", "1", "-n", "0"], repo_root)
    physmem = next((x for x in top.get("stdout", "").splitlines() if x.startswith("PhysMem:")), "")
    pressure = run(["memory_pressure"], repo_root)
    pressure_line = next((x.strip() for x in reversed(pressure.get("stdout", "").splitlines()) if x.strip()), "")
    swap = run(["sysctl", "vm.swapusage"], repo_root).get("stdout", "").strip()
    ps = run(["ollama", "ps"], repo_root).get("stdout", "").strip()
    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "memory_free_percent": parse_free_percent(pressure_line),
        "swap": swap,
        "swap_used_mb": parse_swap_mb(swap),
        "ollama_ps": ps,
        "ollama": parse_ollama_ps(ps),
    }


def parse_jsonl(text: str) -> tuple[list[dict], list[str]]:
    events, errors = [], []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                events.append(obj)
        except Exception as exc:
            errors.append(f"line {i}: {type(exc).__name__}: {exc}")
    return events, errors


def summarize_events(events: list[dict]) -> dict:
    turn_index = 0
    starts, ends, text_parts, event_errors = [], [], [], []
    last_usage = None

    for event in events:
        typ = event.get("type")
        if typ == "turn_start":
            turn_index += 1
        elif typ == "tool_execution_start":
            starts.append({
                "tool": event.get("toolName"),
                "args": event.get("args") if isinstance(event.get("args"), dict) else {},
                "turn_index": turn_index,
                "tool_call_id": event.get("toolCallId"),
            })
        elif typ == "tool_execution_end":
            result = event.get("result") if isinstance(event.get("result"), dict) else {}
            details = result.get("details") if isinstance(result.get("details"), dict) else {}
            ends.append({
                "tool": event.get("toolName"),
                "is_error": bool(event.get("isError")),
                "details": details,
                "tool_call_id": event.get("toolCallId"),
            })
        elif typ == "message_update":
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
        "turn_count": turn_index,
        "tool_starts": starts,
        "tool_ends": ends,
        "final_text": "".join(text_parts).strip(),
        "event_errors": event_errors,
        "last_nonzero_usage": last_usage,
    }


def run_condition(*, label: str, depth: int, repo_root: Path, workspace: Path,
                  pi_agent_dir: Path, extension_path: Path, raw_dir: Path,
                  timeout: int) -> dict:
    env = os.environ.copy()
    env.update({
        "PI_CODING_AGENT_DIR": str(pi_agent_dir),
        "PI_OFFLINE": "1",
        "PI_SKIP_VERSION_CHECK": "1",
        "PI_TELEMETRY": "0",
        "LOOM_PROBE_DEPTH": str(depth),
    })

    before = memory_snapshot(repo_root)
    prompt = (
        "LOOM Pi Multi-turn Memory Probe 003. Use ONLY the probe_step tool. "
        "Call probe_step exactly once now. After each tool result, obey it exactly: "
        "if it says CONTINUE, wait for that result and then call probe_step exactly once "
        "in the next model turn; never emit two tool calls in one assistant response. "
        "If it says STOP, make no more tool calls and reply exactly DONE with no explanation."
    )
    command = [
        "pi", "--provider", "ollama", "--model", MODEL_ID,
        "--no-builtin-tools", "--tools", "probe_step",
        "--extension", str(extension_path), "--no-extensions",
        "--no-skills", "--no-prompt-templates", "--no-themes", "--no-context-files",
        "--no-approve", "--no-session", "--mode", "json", "-p", prompt,
    ]

    started = time.perf_counter()
    try:
        proc = subprocess.run(command, cwd=workspace, capture_output=True, text=True, timeout=timeout, env=env)
        exit_code, stdout, stderr, timed_out = proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        timed_out = True
    wall = round(time.perf_counter() - started, 3)

    (raw_dir / f"{label}-pi.jsonl").write_text(stdout, encoding="utf-8")
    (raw_dir / f"{label}-stderr.txt").write_text(stderr, encoding="utf-8")
    events, parse_errors = parse_jsonl(stdout)
    s = summarize_events(events)
    after = memory_snapshot(repo_root)

    starts = [x for x in s["tool_starts"] if x.get("tool") == "probe_step"]
    ends = [x for x in s["tool_ends"] if x.get("tool") == "probe_step"]
    advanced = [x for x in ends if x.get("details", {}).get("advanced") is True]
    other_tools = [x for x in s["tool_starts"] if x.get("tool") != "probe_step"]
    tool_turns = [x.get("turn_index") for x in starts]
    distinct_tool_turns = len(set(tool_turns)) == len(tool_turns)
    blocked_same_turn = max(
        [int(x.get("details", {}).get("blockedSameTurn", 0) or 0) for x in ends] or [0]
    )

    success = (
        exit_code == 0 and not timed_out and not parse_errors and not s["event_errors"]
        and s["final_text"] == "DONE" and len(starts) == depth and len(ends) == depth
        and len(advanced) == depth and not other_tools and distinct_tool_turns
        and blocked_same_turn == 0 and all(x.get("is_error") is False for x in ends)
        and (ends[-1].get("details", {}).get("stop") is True if ends else False)
        and (ends[-1].get("details", {}).get("completed") == depth if ends else False)
    )

    return {
        "label": label,
        "target_depth": depth,
        "success": success,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "wall_seconds": wall,
        "tool_call_count": len(starts),
        "advanced_count": len(advanced),
        "tool_turn_indices": tool_turns,
        "distinct_tool_turns": distinct_tool_turns,
        "blocked_same_turn": blocked_same_turn,
        "turn_count": s["turn_count"],
        "other_tools": other_tools,
        "final_text": s["final_text"],
        "event_errors": s["event_errors"],
        "jsonl_parse_errors": parse_errors,
        "last_nonzero_usage": s["last_nonzero_usage"],
        "memory_before": before,
        "memory_after": after,
    }


def guard(snapshot: dict, min_free: int, max_swap: float) -> tuple[bool, str]:
    free = snapshot.get("memory_free_percent")
    swap = snapshot.get("swap_used_mb")
    if isinstance(free, int) and free < min_free:
        return True, f"memory free {free}% < {min_free}%"
    if isinstance(swap, (int, float)) and swap > max_swap:
        return True, f"swap {swap:.2f} MB > {max_swap:.2f} MB"
    return False, ""


def print_record(r: dict) -> None:
    a = r["memory_after"]
    o = a.get("ollama", {})
    u = r.get("last_nonzero_usage") or {}
    print(
        f"{r['label']}: success={r['success']} depth={r['target_depth']} "
        f"calls={r['tool_call_count']} advanced={r['advanced_count']} "
        f"distinct_turns={r['distinct_tool_turns']} blocked_same_turn={r['blocked_same_turn']} "
        f"wall={r['wall_seconds']}s ollama_size={o.get('reported_size_gb')}GB "
        f"context={o.get('context')} swap={a.get('swap_used_mb')}MB "
        f"free={a.get('memory_free_percent')}% usage_total={u.get('totalTokens')}"
    )
    if not r["success"]:
        print(f"  tool_turn_indices={r['tool_turn_indices']}")
        print(f"  turn_count={r['turn_count']}")
        print(f"  final_text={r['final_text']!r}")
        print(f"  other_tools={r['other_tools']}")
        print(f"  event_errors={r['event_errors']}")
        print(f"  jsonl_parse_errors={r['jsonl_parse_errors']}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--task-timeout", type=int, default=300)
    p.add_argument("--min-free-percent", type=int, default=8)
    p.add_argument("--max-swap-mb", type=float, default=5600.0)
    args = p.parse_args()

    repo = args.repo_root.resolve()
    extension = repo / "scripts" / "pi_probe_step_extension_v3.ts"
    if not extension.exists():
        raise SystemExit(f"Missing extension: {extension}")
    if shutil.which("pi") is None or shutil.which("ollama") is None:
        raise SystemExit("pi and ollama must be in PATH")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo / "results-local" / "pi-multiturn-memory-v3" / run_id
    raw = run_dir / "raw"
    workspace = run_dir / "workspace"
    agent_dir = run_dir / "pi-agent"
    raw.mkdir(parents=True, exist_ok=True)
    workspace.mkdir(parents=True, exist_ok=True)
    agent_dir.mkdir(parents=True, exist_ok=True)
    (agent_dir / "models.json").write_text(json.dumps(PI_MODELS, indent=2) + "\n", encoding="utf-8")

    summary = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "Pi Multi-turn Memory Probe 003",
        "model": MODEL_ID,
        "context": 4096,
        "conditions": [],
        "initial_memory": memory_snapshot(repo),
    }

    print("LOOM Pi Multi-turn Memory Probe 003")
    print("=== COLD DEPTH ARM ===")
    deepest_valid = False
    for label, depth in [("cold-1turn", 1), ("cold-4turn", 4), ("cold-8turn", 8)]:
        run(["ollama", "stop", MODEL_ID], repo)
        rec = run_condition(
            label=label,
            depth=depth,
            repo_root=repo,
            workspace=workspace,
            pi_agent_dir=agent_dir,
            extension_path=extension,
            raw_dir=raw,
            timeout=args.task_timeout,
        )
        summary["conditions"].append(rec)
        print_record(rec)
        triggered, reason = guard(rec["memory_after"], args.min_free_percent, args.max_swap_mb)
        if label == "cold-8turn":
            deepest_valid = rec["success"] and not triggered
            if triggered:
                print(f"Guardrail after cold-8turn: {reason}")

    print("=== WARM RETENTION ARM ===")
    if deepest_valid:
        rec = run_condition(
            label="warm-1turn-after-8",
            depth=1,
            repo_root=repo,
            workspace=workspace,
            pi_agent_dir=agent_dir,
            extension_path=extension,
            raw_dir=raw,
            timeout=args.task_timeout,
        )
        summary["conditions"].append(rec)
        print_record(rec)
    else:
        print("warm-1turn-after-8: SKIPPED — cold-8turn invalid or guardrail prevented warm follow-up")

    run(["ollama", "stop", MODEL_ID], repo)
    summary["final_after_stop"] = memory_snapshot(repo)
    summary["finished_at_utc"] = utc_now()
    out = run_dir / "probe-summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("=== COMPLETE ===")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
