#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q3 Capability 001.

Runs the preregistered Q3_K_M condition by reusing the frozen, already-exercised
8B Q4 capability runner implementation with only experiment constants/labels
changed. The Q4 template Git blob is verified before transformation so future
edits cannot silently change this experiment.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

TEMPLATE_BLOB_SHA = "83e01eae5ed12d13396f003d5291ba786a668ffd"

REPLACEMENTS = {
    '"""LOOM llama.cpp 8B Q4 Capability 001.': '"""LOOM llama.cpp 8B Q3 Capability 001.',
    'official Qwen3 8B Q4_K_M': 'community Qwen3 8B Q3_K_M',
    'MODEL_REPO = "Qwen/Qwen3-8B-GGUF"': 'MODEL_REPO = "unsloth/Qwen3-8B-GGUF"',
    'MODEL_FILE = "Qwen3-8B-Q4_K_M.gguf"': 'MODEL_FILE = "Qwen3-8B-Q3_K_M.gguf"',
    'MODEL_QUANT = "Q4_K_M"': 'MODEL_QUANT = "Q3_K_M"',
    'MODEL_SHA256 = "d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785"':
        'MODEL_SHA256 = "4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007"',
    'DISK_GUARD_GIB = 12': 'DISK_GUARD_GIB = 10',
    'Downloading {MODEL_FILE} (~4.68 GiB; resumable)...':
        'Downloading {MODEL_FILE} (~3.84 GiB; resumable)...',
    '"experiment": "llama.cpp 8B Q4 Capability 001"':
        '"experiment": "llama.cpp 8B Q3 Capability 001"',
    'print("LOOM llama.cpp 8B Q4 Capability 001")':
        'print("LOOM llama.cpp 8B Q3 Capability 001")',
    'out_dir = llama_root / "8b-q4" / run_id':
        'out_dir = llama_root / "8b-q3" / run_id',
}


def main() -> int:
    here = Path(__file__).resolve()
    template = here.with_name("llama_cpp_8b_q4.py")
    if not template.exists():
        print(f"Template missing: {template}")
        return 2

    blob = subprocess.run(
        ["git", "hash-object", str(template)],
        cwd=here.parents[1],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if blob != TEMPLATE_BLOB_SHA:
        print("LOOM llama.cpp 8B Q3 Capability 001")
        print("Template verification: FAIL")
        print(f"Observed Q4 runner blob: {blob or 'N/A'}")
        print(f"Expected Q4 runner blob: {TEMPLATE_BLOB_SHA}")
        return 2

    source = template.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        count = source.count(old)
        if count != 1:
            print("LOOM llama.cpp 8B Q3 Capability 001")
            print(f"Template transform: FAIL — expected one occurrence, found {count}: {old}")
            return 2
        source = source.replace(old, new)

    namespace = {
        "__name__": "loom_llama_cpp_8b_q3_impl",
        "__file__": str(here),
        "__package__": None,
    }
    exec(compile(source, str(here), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
