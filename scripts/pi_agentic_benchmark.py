#!/usr/bin/env python3
"""Run LOOM Coding Benchmark 01 through Pi in isolated file-agentic mode.

The frozen benchmark is never modified. Each task is presented in a temporary
workspace containing only the task prompt's supplied source/editable files; hidden
tests are NOT copied into the agent workspace. Pi gets read/write/edit tools only
(no bash/test feedback). Produced editable files are copied into a separate scoring
copy, then the frozen v1.0.1 runner scores that copy.

The adapter records three score views:
- artifact_score: raw frozen-runner score of the scoring copy;
- delivery_adjusted_score: task points count only when Pi actually creates/changes
  every permitted editable file and exits without event/parse errors;
- strict_protocol_adjusted_score: delivery-adjusted points additionally require
  no non-editable input mutation, no unexpected persistent files, and final text
  exactly DONE.

Pi is launched with a run-local PI_CODING_AGENT_DIR and customization discovery
disabled, so the user's normal Pi auth/settings/sessions/skills/extensions are not
modified or loaded into the benchmark harness.

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


MODEL_ID = "qwen3.5:4b-mlx"

TASKS = [
    {
        "id": "T01",
        "path": "tasks/t01_generation",
        "editable": ["solution.py"],
        "context": ["solution.py"],
    },
    {
        "id": "T02",
        "path": "tasks/t02_debugging",
        "editable": ["buggy.py"],
        "context": ["buggy.py"],
    },
    {
        "id": "T03",
        "path": "tasks/t03_comprehension",
        "editable": ["answer.json"],
        "context": ["source.py"],
    },
    {
        "id": "T04",
        "path": "tasks/t04_refactor",
        "editable": ["solution.py"],
        "context": ["solution.py"],
    },
    {
        "id": "T05",
        "path": "tasks/t05_multifile",
        "editable": ["order.py"],
        "context": ["order.py", "pricing.py"],
    },
    {
        "id": "T06",
        "path": "tasks/t06_constraints",
        "editable": ["solution.py"],
        "context": ["solution.py"],
    },
]


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
                    "name": "Qwen 3.5 4B MLX (Ollama / LOOM isolated benchmark)",
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


def summarize_events(events: list[dict]) -> dict:
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
        "final_text": "".join(text_parts).strip(),
        "event_errors": errors,
    }


def task_prompt(task_dir: Path, task: dict) -> str:
    prompt = (task_dir / "prompt.md").read_text(encoding="utf-8")
    permitted = ", ".join(task["editable"])
    supplied = ", ".join(task["context"])
    return (
        "LOOM Coding Benchmark 01 — Pi file-agentic mode.\n"
        "You have one attempt and no test feedback. Hidden tests are intentionally unavailable.\n"
        "Work only with files in the current working directory. Do not access parent directories, "
        "absolute paths, network resources, or unrelated files.\n"
        "Use the read/write/edit tools as useful. Do not create persistent scratch files.\n"
        f"Permitted editable output files: {permitted}.\n"
        f"Supplied source files: {supplied}.\n"
        "Modify or create ONLY the permitted editable output files. Do not alter supplied "
        "non-editable source files.\n"
        "When you are completely finished, reply exactly DONE with no explanation.\n\n"
        "TASK PROMPT:\n"
        f"{prompt}"
    )


def workspace_files(root: Path) -> list[str]:
    result: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if "__pycache__" in rel.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
            continue
        result.append(str(rel))
    return sorted(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--model", default=MODEL_ID)
    parser.add_argument("--context", type=int, default=4096)
    parser.add_argument("--task-timeout", type=int, default=300)
    parser.add_argument("--keep-loaded", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    frozen = repo_root / "benchmarks" / "coding" / "v1"
    if not frozen.exists():
        raise SystemExit(f"Frozen benchmark not found: {frozen}")
    if shutil.which("pi") is None:
        raise SystemExit("pi executable not found in PATH")

    manifest = json.loads((frozen / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "1.0.1":
        raise SystemExit(f"Expected frozen benchmark v1.0.1, found {manifest.get('version')}")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo_root / "results-local" / "coding-agentic-pi" / run_id
    scoring = run_dir / "scoring" / "benchmarks" / "coding" / "v1"
    raw_dir = run_dir / "raw"
    archive_dir = run_dir / "workspaces"
    pi_agent_dir = run_dir / "pi-agent"
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    pi_agent_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(frozen, scoring)
    (pi_agent_dir / "models.json").write_text(
        json.dumps(PI_MODELS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if not args.keep_loaded:
        run(["ollama", "stop", args.model], repo_root)

    pi_env = os.environ.copy()
    pi_env.update(
        {
            "PI_CODING_AGENT_DIR": str(pi_agent_dir),
            "PI_OFFLINE": "1",
            "PI_SKIP_VERSION_CHECK": "1",
            "PI_TELEMETRY": "0",
        }
    )

    summary: dict = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "benchmark": manifest["benchmark"],
        "benchmark_version": manifest["version"],
        "mode": "agentic_pi_file_tools_no_test_feedback",
        "pi_version": run(["pi", "--version"], repo_root, env=pi_env).get("stdout", "").strip(),
        "provider": "ollama",
        "model": args.model,
        "context": args.context,
        "tools": ["read", "write", "edit"],
        "isolated_pi_agent_dir": str(pi_agent_dir),
        "memory_before": memory_snapshot(repo_root),
        "tasks": [],
    }

    with tempfile.TemporaryDirectory(prefix=f"loom-pi-agentic-{run_id}-") as tmp:
        temp_root = Path(tmp)

        for index, task in enumerate(TASKS, start=1):
            print(f"[{index}/{len(TASKS)}] {task['id']} running...", flush=True)
            frozen_task = frozen / task["path"]
            scoring_task = scoring / task["path"]
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

            initial_hashes = {name: sha256(workspace / name) for name in copied}
            initial_files = workspace_files(workspace)
            noneditable = set(task["context"]) - set(task["editable"])

            prompt = task_prompt(frozen_task, task)
            command = [
                "pi",
                "--provider",
                "ollama",
                "--model",
                args.model,
                "--tools",
                "read,write,edit",
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
                    timeout=args.task_timeout,
                    env=pi_env,
                )
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                proc = None
                timed_out = True
                stdout = exc.stdout if isinstance(exc.stdout, str) else ""
                stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            wall_seconds = round(time.perf_counter() - started, 3)

            if proc is not None:
                stdout = proc.stdout
                stderr = proc.stderr
                exit_code = proc.returncode
            else:
                exit_code = None

            (raw_dir / f"{task['id']}-pi.jsonl").write_text(stdout, encoding="utf-8")
            (raw_dir / f"{task['id']}-stderr.txt").write_text(stderr, encoding="utf-8")
            events, parse_errors = parse_jsonl(stdout)
            event_summary = summarize_events(events)

            final_files = workspace_files(workspace)
            expected = set(task["editable"])
            unexpected_files = sorted(set(final_files) - set(initial_files) - expected)

            output_status: dict[str, dict] = {}
            all_delivered = True
            for name in task["editable"]:
                path = workspace / name
                existed_initially = name in initial_hashes
                exists_final = path.exists()
                changed = False
                if exists_final:
                    changed = (not existed_initially) or sha256(path) != initial_hashes.get(name)
                    shutil.copy2(path, scoring_task / name)
                if not exists_final or not changed:
                    all_delivered = False
                output_status[name] = {
                    "existed_initially": existed_initially,
                    "exists_final": exists_final,
                    "changed_or_created": changed,
                }

            noneditable_unchanged = True
            for name in noneditable:
                path = workspace / name
                if not path.exists() or sha256(path) != initial_hashes[name]:
                    noneditable_unchanged = False

            process_ok = (
                exit_code == 0
                and not timed_out
                and not parse_errors
                and not event_summary["event_errors"]
            )
            delivery_success = process_ok and all_delivered
            protocol_ok = (
                delivery_success
                and noneditable_unchanged
                and not unexpected_files
                and event_summary["final_text"].strip() == "DONE"
            )

            archive = archive_dir / task["id"]
            shutil.copytree(workspace, archive)

            record = {
                "id": task["id"],
                "started_at_utc": utc_now(),
                "command": command,
                "exit_code": exit_code,
                "timed_out": timed_out,
                "wall_seconds": wall_seconds,
                "tool_names": event_summary["tool_names"],
                "models_seen_in_events": event_summary["models"],
                "final_text": event_summary["final_text"],
                "event_errors": event_summary["event_errors"],
                "jsonl_parse_errors": parse_errors,
                "initial_files": initial_files,
                "final_files": final_files,
                "unexpected_files": unexpected_files,
                "output_status": output_status,
                "noneditable_inputs_unchanged": noneditable_unchanged,
                "delivery_success": delivery_success,
                "protocol_ok": protocol_ok,
                "memory_after_task": memory_snapshot(repo_root),
            }
            summary["tasks"].append(record)
            print(
                f"[{index}/{len(TASKS)}] {task['id']} "
                f"delivery={'PASS' if delivery_success else 'FAIL'} "
                f"protocol={'PASS' if protocol_ok else 'FAIL'}",
                flush=True,
            )

    runner_env = os.environ.copy()
    runner_env.update(
        {
            "LOOM_MODEL": args.model,
            "LOOM_RUNTIME": "ollama",
            "LOOM_BACKEND": "mlx" if args.model.endswith("-mlx") else "unknown",
            "LOOM_MODE": "agentic_pi_file_tools_no_test_feedback",
            "LOOM_CONTEXT": str(args.context),
        }
    )
    runner = subprocess.run(
        [sys.executable, "runner.py"],
        cwd=scoring,
        capture_output=True,
        text=True,
        timeout=180,
        env=runner_env,
    )

    if runner.returncode != 0:
        summary["runner_error"] = {
            "exit_code": runner.returncode,
            "stdout": runner.stdout,
            "stderr": runner.stderr,
        }
    else:
        result = json.loads(runner.stdout)
        summary["benchmark_result"] = result
        summary["artifact_score"] = result.get("score")

        record_by_id = {record["id"]: record for record in summary["tasks"]}
        delivery_score = 0.0
        strict_score = 0.0
        for scored_task in result.get("tasks", []):
            rec = record_by_id.get(scored_task.get("id"), {})
            earned = scored_task.get("points_earned", 0) or 0
            if rec.get("delivery_success"):
                delivery_score += earned
            if rec.get("protocol_ok"):
                strict_score += earned

        summary["delivery_adjusted_score"] = round(delivery_score, 2)
        summary["strict_protocol_adjusted_score"] = round(strict_score, 2)
        summary["delivery_success_count"] = sum(
            1 for r in summary["tasks"] if r.get("delivery_success")
        )
        summary["protocol_success_count"] = sum(
            1 for r in summary["tasks"] if r.get("protocol_ok")
        )

    summary["memory_after"] = memory_snapshot(repo_root)
    summary["finished_at_utc"] = utc_now()
    summary_path = run_dir / "run-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("LOOM Coding Benchmark 01 — Pi agentic complete")
    print(f"Artifact score: {summary.get('artifact_score', 'N/A')}/100")
    print(f"Delivery-adjusted score: {summary.get('delivery_adjusted_score', 'N/A')}/100")
    print(f"Strict protocol-adjusted score: {summary.get('strict_protocol_adjusted_score', 'N/A')}/100")
    print(
        "Delivery success: "
        f"{summary.get('delivery_success_count', 'N/A')}/{len(TASKS)}; "
        "protocol success: "
        f"{summary.get('protocol_success_count', 'N/A')}/{len(TASKS)}"
    )
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")

    return 0 if "runner_error" not in summary else 1


if __name__ == "__main__":
    raise SystemExit(main())
