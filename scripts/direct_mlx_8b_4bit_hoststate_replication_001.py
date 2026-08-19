#!/usr/bin/env python3
"""LOOM Direct MLX 8B 4-bit Host-State Controlled Replication 001.

Adds only a prospective host free-memory launch gate in front of the frozen
4-bit full benchmark runner. If eligible, os.execv replaces this wrapper with
the frozen runner so no extra Python process remains resident during MLX.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TARGET_BLOB_SHA = "541e23ef5a824a29f3f67e162e48228b2ccabb14"
MIN_HOST_FREE_PERCENT = 70
REQUIRED_CONSECUTIVE_SAMPLES = 3
SAMPLE_INTERVAL_SECONDS = 1.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_blob_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def memory_free_percent() -> int | None:
    proc = subprocess.run(
        ["memory_pressure"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    text = proc.stdout + proc.stderr
    match = re.search(r"System-wide memory free percentage:\s*(\d+)%", text)
    return int(match.group(1)) if match else None


def parse_scaled_mb(value: str, unit: str) -> float:
    number = float(value.replace(",", "."))
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


def swap_used_mb() -> float | None:
    proc = subprocess.run(
        ["sysctl", "-n", "vm.swapusage"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if proc.returncode != 0:
        return None
    match = re.search(
        r"\bused\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*([KMGT])(?:B)?\b",
        proc.stdout,
        re.IGNORECASE,
    )
    if not match:
        return None
    return round(parse_scaled_mb(match.group(1), match.group(2)), 2)


def disk_free_gib(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return round(usage.free / (1024 ** 3), 3)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    target = Path(__file__).resolve().with_name("direct_mlx_8b_4bit_coding_benchmark_001.py")

    raw = target.read_bytes()
    observed_blob = git_blob_bytes(raw)
    print("LOOM Direct MLX 8B 4-bit Host-State Controlled Replication 001")
    print(f"Frozen full-runner blob: {observed_blob}")
    if observed_blob != TARGET_BLOB_SHA:
        print(f"Runner blob preflight: FAIL — expected {TARGET_BLOB_SHA}")
        return 2
    print("Runner blob preflight: PASS")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    record_dir = repo / "results-local" / "mlx" / "8b-4bit-hoststate-replication-001" / run_id
    record_dir.mkdir(parents=True, exist_ok=True)
    record_path = record_dir / "hoststate-preflight.json"

    samples = []
    eligible = True
    print(
        f"Host-state gate: require {REQUIRED_CONSECUTIVE_SAMPLES} consecutive "
        f"samples >= {MIN_HOST_FREE_PERCENT}% free"
    )

    for index in range(REQUIRED_CONSECUTIVE_SAMPLES):
        free = memory_free_percent()
        sample = {
            "index": index + 1,
            "timestamp_utc": utc_now(),
            "memory_free_percent": free,
            "swap_used_mb": swap_used_mb(),
        }
        samples.append(sample)
        print(
            f"Host sample {index + 1}/{REQUIRED_CONSECUTIVE_SAMPLES}: "
            f"free={free}% swap={sample['swap_used_mb']} MB"
        )
        if free is None or free < MIN_HOST_FREE_PERCENT:
            eligible = False
        if index + 1 < REQUIRED_CONSECUTIVE_SAMPLES:
            time.sleep(SAMPLE_INTERVAL_SECONDS)

    record = {
        "experiment": "Direct MLX 8B 4-bit Host-State Controlled Replication 001",
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "target_runner": str(target),
        "target_blob_sha": observed_blob,
        "host_gate": {
            "min_free_percent": MIN_HOST_FREE_PERCENT,
            "required_consecutive_samples": REQUIRED_CONSECUTIVE_SAMPLES,
            "sample_interval_seconds": SAMPLE_INTERVAL_SECONDS,
        },
        "samples": samples,
        "disk_free_gib": disk_free_gib(repo),
        "classification": "LAUNCH_ELIGIBLE" if eligible else "HOST_STATE_NOT_READY",
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"Host-state preflight record: {record_path}")
    if not eligible:
        print("Classification: HOST_STATE_NOT_READY")
        print("MLX launch: SKIPPED")
        return 3

    print("Classification: LAUNCH_ELIGIBLE")
    print("Replacing wrapper with frozen 4-bit full benchmark runner...", flush=True)
    os.execv(sys.executable, [sys.executable, str(target)])
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
