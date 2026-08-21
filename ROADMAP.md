# LOOM Roadmap

Last reset: 2026-08-21
Active checkpoint before this roadmap reset: `REALGEN_002_M1_QMV_FAST_NO_GO`
Detailed historical roadmap through REALGEN 002 is preserved in Git history at commit `844325f63b1880107040b219524ad5391276769c`.

## Mission

LOOM exists to make **excellent, large, full-parameter-count LLMs practical on very small Apple Silicon systems**, with Apple M1 / 8 GB as the reference machine.

The long-term target is not to retreat to smaller parameter-count models. The research direction is to move from the current Qwen3-8B frontier toward roughly **27B / 32B-class models on 8 GB**, while preserving useful interactive speed and real capability.

A model merely fitting in RAM is not success. A model that is fast but no longer capable is not success either.

Every major result must therefore be judged on three axes:

1. **Memory** — resident/peak RAM, swap, model bytes, headroom.
2. **Speed** — real autoregressive tok/s, TTFT, latency.
3. **Capability** — ability to complete real useful tasks.

## Operating method — ACTIVE

Canonical protocol: `research/governance/chatgpt-pi-operating-protocol.md`.

### Pi

Pi is reserved for high-value local work:

- serious code implementation;
- local source/runtime inspection required by an experiment;
- running tests and benchmarks;
- producing concise raw result summaries and changed-file paths.

Pi does **not** routinely spend context on Git synchronization, commits/pushes, HANDOFF, ROADMAP or historical recap.

### ChatGPT

ChatGPT owns:

- research direction and experimental design;
- review and GO/NO-GO decisions;
- GitHub synchronization;
- commits/pushes when supported by connected tooling;
- HANDOFF and ROADMAP maintenance;
- checkpoint/provenance continuity.

Default loop:

`ChatGPT designs -> Pi codes/tests -> Pi returns evidence -> ChatGPT reviews + syncs repo -> next experiment`

## Canonical performance state

### Qwen3-8B 3-bit — current real-generation baseline

REALGEN 001:

- full Qwen3-8B parameter count;
- affine 3-bit/group64 weights;
- BF16 KV;
- Apple M1 8 GB;
- MLX 0.31.2 / mlx-lm 0.31.3;
- ordinary built-in M1 `qmv_fast`;
- pooled real autoregressive generation: **13.184615357 tok/s**;
- pooled end-to-end output: **12.046861457 tok/s**;
- exact reference sequence agreement on all six frozen prompts;
- raw persistent weights: **3,583,928,320 B**;
- REALGEN peak MLX memory: **3,826,575,836 B**.

This is the canonical practical baseline.

### M5 verifier evidence

The optimized M5 target-verification path remains useful research evidence but is **not** ordinary generation:

- approximately **13.990655 tok/s** verifier throughput under its frozen scope;
- current five-token verifier cannot reach 20 tok/s even with zero draft cost on the resident 8B baseline.

Do not present M5 verifier throughput as chat-generation throughput.

### REALGEN 002

M1-specific transfer of the S1_R8 geometry is closed:

- exact on all tested payloads;
- representative ten-token replay throughput **-9.178832%** vs built-in M1 `qmv_fast`;
- classification `REALGEN_002_M1_QMV_FAST_NO_GO`;
- built-in M1 `qmv_fast` remains canonical.

## What is already known

### Pure layer streaming

LOOM has already demonstrated that aggressive layer streaming can reduce resident RAM dramatically.

It also destroys throughput because a dense transformer needs every layer for every generated token.

Therefore **pure full-model layer streaming is not the destination and should not be rediscovered as if it were new**.

The new problem is to find the best point between:

- everything resident: fast but memory-hungry;
- everything streamed: memory-efficient but slow.

## Research direction A — CAPABILITY baseline — NEXT

Plan: `research/capability/capability-001-agentic-baseline-plan.md`.

### CAPABILITY 001 — current 8B 3-bit usefulness

Goal: establish how intelligent/useful the current LOOM baseline actually is on real agentic work.

Examples include:

- repository understanding;
- safe Git synchronization reasoning through Pi;
- code modification and tests;
- experiment implementation under frozen constraints;
- reading result artifacts and making correct GO/NO-GO decisions.

Metrics include task success, correction turns, human interventions, constraint violations, destructive/invalid actions and code/test correctness.

This becomes the capability reference for future quantization or representation changes.

**Rule:** future memory/speed improvements must report capability delta against this baseline when the model representation changes.

## Research direction B — RAM / speed frontier — HIGH PRIORITY

The objective is not minimum RAM. It is **minimum RAM loss per unit of useful throughput preserved**.

### MEMORY-FRONTIER 001 — partial residency curve

Using the known 8B as the laboratory, measure real autoregressive generation with controlled resident fractions/windows rather than all-or-nothing streaming.

Candidate points should span approximately:

- fully resident control;
- large resident hotset / small streamed tail;
- medium resident window;
- aggressive streaming reference.

For every point record together:

