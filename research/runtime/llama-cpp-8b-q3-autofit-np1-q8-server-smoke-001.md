# LOOM — llama.cpp 8B Q3 Auto-Fit NP1 Q8 KV Server Smoke 001

Date: 2026-08-19
Run id: `20260819-113658`
Classification: **FULL_PASS**

## Purpose

Test whether the verified Qwen3-8B Q3_K_M GGUF can serve safely at context 4096 on the Apple M1 / 8 GB reference machine after the previous single-slot F16-KV condition still crossed the frozen LOOM memory guardrail.

This condition retained explicit single-sequence server parallelism and changed only the target-model K/V KV cache from the runtime default F16 to Q8_0.

## Frozen artifact

- repository: `unsloth/Qwen3-8B-GGUF`
- file: `Qwen3-8B-Q3_K_M.gguf`
- quantization: `Q3_K_M`
- SHA256: `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed model size: **3.841 GiB**
- model SHA256: **PASS**

## Runtime condition

- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Release/Metal build
- `llama-server`
- context: `4096`
- parallelism: `-np 1`
- Flash Attention: `auto`
- no forced `-ngl -1`
- auto-fit: `--fit on`
- fit target: `--fit-target 1024`
- fit context: `--fit-ctx 4096`
- K KV cache: `Q8_0`
- V KV cache: `Q8_0`
- localhost / offline / no Web UI
- frozen guardrails: abort below 5% system-wide free memory or above 5600 MB swap

## Observed result

- disk free before: **43.599 GiB**
- model SHA256: **PASS**
- llama-server target: **PRESENT**
- server readiness: **PASS**, 8.756 s
- slot evidence `n_slots = 1`: **PASS**
- Q8_0 KV command evidence: **PASS**
- `/v1/chat/completions` smoke: **PASS**
- assistant content: `OK`
- peak process RSS: **2246.75 MB**
- peak observed swap: **2113.88 MB**
- minimum observed free memory: **6%**
- guardrail breach: **none**
- disk free after: **43.597 GiB**

Saved server evidence included:

```text
0.07.873.269 I srv load_model: initializing, n_slots = 1, n_ctx_slot = 4096, kv_unified = 'false'
```

Run directory:
`results-local/llama-cpp/8b-q3-autofit-np1-q8-server-smoke/20260819-113658`

Summary:
`results-local/llama-cpp/8b-q3-autofit-np1-q8-server-smoke/20260819-113658/autofit-server-smoke-summary.json`

## Interpretation

This exact Qwen3-8B Q3_K_M profile is technically API-servable at context 4096 under the frozen LOOM safety criterion when server parallelism is fixed to one sequence and both K/V KV caches use Q8_0.

The result does **not** establish that Q8_0 KV is universally sufficient for Q3, nor that it is superior to other memory strategies. It establishes only that this preregistered condition crossed the technical/API gate that the otherwise-identical NP1 condition with default F16 KV did not.

The safety margin remains narrow: minimum observed free memory was 6%, only one percentage point above the frozen 5% threshold. Full workload validation must therefore retain the same guardrails.

## Comparison with immediately prior NP1 F16-KV condition

Prior NP1/F16 run `20260819-112818`:
- `n_slots = 1`: PASS
- minimum free memory: 4%
- peak RSS: 2100.44 MB
- peak swap: 2295.94 MB
- classification: FAIL

Current NP1/Q8_0 run:
- `n_slots = 1`: PASS
- minimum free memory: 6%
- peak RSS: 2246.75 MB
- peak swap: 2113.88 MB
- classification: FULL_PASS

The frozen pass/fail boundary therefore changes in the expected direction under Q8_0 KV, but the telemetry components are system/process measurements and should not be over-interpreted as a complete decomposition of unified-memory use.

## Next gate

Do not expose this profile to Pi yet.

Next preregistered step: run frozen Coding Benchmark 01 v1.0.1 comparing Qwen3-8B Q3_K_M against Qwen3-4B Q4_K_M through the same pinned llama-server, with identical server/runtime settings for both profiles including `-np 1` and Q8_0 K/V KV cache.
