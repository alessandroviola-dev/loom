#!/usr/bin/env python3
"""LOOM llama.cpp Coding Quality Compare 002.

Reuses the frozen Compare 001 implementation after verifying its exact Git blob,
then transforms only the preregistered profile/runtime fields for the Qwen3-8B
Q3_K_M versus Qwen3-4B Q4_K_M comparison. Both profiles use identical NP1,
auto-fit and Q8_0 K/V KV-cache server settings.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

TEMPLATE_BLOB_SHA = "c8aeac7a56830abca633f0a6629be2c640d115f9"

OLD_Q2_PROFILE = '''    {
        "key": "8b-q2",
        "label": "Qwen3 8B Q2_K",
        "model_file": "Qwen3-8B-Q2_K.gguf",
        "model_dir": "Qwen3-8B-GGUF",
        "model_repo": "unsloth/Qwen3-8B-GGUF",
        "sha256": "7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf",
        "quant": "Q2_K",
        "params": "8B",
        "alias": "loom-qwen3-8b-q2-quality",
    },'''

NEW_Q3_PROFILE = '''    {
        "key": "8b-q3",
        "label": "Qwen3 8B Q3_K_M",
        "model_file": "Qwen3-8B-Q3_K_M.gguf",
        "model_dir": "Qwen3-8B-GGUF",
        "model_repo": "unsloth/Qwen3-8B-GGUF",
        "sha256": "4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007",
        "quant": "Q3_K_M",
        "params": "8B",
        "alias": "loom-qwen3-8b-q3-quality-002",
    },'''

OLD_SERVER_CMD = '''    server_cmd = [
        str(server),
        "-m", str(model_path),
        "-ngl", "-1",
        "-c", str(CTX),
        "-fa", "auto",
        "--host", HOST,
        "--port", str(PORT),
        "--alias", profile["alias"],
        "--no-webui",
        "--offline",
    ]'''

NEW_SERVER_CMD = '''    server_cmd = [
        str(server),
        "-m", str(model_path),
        "-c", str(CTX),
        "-np", "1",
        "-fa", "auto",
        "--fit", "on",
        "--fit-target", "1024",
        "--fit-ctx", str(CTX),
        "-ctk", "q8_0",
        "-ctv", "q8_0",
        "--host", HOST,
        "--port", str(PORT),
        "--alias", profile["alias"],
        "--no-webui",
        "--offline",
    ]'''

REPLACEMENTS = [
    (
        '"""LOOM llama.cpp Coding Quality Compare 001.\\n\\nRuns the frozen LOOM Coding Benchmark 01 v1.0.1 in single-shot mode against\\nQwen3-8B Q2_K and Qwen3-4B Q4_K_M through the same pinned llama-server raw\\n/completion API. No task retries, test feedback, salvage, or prompt changes.\\n"""',
        '"""LOOM llama.cpp Coding Quality Compare 002.\\n\\nRuns the frozen LOOM Coding Benchmark 01 v1.0.1 in single-shot mode against\\nQwen3-8B Q3_K_M and Qwen3-4B Q4_K_M through the same pinned llama-server raw\\n/completion API with identical NP1/Q8-KV auto-fit runtime settings.\\n"""',
    ),
    ('PORT = 18082', 'PORT = 18086'),
    (OLD_Q2_PROFILE, NEW_Q3_PROFILE),
    ('"alias": "loom-qwen3-4b-q4-quality",', '"alias": "loom-qwen3-4b-q4-quality-002",'),
    (OLD_SERVER_CMD, NEW_SERVER_CMD),
    ('run_root = llama_root / "coding-quality-compare-001" / run_id', 'run_root = llama_root / "coding-quality-compare-002" / run_id'),
    ('print("LOOM llama.cpp Coding Quality Compare 001")', 'print("LOOM llama.cpp Coding Quality Compare 002")'),
    ('print("Profiles: 8B Q2 first, then 4B Q4")', 'print("Profiles: 8B Q3 first, then 4B Q4; common runtime NP1 + Q8_0 KV")'),
    ('"experiment": "llama.cpp Coding Quality Compare 001",', '"experiment": "llama.cpp Coding Quality Compare 002",'),
    (
        '"context": CTX,\n        "profile_order": [x["key"] for x in PROFILES],',
        '"context": CTX,\n        "server_settings": {\n            "parallel": 1,\n            "flash_attention": "auto",\n            "fit": "on",\n            "fit_target_mib": 1024,\n            "fit_ctx": CTX,\n            "cache_type_k": "q8_0",\n            "cache_type_v": "q8_0",\n            "forced_gpu_layers": None,\n        },\n        "profile_order": [x["key"] for x in PROFILES],',
    ),
    ('score_8 = by_key.get("8b-q2", {}).get("delivery_adjusted_score")', 'score_8 = by_key.get("8b-q3", {}).get("delivery_adjusted_score")'),
    ('print(f"8B Q2 delivery-adjusted: {score_8}/100")', 'print(f"8B Q3 delivery-adjusted: {score_8}/100")'),
]


def main() -> int:
    here = Path(__file__).resolve()
    repo_root = here.parents[1]
    template = here.with_name("llama_cpp_coding_quality_compare.py")

    if not template.exists():
        print(f"Template missing: {template}")
        return 2

    proc = subprocess.run(
        ["git", "hash-object", str(template)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    blob = proc.stdout.strip() if proc.returncode == 0 else ""
    if blob != TEMPLATE_BLOB_SHA:
        print("LOOM llama.cpp Coding Quality Compare 002")
        print("Template verification: FAIL")
        print(f"Observed template blob: {blob or 'N/A'}")
        print(f"Expected template blob: {TEMPLATE_BLOB_SHA}")
        return 2

    source = template.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS:
        count = source.count(old)
        if count != 1:
            print("LOOM llama.cpp Coding Quality Compare 002")
            print(f"Template transform: FAIL — expected one occurrence, found {count}")
            print(f"Needle: {old[:200]}")
            return 2
        source = source.replace(old, new)

    # Pre-execution invariants: the generated implementation must carry the
    # exact preregistered common server policy and must no longer force -ngl.
    required = [
        '"-np", "1"',
        '"--fit", "on"',
        '"--fit-target", "1024"',
        '"--fit-ctx", str(CTX)',
        '"-ctk", "q8_0"',
        '"-ctv", "q8_0"',
        '"key": "8b-q3"',
    ]
    missing = [needle for needle in required if needle not in source]
    if missing or '"-ngl", "-1"' in source:
        print("LOOM llama.cpp Coding Quality Compare 002")
        print("Generated implementation invariant: FAIL")
        for needle in missing:
            print(f"Missing: {needle}")
        if '"-ngl", "-1"' in source:
            print("Unexpected forced -ngl -1 remains")
        return 2

    namespace = {
        "__name__": "loom_llama_cpp_coding_quality_compare_002_impl",
        "__file__": str(here),
        "__package__": None,
    }
    exec(compile(source, str(here), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
