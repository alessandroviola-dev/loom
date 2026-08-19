# LOOM — llama.cpp 8B Q2 Capability 002 Plan

Date: 2026-08-19
Status: **PREREGISTERED — CORRECTED SINGLE-TURN STAGE A**

## Purpose

Repeat the Q2_K capability condition after Capability 001 was invalidated by a Stage A harness defect that left `llama-cli` in interactive conversation mode.

This is not a parameter rescue and does not change the research condition.

## Frozen condition

Unchanged from Q2 Capability 001:

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- quantization `Q2_K`
- expected SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- context **4096**
- requested Metal offload `-ngl -1`
- Stage A: tiny prompt, 8 generated tokens
- memory-free abort below **5%**
- swap abort above **5600 MB**
- Stage B pp512/tg128 x3 only if Stage A passes
- no automatic fallback

## Only correction

Add `-st` (`--single-turn`) to the Stage A `llama-cli` command.

At the pinned llama.cpp commit this option is documented to run one conversation turn and then exit. With a predefined `--prompt`, the CLI should not remain interactive after the response.

No model, context, offload, generation length, telemetry threshold, benchmark shape or success criterion changes.

## Artifact reuse

The Q2 model downloaded during Capability 001 passed SHA256 verification. Capability 002 must reuse that local artifact and independently verify its SHA256 before execution. It must not intentionally redownload the model when the verified file is already present.

## Success classification

- `FULL_PASS`: Stage A exits cleanly without guardrail breach, Stage B passes, Metal evidence present.
- `LAUNCH_PASS_BENCH_FAIL`: Stage A passes but Stage B fails or hits a guardrail.
- `FAIL`: verified Stage A cannot complete under the unchanged Q2 condition or hits a guardrail.

Capability 001 remains explicitly INVALID and must not be merged into Capability 002 measurements.
