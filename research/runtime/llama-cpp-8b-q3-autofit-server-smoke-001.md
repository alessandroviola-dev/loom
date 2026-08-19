# LOOM — llama.cpp 8B Q3 Auto-Fit Server Smoke 001

Date: 2026-08-19
Run id: `20260819-111648`
Status: **VALID FAIL — MEMORY GUARDRAIL**

## Purpose

Test whether the existing higher-quality Qwen3-8B Q3_K_M artifact can serve at context 4096 when pinned llama.cpp is allowed to use its automatic fit/device-placement policy instead of the earlier forced `-ngl -1` condition.

## Frozen condition

- Apple M1, 8 GB unified memory
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- `llama-server`
- Qwen3-8B Q3_K_M
- local artifact `Qwen3-8B-Q3_K_M.gguf`
- expected SHA256 `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`
- observed size **3.841 GiB**
- explicit context **4096**
- Flash Attention `auto`
- no forced `-ngl -1`
- `--fit on`
- `--fit-target 1024`
- `--fit-ctx 4096`
- default KV-cache types
- localhost only / Web UI disabled / offline
- abort below **5% free memory** or above **5600 MB swap**

Plan: `research/runtime/llama-cpp-8b-q3-autofit-server-smoke-001-plan.md`
Runner: `scripts/llama_cpp_8b_q3_autofit_server_smoke.py`

## Observed console result

- disk free before: **43.659 GiB**
- model SHA256: **PASS**
- model size: **3.841 GiB**
- `llama-server` target already present
- server launched with automatic fit
- API smoke: **FAIL**
- peak process RSS: **2121.859375 MB**
- peak observed swap: **2263.31 MB**
- minimum observed free memory: **4%**
- guardrail: `memory free 4% < 5%`
- classification: **FAIL**
- disk free after: **43.658 GiB**

Run directory:
`results-local/llama-cpp/8b-q3-autofit-server-smoke/20260819-111648`

Summary:
`results-local/llama-cpp/8b-q3-autofit-server-smoke/20260819-111648/autofit-server-smoke-summary.json`

## Interpretation

This is a valid failure of the preregistered Q3 auto-fit condition because the frozen memory guardrail was crossed. The Q3 profile is therefore **not authorized for the coding-quality benchmark** under this exact server/fit condition.

The console output does not by itself establish exactly what device-placement decision `--fit` made before the guardrail fired. The runner persisted `fit_offload_log_lines`, health history and memory samples; those existing artifacts must be inspected before choosing the next one-variable rescue.

Descriptively, the minimum-free-memory observation improved from **1%** in the earlier forced-Q3 capability run to **4%** here, but these are different execution shapes (`llama-cli` forced maximum offload vs `llama-server` auto-fit), so this is not a controlled performance comparison.

## Decision boundary

Do not:
- lower the 5% safety guardrail post hoc;
- reduce context in this result;
- change several memory variables at once;
- proceed to Pi or the coding-quality benchmark with this Q3 condition.

Next action: inspect the already-saved auto-fit/offload lines, readiness state and final memory samples without rerunning inference. Based on that evidence, preregister exactly one next memory intervention (candidate already anticipated by the roadmap: Q3 KV-cache compression starting with Q8_0) or move to Direct MLX if the fit logs show no useful remaining llama.cpp headroom.
