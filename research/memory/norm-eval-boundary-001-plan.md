# NORM-EVAL-BOUNDARY 001 — Plan

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Question

On the cleanup-consolidated S1 path, does removing/defering only the explicit `mx.eval(h2)` immediately after final norm improve real-M1 throughput while preserving exact model output?

## Why this boundary

`EMBED-EVAL-BOUNDARY 001` was a clean NO-GO: removing the post-embedding eval regressed generation by 3.346% with exact parity. That boundary remains frozen.

The final-norm eval is the next clean shared-stage candidate because the downstream LM-head explicit `mx.eval(logits)` remains in place and can serve as the next materialization boundary. Removing the LM-head eval directly is not tested yet because final cleanup/token selection depend on materialized logits and would create a less isolated lifecycle change.

## Frozen baseline

Use the successful cleanup-consolidated S1 runtime:
- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1 where inherited
- thinking disabled
- layers 0..34 persistent
- layer 35 streamed only
- embedding/final norm/LM head persistent
- persistent raw weights 3,499,501,056 B
- logical streamed traffic 84,427,264 B/token
- post-embedding shared cleanup absent
- post-norm shared cleanup absent
- layer-35 cleanup unchanged
- exactly one final post-head cleanup
- post-embedding eval retained
- all transformer-block eval topology unchanged
- LM-head eval retained

## Arms

CONTROL: exact cleanup-consolidated S1 including explicit final-norm `mx.eval(h2)`.

TREATMENT: remove/defer only final-norm `mx.eval(h2)`.

Everything else must be identical, especially:
- post-embedding eval retained;
- LM-head `mx.eval(logits)` retained;
- layer-35 loading/materialization/forward/release/cleanup unchanged;
- cleanup cadence unchanged;
- residency and source representation unchanged;
- no new sync/eval inserted.

## Preflight

Separate fresh processes on the first canonical REALGEN 001 prompt. Generate at least 16 greedy unknown tokens or EOS. CONTROL and TREATMENT must match canonical S0 exact token IDs.

A genuine parity failure is a treatment failure and must not be rescued with a replacement synchronization boundary.

## Scientific run

ABBA order:
1. CONTROL
2. TREATMENT
3. TREATMENT
4. CONTROL

Fresh process each constituent. Each runs the first three canonical REALGEN 001 prompts, unchanged, greedy, thinking disabled, max 64 generated tokens or EOS.

Host admission before each process:
- system free >=60% on two consecutive passive samples;
- swap <=5600 MB.

Abort after inference begins if free <5% or swap >5600 MB. No scientific retry.

## Measurements

Low-overhead only. No profiler and no additional synchronization.

Collect:
- exact token IDs/EOS;
- generation wall and tok/s;
- wall/token;
- E2E tok/s;
- TTFT;
- peak MLX;
- min free;
- peak swap;
- logical streamed B/token;
- process-read B/token diagnostic;
- integer invocation count for final-norm eval if useful.

## Interpretation

`NORM_EVAL_COST_MATERIAL` if generation improves >=5% with parity and acceptable resources.

`NORM_EVAL_COST_SMALL` if stable positive gain is >0 and <5%.

`NORM_EVAL_NO_GO` if no gain, regression, parity failure, or unacceptable resource cost.

Do not attribute any measured effect internally to GPU/Metal/SSD/materialization/etc. The causal factor is only the explicit final-norm eval boundary.

## Classification

`NORM_EVAL_BOUNDARY_001_COMPLETE` if 2 valid CONTROL + 2 valid TREATMENT runs and correctness is known.

`NORM_EVAL_BOUNDARY_001_PARTIAL` if at least one valid run per arm exists but another constituent fails a gate.

`NORM_EVAL_BOUNDARY_001_INFRASTRUCTURE_INCOMPLETE` only for harness/implementation failure.

## Evidence

Store under:
`results-local/memory/norm-eval-boundary-001/<run-id>/`

At minimum:
- summary.json
- implementation-audit.json
- parity.json
- host-admission.jsonl
- comparison.json
- invocation-counts.json
- runs/

## Pi role

Pi implements/runs only. No Git/HANDOFF/ROADMAP and no next-experiment proposal.
