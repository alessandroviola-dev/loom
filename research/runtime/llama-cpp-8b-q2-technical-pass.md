# LOOM — llama.cpp Qwen3 8B Q2_K Technical Pass

Date: 2026-08-19
Status: **CANONICAL TECHNICAL FULL PASS**

## Scope

This record combines the recovered-valid Stage A launch/memory evidence from Q2 Capability 003 with the independently preregistered Stage B 001 throughput result.

It establishes technical runnability of this exact profile. It does **not** establish that Q2 8B is a better model-quality choice than the 4B Q4 control.

## Frozen profile

- reference machine: Apple M1, 8 GB unified memory
- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- backend: Metal / Accelerate
- model source: `unsloth/Qwen3-8B-GGUF`
- file: `Qwen3-8B-Q2_K.gguf`
- observed model size: **3.056 GiB**
- SHA256: `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`
- context for Stage A: **4096**
- requested GPU layers: `-ngl -1`
- frozen guardrails: abort below 5% memory free or above 5600 MB swap

## Stage A — recovered PASS

Source run: `20260819-103347`

Validated evidence:
- exit code 0
- no timeout
- no guardrail abort
- exact `-c 4096` command evidence
- exact `-ngl -1` command evidence
- `-st` single-turn evidence
- same-run Metal device preflight evidence
- one turn visibly executed and CLI exited
- wall: **7.134 s**
- peak process RSS: **2092.97 MB**
- peak observed swap: **1986.56 MB**
- minimum observed free memory: **10%**
- visible diagnostic timing: prompt ~42.7 t/s, generation ~13.4 t/s

The original Stage A boolean was false only because the harness required captured stdout while llama-cli emitted visible TTY output outside the captured pipes. That capture criterion was invalidated separately; Stage A operational evidence is accepted as recovered PASS.

Record: `research/runtime/llama-cpp-8b-q2-003-recovered-stage-a.md`.

## Stage B 001 — FULL PASS

Run id: `20260819-103952`
Run directory: `results-local/llama-cpp/8b-q2-stage-b/20260819-103952`

Benchmark shape:
- `llama-bench`
- `-ngl -1`
- flash attention auto
- pp512
- tg128
- 3 repetitions

Observed:
- **pp512: 103.00 t/s ± 0.67**
- **tg128: 13.72 t/s ± 0.34**
- backend: `MTL,BLAS`
- reported `n_gpu_layers=-1`
- Stage B: **PASS**
- wall: **53.536 s**
- peak process RSS: **2461.17 MB**
- peak observed swap: **1990.38 MB**
- minimum observed free memory: **8%**
- classification: **FULL_PASS**
- disk free after: **43.688 GiB**

No safety guardrail was breached.

## Descriptive scaling vs 4B Q4 control

4B Q4 Runtime Control 001:
- pp512 230.85 t/s
- tg128 22.33 t/s
- peak RSS 1914.91 MB
- peak swap 1097.19 MB
- minimum free memory 22%

8B Q2 Stage B 001:
- pp512 103.00 t/s
- tg128 13.72 t/s
- peak RSS 2461.17 MB
- peak swap 1990.38 MB
- minimum free memory 8%

Descriptive ratios:
- 8B Q2 prompt throughput is **44.6%** of 4B Q4, a **55.4% reduction**
- 8B Q2 generation throughput is **61.4%** of 4B Q4, a **38.6% reduction**
- observed process RSS is **28.5% higher**
- observed peak swap is **81.4% higher**
- free-memory headroom is materially tighter: 8% vs 22%

These are runtime-descriptive comparisons, not a quality comparison. Process RSS is not treated as total Apple unified-memory footprint.

## Canonical conclusion

> Qwen3 8B Q2_K is technically runnable on the reference Apple M1 8 GB machine under llama.cpp/Metal at context 4096 and completes the frozen throughput benchmark without breaching LOOM safety guardrails.

This is the first tested 8B quantization in the sequence to clear the technical capability gate. Q4_K_M and Q3_K_M both hit the 1% free-memory guardrail during Stage A.

## What this does not prove

Q2 is an aggressive quantization. Parameter count alone does not establish useful quality. Do not call this a practical upgrade over the 4B Q4 profile until a controlled quality/usefulness comparison is completed.

## Next action

Freeze a direct same-runtime quality comparison between:
- Qwen3 4B Q4_K_M
- Qwen3 8B Q2_K

Use the same llama.cpp commit, context and prompts. Only after that result should LOOM decide whether to integrate the 8B Q2 profile into Pi or move on to alternative memory/offload/runtime strategies.