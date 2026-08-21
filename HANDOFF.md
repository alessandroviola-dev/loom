# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — capability bridge blocked by agentic prefill memory
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Last completed experiment: `CAPABILITY_000A_MEMORY_ATTRIBUTION_COMPLETE`
Next experiment: `CAPABILITY_000B_PI_PREFILL_ENVELOPE`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual `research/` reports. Do not rebuild the full historical narrative here.

## Mission

**Big models. Small machines.**

LOOM aims to run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately pushing toward approximately 27B / 32B-class models rather than retreating to smaller parameter-count models.

Success requires all three:

1. memory fit/headroom;
2. useful interactive speed;
3. retained real capability.

A model that merely fits but is unusably slow is not success.

## Operating protocol

Canonical policy: `research/governance/chatgpt-pi-operating-protocol.md`.

Pi owns serious local implementation, runtime/source inspection needed for experiments, test execution and concise raw evidence.

ChatGPT owns scientific direction, experiment design/review, GitHub synchronization, HANDOFF, ROADMAP and checkpoint continuity.

Default loop:
`ChatGPT designs -> Pi codes/tests -> Pi returns evidence -> ChatGPT reviews/syncs -> next experiment`.

## Canonical current model/runtime

- Qwen3-8B full parameter count;
- affine 3-bit/group64 weights;
- BF16 KV;
- 36 layers, hidden 4096, intermediate 12288;
- Apple M1 / 8 GB;
- MLX 0.31.2 / mlx-metal 0.31.2;
- mlx-lm 0.31.3;
- transformers 5.12.1;
- ordinary built-in M1 `qmv_fast` for real autoregressive generation;
- raw persistent weights `3,583,928,320 B`.

## Canonical performance baseline

REALGEN 001:

- pooled real autoregressive generation: **13.184615357 tok/s**;
- pooled end-to-end output: **12.046861457 tok/s**;
- six frozen public prompts;
- exact generated-token agreement with ordinary MLX-LM greedy reference;
- minimum free memory: 20%;
- peak swap: 1591.19 MB;
- MLX peak: 3,826,575,836 B.

The M5 verifier remains separate oracle-verification evidence at ~13.990655 tok/s. It is not ordinary chat generation.

REALGEN 002 tested transfer of S1_R8 to real M1 generation. The treatment stayed exact but reduced representative throughput by **9.178832%**, so built-in M1 `qmv_fast` remains canonical.

## Known memory-hierarchy result

Aggressive layer streaming already reduces resident RAM substantially but destroys throughput because every dense layer is needed for every autoregressive token.

Do not repeat pure full-model streaming as the final solution. Future work must search the RAM/speed frontier using partial residency, prefetch and I/O amortization.

## Capability track

CAPABILITY 001 is intended to baseline practical intelligence/usefulness of the current 8B 3-bit system on real agentic tasks through Pi. Its frozen suite includes coding, safe Git operations and experiment/result reasoning.

Before CAPABILITY 001 can run, the canonical model must be usable behind Pi without crossing the hard resource floor.

### CAPABILITY 000 — bridge result

The localhost MLX bridge successfully connected Pi to the canonical local Qwen3-8B 3-bit model. Qwen produced a real Pi tool call `read(numbers.txt)`, proving the reasoning model was participating in the agent loop.

The smoke then aborted at 4% free memory before completion.

### CAPABILITY 000A — memory attribution — COMPLETE

Report: `research/capability/capability-000a-memory-attribution-result.md`.

Key result:

- exactly **1** model instance;
- no model duplication;
- Pi RSS only **45.55 MB** at S5;
- largest static jump is model materialization S1 -> S2: free memory **67% -> 30%**, swap **+828.18 MB**;
- direct simple request works: 18 tokens, 20% free;
- direct tool-schema request works: 366 tokens, 17% free;
- starting Pi alone leaves 18% free;
- first real Pi prefill crosses the <5% hard floor before S6 completes.

BF16 KV arithmetic:

- 147,456 bytes/token;
- 288 MiB @2048;
- 432 MiB @3072;
- 576 MiB @4096.

Interpretation: the failure is not Pi process RSS and not duplicate model weights. The unresolved dynamic cost is the first real Pi prefill. Do not blame KV alone without measuring the exact Pi request and temporary prefill allocations.

## Exact next step

Run `CAPABILITY 000B — Pi prefill envelope` using the frozen plan:
`research/capability/capability-000b-pi-prefill-envelope-plan.md`.

Keep unchanged during 000B:

- Qwen3-8B 3-bit;
- BF16 KV;
- context 4096;
- max output 2048;
- Pi read/write/edit/bash surface;
- current runtime.

000B must:

1. capture the exact first Pi request without executing the model;
2. tokenize the exact request with the canonical chat template;
3. direct-replay that exact payload without Pi;
4. measure high-water prefill allocations;
5. inspect whether KV or other temporaries are allocated to actual length or capacity;
6. identify the first justified memory-reduction factor.

CAPABILITY 001 remains blocked until this is understood or resolved.

## Later architectural directions

After the capability bridge is sustainable:

1. run CAPABILITY 001 baseline;
2. map real M1 partial-residency RAM/tok/s frontier;
3. asynchronous prefetch;
4. double/triple buffering and transfer chunk sizing;
5. direct safetensors range I/O and macOS cache behavior;
6. resident-hotset selection;
7. M>1/block execution to amortize SSD I/O;
8. representation/KV compression only with capability measurement;
9. scale toward 27B/32B-class full-parameter-count models.

## Closed / paused paths

Do not routinely reopen without new evidence:

- Stretch 037–041;
- REALGEN 002 M1 S1_R8 transfer;
- row-chunk qmatmul;
- gate/up fusion;
- outer MLP compile;
- fused residual/RMSNorm;
- persistent BF16 dequantized projection caches;
- MLX 0.32 M5 comparison;
- GQA shared-KV clone;
- GC-only cleanup removal.
