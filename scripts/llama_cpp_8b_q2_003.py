#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q2 Capability 003.

Repeats the frozen Q2_K condition after Capability 002 was invalidated by an
over-strict Stage A evidence parser. Runtime/model parameters remain unchanged;
only Stage A evidence validation is corrected.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

TEMPLATE_BLOB_SHA = "83e01eae5ed12d13396f003d5291ba786a668ffd"

REPLACEMENTS = {
    '"""LOOM llama.cpp 8B Q4 Capability 001.': '"""LOOM llama.cpp 8B Q2 Capability 003.',
    'official Qwen3 8B Q4_K_M': 'community Qwen3 8B Q2_K',
    'MODEL_REPO = "Qwen/Qwen3-8B-GGUF"': 'MODEL_REPO = "unsloth/Qwen3-8B-GGUF"',
    'MODEL_FILE = "Qwen3-8B-Q4_K_M.gguf"': 'MODEL_FILE = "Qwen3-8B-Q2_K.gguf"',
    'MODEL_QUANT = "Q4_K_M"': 'MODEL_QUANT = "Q2_K"',
    'MODEL_SHA256 = "d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785"':
        'MODEL_SHA256 = "7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf"',
    'DISK_GUARD_GIB = 12': 'DISK_GUARD_GIB = 8',
    'Downloading {MODEL_FILE} (~4.68 GiB; resumable)...':
        'Downloading {MODEL_FILE} (~3.06 GiB; resumable)...',
    '"experiment": "llama.cpp 8B Q4 Capability 001"':
        '"experiment": "llama.cpp 8B Q2 Capability 003"',
    'print("LOOM llama.cpp 8B Q4 Capability 001")':
        'print("LOOM llama.cpp 8B Q2 Capability 003")',
    'out_dir = llama_root / "8b-q4" / run_id':
        'out_dir = llama_root / "8b-q2-003" / run_id',
    '"-n", "8", "-p", "Reply only with OK.", "--temp", "0", "--perf",':
        '"-n", "8", "-p", "Reply only with OK.", "--temp", "0", "--perf", "-st",',
    '    smoke_metal = "metal" in smoke_text or "mtl" in smoke_text\n':
        '    device_text = (devices.get("stdout", "") + devices.get("stderr", "")).lower()\n'
        '    smoke_metal = "mtl0" in device_text and "metal" in device_text\n',
    '    context_evidence = "4096" in smoke_text\n':
        '    smoke_command = smoke.get("command", [])\n'
        '    context_evidence = any(\n'
        '        smoke_command[i] == "-c" and i + 1 < len(smoke_command) and smoke_command[i + 1] == str(CTX)\n'
        '        for i in range(len(smoke_command))\n'
        '    )\n'
        '    offload_evidence = any(\n'
        '        smoke_command[i] == "-ngl" and i + 1 < len(smoke_command) and smoke_command[i + 1] == "-1"\n'
        '        for i in range(len(smoke_command))\n'
        '    )\n'
        '    single_turn_evidence = "-st" in smoke_command or "--single-turn" in smoke_command\n',
    '        and context_evidence\n    )\n':
        '        and context_evidence\n'
        '        and offload_evidence\n'
        '        and single_turn_evidence\n'
        '    )\n',
    '        "context_4096_evidence": context_evidence,\n        "pass": smoke_pass,\n':
        '        "context_4096_evidence": context_evidence,\n'
        '        "requested_offload_evidence": offload_evidence,\n'
        '        "single_turn_evidence": single_turn_evidence,\n'
        '        "stage_a_metal_preflight_evidence": smoke_metal,\n'
        '        "pass": smoke_pass,\n',
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
        print("LOOM llama.cpp 8B Q2 Capability 003")
        print("Template verification: FAIL")
        print(f"Observed Q4 runner blob: {blob or 'N/A'}")
        print(f"Expected Q4 runner blob: {TEMPLATE_BLOB_SHA}")
        return 2

    source = template.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        count = source.count(old)
        if count != 1:
            print("LOOM llama.cpp 8B Q2 Capability 003")
            print(f"Template transform: FAIL — expected one occurrence, found {count}: {old}")
            return 2
        source = source.replace(old, new)

    namespace = {
        "__name__": "loom_llama_cpp_8b_q2_003_impl",
        "__file__": str(here),
        "__package__": None,
    }
    exec(compile(source, str(here), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
