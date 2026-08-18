#!/usr/bin/env python3
"""Rescore an existing LOOM Coding Benchmark working copy without rerunning the model.

This is primarily for benchmark-scoring patches. The script preserves the task outputs
from the original run, replaces only the isolated copy's runner/manifest with the
current canonical scorer, and executes the scorer again.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--model", default="qwen3.5:4b-mlx")
    parser.add_argument("--runtime", default="ollama")
    parser.add_argument("--backend", default="mlx")
    parser.add_argument("--mode", default="single_shot")
    parser.add_argument("--context", default="4096")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    canonical = repo_root / "benchmarks" / "coding" / "v1"
    run_dir = args.run_dir.expanduser().resolve()
    target = run_dir / "benchmarks" / "coding" / "v1"

    if not target.exists():
        raise SystemExit(f"Run benchmark tree not found: {target}")

    backup_dir = run_dir / "scorer-backup"
    backup_dir.mkdir(exist_ok=True)
    for name in ("runner.py", "manifest.json"):
        source = target / name
        if source.exists() and not (backup_dir / name).exists():
            shutil.copy2(source, backup_dir / name)
        shutil.copy2(canonical / name, target / name)

    env = dict(os.environ)
    env.update({
        "LOOM_MODEL": args.model,
        "LOOM_RUNTIME": args.runtime,
        "LOOM_BACKEND": args.backend,
        "LOOM_MODE": args.mode,
        "LOOM_CONTEXT": str(args.context),
    })

    proc = subprocess.run(
        [sys.executable, "runner.py"],
        cwd=target,
        env=env,
        text=True,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
