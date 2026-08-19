#!/usr/bin/env python3
"""LOOM llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001.

Executes the preregistered Q8_0 KV-cache rescue by reusing the frozen Q3
auto-fit server-smoke implementation. Relative to the already-run NP1
condition, only main-model K/V KV-cache precision changes from F16 to Q8_0.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

TEMPLATE_BLOB_SHA = "9dd7677107601132e57e7c84bd58d0710fb138f9"

REPLACEMENTS = {
    '"""LOOM llama.cpp 8B Q3 Auto-Fit Server Smoke 001.':
        '"""LOOM llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001.',
    'MODEL_ALIAS = "loom-qwen3-8b-q3-autofit"':
        'MODEL_ALIAS = "loom-qwen3-8b-q3-autofit-np1-q8"',
    'PORT = 18083': 'PORT = 18085',
    'needles = ("fit", "offload", "gpu layer", "gpu_layers", "n_gpu_layers", "metal")':
        'needles = ("fit", "offload", "gpu layer", "gpu_layers", "n_gpu_layers", "metal", "n_slots", "n_ctx_slot", "cache", "q8_0")',
    'print("LOOM llama.cpp 8B Q3 Auto-Fit Server Smoke 001")':
        'print("LOOM llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001")',
    '"experiment": "llama.cpp 8B Q3 Auto-Fit Server Smoke 001"':
        '"experiment": "llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001"',
    '"gpu_layers_override": None,\n            "fit": "on",':
        '"gpu_layers_override": None,\n            "n_parallel": 1,\n            "fit": "on",',
    '"kv_cache_types": "runtime defaults",':
        '"kv_cache_types": {"k": "q8_0", "v": "q8_0"},',
    'out_dir = llama_root / "8b-q3-autofit-server-smoke" / run_id':
        'out_dir = llama_root / "8b-q3-autofit-np1-q8-server-smoke" / run_id',
    '        "-c", str(CTX),\n        "-fa", "auto",':
        '        "-c", str(CTX),\n        "-np", "1",\n        "-ctk", "q8_0",\n        "-ctv", "q8_0",\n        "-fa", "auto",',
    'print("Launching llama-server with automatic fit...", flush=True)':
        'print("Launching llama-server with automatic fit, -np 1 and Q8_0 KV...", flush=True)',
    '    full_pass = ready and guard_abort_reason is None and request_pass\n    summary["classification"] = "FULL_PASS" if full_pass else "FAIL"\n    if not full_pass:\n        if guard_abort_reason:\n            summary["failure_reason"] = guard_abort_reason\n        elif not ready:\n            summary["failure_reason"] = "server did not reach healthy state before timeout/exit"\n        else:\n            summary["failure_reason"] = "chat completion API smoke failed"':
        '    slot_evidence = any("n_slots = 1" in line for line in stderr_text.splitlines())\n    q8_requested = ("-ctk" in server_cmd and server_cmd[server_cmd.index("-ctk") + 1] == "q8_0" and "-ctv" in server_cmd and server_cmd[server_cmd.index("-ctv") + 1] == "q8_0")\n    summary["slot_evidence_n_slots_1"] = slot_evidence\n    summary["kv_cache_q8_command_evidence"] = q8_requested\n    full_pass = ready and guard_abort_reason is None and request_pass and slot_evidence and q8_requested\n    summary["classification"] = "FULL_PASS" if full_pass else "FAIL"\n    if not full_pass:\n        if guard_abort_reason:\n            summary["failure_reason"] = guard_abort_reason\n        elif not ready:\n            summary["failure_reason"] = "server did not reach healthy state before timeout/exit"\n        elif not slot_evidence:\n            summary["failure_reason"] = "missing required n_slots = 1 server-log evidence"\n        elif not q8_requested:\n            summary["failure_reason"] = "missing required Q8_0 KV command evidence"\n        else:\n            summary["failure_reason"] = "chat completion API smoke failed"',
    '    print(f"API smoke: {\'PASS\' if request_pass else \'FAIL\'}")':
        '    print(f"Slot evidence n_slots=1: {\'PASS\' if slot_evidence else \'FAIL\'}")\n    print(f"Q8_0 KV command evidence: {\'PASS\' if q8_requested else \'FAIL\'}")\n    print(f"API smoke: {\'PASS\' if request_pass else \'FAIL\'}")',
}


def main() -> int:
    here = Path(__file__).resolve()
    template = here.with_name("llama_cpp_8b_q3_autofit_server_smoke.py")
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
        print("LOOM llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001")
        print("Template verification: FAIL")
        print(f"Observed template blob: {blob or 'N/A'}")
        print(f"Expected template blob: {TEMPLATE_BLOB_SHA}")
        return 2

    source = template.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        count = source.count(old)
        if count != 1:
            print("LOOM llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001")
            print(f"Template transform: FAIL — expected one occurrence, found {count}: {old}")
            return 2
        source = source.replace(old, new)

    namespace = {
        "__name__": "loom_llama_cpp_8b_q3_autofit_np1_q8_impl",
        "__file__": str(here),
        "__package__": None,
    }
    exec(compile(source, str(here), "exec"), namespace)
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
