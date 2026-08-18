#!/usr/bin/env python3
"""LOOM Pi read-only smoke test at context 4096.

Uses the existing Pi installation but selects Ollama/Qwen only for this invocation.
The run is ephemeral (--no-session) and exposes only the built-in read tool.
It captures JSONL events, tool use, final text, memory/swap/Ollama state, and Git status.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 20) -> dict:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "error": f"{type(exc).__name__}: {exc}"}


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

    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "swap": run(["sysctl", "vm.swapusage"], repo_root).get("stdout", "").strip(),
        "ollama_ps": run(["ollama", "ps"], repo_root).get("stdout", "").strip(),
    }


def git_status(repo_root: Path) -> str:
    return run(["git", "status", "--porcelain"], repo_root).get("stdout", "")


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


def summarize(events: list[dict]) -> dict:
    tools: list[str] = []
    final_text_parts: list[str] = []
    api_errors: list[str] = []
    model_ids: list[str] = []

    for event in events:
        if event.get("type") == "tool_execution_start":
            name = event.get("toolName")
            if isinstance(name, str):
                tools.append(name)

        message = event.get("message")
        if isinstance(message, dict):
            model = message.get("model")
            if isinstance(model, str) and model not in model_ids:
                model_ids.append(model)

        if event.get("type") == "message_update":
            update = event.get("assistantMessageEvent")
            if isinstance(update, dict) and update.get("type") == "text_delta":
                delta = update.get("delta")
                if isinstance(delta, str):
                    final_text_parts.append(delta)

        if event.get("type") in {"error", "auto_retry_end"}:
            api_errors.append(json.dumps(event, ensure_ascii=False))

    return {
        "tool_names": tools,
        "models": model_ids,
        "text": "".join(final_text_parts).strip(),
        "errors": api_errors,
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if shutil.which("pi") is None:
        print("ERROR: pi executable not found in PATH", file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = repo_root / "results-local" / "agent-smoke" / f"pi-{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    before_status = git_status(repo_root)
    before_memory = memory_snapshot(repo_root)

    prompt = (
        "This is a LOOM read-only smoke test. You MUST use the read tool to read README.md. "
        "Return exactly the first Markdown heading from README.md, with no explanation."
    )

    command = [
        "pi",
        "--provider",
        "ollama",
        "--model",
        "qwen3.5:4b-mlx",
        "--tools",
        "read",
        "--no-session",
        "--mode",
        "json",
        "-p",
        prompt,
    ]

    proc = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=180,
    )

    (out_dir / "pi-stdout.jsonl").write_text(proc.stdout, encoding="utf-8")
    (out_dir / "pi-stderr.txt").write_text(proc.stderr, encoding="utf-8")

    events, parse_errors = parse_jsonl(proc.stdout)
    pi_summary = summarize(events)

    after_memory = memory_snapshot(repo_root)
    after_status = git_status(repo_root)

    expected = "# LOOM"
    used_read = "read" in pi_summary["tool_names"]
    answer_ok = pi_summary["text"].strip() == expected
    tree_ok = before_status == after_status
    success = proc.returncode == 0 and used_read and answer_ok and tree_ok and not pi_summary["errors"]

    summary = {
        "run_id": f"pi-{run_id}",
        "started_at_utc": before_memory["timestamp_utc"],
        "pi_version": run(["pi", "--version"], repo_root).get("stdout", "").strip(),
        "provider": "ollama",
        "model": "qwen3.5:4b-mlx",
        "context_window_configured": 4096,
        "command": command,
        "exit_code": proc.returncode,
        "success": success,
        "tool_names": pi_summary["tool_names"],
        "models_seen_in_events": pi_summary["models"],
        "final_text": pi_summary["text"],
        "expected_text": expected,
        "event_errors": pi_summary["errors"],
        "jsonl_parse_errors": parse_errors,
        "git_status_before": before_status,
        "git_status_after": after_status,
        "working_tree_unchanged": tree_ok,
        "memory_before": before_memory,
        "memory_after": after_memory,
        "stderr": proc.stderr,
        "finished_at_utc": utc_now(),
    }
    (out_dir / "smoke-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("LOOM Pi read-only smoke test")
    print(f"Exit code: {proc.returncode}")
    print(f"Provider/model: ollama/qwen3.5:4b-mlx")
    print(f"Tools: {pi_summary['tool_names'] or 'not detected'}")
    print(f"Result: {pi_summary['text']!r}")
    print(f"Working tree unchanged: {tree_ok}")
    print(f"Success: {success}")
    if parse_errors:
        print(f"JSONL parse errors: {parse_errors}")
    if pi_summary["errors"]:
        print("Pi event errors detected")
    if proc.stderr.strip():
        print("--- pi stderr ---")
        print(proc.stderr.strip())
    print(f"Run directory: {out_dir}")
    print(f"Summary: {out_dir / 'smoke-summary.json'}")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