- persistent/resident bytes;
- MLX peak;
- system free memory/swap;
- SSD bytes read per generated token;
- real generation tok/s;
- TTFT;
- exactness/correctness where representation is unchanged.

Primary output: a **RAM <-> tok/s frontier**, not a single winner.

Do not repeat old M5-only residency results as if they were real-generation evidence.

## Research direction C — hide SSD cost instead of merely accepting it

Once the real frontier is measured, explore one factor at a time:

1. **Asynchronous prefetch** — read the next weight block while the current block computes.
2. **Double/triple buffering** — separate compute, ready and loading buffers.
3. **Chunk/super-layer sizing** — find the transfer size that maximizes overlap without consuming excessive RAM.
4. **Direct safetensors range reads / mmap / pread** — avoid unnecessary copies and full checkpoint materialization.
5. **macOS filesystem-cache control and measurement** — distinguish true model residency from page-cache duplication.
6. **Resident hotset selection** — keep the highest-value bytes resident and stream only the unavoidable remainder.

Every technique must report both RAM saved and tok/s preserved.

## Research direction D — amortize weight I/O across multiple tokens

This is a key unexplored direction for models larger than RAM.

For an out-of-core dense model, the expensive event may become **loading weights**, not matrix multiplication. Ordinary M1 generation reloads streamed weights for every token.

A block-verification or multi-token scheme can potentially use one weight load for several candidate positions.

The current resident-8B M5 result does not reach 20 tok/s, but that does **not** close M>1 verification as an out-of-core technique: its value may be much larger when SSD I/O dominates.

Future experiment family:

### OUTCORE-BLOCK 001

With the 8B streamed/partially resident laboratory and fixed known candidate tokens, measure the theoretical I/O amortization frontier for M=1 vs larger exact-valid blocks.

Questions:

- SSD bytes read per accepted/candidate token;
- wall time per block;
- degree of prefetch overlap;
- resident-memory requirement;
- whether larger M materially changes the RAM-speed frontier.

This is target-side feasibility only. A real drafter comes later, after the out-of-core target economics justify it.

## Research direction E — model representation without shrinking parameter count

LOOM does not use a smaller parameter-count model as the primary escape hatch.

Representation changes remain valid research tools if all model parameters remain represented, for example:

- mixed precision by layer/tensor;
- selective higher/lower bit widths;
- compressed cold weights with fast decode;
- quantized KV cache;
- other storage formats designed for out-of-core execution.

But any representation change must be judged jointly on:

`memory + real tok/s + CAPABILITY score`

A lower-bit model is not automatically an improvement.

## Research direction F — scale beyond 8B

Progressive objective:

1. Use 8B as the controlled laboratory because its full-resident baseline is well characterized.
2. Demonstrate a partial-residency/out-of-core method that preserves a useful fraction of the 13.18 tok/s baseline.
3. Apply the same engine to a model whose weights no longer fit comfortably in 8 GB.
4. First major scaling checkpoint: a **27B/32B-class full-parameter-count model produces correct tokens without OOM on M1 8 GB**.
5. Then optimize the larger model from merely-running toward interactive speed.

For the large-model checkpoint, initial throughput may be low. After correctness/fit is established, speed becomes the primary optimization objective.

## Promotion philosophy

A technique is interesting only if it moves the Pareto frontier.

Examples:

- save 40% RAM and lose 70% speed -> not a useful final point;
- save 25% RAM and lose 5% speed -> potentially valuable;
- same RAM with substantially better speed -> valuable;
- same speed with substantially more capability -> valuable;
- smaller/faster representation with severe capability loss -> not promoted.

Do not require every exploratory feasibility test to clear 5%; the old >=5% gate applied to the mature micro-optimization phase. In the new architectural phase, small experiments may be used to map a frontier or validate mechanisms, but promotions still require material system-level value.

## Closed / paused work

Do not routinely reopen without genuinely new evidence:

- Stretch 037–041;
- REALGEN 002 M1 S1_R8 geometry;
- gate/up fusion;
- row-chunk qmatmul;
- outer MLP compile;
- fused residual/RMSNorm;
- persistent BF16 dequantized projection caches;
- MLX 0.32 M5 runtime comparison;
- GQA shared-KV clone attempt;
- GC-only cleanup removal.

Detailed evidence remains in repository history and the corresponding research reports.

## Immediate order of work

1. **Freeze and run CAPABILITY 001** on the current canonical Qwen3-8B 3-bit system.
2. **MEMORY-FRONTIER 001:** measure real M1 RAM/tok/s curve for partial residency versus streaming.
3. Select the first overlap mechanism from actual frontier evidence: prefetch / buffering / chunk sizing.
4. **OUTCORE-BLOCK 001:** test whether multi-token block execution can amortize SSD traffic enough to change the frontier.
5. Only then choose the next representation or larger-model scaling experiment.

## Final objective

LOOM should become an execution system that treats **RAM + SSD + Apple unified memory + scheduling** as one managed memory hierarchy and can run an LLM whose total weights exceed physical RAM, while preserving enough speed and capability to be genuinely useful.
