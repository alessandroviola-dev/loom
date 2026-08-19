# LOOM — llama.cpp 8B Q2 Server Smoke 001

Date: 2026-08-19
Run id: `20260819-104946`
Status: **CANONICAL FULL_PASS**

## Purpose

Validate that the technically runnable Qwen3-8B Q2_K profile can be exposed through `llama-server` on localhost at context 4096 under the established LOOM memory/swap guardrails.

## Frozen condition

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- observed size `3.056 GiB`
- model SHA256 PASS
- context `4096`
- requested GPU layers `-ngl -1`
- Flash Attention `auto`
- localhost only (`127.0.0.1`)
- Web UI disabled
- abort below 5% free memory
- abort above 5600 MB swap

## Observed result

- disk free before: **44.696 GiB**
- model SHA256: **PASS**
- `llama-server` target build: **PASS**
- server readiness: **PASS in 5.684 s**
- `/v1/chat/completions` smoke: **PASS**
- assistant content: `OK`
- peak process RSS: **1729.328125 MB**
- peak observed swap: **1855.12 MB**
- minimum observed free memory: **6%**
- classification: **FULL_PASS**
- disk free after: **43.611 GiB**

Run directory:
`results-local/llama-cpp/8b-q2-server-smoke/20260819-104946`

Summary:
`results-local/llama-cpp/8b-q2-server-smoke/20260819-104946/server-smoke-summary.json`

## Interpretation

The 8B Q2 profile is not only runnable through `llama-cli`/`llama-bench`; it can also serve a real localhost API request through `llama-server` at context 4096 without breaching the frozen guardrails.

The headroom is narrow: minimum free memory reached **6%**, only one percentage point above the 5% abort threshold. Therefore subsequent quality/agent tests must keep the same live guardrails and run only one llama.cpp model server at a time.

This result does not establish model quality. It authorizes the next objective comparison against the 4B Q4 control using the frozen Coding Benchmark 01 v1.0.1.
