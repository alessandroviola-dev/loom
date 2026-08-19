#!/usr/bin/env python3
"""Read-only diagnostic for LOOM macOS swap telemetry parsing."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20, check=False)
    return {
        "command": cmd,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def parse_scaled_mb(value: str, unit: str) -> float:
    number = float(value)
    unit = unit.upper()
    if unit == "K":
        return number / 1024.0
    if unit == "M":
        return number
    if unit == "G":
        return number * 1024.0
    if unit == "T":
        return number * 1024.0 * 1024.0
    return number


def parse_current_regex(text: str):
    match = re.search(r"used\s*=\s*([0-9.]+)([KMGT])", text)
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def parse_robust_regex(text: str):
    match = re.search(r"\bused\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*([KMGT])(?:B)?\b", text, re.IGNORECASE)
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    raw_n = run(["sysctl", "-n", "vm.swapusage"])
    raw_full = run(["sysctl", "vm.swapusage"])
    pressure = run(["memory_pressure"])
    disk = shutil.disk_usage(repo_root)

    print("LOOM macOS Swap Telemetry Diagnostic")
    print("=" * 72)
    print("sysctl -n vm.swapusage")
    print(f"exit_code: {raw_n['exit_code']}")
    print(f"stdout_repr: {raw_n['stdout']!r}")
    print(f"stderr_repr: {raw_n['stderr']!r}")
    print(f"current_parser_mb: {parse_current_regex(raw_n['stdout'])!r}")
    print(f"robust_parser_mb: {parse_robust_regex(raw_n['stdout'])!r}")

    print("\nsysctl vm.swapusage")
    print(f"exit_code: {raw_full['exit_code']}")
    print(f"stdout_repr: {raw_full['stdout']!r}")
    print(f"stderr_repr: {raw_full['stderr']!r}")
    print(f"current_parser_mb: {parse_current_regex(raw_full['stdout'])!r}")
    print(f"robust_parser_mb: {parse_robust_regex(raw_full['stdout'])!r}")

    text = pressure["stdout"] + pressure["stderr"]
    free_match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    print("\nmemory_pressure")
    print(f"exit_code: {pressure['exit_code']}")
    print(f"free_percent: {int(free_match.group(1)) if free_match else None!r}")

    print("\nDisk")
    print(f"free_gib: {disk.free / (1024 ** 3):.3f}")

    result = {
        "swap_n": raw_n,
        "swap_full": raw_full,
        "current_parser_n_mb": parse_current_regex(raw_n["stdout"]),
        "robust_parser_n_mb": parse_robust_regex(raw_n["stdout"]),
        "current_parser_full_mb": parse_current_regex(raw_full["stdout"]),
        "robust_parser_full_mb": parse_robust_regex(raw_full["stdout"]),
        "memory_free_percent": int(free_match.group(1)) if free_match else None,
        "disk_free_gib": round(disk.free / (1024 ** 3), 3),
    }
    print("\nJSON")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
