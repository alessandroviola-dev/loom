# LOOM — llama.cpp 8B Q3 Auto-Fit NP1 Server Smoke 001

Date: 2026-08-19
Run id: `20260819-112818`
Status: **VALID FAIL — MEMORY GUARDRAIL**

## Frozen condition

- Apple M1, 8 GB unified memory
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Qwen3-8B Q3_K_M
- exact local model SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- model size 3.841 GiB
- `llama-server` / Metal
- context 4096
- explicit `-np 1`
- Flash Attention auto
- no forced `-ngl -1`
- `--fit on --fit-target 1024 --fit-ctx 4096`
- default KV-cache types (F16 K / F16 V)
- localhost only / offline / no Web UI
- abort below 5% free memory or above 5600 MB swap

Plan: `research/runtime/llama-cpp-8b-q3-autofit-np1-server-smoke-001-plan.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_np1_server_smoke.py`

## Observed

- disk free before: **43.628 GiB**
- model SHA256: **PASS**
- llama-server target: **PRESENT**
- required slot evidence: **PASS**
- stderr: `n_slots = 1, n_ctx_slot = 4096, kv_unified = 'false'`
- API smoke: **FAIL / not authorized to complete after guardrail breach**
- peak process RSS: **2100.4375 MB**
- peak observed swap: **2295.94 MB**
- minimum observed free memory: **4%**
- guardrail: `memory free 4% < 5%`
- classification: **FAIL**
- disk free after: **43.632 GiB**

Run directory:
`results-local/llama-cpp/8b-q3-autofit-np1-server-smoke/20260819-112818`

Summary:
`results-local/llama-cpp/8b-q3-autofit-np1-server-smoke/20260819-112818/autofit-server-smoke-summary.json`

## Interpretation

This is a valid failure of the preregistered single-slot condition. The experiment successfully changed server concurrency from the previously observed four slots to exactly one slot, but the frozen memory margin was still violated at 4% free memory.

Therefore four-way server parallelism was not the dominant cause of the Q3 memory failure. The NP1 result does not establish zero memory effect: process RSS was slightly lower than in the prior auto-four-slot run, but minimum system free memory remained 4% and the runs are not suitable for claiming a precise causal memory saving from RSS alone.

Do not lower the 5% guardrail or reduce context post hoc.

## Next branch

The next separately preregistered one-variable rescue keeps this NP1 profile fixed and changes only the main-model KV-cache precision from the pinned default F16/F16 to Q8_0/Q8_0 using `-ctk q8_0 -ctv q8_0`.
