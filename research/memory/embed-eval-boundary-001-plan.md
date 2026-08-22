# EMBED-EVAL-BOUNDARY 001 — Frozen plan

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Goal

Test whether the explicit stream-only `mx.eval(h)` immediately after the persistent embedding is a material part of the remaining fixed S1 stream-activation overhead.

## Frozen context

Current optimized S1 baseline after SHARED-CLEANUP-CONSOLIDATION 001:
- Qwen3-8B full parameter count, affine 3-bit/group64, BF16 KV;
- MLX/mlx-metal 0.31.2, mlx-lm 0.31.3;
- transformer layers 0..34 persistent;
- transformer layer 35 streamed;
- embedding/final norm/LM head persistent;
- persistent raw weights 3,499,501,056 B;
- logical streamed transformer traffic 84,427,264 B/token;
- post-embedding cleanup consolidated away;
- post-norm cleanup consolidated away;
- layer-35 cleanup unchanged;
- one final post-head shared cleanup retained.

Pooled current baseline from SHARED-CLEANUP-CONSOLIDATION 001 treatment:
- 7.065 real generation tok/s;
- 141.548 ms/token;
- E2E 6.206 tok/s;
- median TTFT 1.228 s;
- peak MLX 3,537,250,032 B.

STREAMING-ACTIVATION-AUDIT 001 showed that the stream path adds an explicit embedding-stage `mx.eval(h)` once per token for every S1/S2/S4 arm, whereas S0 does not use this boundary. The streamed path also explicitly evaluates each transformer block output; therefore the first block's existing eval is a natural downstream materialization boundary.

## Scientific factor

CONTROL: exact optimized S1 baseline above, including the explicit post-embedding `mx.eval(h)`.

TREATMENT: remove/defer only that one post-embedding `mx.eval(h)` call. No other `mx.eval`, cleanup, residency, loading, materialization, forward, I/O or model operation may change.

The downstream transformer block eval topology remains exactly unchanged.

## One-factor invariants

Both arms must have identical:
- model/runtime/weights/quantization/KV;
- tokenizer/chat template/thinking=false/greedy decoding;
- persistent and streamed layers;
- persistent shared stages;
- source representation and layer-35 streaming implementation;
- layer-35 `mx.load`, selection, reconstruction, parameter materialization, forward and release;
- cleanup schedule from SHARED-CLEANUP-CONSOLIDATION 001 treatment;
- norm `mx.eval`;
- LM-head `mx.eval`;
- final token eval/argmax;
- logical streamed bytes/token 84,427,264 B.

No prefetch, buffering, threading, range-I/O, mmap/pread, chunking, cache policy, quantization, M>1 or speculation changes.

## Implementation audit

Before inference prove:

CONTROL per token:
- embedding explicit eval = 1
- post-embedding cleanup = 0
- layer-35 lifecycle/cleanup = canonical
- norm explicit eval = canonical
- post-norm cleanup = 0
- head explicit eval = canonical
- final post-head cleanup = 1

TREATMENT differs only:
- embedding explicit eval = 0

Verify the first transformer block retains its existing output eval and no new explicit synchronization is introduced.

If any unintended difference exists, classify `EMBED_EVAL_BOUNDARY_001_INFRASTRUCTURE_INCOMPLETE` and stop.

## Parity preflight

Fresh non-scientific processes. Use exact first canonical REALGEN 001 prompt, at least 16 greedy unknown tokens or EOS. CONTROL and TREATMENT must both match canonical S0 token IDs exactly.

If removing the boundary genuinely changes token IDs, record parity failure; do not rescue by adding a different synchronization boundary.

## Scientific workload

First three canonical REALGEN 001 prompts, unchanged, normal Qwen chat template, thinking disabled, greedy generation, max 64 generated tokens/EOS.

Balanced order: CONTROL -> TREATMENT -> TREATMENT -> CONTROL. Fresh process each constituent. No scientific retries.

## Host admission and resource gate

Before each process: system free >=60% on two consecutive passive samples; swap <=5600 MB. No purge, unrelated process kills, swap manipulation, artificial allocation/free or deliberate page-cache flush.

Abort after model start if free <5% or swap >5600 MB. Preserve failure.

## Measurements

Low-overhead only; no per-stage profiler/timers and no extra `mx.eval`/`mx.synchronize`.

Per prompt/run record:
- exact token IDs/EOS;
- tokens, generation wall, real generation tok/s, wall/token, TTFT, E2E tok/s;
- MLX active/cache after load where naturally available;
- peak MLX active/active+cache where available;
- min system free, peak swap, RSS diagnostic;
- logical streamed B/token;
- Darwin process-read B/token diagnostic;
- integer invocation counters for the explicit embedding eval and cleanup sites if needed.

## Primary comparison

Use contemporaneous TREATMENT / CONTROL. Report generation ratio/change, E2E change, wall/token delta/reduction, TTFT change, peak MLX delta, min-free delta, swap delta.

Contextually compare removed wall with the residual descriptive fixed activation term after cleanup consolidation (~25.606 ms/token = 61.284 - 35.678). This is descriptive only and must not be treated as a causal budget.

## Interpretation

`EMBED_EVAL_COST_MATERIAL` if generation improves >=5% with exact parity and acceptable resources.

`EMBED_EVAL_COST_SMALL` if stable positive gain >0 but <5%.

`EMBED_EVAL_NO_GO` if no gain/regression, parity failure or unacceptable resource cost.

Even if faster, the isolated causal factor is only the explicit embedding eval boundary. Do not attribute the improvement internally to GPU/Metal/allocator/SSD/materialization or overlap without further evidence.

## Classification

`EMBED_EVAL_BOUNDARY_001_COMPLETE` if 2 valid CONTROL + 2 valid TREATMENT and correctness known.

`EMBED_EVAL_BOUNDARY_001_PARTIAL` if at least one valid run/arm exists but another constituent fails resource/correctness.

`EMBED_EVAL_BOUNDARY_001_INFRASTRUCTURE_INCOMPLETE` only for harness/implementation failure.

## Evidence

Store under `results-local/memory/embed-eval-boundary-001/<run-id>/` with at minimum:
- summary.json
- implementation-audit.json
- parity.json
- host-admission.jsonl
- comparison.json
- invocation-counts.json
- runs/

## Pi role

Pi implements/runs only. No Git/HANDOFF/ROADMAP and no next-experiment proposal.
