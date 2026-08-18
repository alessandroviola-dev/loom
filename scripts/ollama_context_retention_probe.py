#!/usr/bin/env python3
"""LOOM direct Ollama Context Retention Probe 001.

Removes Pi from the path and measures Qwen 3.5 4B MLX allocation under
controlled prompt pressure. Runs warm low/medium/high/low-after-high calls,
then cold low/high controls with an explicit model unload before each.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODEL_ID = "qwen3.5:4b-mlx"
PRESSURE = {
    "low": 400,
    "medium": 1600,
    "high": 3000,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(args: list[str], cwd: Path, timeout: int = 30) -> dict:
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

    row = next((line for line in lines[1:] if MODEL_ID in line), None)
    if row is None:
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


def build_prompt(repetitions: int) -> str:
    return ("hello " * repetitions) + "\nReply with exactly OK."


def direct_generate(base_url: str, repetitions: int, context: int) -> tuple[dict | None, str | None, float]:
    payload = {
        "model": MODEL_ID,
        "prompt": build_prompt(repetitions),
        "stream": False,
        "think": False,
        "keep_alive": "5m",
        "options": {
            "num_ctx": context,
            "temperature": 0,
            "num_predict": 8,
        },
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            raw = response.read().decode("utf-8")
        wall = time.perf_counter() - started
        return json.loads(raw), None, wall
    except urllib.error.HTTPError as exc:
        wall = time.perf_counter() - started
        body = exc.read().decode("utf-8", errors="replace")
        return None, f"HTTP {exc.code}: {body}", wall
    except Exception as exc:
        wall = time.perf_counter() - started
        return None, f"{type(exc).__name__}: {exc}", wall


def throughput(count: int | None, duration_ns: int | None) -> float | None:
    if not count or not duration_ns:
        return None
    return round(count / (duration_ns / 1e9), 3)


def run_call(
    *,
    repo_root: Path,
    raw_dir: Path,
    base_url: str,
    label: str,
    repetitions: int,
    context: int,
) -> dict:
    before = memory_snapshot(repo_root)
    data, error, wall = direct_generate(base_url, repetitions, context)
    after = memory_snapshot(repo_root)

    if data is not None:
        (raw_dir / f"{label}-api.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    else:
        (raw_dir / f"{label}-error.txt").write_text((error or "unknown error") + "\n", encoding="utf-8")

    record = {
        "label": label,
        "repetitions": repetitions,
        "success": data is not None,
        "error": error,
        "wall_seconds": round(wall, 3),
        "memory_before": before,
        "memory_after": after,
    }

    if data is not None:
        record.update(
            {
                "response": data.get("response"),
                "done_reason": data.get("done_reason"),
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
                "prompt_tokens_per_second": throughput(
                    data.get("prompt_eval_count"), data.get("prompt_eval_duration")
                ),
                "generation_tokens_per_second": throughput(
                    data.get("eval_count"), data.get("eval_duration")
                ),
                "load_duration_ns": data.get("load_duration"),
                "total_duration_ns": data.get("total_duration"),
            }
        )

    return record


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
    print(
        f"{record['label']}: success={record['success']} "
        f"wall={record['wall_seconds']}s "
        f"prompt_tokens={record.get('prompt_eval_count')} "
        f"ollama_size={ollama.get('reported_size_gb')}GB "
        f"context={ollama.get('context')} "
        f"swap={after.get('swap_used_mb')}MB "
        f"free={after.get('memory_free_percent')}%"
    )
    if record.get("error"):
        print(f"  error: {record['error']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--context", type=int, default=4096)
    parser.add_argument("--min-free-percent", type=int, default=8)
    parser.add_argument("--max-swap-mb", type=float, default=5600.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if shutil.which("ollama") is None:
        raise SystemExit("ollama executable not found in PATH")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = repo_root / "results-local" / "ollama-context-retention" / run_id
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "run_id": run_id,
        "started_at_utc": utc_now(),
        "experiment": "Ollama Context Retention Probe 001",
        "model": MODEL_ID,
        "context": args.context,
        "pressure_repetitions": PRESSURE,
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

    print("LOOM Ollama Context Retention Probe 001")
    print("=== WARM ARM ===")
    run(["ollama", "stop", MODEL_ID], repo_root)
    summary["warm_after_initial_stop"] = memory_snapshot(repo_root)

    warm_sequence = [
        ("warm-low", PRESSURE["low"]),
        ("warm-medium", PRESSURE["medium"]),
        ("warm-high", PRESSURE["high"]),
        ("warm-low-after-high", PRESSURE["low"]),
    ]

    for label, repetitions in warm_sequence:
        record = run_call(
            repo_root=repo_root,
            raw_dir=raw_dir,
            base_url=args.base_url,
            label=label,
            repetitions=repetitions,
            context=args.context,
        )
        summary["warm"].append(record)
        print_record(record)
        triggered, reason = guard_triggered(record["memory_after"], args.min_free_percent, args.max_swap_mb)
        if triggered:
            summary["warm_aborted"] = True
            summary["warm_abort_reason"] = reason
            print(f"Warm arm guardrail triggered: {reason}")
            run(["ollama", "stop", MODEL_ID], repo_root)
            break

    print("=== COLD ARM ===")
    cold_sequence = [
        ("cold-low", PRESSURE["low"]),
        ("cold-high", PRESSURE["high"]),
    ]

    for label, repetitions in cold_sequence:
        run(["ollama", "stop", MODEL_ID], repo_root)
        after_stop = memory_snapshot(repo_root)
        record = run_call(
            repo_root=repo_root,
            raw_dir=raw_dir,
            base_url=args.base_url,
            label=label,
            repetitions=repetitions,
            context=args.context,
        )
        record["memory_after_stop_before_call"] = after_stop
        summary["cold"].append(record)
        print_record(record)

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
