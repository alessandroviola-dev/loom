# LOOM — llama.cpp 8B Q2 Capability 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED / READY**

## Research question

Can the reference Apple M1 / 8 GB machine run the same Qwen3-8B model class at context 4096 when reduced to a Q2_K GGUF, while preserving the same llama.cpp/Metal profile and safety criteria used for Q4 and Q3?

## Frozen runtime

- Machine: Apple M1, 8 GB unified memory
- llama.cpp commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- canonical Phase 4 Metal build
- context: **4096**
- requested GPU layers: `-ngl -1`
- flash attention: auto for benchmark

## Frozen model artifact

Repository:
- `unsloth/Qwen3-8B-GGUF`

File:
- `Qwen3-8B-Q2_K.gguf`

Quantization:
- `Q2_K`

Remote size:
- `3,281,733,440` bytes
- about **3.06 GiB**

Expected SHA256:
- `7226e0183d31dca14d81c6f799ada2944be62160b8b7549a70254fba4124a5cf`

The complete SHA256 must pass before inference.

## Why Q2

Observed Stage A failures at the same frozen context/offload profile:

- Q4_K_M: 4.682 GiB artifact, minimum memory free 1%, FAIL
- Q3_K_M: ~3.84 GiB artifact, minimum memory free 1%, FAIL

Q2_K is about 3.06 GiB, approximately 0.78 GiB smaller than Q3_K_M and 1.63 GiB smaller than Q4_K_M. This is a materially smaller 8B representation while keeping parameter count/model class unchanged.

Because Q2 is a stronger quantization, launchability does not imply acceptable model quality. If it passes, quality/agent usefulness must be tested separately before calling it a practical upgrade.

## Storage

Latest observed disk free after Q3: **46.763 GiB**. This is comfortably above the fresh-download guard.

Frozen fresh-download minimum for Q2: **8 GiB**.

No automatic deletion of Q4/Q3/4B artifacts.

## Stage A — context-4096 smoke

- stop canonical Ollama model if available;
- run `llama-cli` with verified Q2 model;
- `-ngl -1`;
- `-c 4096`;
- deterministic tiny prompt;
- generate 8 tokens;
- monitor process RSS, swap and `memory_pressure`.

Stage A PASS requires clean exit, no timeout, no guardrail abort, nonempty output, Metal evidence and context-4096 evidence.

## Safety guardrails

Unchanged from Q4/Q3:
- abort child if observed memory free < **5%**;
- abort child if swap > **5600 MB**;
- no automatic rescue or parameter alteration.

## Stage B — benchmark

Run only if Stage A passes.

Use the same descriptive benchmark shape as the 4B control:
- `llama-bench`
- `-ngl -1`
- flash attention auto
- pp512
- tg128
- 3 repetitions
- JSON output

Capture throughput, backend/device evidence, GPU layer field, wall time, peak RSS, peak swap and minimum free memory.

## Classification

- `FULL_PASS`: Stage A + Stage B pass with no guardrail breach.
- `LAUNCH_PASS_BENCH_FAIL`: Stage A passes, Stage B fails/aborts.
- `FAIL`: artifact verification or Stage A fails/aborts.

## Decision after Q2

If `FULL_PASS`:
- stop reducing quantization;
- measure actual model quality/usefulness and a small Pi/agent compatibility path before deciding whether Q2 8B is a practical upgrade over the current 4B profile.

If Stage A still `FAIL`:
- do not keep descending blindly through quantizations;
- pause the full-offload 8B path and compare a separately preregistered partial-offload/context-memory strategy, then return to Direct MLX/other Phase 4/5 runtime questions as appropriate.