#!/usr/bin/env python3
"""LOOM Direct MLX Qwen3-8B-4bit KV8 Rescue 001.

Host-state-gated one-factor rescue of the frozen Direct MLX full coding
benchmark. The validated 3-bit full benchmark source is transformed to the
verified 4-bit model and an explicitly active 8-bit KV-cache policy. No other
benchmark/runtime/safety setting is changed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE_BLOB_SHA = "01b00d604026affff4bad0d599a3159faaf786ae"
OLD_MODEL_REPO = "mlx-community/Qwen3-8B-3bit"
NEW_MODEL_REPO = "mlx-community/Qwen3-8B-4bit"
OLD_MODEL_SHA = "b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1"
NEW_MODEL_SHA = "f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8"

HOST_MIN_FREE_PERCENT = 70
HOST_REQUIRED_CONSECUTIVE = 3
HOST_POLL_SECONDS = 1.0

KV_BITS = 8
KV_GROUP_SIZE = 64
QUANTIZED_KV_START = 0

REPLACEMENTS = [
    ("LOOM Direct MLX Coding Benchmark 001", "LOOM Direct MLX 8B 4-bit KV8 Rescue 001"),
    ("Direct MLX Coding Benchmark 001", "Direct MLX 8B 4-bit KV8 Rescue 001"),
    (OLD_MODEL_REPO, NEW_MODEL_REPO),
    (OLD_MODEL_SHA, NEW_MODEL_SHA),
    ("Qwen3-8B-3bit", "Qwen3-8B-4bit"),
    ('"coding-benchmark-001"', '"8b-4bit-kv8-rescue-001"'),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_blob_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def parse_scaled_mb(value: str, unit: str) -> float:
    n = float(value.replace(",", "."))
    unit = unit.upper()
    if unit == "K":
        return n / 1024.0
    if unit == "M":
        return n
    if unit == "G":
        return n * 1024.0
    if unit == "T":
        return n * 1024.0 * 1024.0
    return n


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


def host_gate(repo: Path) -> int:
    print("LOOM Direct MLX 8B 4-bit KV8 Rescue 001")
    print(f"Frozen template blob required: {TEMPLATE_BLOB_SHA}")
    print(
        "Host-state gate: require "
        f"{HOST_REQUIRED_CONSECUTIVE} consecutive samples >= {HOST_MIN_FREE_PERCENT}% free"
    )

    template = repo / "scripts" / "direct_mlx_coding_benchmark_001.py"
    raw = template.read_bytes()
    observed_blob = git_blob_bytes(raw)
    print(f"Template blob: {observed_blob}")
    if observed_blob != TEMPLATE_BLOB_SHA:
        print("Template blob preflight: FAIL")
        return 2
    print("Template blob preflight: PASS")

    samples = []
    consecutive = 0
    for index in range(1, HOST_REQUIRED_CONSECUTIVE + 1):
        free = memory_free_percent()
        swap = swap_used_mb()
        sample = {
            "index": index,
            "observed_at_utc": utc_now(),
            "memory_free_percent": free,
            "swap_used_mb": swap,
        }
        samples.append(sample)
        free_text = "None" if free is None else f"{free}%"
        swap_text = "None" if swap is None else f"{swap:.2f} MB"
        print(f"Host sample {index}/{HOST_REQUIRED_CONSECUTIVE}: free={free_text} swap={swap_text}")

        if free is None or swap is None:
            consecutive = 0
            break
        if free >= HOST_MIN_FREE_PERCENT:
            consecutive += 1
        else:
            consecutive = 0
            break
        if index < HOST_REQUIRED_CONSECUTIVE:
            time.sleep(HOST_POLL_SECONDS)

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    preflight_dir = repo / "results-local" / "mlx" / "8b-4bit-kv8-rescue-001-hoststate" / run_id
    preflight_dir.mkdir(parents=True, exist_ok=True)
    record_path = preflight_dir / "hoststate-preflight.json"
    record = {
        "experiment": "Direct MLX 8B 4-bit KV8 Rescue 001 host-state gate",
        "created_at_utc": utc_now(),
        "required_free_percent": HOST_MIN_FREE_PERCENT,
        "required_consecutive_samples": HOST_REQUIRED_CONSECUTIVE,
        "samples": samples,
        "template_blob_sha": observed_blob,
        "kv_policy": {
            "kv_bits": KV_BITS,
            "kv_group_size": KV_GROUP_SIZE,
            "quantized_kv_start": QUANTIZED_KV_START,
            "max_kv_size": 4096,
        },
        "classification": (
            "LAUNCH_ELIGIBLE"
            if consecutive == HOST_REQUIRED_CONSECUTIVE
            else "HOST_STATE_NOT_READY"
        ),
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"Host-state preflight record: {record_path}")
    print(f"Classification: {record['classification']}")

    if record["classification"] != "LAUNCH_ELIGIBLE":
        print("MLX launch: SKIPPED")
        return 3

    print("Host-state gate passed; re-executing clean KV8 rescue process...", flush=True)
    os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve()), "--launched"])
    return 1


def launch_transformed_benchmark(repo: Path) -> int:
    template = repo / "scripts" / "direct_mlx_coding_benchmark_001.py"
    raw = template.read_bytes()
    observed_blob = git_blob_bytes(raw)
    if observed_blob != TEMPLATE_BLOB_SHA:
        print(
            "Template preflight: FAIL — "
            f"expected {TEMPLATE_BLOB_SHA}, got {observed_blob}"
        )
        return 2

    source = raw.decode("utf-8")
    for old, new in REPLACEMENTS:
        count = source.count(old)
        if count < 1:
            print(f"Transform preflight: FAIL — missing token {old!r}")
            return 2
        source = source.replace(old, new)

    stream_old = """        max_tokens=2048,\n        max_kv_size=4096,\n"""
    stream_new = """        max_tokens=2048,\n        max_kv_size=4096,\n        kv_bits=8,\n        kv_group_size=64,\n        quantized_kv_start=0,\n"""
    stream_count = source.count(stream_old)
    if stream_count != 1:
        print(f"KV transform preflight: FAIL — stream_generate target count={stream_count}, expected 1")
        return 2
    source = source.replace(stream_old, stream_new, 1)

    kv_old = '            "kv_bits": None,\n'
    kv_new = (
        '            "kv_bits": 8,\n'
        '            "kv_group_size": 64,\n'
        '            "quantized_kv_start": 0,\n'
    )
    kv_count = source.count(kv_old)
    if kv_count != 1:
        print(f"Runtime-summary KV transform preflight: FAIL — target count={kv_count}, expected 1")
        return 2
    source = source.replace(kv_old, kv_new, 1)

    child_kv_old = '        "kv_bits": None,\n'
    child_kv_new = (
        '        "kv_bits": 8,\n'
        '        "kv_group_size": 64,\n'
        '        "quantized_kv_start": 0,\n'
    )
    child_kv_count = source.count(child_kv_old)
    if child_kv_count != 1:
        print(f"Child-result KV transform preflight: FAIL — target count={child_kv_count}, expected 1")
        return 2
    source = source.replace(child_kv_old, child_kv_new, 1)

    required = [
        'MODEL_REPO = "' + NEW_MODEL_REPO + '"',
        'MODEL_SHA256 = "' + NEW_MODEL_SHA + '"',
        'model_dir = mlx_root / "models" / "Qwen3-8B-4bit"',
        'run_dir = mlx_root / "8b-4bit-kv8-rescue-001" / run_id',
        'ADAPTER_BLOB_SHA = "62abab57f6463c5813809b43d8f1e7bdfec5f304"',
        'SCORER_BLOB_SHA = "754e9a6506968d2b191bff57997710591efe8133"',
        'BENCHMARK_VERSION = "1.0.1"',
        "MAX_KV_SIZE = 4096",
        "MAX_TOKENS = 2048",
        "MIN_FREE_PERCENT = 5",
        "MAX_SWAP_MB = 5600.0",
        "kv_bits=8",
        "kv_group_size=64",
        "quantized_kv_start=0",
        '"kv_bits": 8',
        '"single_loaded_model_session": True',
    ]
    for needle in required:
        if needle not in source:
            print(f"Runtime invariant preflight: FAIL — missing {needle!r}")
            return 2

    forbidden = [
        OLD_MODEL_REPO,
        OLD_MODEL_SHA,
        '"Qwen3-8B-3bit"',
        '"coding-benchmark-001"',
        '"kv_bits": None',
    ]
    for needle in forbidden:
        if needle in source:
            print(f"Runtime invariant preflight: FAIL — forbidden token remains {needle!r}")
            return 2

    print("LOOM Direct MLX 8B 4-bit KV8 Rescue 001 — frozen transform")
    print(f"Template blob: PASS {observed_blob}")
    print("Model transform: PASS Qwen3-8B-4bit")
    print("KV policy: PASS kv_bits=8, kv_group_size=64, quantized_kv_start=0")
    print("max_kv_size remains 4096; benchmark/safety invariants frozen")

    namespace = {
        "__name__": "__main__",
        "__file__": str(template),
        "__package__": None,
    }
    try:
        exec(compile(source, str(template), "exec"), namespace)
    except SystemExit as exc:
        code = exc.code
        return int(code) if isinstance(code, int) else 1
    return 0


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    if len(sys.argv) == 2 and sys.argv[1] == "--launched":
        return launch_transformed_benchmark(repo)
    if len(sys.argv) != 1:
        print("usage: direct_mlx_8b_4bit_kv8_rescue_001.py")
        return 2
    return host_gate(repo)


if __name__ == "__main__":
    raise SystemExit(main())
