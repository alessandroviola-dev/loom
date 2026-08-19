# LOOM — llama.cpp 8B Q2 Capability 003 Plan

Date: 2026-08-19
Status: **PREREGISTERED — CORRECTED STAGE A EVIDENCE VALIDATION**

## Purpose

Repeat the frozen Q2_K condition after Capability 002 completed a single turn with healthy memory headroom but was invalidated by an over-strict Stage A evidence parser.

This is not a model/runtime parameter rescue.

## Frozen runtime/model condition

Unchanged from Capability 002:
- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- context **4096**
- `-ngl -1`
- `-st`
- 8-token Stage A prompt
- abort below 5% memory free
- abort above 5600 MB swap
- Stage B pp512/tg128 x3 only if Stage A passes
- no automatic fallback

## Validation defect being corrected

The inherited Q4 validator required the literal strings `4096` and `metal`/`mtl` to appear in Stage A child stdout/stderr. Capability 002 completed inference and exited cleanly but those strings were not printed by the child, causing a false Stage A FAIL.

## Capability 003 Stage A evidence

Stage A will validate the execution condition from deterministic runtime evidence rather than optional log text:

1. the executed command must contain the exact adjacent pair `-c 4096`;
2. the executed command must contain the exact adjacent pair `-ngl -1`;
3. the executed command must contain `-st` or `--single-turn`;
4. the same-run device preflight must show both `MTL0` and Metal backend initialization/evidence;
5. the child must exit with code 0;
6. it must not time out;
7. it must not hit a memory/swap guardrail;
8. stdout must be non-empty.

Rationale: `-c` is the documented llama.cpp context-size argument. A cleanly completed inference command containing `-c 4096` demonstrates that the requested value was accepted. Effective offload/performance remains independently characterized by Stage B `llama-bench` backend and `n_gpu_layers` output.

## Stage B

Unchanged:
- same verified Q2 model;
- `-ngl -1`;
- flash attention auto;
- pp512;
- tg128;
- 3 repetitions;
- JSON output;
- same memory/swap guardrails.

## Classification

- `FULL_PASS`: corrected Stage A passes and Stage B passes without guardrail breach.
- `LAUNCH_PASS_BENCH_FAIL`: Stage A passes; Stage B fails/aborts.
- `FAIL`: Stage A genuinely fails under the frozen profile or breaches a guardrail.

Capability 001 and Capability 002 remain INVALID and diagnostic only.
