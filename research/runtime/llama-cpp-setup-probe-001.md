# LOOM — llama.cpp Setup Probe 001

Date: 2026-08-18
Classification: `BLOCKED_MISSING_CMAKE`
Phase: 4 — llama.cpp

## Purpose

Run the preregistered Apple Silicon/Metal llama.cpp setup probe before any model download.

Plan:
- `research/runtime/llama-cpp-phase4-plan.md`

Runner:
- `scripts/llama_cpp_setup_probe.py`

Pinned llama.cpp source commit:
- `60addddf3c567c43ec3caf70fc953fba3572d96f`

## Observed run

Terminal result:

```text
LOOM llama.cpp Phase 4 setup probe
Prerequisites: FAIL — missing cmake
Summary: <repository-root>/results-local/llama-cpp/setup/20260818-233856/setup-summary.json
```

## Interpretation

The probe stopped at the prerequisite gate before cloning/configuring/building llama.cpp.

This is **not** a llama.cpp build failure and provides no evidence about Metal compatibility, compiler compatibility, or runtime feasibility.

The only observed blocker is that `cmake` is not currently available on PATH.

No experimental parameter should change. After installing CMake, rerun the exact same setup probe.

## Next step

1. Install/verify CMake on the reference Mac.
2. Rerun `scripts/llama_cpp_setup_probe.py` unchanged.
3. Only after a successful build proceed to the 4B GGUF runtime-control test.
