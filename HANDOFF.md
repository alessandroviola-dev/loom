# LOOM — Active Handoff

Last updated: 2026-08-21
Status: ACTIVE — architectural RAM / speed / capability frontier
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Last completed experiment: `REALGEN_002_M1_QMV_FAST_NO_GO`

Historical detailed HANDOFF/ROADMAP state through REALGEN 002 is preserved in Git history at commit `844325f63b1880107040b219524ad5391276769c` and in the individual research reports. Do not rebuild the full historical narrative into this active handoff.

## Mission

**Big models. Small machines.**

LOOM aims to run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately pushing toward approximately 27B / 32B-class models rather than solving the problem by retreating to a smaller parameter-count model.

Success requires all three:

1. memory fit/headroom;
2. useful interactive speed;
3. retained real capability.

A model that merely fits but is unusably slow is not a successful endpoint.

## Operating protocol

Canonical policy:
`research/governance/chatgpt-pi-operating-protocol.md`

### Pi owns

- serious local code implementation;
- experiment/runtime inspection required for code/test work;
- execution of tests and benchmarks;
- concise raw evidence and changed-file paths.

Pi does NOT routinely own:

- Git synchronization;
- commits/pushes;
- HANDOFF updates;
- ROADMAP updates;
- long historical recaps.

### ChatGPT owns

- scientific direction;
- experiment design;
- evidence review and GO/NO-GO decisions;
- GitHub synchronization and repository administration;
- HANDOFF and ROADMAP maintenance;
- checkpoint/provenance continuity.

Default loop:
`ChatGPT designs -> Pi codes/tests -> Pi returns evidence -> ChatGPT reviews/syncs -> next experiment`.

## Canonical current system

Model/runtime:

- Qwen3-8B full parameter count;
- affine 3-bit/group64 weights;
- BF16 KV;
- 36 layers, hidden 4096, intermediate 12288;
- Apple M1 / 8 GB;
- MLX 0.31.2 / mlx-metal 0.31.2;
- mlx-lm 0.31.3;
- transformers 5.12.1;
- ordinary built-in M1 `qmv_fast` for real autoregressive generation.

Raw persistent weights:
`3,583,928,320 B`.

## Canonical real-generation baseline

REALGEN 001 is the user-facing baseline:

- pooled real autoregressive generation: **13.184615357 tok/s**;
- pooled end-to-end output: **12.046861457 tok/s**;
- six frozen public prompts;
- all direct-driver generated token-ID sequences exactly matched the ordinary MLX-LM greedy reference;
- minimum free memory during run: 20%;
- peak swap: 1591.19 MB;
- MLX peak: 3,826,575,836 B.

Do not confuse this with M5 verifier performance.

## M5 verifier evidence

The promoted M5 oracle-verification path remains research infrastructure:

- approximately 13.990655 tok/s under its frozen verifier scope;
- S1_R8 is M5-only;
- this is not ordinary unknown-next-token generation;
- on the fully resident 8B, a five-token verifier cannot reach 20 tok/s even with zero draft cost.

Important future nuance: M>1/block verification may still become valuable for **out-of-core models** because it can potentially amortize SSD weight reads across multiple token positions. The resident-8B speculative ceiling does not close that architectural question.

## Latest result — REALGEN 002

Question: can the successful M5 S1_R8 execution geometry be transferred to a new M1-specific qmv kernel?

Result:

- canonical custom clone exact;
- M1_S1_R8 treatment exact on all 66 real payloads;
- q/k/v/o generally slower;
- representative ten-token replay exact;
- CONTROL 0.779169 s;
- TREATMENT 0.857916 s;
- equivalent throughput change **-9.178832%**.

Classification:
`REALGEN_002_M1_QMV_FAST_NO_GO`.

Decision: retain built-in MLX M1 `qmv_fast`. Do not create REALGEN 003 from this treatment.

## Known memory result

Aggressive layer streaming has already been demonstrated to reduce resident RAM substantially, but it destroys throughput because every dense transformer layer is needed for every autoregressive token.

Do not repeat pure full-model layer streaming as if it were a new solution.

The new architectural research question is:

> How much of the model must remain resident, and how much can be streamed/prefetched, to minimize RAM while preserving useful real tok/s?

## New measurement rule

Major architectural changes are evaluated on:

- **Memory**;
- **Speed**;
- **Capability**.

The old >=5% micro-optimization gate is not a universal exploratory gate anymore. Frontier-mapping experiments may be informative without individually producing >=5%, but promotion still requires meaningful system-level value.

## Capability track

Plan:
`research/capability/capability-001-agentic-baseline-plan.md`

CAPABILITY 001 will baseline the current 8B 3-bit system on real, checkable agentic tasks through Pi, including:

- repository understanding;
- safe Git synchronization reasoning;
- code modifications and tests;
- frozen-experiment discipline;
- result interpretation.

This becomes the reference against which future quantization/representation changes are judged.

## Active architectural directions

See compact `ROADMAP.md` for ordering. Primary directions are:

1. CAPABILITY 001 baseline;
2. real M1 partial-residency RAM/tok/s frontier;
3. asynchronous prefetch;
4. double/triple buffering and transfer chunk sizing;
5. direct safetensors range I/O / mmap / pread and macOS cache behavior;
6. resident-hotset selection;
7. block/multi-token execution to amortize SSD weight I/O;
8. representation/KV compression only with capability measurement;
9. scale the resulting engine toward 27B/32B-class full-parameter-count models.

## Closed / paused paths

Do not routinely reopen without new evidence:

- Stretch 037–041;
- REALGEN 002 M1 S1_R8 transfer;
- row-chunk qmatmul;
- gate/up fusion;
- outer MLP compile;
- fused residual/RMSNorm;
- persistent BF16 dequantized projection caches;
- MLX 0.32 M5 runtime comparison;
- GQA shared-KV clone;
- GC-only cleanup removal.

Historical details remain in the corresponding `research/` reports and Git history.

## Exact next step

First freeze and run **CAPABILITY 001** on the canonical Qwen3-8B 3-bit baseline before changing model representation.

Then run **MEMORY-FRONTIER 001** on the same 8B to build the real autoregressive RAM <-> tok/s curve for partial residency versus aggressive streaming.

Pi should receive code/test-only prompts. After Pi returns evidence, ChatGPT performs result review and repository synchronization.
