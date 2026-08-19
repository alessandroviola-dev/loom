# LOOM — llama.cpp Coding Quality Compare 002 — Invalid Harness Attempt 001

Date: 2026-08-19
Status: **INVALID — HARNESS TRANSFORM FAILURE**

## Attempt

The preregistered `scripts/llama_cpp_coding_quality_compare_002.py` was invoked after a clean `git pull` and successful Python bytecode compilation.

Observed output stopped immediately at template transformation:

```text
LOOM llama.cpp Coding Quality Compare 002
Template transform: FAIL — expected one occurrence, found 0
Needle: """LOOM llama.cpp Coding Quality Compare 001.\n\nRuns the frozen LOOM Coding Benchmark 01 v1.0.1 in single-shot mode against\nQwen3-8B Q2_K and Qwen3-4B Q4_K_M through the same pinned llama-server raw
```

## Classification

**INVALID_HARNESS**.

No Q3 or 4B model server was launched, no benchmark task was executed, and no quality or resource measurement was produced. This attempt therefore has no scientific result and does not consume the preregistered comparison.

## Root cause

The Compare 002 wrapper verified the correct Compare 001 Git blob, then attempted a replacement using a needle containing literal escaped newline sequences (`\\n`) rather than matching the template's actual newline characters. A later summary-insertion needle used the same fragile pattern and would also have failed.

This was a harness-only defect. It did not alter model, benchmark, prompt, scorer, runtime policy, safety guardrails or decision criteria.

## Correction

The runner was revised to use smaller unique replacements plus the existing exact block replacements for the Q2 profile and server command. Pre-execution invariants still require:

- Qwen3 8B Q3_K_M profile;
- `-np 1`;
- `--fit on --fit-target 1024 --fit-ctx 4096`;
- `-ctk q8_0` and `-ctv q8_0`;
- no forced `-ngl -1`;
- same frozen Compare 001 template blob.

The scientific checkpoint remains `LLAMA_CPP_CODING_QUALITY_COMPARE_002_READY`; the corrected runner may be rerun without changing the preregistered experiment.