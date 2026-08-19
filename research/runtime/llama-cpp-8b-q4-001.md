# LOOM — llama.cpp 8B Q4 Capability 001

Date: 2026-08-19
Status: **VALID FAIL — MEMORY GUARDRAIL TRIGGERED DURING STAGE A**
Run id: `20260819-091424`

## Frozen condition

- Machine: Apple M1, 8 GB unified memory
- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Metal build: canonical Phase 4 build
- Model: official `Qwen/Qwen3-8B-GGUF`
- File: `Qwen3-8B-Q4_K_M.gguf`
- Quantization: `Q4_K_M`
- Context: 4096
- Requested GPU/Metal offload: `-ngl -1`
- Stage A generation: 8 tokens
- Guardrails: abort below 5% memory free or above 5600 MB swap
- No same-run rescue permitted

## Artifact / storage

- Disk free before: **56.285 GiB**
- Download: PASS
- SHA256: PASS
- Observed model size: **4.682 GiB**
- Disk free after: **50.567 GiB**

## Device evidence

`llama-bench --list-devices` reported:

- `MTL0: Apple M1 (5461 MiB, 5460 MiB free)`
- Accelerate BLAS
- unified memory: true
- embedded Metal library loaded
- recommended Metal max working set: **5726.63 MB**

## Stage A — context-4096 launch smoke

Result: **FAIL**

Observed before termination:

- wall: **21.558 s**
- peak process RSS: **1940.5 MB**
- peak observed swap: **2108.38 MB**
- minimum observed free memory: **1%**
- guardrail: `memory free 1% < 5%`

The runner terminated the child process according to the frozen safety protocol while the model was loading / initializing Stage A.

Stage B benchmark: **SKIPPED**.

Final classification: **FAIL**.

## Interpretation

Under the frozen profile — 8B Q4_K_M, context 4096, maximum requested Metal offload on the reference M1 8 GB machine — the runtime reached unacceptable system memory pressure before a valid Stage A completion.

This is a valid capability result, not a runner or download failure. It does **not** prove that the model can never be launched under any altered configuration; it proves that this exact Q4_K_M / context-4096 / maximum-offload profile is not acceptable under LOOM's safety criterion.

Process RSS is not interpreted as total model footprint on Apple unified memory. The decisive safety signal was the measured `memory_pressure` free percentage crossing the preregistered 5% threshold.

Do not rescue this run by silently reducing context, GPU layers, or other parameters.

## Next experiment

Per the preregistered Q4 plan, move to a separately frozen 8B lower-quantization condition. The next candidate is Qwen3 8B `Q3_K_M` while preserving context 4096 and the same staged smoke/benchmark structure and memory guardrails.
