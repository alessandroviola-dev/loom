#!/usr/bin/env python3
"""LOOM Qwen Code safe-mode read-only diagnostic.

Runs Qwen Code 0.21.13 against the local Ollama/Qwen model with official
--safe-mode and explicit OpenAI-compatible provider/model CLI arguments.
Captures preflight/API/tool outcome, repository deltas and memory/Ollama state.

This is a harness-feasibility diagnostic, not a coding benchmark.
Standard library only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID = "qwen3.5:4b-mlx"
EXPECTED_TEXT = "# LOOM"


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


def memory_snapshot(repo_root: Path, env: dict) -> dict:
    top = run(["top", "-l", "1", "-n", "0"], repo_root, env=env)
    physmem = next(
        (line for line in top.get("stdout", "").splitlines() if line.startswith("PhysMem:")),
        "",
    )
    pressure = run(["memory_pressure"], repo_root, env=env)
    pressure_line = next(
        (line.strip() for line in reversed(pressure.get("stdout", "").splitlines()) if line.strip()),
        "",
    )
    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "swap": run(["sysctl", "vm.swapusage"], repo_root, env=env).get("stdout", "").strip(),
        "ollama_ps": run(["ollama", "ps"], repo_root, env=env).get("stdout", "").strip(),
    }


def git_status(repo_root: Path, env: dict) -> str:
    return run(["git", "status", "--porcelain"], repo_root, env=env).get("stdout", "")


def qwen_settings_diff(repo_root: Path, env: dict) -> str:
    return run(
        ["git", "diff", "--", ".qwen/settings.json"],
        repo_root,
        env=env,
    ).get("stdout", "")


def summarize_qwen_output(parsed: object) -> dict:
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


def semantic_api_error(final_result: object) -> bool:
    return isinstance(final_result, str) and final_result.lstrip().startswith("[API Error:")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if shutil.which("qwen") is None:
        print("ERROR: qwen executable not found in PATH", file=sys.stderr)
        return 2
    if shutil.which("ollama") is None:
        print("ERROR: ollama executable not found in PATH", file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = repo_root / "results-local" / "agent-smoke" / f"qwen-safe-{run_id}"
    runtime_dir = out_dir / "qwen-runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "OPENAI_API_KEY": "ollama",
            "OPENAI_BASE_URL": "http://localhost:11434/v1",
            "OPENAI_MODEL": MODEL_ID,
            "QWEN_CODE_MAX_OUTPUT_TOKENS": "2048",
            "QWEN_RUNTIME_DIR": str(runtime_dir),
        }
    )

    run(["ollama", "stop", MODEL_ID], repo_root, env=env)

    before_status = git_status(repo_root, env)
    before_diff = qwen_settings_diff(repo_root, env)
    before_memory = memory_snapshot(repo_root, env)

    prompt = (
        "This is a LOOM read-only smoke test. You MUST use the repository file-reading tool "
        "to read README.md. Do not modify, create, rename, or delete any file and do not run "
        "shell commands. Return exactly the first Markdown heading from README.md, with no explanation."
    )

    command = [
        "qwen",
        "--safe-mode",
        "--auth-type",
        "openai",
        "--model",
        MODEL_ID,
        "--openai-api-key",
        "ollama",
        "--openai-base-url",
        "http://localhost:11434/v1",
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

    started_at = utc_now()
    try:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        timed_out = False
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = None
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""

    (out_dir / "qwen-stdout.json").write_text(stdout, encoding="utf-8")
    (out_dir / "qwen-stderr.txt").write_text(stderr, encoding="utf-8")

    parsed = None
    parse_error = None
    qwen_summary = {"models": [], "tool_names": [], "final_result": None}
    try:
        parsed = json.loads(stdout)
        qwen_summary = summarize_qwen_output(parsed)
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {exc}"

    after_memory = memory_snapshot(repo_root, env)
    after_status = git_status(repo_root, env)
    after_diff = qwen_settings_diff(repo_root, env)

    api_error = semantic_api_error(qwen_summary["final_result"])
    working_tree_unchanged = before_status == after_status and before_diff == after_diff
    success = (
        exit_code == 0
        and not timed_out
        and parsed is not None
        and not api_error
        and qwen_summary["final_result"] == EXPECTED_TEXT
        and bool(qwen_summary["tool_names"])
        and working_tree_unchanged
    )

    summary = {
        "run_id": f"qwen-safe-{run_id}",
        "started_at_utc": started_at,
        "qwen_version": run(["qwen", "--version"], repo_root, env=env).get("stdout", "").strip(),
        "provider": "openai-compatible-ollama",
        "model": MODEL_ID,
        "intended_context": 4096,
        "safe_mode": True,
        "command": command,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "parsed_output": parsed is not None,
        "parse_error": parse_error,
        "semantic_api_error": api_error,
        "success": success,
        "models": qwen_summary["models"],
        "tool_names": qwen_summary["tool_names"],
        "final_result": qwen_summary["final_result"],
        "expected_text": EXPECTED_TEXT,
        "git_status_before": before_status,
        "git_status_after": after_status,
        "qwen_settings_diff_before": before_diff,
        "qwen_settings_diff_after": after_diff,
        "working_tree_unchanged": working_tree_unchanged,
        "memory_before": before_memory,
        "memory_after": after_memory,
        "stderr": stderr,
        "finished_at_utc": utc_now(),
    }
    summary_path = out_dir / "smoke-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("LOOM Qwen Code safe-mode read-only diagnostic")
    print(f"Exit code: {exit_code}")
    print(f"Timed out: {timed_out}")
    print(f"Qwen version: {summary['qwen_version']}")
    print(f"Models: {qwen_summary['models'] or 'not detected'}")
    print(f"Tools: {qwen_summary['tool_names'] or 'not detected'}")
    print(f"Result: {qwen_summary['final_result']!r}")
    print(f"Semantic API error: {api_error}")
    print(f"Working tree unchanged: {working_tree_unchanged}")
    print(f"Success: {success}")
    if parse_error:
        print(f"Output parse error: {parse_error}")
    if stderr.strip():
        print("--- qwen stderr ---")
        print(stderr.strip())
    print(f"Run directory: {out_dir}")
    print(f"Summary: {summary_path}")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
