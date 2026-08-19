# LOOM — llama.cpp Coding Quality Compare 001

Date: 2026-08-19
Run id: `20260819-110234`
Status: **COMPLETE — PRIMARY RELATION 4B_HIGHER; FAILURE-MODE DIAGNOSTIC PENDING**

## Frozen comparison

Plan: `research/runtime/llama-cpp-coding-quality-compare-001-plan.md`
Runner: `scripts/llama_cpp_coding_quality_compare.py`
Benchmark: LOOM Coding Benchmark 01 v1.0.1, `single_shot`

Compared conditions:
1. Qwen3-8B Q2_K via pinned llama.cpp/Metal/llama-server
2. Qwen3-4B Q4_K_M via the same pinned llama.cpp/Metal/llama-server

Shared frozen runtime/request condition:
- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- context 4096
- `-ngl -1`
- Flash Attention auto
- localhost-only server
- raw `POST /completion`
- exact frozen benchmark prompt construction
- `n_predict=2048`
- `temperature=0`
- `seed=0`
- `stream=false`
- `cache_prompt=false`
- `json_schema={}`
- one request per task, no retry, salvage, re-prompt or test feedback

## Observed result

Disk free before: **44.594 GiB**
Disk free after: **43.591 GiB**

### Qwen3 8B Q2_K

- server readiness: PASS in **6.294 s**
- T01: adapter `failed`
- T02: adapter `failed`
- T03: adapter `failed`
- T04: adapter `failed`
- T05: adapter `failed`
- T06: adapter `failed`
- artifact score: **15.0/100**
- delivery-adjusted score: **0/100**
- profile classification: `COMPLETE`

### Qwen3 4B Q4_K_M

- server readiness: PASS in **1.043 s**
- T01: `written`
- T02: `written`
- T03: adapter `failed`
- T04: adapter `failed`
- T05: `written`
- T06: `written`
- artifact score: **42.86/100**
- delivery-adjusted score: **34.29/100**
- profile classification: `COMPLETE`

## Primary comparison

Frozen primary metric: delivery-adjusted score.

- 8B Q2: **0/100**
- 4B Q4: **34.29/100**
- signed delta `8B - 4B`: **-34.29**
- preregistered descriptive relation: **`4B_HIGHER`**
- overall runner classification: **`COMPLETE`**

This primary result is canonical and must not be changed after failure-mode inspection.

## Important interpretation boundary

Do **not** yet translate the 0/100 delivery score into a claim that the 8B Q2 has zero semantic coding capability.

All six 8B tasks failed at the adapter/delivery layer. The runner marks a task failed when, for example:
- HTTP transport is not 200;
- the server response does not contain string `content`;
- generated content cannot be parsed as the exact required JSON file envelope;
- returned filenames/values violate the frozen adapter contract.

The model response is saved before adapter parsing, so these failure modes can be diagnosed without rerunning inference.

Also, the 8B artifact score of 15.0/100 must not be treated as 15 model-earned points. The frozen benchmark tree is copied before inference, and failed adapter outputs are not written. Some raw artifact points may therefore come from the initial fixture state.

## Canonical conclusion at this checkpoint

> Under the frozen end-to-end single-shot delivery metric, Qwen3-4B Q4_K_M clearly outperformed Qwen3-8B Q2_K: 34.29 vs 0. The 8B Q2 is therefore **not established as a practical upgrade** despite its technical runtime PASS.

However, because every 8B task failed at delivery, the exact failure classes must be inspected before deciding whether the next research branch should target quantization quality, prompt/protocol robustness, or a higher-quality Q3/Q4 memory strategy.

## Next action

Do not rerun either model. Inspect the persisted `comparison-summary.json`, profile summaries and raw API responses from run `20260819-110234`.

Required diagnostic:
- per-task adapter error;
- HTTP status;
- stop type;
- evaluated/predicted token counts;
- whether response content exists;
- content length;
- JSON parseability and top-level shape when possible;
- short content prefix for diagnosis only;
- profile telemetry/guardrail state.

After the diagnostic, freeze the failure-mode interpretation and choose the next preregistered experiment.