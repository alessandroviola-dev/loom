# LOOM — llama.cpp 8B Q2 Stage B 001

Date: 2026-08-19
Run id: `20260819-103952`
Status: **FULL_PASS**

## Purpose

Complete the preregistered throughput stage for the Qwen3-8B Q2_K profile after Capability 003 provided recovered-valid Stage A launch/memory evidence.

Plan: `research/runtime/llama-cpp-8b-q2-stage-b-001-plan.md`
Runner: `scripts/llama_cpp_8b_q2_stage_b.py`

## Frozen profile

- Apple M1, 8 GB unified memory
- llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- model `unsloth/Qwen3-8B-GGUF`
- file `Qwen3-8B-Q2_K.gguf`
- observed size 3.056 GiB
- expected/verified SHA256 `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- `llama-bench`
- `-ngl -1`
- flash attention auto
- pp512
- tg128
- repetitions 3
- JSON output
- abort below 5% free memory or above 5600 MB swap

## Device evidence

- `MTL0: Apple M1 (5461 MiB, 5460 MiB free)`
- BLAS: Accelerate
- unified memory true
- embedded Metal library loaded
- recommended Metal max working set 5726.63 MB

## Result

- pp512: **103.00 t/s ± 0.67**
- tg128: **13.72 t/s ± 0.34**
- backend: `MTL,BLAS`
- reported `n_gpu_layers=-1`
- Stage B: **PASS**
- wall: **53.536 s**
- peak process RSS: **2461.171875 MB**
- peak observed swap: **1990.38 MB**
- minimum observed free memory: **8%**
- guardrail breach: none
- classification: **FULL_PASS**
- disk free after: **43.688 GiB**

Run directory:
`results-local/llama-cpp/8b-q2-stage-b/20260819-103952`

Summary:
`results-local/llama-cpp/8b-q2-stage-b/20260819-103952/stage-b-summary.json`

## Interpretation

> Stage B confirms that the Qwen3-8B Q2_K profile can complete the frozen pp512/tg128 throughput workload on the reference M1 8 GB machine with Metal active and without breaching the established LOOM safety guardrails.

Combined with recovered Stage A run `20260819-103347`, this closes the technical capability gate for 8B Q2_K.

This result measures runtime feasibility and speed only. It does not establish model-quality superiority over the 4B Q4 profile.