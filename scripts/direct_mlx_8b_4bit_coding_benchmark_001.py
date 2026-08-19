#!/usr/bin/env python3
"""LOOM Direct MLX 8B 4-bit Coding Benchmark 001.

Derives the 4-bit full benchmark runner from the already-validated 3-bit
Direct MLX Coding Benchmark 001 implementation. Only model identity and result
labels/directories are transformed; benchmark, prompts, parser, scorer, runtime,
KV policy, generation budget, telemetry and safety logic remain frozen.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

TEMPLATE_BLOB_SHA = "01b00d604026affff4bad0d599a3159faaf786ae"
OLD_MODEL_REPO = "mlx-community/Qwen3-8B-3bit"
NEW_MODEL_REPO = "mlx-community/Qwen3-8B-4bit"
OLD_MODEL_SHA = "b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1"
NEW_MODEL_SHA = "f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8"

REPLACEMENTS = [
    ("LOOM Direct MLX Coding Benchmark 001", "LOOM Direct MLX 8B 4-bit Coding Benchmark 001"),
    ("Direct MLX Coding Benchmark 001", "Direct MLX 8B 4-bit Coding Benchmark 001"),
    (OLD_MODEL_REPO, NEW_MODEL_REPO),
    (OLD_MODEL_SHA, NEW_MODEL_SHA),
    ("Qwen3-8B-3bit", "Qwen3-8B-4bit"),
    ('"coding-benchmark-001"', '"8b-4bit-coding-benchmark-001"'),
]


def git_blob_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    here = Path(__file__).resolve()
    template = here.with_name("direct_mlx_coding_benchmark_001.py")
    raw = template.read_bytes()
    observed_blob = git_blob_bytes(raw)
    if observed_blob != TEMPLATE_BLOB_SHA:
        print(
            "Template preflight: FAIL — "
            f"expected blob {TEMPLATE_BLOB_SHA}, got {observed_blob}"
        )
        return 2

    source = raw.decode("utf-8")
    for old, new in REPLACEMENTS:
        count = source.count(old)
        if count < 1:
            print(f"Template transform: FAIL — missing required token: {old!r}")
            return 2
        source = source.replace(old, new)

    required = [
        'MODEL_REPO = "' + NEW_MODEL_REPO + '"',
        'MODEL_SHA256 = "' + NEW_MODEL_SHA + '"',
        'model_dir = mlx_root / "models" / "Qwen3-8B-4bit"',
        'run_dir = mlx_root / "8b-4bit-coding-benchmark-001" / run_id',
        'ADAPTER_BLOB_SHA = "62abab57f6463c5813809b43d8f1e7bdfec5f304"',
        'SCORER_BLOB_SHA = "754e9a6506968d2b191bff57997710591efe8133"',
        'BENCHMARK_VERSION = "1.0.1"',
        "MAX_KV_SIZE = 4096",
        "MAX_TOKENS = 2048",
        "MIN_FREE_PERCENT = 5",
        "MAX_SWAP_MB = 5600.0",
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
    ]
    for needle in forbidden:
        if needle in source:
            print(f"Runtime invariant preflight: FAIL — old 3-bit token remains: {needle!r}")
            return 2

    print("LOOM Direct MLX 8B 4-bit Coding Benchmark 001 — frozen transform")
    print(f"Template blob: PASS {observed_blob}")
    print("4-bit model/runtime transform: PASS")

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


if __name__ == "__main__":
    raise SystemExit(main())
