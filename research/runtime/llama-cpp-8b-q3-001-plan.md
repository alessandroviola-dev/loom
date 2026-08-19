# LOOM — llama.cpp 8B Q3 Capability 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED / READY AFTER Q4 FAIL**

## Research question

Does reducing the same Qwen3 8B class from Q4_K_M to Q3_K_M provide enough memory headroom for a stable context-4096 llama.cpp/Metal run on the reference Apple M1 / 8 GB machine?

This experiment follows the valid 8B Q4 Capability 001 failure, where Stage A hit the frozen memory guardrail at 1% reported free memory.

## Frozen runtime

- Machine: Apple M1, 8 GB unified memory
- llama.cpp source commit: `60addddf3c567c43ec3caf70fc953fba3572d96f`
- Same canonical Release/Metal build used by the 4B control and 8B Q4 test
- Context: **4096**
- Requested GPU/Metal offload: `-ngl -1`
- Flash Attention: auto where benchmarked

## Model artifact

The official `Qwen/Qwen3-8B-GGUF` repository used for Q4 does not publish a Q3_K_M artifact in its current file set. Therefore this condition uses a separately identified community GGUF quantization from Unsloth.

Repository:
- `unsloth/Qwen3-8B-GGUF`

File:
- `Qwen3-8B-Q3_K_M.gguf`

Quantization:
- `Q3_K_M`

Remote pointer size:
- **4,124,161,856 bytes** (~3.84 GiB)

Expected SHA256:
- `4924cf38a3b3c4b27ead5ccb93e27027f9418738506ac50a24a70dfe8581a007`

The runner must verify the complete SHA256 before inference.

## Source caveat

This is not the exact same distributed GGUF artifact source as the official Q4 condition. The base model is Qwen3-8B, but the quantized artifact is community-produced by Unsloth. Interpret performance/quality comparisons as quantization/runtime capability evidence, not as a perfectly controlled quantizer-source comparison.

## Why Q3_K_M

8B Q4 Capability 001 observed:
- Q4 artifact: 4.682 GiB
- Stage A wall before abort: 21.558 s
- peak process RSS: 1940.5 MB
- peak swap: 2108.38 MB
- minimum free memory: 1%
- guardrail abort below frozen 5% threshold

Q3_K_M reduces stored model size by roughly 0.84 GiB while retaining the same 8B parameter class. It is the next planned lower-memory condition before considering Q2 or more invasive runtime changes.

## Storage

The Q4 run ended with about 50.567 GiB free. Do not delete the verified Q4 artifact merely to run Q3.

Require at least **10 GiB free** before a fresh Q3 download. Record disk free before and after the experiment.

## Stage A — context-4096 smoke

After verified download:

1. stop the canonical Ollama model if available;
2. launch `llama-cli` with the Q3_K_M GGUF;
3. request `-ngl -1`;
4. force context 4096;
5. use the same tiny deterministic prompt as Q4 and generate 8 tokens;
6. monitor RSS, swap and memory pressure.

Stage A PASS requires:
- clean exit;
- no timeout;
- no guardrail abort;
- non-empty output;
- Metal evidence;
- context-4096 evidence.

## Safety guardrails

Preserve the Q4 thresholds unchanged:
- abort if observed memory free < **5%**;
- abort if observed swap > **5600 MB**.

No same-run rescue is permitted.

## Stage B — benchmark

Run only if Stage A passes.

Use the same descriptive workload as the 4B control:
- pp512
- tg128
- 3 repetitions
- `-ngl -1`
- Flash Attention auto
- JSON output

Capture throughput, effective backend/offload evidence, wall time, peak RSS, peak swap, minimum free memory and disk state.

## Classification

### FULL_PASS
Stage A and Stage B both pass with Metal evidence and no guardrail breach.

### LAUNCH_PASS_BENCH_FAIL
Stage A passes, Stage B fails or breaches a guardrail.

### FAIL
Stage A cannot complete at frozen parameters or breaches a guardrail.

## Next decision

If FULL_PASS:
- quantify Q4 failure -> Q3 viability and 4B -> 8B throughput scaling;
- then run quality/agent usefulness checks before declaring Q3 8B a practical upgrade.

If Stage A passes but Stage B fails:
- consider a separately frozen partial-offload condition or Q2_K.

If Stage A fails:
- move to a separately preregistered Q2-class 8B condition rather than repeatedly tuning Q3.
