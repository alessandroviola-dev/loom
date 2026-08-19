# LOOM — llama.cpp 8B Q2 Capability 001 — INVALID

Date: 2026-08-19
Status: **INVALID AS FINAL CAPABILITY RESULT — STAGE A CLI INTERACTION DEFECT**

## Frozen profile attempted

- Model: `unsloth/Qwen3-8B-GGUF`
- File: `Qwen3-8B-Q2_K.gguf`
- Quantization: `Q2_K`
- Observed model size: **3.056 GiB**
- SHA256: PASS
- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- context: **4096**
- requested Metal offload: `-ngl -1`
- memory guardrails unchanged from Q4/Q3

## What happened

The model loaded successfully and reached actual inference. `llama-cli` displayed the model and accepted the frozen prompt `Reply only with OK.`. It began generation and reported an on-screen preliminary timing line of approximately:

- prompt: **32.8 t/s**
- generation: **14.3 t/s**

However, after the first response `llama-cli` remained at an interactive prompt instead of exiting, so the Stage A child did not complete the runner protocol automatically.

## Root cause

At the pinned llama.cpp commit, conversation mode is auto-enabled when a chat template is available. The CLI option `-st` / `--single-turn` is specifically documented to run one conversation turn and exit; when the first turn is supplied with `--prompt`, it does not remain interactive.

The original Q2 Stage A inherited the frozen Q4 command and did not include `-st`.

## Classification

This attempt is **INVALID**, not PASS or FAIL.

It provides useful diagnostic evidence that Q2_K can load and begin inference at context 4096 on the reference machine, but it does not satisfy the preregistered automated Stage A completion criteria and must not be used as the final Q2 capability result.

## Corrective action

Create Capability 002 with the same model/runtime/context/offload/guardrails and add only `-st` to the Stage A `llama-cli` invocation. The already SHA256-verified Q2 artifact must be reused; no redownload is required.
