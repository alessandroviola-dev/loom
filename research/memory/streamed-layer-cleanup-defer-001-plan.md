# LOOM — STREAMED-LAYER-CLEANUP-DEFER 001 — Frozen Plan

Status: FROZEN / RUN PENDING
Date: 2026-08-22

## Question

On the current cleanup-consolidated S1 real-M1 path, does deferring only the streamed layer-35 `gc.collect()/mx.clear_cache()` cleanup until the already-retained final post-head cleanup reduce the marginal streamed-layer lifecycle cost while preserving exact model semantics and acceptable memory pressure?

## Baseline

Use the promoted cleanup-consolidated S1, not the small norm-eval treatment:
- transformer layers 0..34 persistent;
- transformer layer 35 streamed;
- embedding/final norm/LM head persistent;
- persistent raw weights 3,499,501,056 B;
- logical streamed transformer traffic 84,427,264 B/token;
- post-embedding `mx.eval(h)` retained;
- post-embedding shared cleanup absent;
- final-norm `mx.eval(h2)` retained;
- post-norm shared cleanup absent;
- LM-head `mx.eval(logits)` retained;
- final post-head cleanup retained.

`NORM_EVAL_BOUNDARY 001` produced only +0.762% and is not promoted.

## One factor

CONTROL retains the canonical streamed layer-35 lifecycle including its cleanup.

TREATMENT keeps layer-35 load/select/reconstruction/materialization/forward/eval and object/value deletion/release semantics unchanged, but omits/defers only the layer-local `gc.collect()/mx.clear_cache()` cleanup sequence. The already-existing final post-head cleanup remains exactly once per generated token.

No other behavior may differ.

## Correctness

Separate preflight processes must establish exact token-ID parity against canonical S0 for CONTROL and TREATMENT over at least 16 greedy unknown tokens or EOS.

## Scientific workload

Use the first three canonical REALGEN 001 prompts exactly, normal Qwen chat template, thinking disabled, greedy generation, max 64 generated tokens or EOS.

Run fresh processes in ABBA order:
`CONTROL -> TREATMENT -> TREATMENT -> CONTROL`.

Two valid runs per arm.

## Host admission

Before each scientific process:
- system free >=60% for two consecutive passive samples;
- swap <=5600 MB.

Passive recovery only. No purge, unrelated process kills, swap manipulation, artificial allocation/free or deliberate OS/page-cache flush.

## Resource abort

After inference begins, hard abort if:
- system free <5%; or
- swap >5600 MB.

No rescue or scientific retry.

## Measurements

Per prompt/run:
- generated tokens and exact token IDs;
- generation wall and real tok/s;
- wall/token;
- TTFT;
- E2E output tok/s;
- peak MLX active;
- peak active+cache when naturally available;
- minimum system free;
- peak swap;
- RSS diagnostic;
- logical streamed B/token;
- process-read B/token diagnostic;
- cleanup invocation counts.

No invasive per-stage timers and no extra synchronization.

## Primary comparison

Use contemporaneous TREATMENT/CONTROL only for causal claims.

Calculate:
- generation ratio / % change;
- E2E % change;
- wall/token delta / reduction;
- TTFT change;
- peak MLX delta;
- peak active+cache delta if available;
- min-free delta;
- peak-swap delta;
- process-read diagnostic delta.

## Interpretation

`STREAMED_LAYER_CLEANUP_COST_MATERIAL` if generation improves >=5% with exact parity and acceptable memory/resource behavior.

`STREAMED_LAYER_CLEANUP_COST_SMALL` if stable positive gain >0 but <5%.

`STREAMED_LAYER_CLEANUP_NO_GO` if no gain/regression, parity failure or unacceptable resource cost.

Even if faster, the causal conclusion is only that layer-local cleanup cadence is a system-level part of streamed-layer lifecycle cost. Do not attribute the saved wall to SSD, Metal, GPU, allocator or another internal subsystem.

## Classification

`STREAMED_LAYER_CLEANUP_DEFER_001_COMPLETE` if 2 valid runs/arm and correctness is known.

`STREAMED_LAYER_CLEANUP_DEFER_001_PARTIAL` if at least one valid run/arm exists but another constituent fails a gate.

`STREAMED_LAYER_CLEANUP_DEFER_001_INFRASTRUCTURE_INCOMPLETE` only if the harness cannot produce a valid one-factor A/B.

## Evidence

Store under:
`results-local/memory/streamed-layer-cleanup-defer-001/<run-id>/`

Minimum artifacts:
- summary.json
- implementation-audit.json
- parity.json
- host-admission.jsonl
- comparison.json
- cleanup-counts.json
- runs/

## Explicit exclusions

No Git/admin by Pi. No prefetch, buffering, range-I/O redesign, mmap/pread changes, source-format changes, quantization changes, KV changes, residency changes, model changes, M>1 execution or capability rerun inside this experiment.
