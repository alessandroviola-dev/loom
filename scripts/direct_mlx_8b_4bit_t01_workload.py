#!/usr/bin/env python3
"""LOOM Direct MLX 8B 4-bit T01 Workload Safety 001.

This wrapper derives the 4-bit workload runner from the already-validated 3-bit
T01 runner and changes only model identity/result labels. The frozen benchmark,
runtime, KV policy, generation budget, telemetry and safety logic remain the
same.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

TEMPLATE_BLOB_SHA = "e063fdaa11d7cee9bbbbf9ce0b8306e62855388e"
OLD_MODEL_SHA = "b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1"
NEW_MODEL_SHA = "f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8"

REPLACEMENTS = [
    ("LOOM Direct MLX 8B 3-bit T01 Workload Safety 001", "LOOM Direct MLX 8B 4-bit T01 Workload Safety 001"),
    (OLD_MODEL_SHA, NEW_MODEL_SHA),
    ("Qwen3-8B-3bit", "Qwen3-8B-4bit"),
    ("8b-3bit-t01-workload-001", "8b-4bit-t01-workload-001"),
]


def git_blob_bytes(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    here = Path(__file__).resolve()
    template = here.with_name("direct_mlx_8b_3bit_t01_workload.py")
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
        'MODEL_SHA256 = "' + NEW_MODEL_SHA + '"',
        'model_dir = mlx_root / "models" / "Qwen3-8B-4bit"',
        'run_dir = mlx_root / "8b-4bit-t01-workload-001" / run_id',
        "MAX_KV_SIZE = 4096",
        "MAX_TOKENS = 2048",
        "MIN_FREE_PERCENT = 5",
        "MAX_SWAP_MB = 5600.0",
        'ADAPTER_BLOB_SHA = "62abab57f6463c5813809b43d8f1e7bdfec5f304"',
    ]
    for needle in required:
        if needle not in source:
            print(f"Runtime invariant preflight: FAIL — missing {needle!r}")
            return 2

    forbidden = [OLD_MODEL_SHA, "Qwen3-8B-3bit", "8b-3bit-t01-workload-001"]
    for needle in forbidden:
        if needle in source:
            print(f"Runtime invariant preflight: FAIL — old 3-bit token remains: {needle!r}")
            return 2

    print("LOOM Direct MLX 8B 4-bit T01 Workload Safety 001 — frozen transform")
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
