#!/usr/bin/env python3
"""Run LOOM Coding Benchmark 01 against a local Ollama model in single-shot mode.

The frozen benchmark tree is never modified. A complete working copy is created under
results-local/, each task is sent once without test visibility, permitted output files
are written into that isolated copy, and the frozen benchmark runner scores the result.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(args: list[str]) -> dict:
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=20)
        return {
            "command": args,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": args, "error": str(exc)}


def memory_snapshot() -> dict:
    top = run_command(["top", "-l", "1", "-n", "0"])
    physmem = ""
    for line in top.get("stdout", "").splitlines():
        if line.startswith("PhysMem:"):
            physmem = line
            break

    pressure = run_command(["memory_pressure"])
    pressure_line = ""
    for line in reversed(pressure.get("stdout", "").splitlines()):
        if line.strip():
            pressure_line = line.strip()
            break

    return {
        "timestamp_utc": utc_now(),
        "physmem": physmem,
        "memory_pressure": pressure_line,
        "swap": run_command(["sysctl", "vm.swapusage"]).get("stdout", ""),
        "ollama_ps": run_command(["ollama", "ps"]).get("stdout", ""),
    }


def build_prompt(task_dir: Path, task: dict) -> str:
    prompt = (task_dir / "prompt.md").read_text()
    chunks = [
        "LOOM Coding Benchmark 01 — single_shot mode.",
        "You get exactly one attempt and no test feedback.",
        "Follow the task prompt exactly.",
        "Return ONLY valid JSON in this exact outer shape:",
        '{"files": {"filename": "complete UTF-8 file contents"}}',
        "Every value inside files must be a JSON string containing the complete replacement file.",
        "Return exactly the permitted editable filenames and no others.",
        "Do not use Markdown fences or explanatory text outside the JSON.",
        "",
        "PERMITTED EDITABLE FILES:",
        *[f"- {name}" for name in task["editable"]],
        "",
        "TASK PROMPT:",
        prompt,
        "",
        "SUPPLIED SOURCE FILES:",
    ]

    for name in task["context"]:
        chunks.extend([
            f"--- FILE: {name} ---",
            (task_dir / name).read_text(),
            f"--- END FILE: {name} ---",
            "",
        ])

    return "\n".join(chunks)


def ollama_generate(base_url: str, model: str, prompt: str, context: int) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "format": "json",
        "options": {
            "num_ctx": context,
            "temperature": 0,
            "num_predict": 2048,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw_error = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama HTTP {exc.code}: {raw_error}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot reach Ollama at {base_url}: {exc}") from exc

    elapsed = time.perf_counter() - started
    data = json.loads(raw)
    data["loom_wall_seconds"] = round(elapsed, 3)
    return data


def extract_files(api_response: dict, editable: list[str]) -> dict[str, str]:
    response_text = api_response.get("response")
    if not isinstance(response_text, str):
        raise ValueError("Ollama response does not contain a string 'response' field")

    parsed = json.loads(response_text)
    if not isinstance(parsed, dict) or set(parsed) != {"files"}:
        raise ValueError("Model output must contain only the top-level key 'files'")
    files = parsed["files"]
    if not isinstance(files, dict):
        raise ValueError("'files' must be a JSON object")
    if set(files) != set(editable):
        raise ValueError(f"Expected exactly files {editable}, received {sorted(files)}")
    for name, content in files.items():
        if name not in editable:
            raise ValueError(f"Unexpected output file: {name}")
        if not isinstance(content, str):
            raise ValueError(f"Output for {name} must be a JSON string")
    return files


def metric_summary(api_response: dict) -> dict:
    eval_count = api_response.get("eval_count", 0) or 0
    eval_ns = api_response.get("eval_duration", 0) or 0
    prompt_count = api_response.get("prompt_eval_count", 0) or 0
    prompt_ns = api_response.get("prompt_eval_duration", 0) or 0

    return {
        "prompt_eval_count": prompt_count,
        "prompt_eval_duration_ns": prompt_ns,
        "prompt_tokens_per_second": round(prompt_count / (prompt_ns / 1e9), 3) if prompt_ns else None,
        "eval_count": eval_count,
        "eval_duration_ns": eval_ns,
        "generation_tokens_per_second": round(eval_count / (eval_ns / 1e9), 3) if eval_ns else None,
        "load_duration_ns": api_response.get("load_duration"),
        "total_duration_ns": api_response.get("total_duration"),
        "wall_seconds": api_response.get("loom_wall_seconds"),
        "done_reason": api_response.get("done_reason"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3.5:4b-mlx")
    parser.add_argument("--context", type=int, default=4096)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--keep-loaded",
        action="store_true",
        help="Do not issue 'ollama stop MODEL' before the benchmark run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    frozen = repo_root / "benchmarks" / "coding" / "v1"
    if not frozen.exists():
        raise SystemExit(f"Frozen benchmark not found: {frozen}")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo_root / "results-local" / "coding-single-shot" / run_id
    working = run_dir / "benchmarks" / "coding" / "v1"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(frozen, working)

    if not args.keep_loaded:
        run_command(["ollama", "stop", args.model])

    summary = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "benchmark": "LOOM Coding Benchmark 01",
        "benchmark_version": "1.0.0",
        "mode": "single_shot",
        "runtime": "ollama",
        "model": args.model,
        "context": args.context,
        "base_url": args.base_url,
        "memory_before": memory_snapshot(),
        "tasks": [],
    }

    for task in TASKS:
        task_dir = working / task["path"]
        prompt = build_prompt(task_dir, task)
        task_record = {
            "id": task["id"],
            "editable": task["editable"],
            "started_at_utc": utc_now(),
        }
        try:
            response = ollama_generate(args.base_url, args.model, prompt, args.context)
            (raw_dir / f"{task['id']}-api.json").write_text(json.dumps(response, indent=2) + "\n")
            files = extract_files(response, task["editable"])
            for name, content in files.items():
                (task_dir / name).write_text(content)
            task_record["adapter_status"] = "written"
            task_record["metrics"] = metric_summary(response)
        except Exception as exc:  # benchmark must continue so failures are scored
            task_record["adapter_status"] = "failed"
            task_record["error"] = f"{type(exc).__name__}: {exc}"
        task_record["finished_at_utc"] = utc_now()
        task_record["memory_after_task"] = memory_snapshot()
        summary["tasks"].append(task_record)

    env = dict(**__import__("os").environ)
    env.update({
        "LOOM_MODEL": args.model,
        "LOOM_RUNTIME": "ollama",
        "LOOM_BACKEND": "mlx" if args.model.endswith("-mlx") else "unknown",
        "LOOM_MODE": "single_shot",
        "LOOM_CONTEXT": str(args.context),
    })
    proc = subprocess.run(
        [sys.executable, "runner.py"],
        cwd=working,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    if proc.returncode != 0:
        summary["runner_error"] = {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    else:
        summary["benchmark_result"] = json.loads(proc.stdout)

    summary["memory_after"] = memory_snapshot()
    summary["finished_at_utc"] = utc_now()
    summary_path = run_dir / "run-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    score = summary.get("benchmark_result", {}).get("score", "N/A")
    print(f"LOOM Coding Benchmark 01 complete — score: {score}/100")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
