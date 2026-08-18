#!/usr/bin/env python3
"""LOOM Qwen Code read-only smoke test.

Runs Qwen Code headlessly in plan mode against the project-local Ollama config,
forces a read_file-style repository read, captures raw JSON output, verifies the
working tree is unchanged, and records memory/swap/Ollama state before/after.

Standard library only.
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


def summarize_qwen_output(parsed) -> dict:
    models: list[str] = []
    tool_names: list[str] = []
    final_result = None

    messages = parsed if isinstance(parsed, list) else [parsed]
    for item in messages:
        if not isinstance(item, dict):
            continue
        model = item.get("model")
        if isinstance(model, str) and model not in models:
            models.append(model)

        message = item.get("message")
        if isinstance(message, dict):
            msg_model = message.get("model")
            if isinstance(msg_model, str) and msg_model not in models:
                models.append(msg_model)
            content = message.get("content")
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") in {"tool_use", "tool_call"}:
                        name = block.get("name")
                        if isinstance(name, str):
                            tool_names.append(name)

        if item.get("type") == "result":
            final_result = item.get("result")

    return {
        "models": models,
        "tool_names": tool_names,
        "final_result": final_result,
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if shutil.which("qwen") is None:
        print("ERROR: qwen executable not found in PATH", file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = repo_root / "results-local" / "agent-smoke" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    before_status = git_status(repo_root)
    before_memory = memory_snapshot(repo_root)

    prompt = (
        "This is a LOOM read-only smoke test. You MUST use the repository file-reading tool "
        "to read README.md. Do not modify, create, rename, or delete any file and do not run "
        "shell commands. Return exactly the first Markdown heading from README.md, with no "
        "explanation."
    )

    command = [
        "qwen",
        "--prompt",
        prompt,
        "--approval-mode",
        "plan",
        "--output-format",
        "json",
        "--max-wall-time",
        "2m",
        "--max-tool-calls",
        "5",
        "--max-session-turns",
        "8",
    ]

    proc = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=180,
    )

    (out_dir / "qwen-stdout.json").write_text(proc.stdout)
    (out_dir / "qwen-stderr.txt").write_text(proc.stderr)

    parsed = None
    parse_error = None
    qwen_summary = {"models": [], "tool_names": [], "final_result": None}
    try:
        parsed = json.loads(proc.stdout)
        qwen_summary = summarize_qwen_output(parsed)
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"

    after_memory = memory_snapshot(repo_root)
    after_status = git_status(repo_root)

    summary = {
        "run_id": run_id,
        "started_with_clean_or_known_status": before_status,
        "qwen_exit_code": proc.returncode,
        "qwen_version": run(["qwen", "--version"], repo_root).get("stdout", "").strip(),
        "command": command,
        "parsed_output": parsed is not None,
        "parse_error": parse_error,
        "models": qwen_summary["models"],
        "tool_names": qwen_summary["tool_names"],
        "final_result": qwen_summary["final_result"],
        "git_status_before": before_status,
        "git_status_after": after_status,
        "working_tree_unchanged": before_status == after_status,
        "memory_before": before_memory,
        "memory_after": after_memory,
        "stderr": proc.stderr,
        "finished_at_utc": utc_now(),
    }
    (out_dir / "smoke-summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print("LOOM Qwen Code read-only smoke test")
    print(f"Exit code: {proc.returncode}")
    print(f"Models: {qwen_summary['models'] or 'not detected'}")
    print(f"Tools: {qwen_summary['tool_names'] or 'not detected'}")
    print(f"Result: {qwen_summary['final_result']!r}")
    print(f"Working tree unchanged: {before_status == after_status}")
    if parse_error:
        print(f"Output parse error: {parse_error}")
    if proc.stderr.strip():
        print("--- qwen stderr ---")
        print(proc.stderr.strip())
    print(f"Run directory: {out_dir}")
    print(f"Summary: {out_dir / 'smoke-summary.json'}")

    return 0 if proc.returncode == 0 and before_status == after_status else 1


if __name__ == "__main__":
    raise SystemExit(main())
