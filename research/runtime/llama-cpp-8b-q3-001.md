# LOOM — llama.cpp 8B Q3 Capability 001

Date: 2026-08-19
Status: **VALID FAIL — FROZEN MEMORY GUARDRAIL HIT**
Run id: `20260819-093842`

## Frozen condition

- Machine: Apple M1, 8 GB unified memory
- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Metal build: canonical Phase 4 build
- Model: `unsloth/Qwen3-8B-GGUF`
- File: `Qwen3-8B-Q3_K_M.gguf`
- Quantization: `Q3_K_M`
- Context: `4096`
- Requested GPU layers: `-ngl -1`
- Memory-free abort threshold: `<5%`
- Swap abort threshold: `>5600 MB`
- No same-run rescue

## Result

Stage A — context-4096 smoke:

- result: **FAIL**
- wall time: **18.919 s**
- peak process RSS: **1670.484375 MB**
- peak observed swap: **2269.38 MB**
- minimum observed memory free: **1%**
- guardrail: `memory free 1% < 5%`
- Stage B: **SKIPPED**
- classification: **FAIL**

Disk free after run: **46.763 GiB**.

Run directory:
`results-local/llama-cpp/8b-q3/20260819-093842`

## Comparison with 8B Q4

Q4 Stage A previously failed at the same 1% minimum-memory signal:
- Q4 wall: 21.558 s
- Q4 peak process RSS: 1940.5 MB
- Q4 peak swap: 2108.38 MB

Q3 reduced the observed process RSS by about 270 MB and reached the guardrail somewhat sooner, but it did **not** recover enough system memory headroom to pass the frozen safety criterion.

Do not treat RSS as total unified-memory footprint. The decisive experiment criterion is the preregistered macOS `memory_pressure` guardrail.

## Interpretation

The exact Qwen3-8B Q3_K_M / context-4096 / maximum-requested-Metal-offload profile is not acceptable under LOOM's frozen safety criterion on the reference M1 8 GB machine.

Together with the Q4 failure, this is stronger evidence that an 8B model at context 4096 needs a materially smaller representation and/or a separately controlled runtime/offload change on this machine.

This does **not** prove all 8B configurations impossible.

## Next action

Proceed to a separately preregistered Qwen3-8B `Q2_K` condition while preserving context 4096, `-ngl -1`, the same smoke/benchmark staging and the same safety thresholds. No retroactive changes to Q3.