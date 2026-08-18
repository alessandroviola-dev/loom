#!/usr/bin/env python3
"""LOOM Pi isolated edit+test smoke at context 4096.

Creates a disposable ignored workspace under results-local, asks Pi/Ollama/Qwen
to inspect and fix one Python file, requires read/edit/bash tool use, runs tests,
and verifies no tracked LOOM file changed.

Reports two outcomes:
- functional_success: the coding/tool/test workflow succeeded;
- strict_success: functional success plus exact final-output compliance.
"""

from __future__ import annotations

import hashlib
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    text_parts: list[str] = []
    errors: list[str] = []
    models: list[str] = []

    for event in events:
        if event.get("type") == "tool_execution_start":
            name = event.get("toolName")
            if isinstance(name, str):
                tools.append(name)

        message = event.get("message")
        if isinstance(message, dict):
            model = message.get("model")
            if isinstance(model, str) and model not in models:
                models.append(model)

        if event.get("type") == "message_update":
            update = event.get("assistantMessageEvent")
            if isinstance(update, dict) and update.get("type") == "text_delta":
                delta = update.get("delta")
                if isinstance(delta, str):
                    text_parts.append(delta)

        if event.get("type") in {"error", "auto_retry_end"}:
            errors.append(json.dumps(event, ensure_ascii=False))

    return {
        "tool_names": tools,
        "models": models,
        "text": "".join(text_parts).strip(),
        "errors": errors,
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if shutil.which("pi") is None:
        print("ERROR: pi executable not found in PATH", file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = repo_root / "results-local" / "agent-smoke" / f"pi-edit-{run_id}"
    workspace = out_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    solution = workspace / "range_utils.py"
    tests = workspace / "test_range_utils.py"

    solution.write_text(
        '''def clamp(value, low, high):\n'''
        '''    """Return value constrained to the inclusive [low, high] interval."""\n'''
        '''    if low > high:\n'''
        '''        raise ValueError("low must be <= high")\n'''
        '''    return max(high, min(low, value))\n''',
        encoding="utf-8",
    )

    tests.write_text(
        '''import unittest\n\n'''
        '''from range_utils import clamp\n\n\n'''
        '''class ClampTests(unittest.TestCase):\n'''
        '''    def test_inside(self):\n'''
        '''        self.assertEqual(clamp(5, 0, 10), 5)\n\n'''
        '''    def test_below(self):\n'''
        '''        self.assertEqual(clamp(-3, 0, 10), 0)\n\n'''
        '''    def test_above(self):\n'''
        '''        self.assertEqual(clamp(99, 0, 10), 10)\n\n'''
        '''    def test_invalid_bounds(self):\n'''
        '''        with self.assertRaises(ValueError):\n'''
        '''            clamp(5, 10, 0)\n\n\n'''
        '''if __name__ == "__main__":\n'''
        '''    unittest.main()\n''',
        encoding="utf-8",
    )

    tests_hash_before = sha256(tests)
    solution_hash_before = sha256(solution)
    repo_status_before = git_status(repo_root)
    memory_before = memory_snapshot(repo_root)

    prompt = (
        "This is a LOOM isolated edit-and-test smoke test. Work only in the current directory. "
        "Inspect range_utils.py and test_range_utils.py. Fix range_utils.py only so all tests pass. "
        "You MUST use the read tool to inspect the files, the edit tool to change range_utils.py, "
        "and bash to run `python3 -m unittest -v`. Do not modify the test file. "
        "When the tests pass, reply exactly PASS."
    )

    command = [
        "pi",
        "--provider",
        "ollama",
        "--model",
        "qwen3.5:4b-mlx",
        "--tools",
        "read,edit,bash",
        "--no-session",
        "--mode",
        "json",
        "-p",
        prompt,
    ]

    proc = subprocess.run(
        command,
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=240,
    )

    (out_dir / "pi-stdout.jsonl").write_text(proc.stdout, encoding="utf-8")
    (out_dir / "pi-stderr.txt").write_text(proc.stderr, encoding="utf-8")

    events, parse_errors = parse_jsonl(proc.stdout)
    pi_summary = summarize(events)

    external_tests = run(["python3", "-m", "unittest", "-v"], workspace, timeout=60)
    memory_after = memory_snapshot(repo_root)
    repo_status_after = git_status(repo_root)

    tests_unchanged = sha256(tests) == tests_hash_before
    solution_changed = sha256(solution) != solution_hash_before
    required_tools = {"read", "edit", "bash"}
    tools_ok = required_tools.issubset(set(pi_summary["tool_names"]))
    tests_pass = external_tests.get("exit_code") == 0
    repo_unchanged = repo_status_before == repo_status_after
    answer_ok = pi_summary["text"].strip() == "PASS"

    functional_success = (
        proc.returncode == 0
        and tools_ok
        and tests_pass
        and tests_unchanged
        and solution_changed
        and repo_unchanged
        and not pi_summary["errors"]
    )
    strict_success = functional_success and answer_ok

    summary = {
        "run_id": f"pi-edit-{run_id}",
        "started_at_utc": memory_before["timestamp_utc"],
        "pi_version": run(["pi", "--version"], repo_root).get("stdout", "").strip(),
        "provider": "ollama",
        "model": "qwen3.5:4b-mlx",
        "context_window_configured": 4096,
        "workspace": str(workspace),
        "command": command,
        "exit_code": proc.returncode,
        "functional_success": functional_success,
        "strict_success": strict_success,
        "success": strict_success,
        "tool_names": pi_summary["tool_names"],
        "models_seen_in_events": pi_summary["models"],
        "final_text": pi_summary["text"],
        "answer_exact_pass": answer_ok,
        "event_errors": pi_summary["errors"],
        "jsonl_parse_errors": parse_errors,
        "tests_unchanged": tests_unchanged,
        "solution_changed": solution_changed,
        "external_tests_pass": tests_pass,
        "external_test_stdout": external_tests.get("stdout", ""),
        "external_test_stderr": external_tests.get("stderr", ""),
        "repo_git_status_before": repo_status_before,
        "repo_git_status_after": repo_status_after,
        "repo_working_tree_unchanged": repo_unchanged,
        "memory_before": memory_before,
        "memory_after": memory_after,
        "stderr": proc.stderr,
        "finished_at_utc": utc_now(),
    }
    (out_dir / "smoke-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("LOOM Pi edit+test smoke test")
    print(f"Exit code: {proc.returncode}")
    print("Provider/model: ollama/qwen3.5:4b-mlx")
    print(f"Tools: {pi_summary['tool_names'] or 'not detected'}")
    print(f"Final text: {pi_summary['text']!r}")
    print(f"Exact PASS response: {answer_ok}")
    print(f"Solution changed: {solution_changed}")
    print(f"Tests unchanged: {tests_unchanged}")
    print(f"External tests pass: {tests_pass}")
    print(f"LOOM tracked tree unchanged: {repo_unchanged}")
    print(f"Functional success: {functional_success}")
    print(f"Strict success: {strict_success}")
    if parse_errors:
        print(f"JSONL parse errors: {parse_errors}")
    if pi_summary["errors"]:
        print("Pi event errors detected")
    if proc.stderr.strip():
        print("--- pi stderr ---")
        print(proc.stderr.strip())
    print(f"Run directory: {out_dir}")
    print(f"Summary: {out_dir / 'smoke-summary.json'}")

    return 0 if strict_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
