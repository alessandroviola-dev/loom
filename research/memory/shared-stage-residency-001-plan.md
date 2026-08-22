# SHARED-STAGE-RESIDENCY 001 — F1 shared-stage persistence plan

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Goal

Test one architectural factor suggested by MEMORY-FRONTIER 001 and STREAMING-ATTRIBUTION 001:

> On the F1/H32 partial-residency path, what happens if embedding, final norm and LM head are kept persistent while only transformer layers 32..35 remain streamed?

This is a direct system A/B experiment, not another profiler run.

## Rationale

Canonical F1/H32 currently keeps transformer layers 0..31 persistent but streams:

- transformer layers 32..35: 4 × 84,427,264 B = 337,709,056 B/pass
- embedding: 272,269,312 B/pass
- final norm: 8,192 B/pass
- LM head: 272,269,312 B/pass

Token-path logical streaming total: 882,255,872 B/token.

Embedding + final norm + LM head account for 544,546,816 B/token, about 61.7% of F1 logical streamed traffic.

STREAMING-ATTRIBUTION 001 could not establish a definitive bottleneck because tracing reduced throughput substantially, but embedding and LM head were the two largest traced stage hotspots and materialization/sync was the largest observed interval. This justifies a one-factor direct A/B without claiming a primary bottleneck in advance.

## Frozen model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1 where inherited
- greedy real M1 unknown-token generation
- normal Qwen chat template
- `enable_thinking=false`
- no speculation/drafter/oracle
- no cloud/Ollama

Canonical weights:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

## CONTROL — F1/H32 canonical

Exact MEMORY-FRONTIER 001 F1 behavior:

- persistent transformer layers: 0..31
- streamed transformer layers: 32..35
- embedding streamed
- final norm streamed
- LM head streamed
- logical persistent raw-weight bytes: 2,701,672,448 B
- logical streamed bytes/token path: 882,255,872 B

No implementation changes other than measurement hooks that are equally present in both arms.

## TREATMENT — H32 + persistent shared stages

Keep exactly the same transformer residency:

- persistent transformer layers: 0..31
- streamed transformer layers: 32..35

Change only shared-stage persistence:

- embedding persistent
- final norm persistent
- LM head persistent

Expected logical persistent raw-weight bytes:
3,246,219,264 B

Expected logical streamed bytes/token path:
337,709,056 B

This treatment adds 544,546,816 B of persistent raw weights versus CONTROL and still leaves 337,709,056 B (~9.42% of total raw weights) non-persistent versus F0/FULL.

Do not change transformer math, quantization, KV, prompt, tokenizer, generation algorithm, cleanup, source format or stream-layer implementation.

## Mandatory implementation audit

Before science, verify from actual local code:

- CONTROL exactly reproduces F1/H32 behavior;
- TREATMENT differs only in embedding/final-norm/LM-head persistence;
- shared-stage objects in TREATMENT are loaded/materialized once before prompt generation and reused across generated tokens;
- streamed transformer layers 32..35 follow the identical path in both arms;
- no hidden extra caching of streamed transformer layers occurs.

Store `implementation-audit.json`.

## Exact-parity preflight

Use a separate non-scientific process.

For the first canonical REALGEN 001 prompt, generate at least 16 greedy unknown tokens or EOS.

Require exact token-ID equality among:

- F0 canonical reference
- CONTROL F1
- TREATMENT

Any genuine divergence invalidates TREATMENT.

Terminate preflight processes before science.

## Workload

Use exactly the first three canonical REALGEN 001 prompts, unchanged.

For each prompt:

- normal chat template
- thinking disabled
- greedy generation
- max 64 generated tokens or EOS

## Balanced scientific order

Use four fresh constituent processes in ABBA order:

1. CONTROL
2. TREATMENT
3. TREATMENT
4. CONTROL

Every constituent run executes all three prompts.

No scientific retries.

## Host admission

Before every constituent process:

- system free >=60% on two consecutive passive samples
- swap <=5600 MB

Wait passively for natural recovery.

Forbidden:

- `purge`
- unrelated process kills
- swap manipulation
- artificial allocation/free
- deliberate page-cache flush

## Resource abort

After execution starts, abort the constituent run if:

- system free <5%; or
- swap >5600 MB

No rescue/retry.

## Measurements

Per constituent and prompt where feasible:

### Correctness
- generated token IDs
- EOS position
- exact parity

### Residency / memory
- logical persistent raw-weight bytes
- logical streamed bytes/model pass
- MLX active after load
- MLX allocator cache after load
- peak MLX active
- peak active+cache
- minimum system free %
- peak swap MB
- process RSS diagnostic

### Performance
- generated tokens
- generation wall
- real generation tok/s
- TTFT
- E2E output tok/s

### I/O
- logical streamed bytes/generated token
- process-read bytes/generated token diagnostic

Do not call process-read bytes physical SSD traffic.

## Primary comparison

Pool the two valid runs per arm and report TREATMENT vs CONTROL:

- generation tok/s ratio and percent change
- E2E tok/s ratio and percent change
- TTFT delta
- peak MLX delta
- minimum-free delta
- persistent raw-weight delta
- logical streamed B/token delta
- process-read diagnostic delta

Also compare TREATMENT descriptively with fresh F0 from MEMORY-FRONTIER 001:

- throughput retained vs F0
- peak MLX saved vs F0
- persistent raw-weight bytes saved vs F0

Historical F0 is contextual only; causal claims come from contemporaneous CONTROL/TREATMENT.

## Interpretation

This experiment does not assume that physical I/O, materialization or shared-stage compute is the bottleneck.

A large treatment speedup would show that repeated shared-stage streaming is a major addressable system cost, regardless of the exact internal subcomponent.

A small/no speedup would reject shared-stage persistence as the main route and force attention back to the four streamed transformer layers / scheduling path.

## Classification

Use `SHARED_STAGE_RESIDENCY_001_COMPLETE` when both arms have two valid/scorable constituent runs and exact parity is preserved.

Use `SHARED_STAGE_RESIDENCY_001_PARTIAL` when at least one valid run exists per arm but another constituent fails a resource/correctness gate.

Use `SHARED_STAGE_RESIDENCY_001_INFRASTRUCTURE_INCOMPLETE` only for harness/implementation failure preventing a scientifically interpretable comparison.

No automatic promotion threshold is frozen; ChatGPT reviews the measured RAM/speed trade-off.

## Evidence

Store raw evidence under:
`results-local/memory/shared-stage-residency-001/<run-id>/`

At minimum:

- `summary.json`
- `implementation-audit.json`
- `parity.json`
- `host-admission.jsonl`
- `comparison.json`
- `runs/`

## Pi role

Pi implements/adapts the local runner and runs measurements only.

Pi must not:

- update Git/HANDOFF/ROADMAP
- rerun CAPABILITY 001
- start prefetch/buffering/range-I/O work
- start OUTCORE-BLOCK 001
- propose the next experiment
