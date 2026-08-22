# LOOM — STREAMED-LAYER-GRADIENT 002 — Frozen Plan

Status: `FROZEN / RUN PENDING`
Date: 2026-08-22

## Question

Remeasure the REAL-M1 S0/S1/S2/S4 transformer streaming gradient after promoting deferred post-forward streamed-layer cleanup.

Primary questions:
1. Does the marginal wall/token slope materially improve versus the previous lifecycle?
2. Does deferred cleanup remain resource-safe as 1, 2, and 4 streamed layers accumulate within one token pass?
3. Is the new per-layer cost approximately additive, fixed/nonlinear, or resource-limited?

## Frozen model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1 where inherited
- `enable_thinking=false`
- greedy REAL M1 unknown-token generation
- no drafter/speculation/oracle/cloud/Ollama
- canonical weights: `results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

## Shared-stage policy — all arms

Embedding, final norm, LM head are persistent.

Use promoted fixed-activation lifecycle:
- post-embedding `mx.eval(h)` retained;
- post-embedding shared cleanup absent;
- final-norm `mx.eval(h2)` retained;
- post-norm shared cleanup absent;
- LM-head `mx.eval(logits)` retained;
- exactly one final post-head cleanup retained.

Do not inherit the failed embed-eval treatment or the non-promoted norm-eval treatment.

## Streamed-layer policy — all streamed arms

For every streamed transformer layer:
- source/load unchanged;
- selection unchanged;
- select-time deletion/GC unchanged;
- anatomy validation unchanged;
- transient block construction/quantized parameter rebinding unchanged;
- parameter materialization unchanged;
- block forward unchanged;
- block-output eval unchanged;
- transient module/value deletion/release unchanged;
- **post-forward layer-local `gc.collect()/mx.clear_cache()` omitted/deferred**.

Do not retain/carry streamed layer modules or weights into later tokens.

One existing final post-head cleanup occurs after the complete token path.

## Arms

S0:
- 0 streamed transformer layers;
- all layers 0..35 persistent;
- persistent raw `3,583,928,320 B`;
- logical streamed transformer bytes/token `0`.

S1:
- layers 0..34 persistent;
- layer 35 streamed;
- persistent raw `3,499,501,056 B`;
- logical streamed bytes/token `84,427,264 B`.

S2:
- layers 0..33 persistent;
- layers 34..35 streamed;
- persistent raw `3,415,073,792 B`;
- logical streamed bytes/token `168,854,528 B`.

S4:
- layers 0..31 persistent;
- layers 32..35 streamed;
- persistent raw `3,246,219,264 B`;
- logical streamed bytes/token `337,709,056 B`.

## Implementation audit

Before science prove for every arm:
- exact persistent/streamed layer sets;
- all shared stages persistent;
- promoted shared cleanup schedule;
- streamed layer deletion/release occurs after every streamed layer;
- streamed layer post-forward GC/cache cleanup count is zero;
- select-time cleanup remains canonical and scales with streamed layer count;
- final post-head cleanup exactly once/token;
- no streamed module/weight survives into next token;
- logical byte accounting matches expected values.

If not possible: `STREAMED_LAYER_GRADIENT_002_INFRASTRUCTURE_INCOMPLETE` and stop.

## Parity preflight

Separate non-scientific fresh processes.

Use exact first canonical REALGEN 001 prompt and generate >=16 greedy unknown tokens or EOS.

Require exact token IDs:
- S1 == S0
- S2 == S0
- S4 == S0

No rescue by adding cleanup/synchronization.

## Workload

Use exact first three canonical REALGEN 001 prompts, in canonical order, unchanged.

Each prompt:
- normal Qwen chat template
- thinking disabled
- greedy
- max 64 generated tokens or EOS

## Scientific order

Exactly:
`S0 -> S4 -> S2 -> S1 -> S1 -> S2 -> S4 -> S0`

Two fresh constituent processes per arm; each process runs all three prompts.

## Host admission

Before every constituent:
- system free >=60% for two consecutive passive samples;
- swap <=5600 MB.

Passive recovery only. No purge, unrelated process kills, swap manipulation, artificial allocations/frees, deliberate page-cache flush.

Failed pre-load admission does not consume a run.

## Resource abort

After inference starts, abort if:
- system free <5%; or
- swap >5600 MB.

No rescue/retry.

## Measurements

Per prompt:
- exact token IDs/EOS
- generated tokens
- generation wall
- REAL generation tok/s
- wall/token
- TTFT
- E2E tok/s

Per run:
- configured persistent/streamed layers
- persistent raw bytes/fraction
- logical streamed B/token
- MLX active/cache after load where naturally available
- peak MLX active
- peak active+cache where valid without added synchronization
- minimum system free
- peak swap
- RSS diagnostic
- process-read B/token diagnostic
- select-time cleanup count
- layer post-forward cleanup count
- final cleanup count

No invasive profiler and no extra `mx.eval`/`mx.synchronize`.

## Pooled gradient

For S0/S1/S2/S4 compute:
- valid runs/2
- total tokens/wall
- pooled real gen tok/s
- pooled wall/token from total wall / total tokens
- pooled E2E
- median TTFT
- peak MLX active
- peak active+cache
- minimum free
- peak swap
- persistent raw B
- logical streamed B/token
- process-read diagnostic
- exact parity status

## Marginals

Compute:
- S1-S0 delta wall/token; marginal ms/layer
- S2-S1 delta wall/token; marginal ms/layer
- S4-S2 delta wall/token divided by 2

Also compute mean/range/CV if meaningful and descriptive linear fit for wall/token vs streamed layer count.

Classify exactly one:
- `DEFERRED_STREAM_LAYER_COST_APPROX_ADDITIVE`
- `DEFERRED_STREAM_LAYER_COST_FIXED_OR_NONLINEAR`
- `DEFERRED_STREAM_LAYER_COST_RESOURCE_LIMITED`
- `DEFERRED_STREAM_LAYER_COST_UNRESOLVED`

`RESOURCE_LIMITED` if deferred cleanup causes materially worsening active+cache/free/swap behavior or resource aborts as streamed-layer count rises such that speed-only interpretation is unsafe.

## Context against Gradient 001

Historical Gradient 001 used older cleanup lifecycle:
- S0 71.315 ms/token
- S1 171.824
- S2 210.287
- S4 288.737
- post-activation marginal ~38–39 ms/layer.

Compare Gradient 002 descriptively only:
- wall/token difference by arm
- throughput difference by arm
- marginal-slope difference
- memory-envelope difference

Do not call cross-experiment deltas causal.

## Completion

`STREAMED_LAYER_GRADIENT_002_COMPLETE` if all four arms have 2 valid runs and correctness known.

`STREAMED_LAYER_GRADIENT_002_PARTIAL` if S0 plus at least two streamed arms are scientifically valid.

`STREAMED_LAYER_GRADIENT_002_INFRASTRUCTURE_INCOMPLETE` only for harness/implementation failure.

## Evidence

Store under:
`results-local/memory/streamed-layer-gradient-002/<run-id>/`

At minimum:
- `summary.json`
- `implementation-audit.json`
- `parity.json`
- `host-admission.jsonl`
- `gradient.json`
- `runs/`

Do not implement prefetch, buffering, range-I/O redesign, new representation, or OUTCORE-BLOCK inside this experiment.
