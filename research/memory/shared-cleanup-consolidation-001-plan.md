# SHARED-CLEANUP-CONSOLIDATION 001 — plan

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Goal

Test whether the fixed once-per-token shared-stage cleanup cadence materially contributes to the S1 streamed-layer activation penalty.

## Proven context

STREAMED-LAYER-GRADIENT 001 measured, with all shared stages persistent:

- S0: 71.315 ms/token;
- S1: 171.824 ms/token;
- S2: 210.287 ms/token;
- S4: 288.737 ms/token.

The first streamed layer adds ~100.508 ms/token, while later layers add ~38–39 ms/layer. A descriptive piecewise fit is consistent with a fixed stream-activation term plus a per-streamed-layer term.

STREAMING-ACTIVATION-AUDIT 001 found three once-per-token stream-only shared-stage cleanup sequences in S1/S2/S4:

- post-embedding cleanup;
- post-norm cleanup;
- final post-head cleanup.

Historical Stretch 026 found that consolidating analogous shared-stage cleanup points produced a controlled +14.11% improvement on a different frozen execution geometry. This is plausibility context only.

## Frozen model/runtime

- Qwen3-8B full parameter count;
- affine 3-bit/group64;
- BF16 KV;
- MLX/mlx-metal 0.31.2;
- mlx-lm 0.31.3;
- transformers 5.12.1 where inherited;
- thinking disabled;
- real greedy unknown-token M1 generation;
- no cloud/Ollama/speculation/drafter/oracle.

## Frozen residency

Use S1 exactly:

- transformer layers 0..34 persistent;
- transformer layer 35 streamed through the proven path;
- embedding persistent;
- final norm persistent;
- LM head persistent.

Expected persistent raw weights: 3,499,501,056 B.
Expected logical streamed bytes/token: 84,427,264 B.

## CONTROL

Exact current S1 execution path from STREAMED-LAYER-GRADIENT 001, including:

- embedding stage-local eval + post-embedding cleanup;
- layer-35 streamed lifecycle and its per-layer cleanup;
- norm stage-local eval + post-norm cleanup;
- LM-head stage-local eval + final post-head cleanup.

## TREATMENT

Change one factor only: shared-stage cleanup cadence.

- retain embedding stage-local `mx.eval`;
- omit/defer only post-embedding `gc.collect()/mx.clear_cache()` cleanup;
- retain exact layer-35 streamed lifecycle and its cleanup;
- retain norm stage-local `mx.eval`;
- omit/defer only post-norm shared cleanup;
- retain LM-head stage-local `mx.eval`;
- retain exactly one final post-head shared cleanup.

Do not remove the streamed-layer cleanup. Do not remove or move any explicit `mx.eval`. Do not change deletion/release semantics beyond the two selected shared cleanup calls. No weights may become more or less resident.

## Correctness preflight

Separate non-scientific processes, first canonical REALGEN 001 prompt, at least 16 greedy unknown tokens or EOS. CONTROL and TREATMENT must exactly match canonical S0/S1 token IDs.

## Scientific workload

First three canonical REALGEN 001 prompts, normal chat template, thinking disabled, greedy generation, max 64 tokens/EOS.

Use four fresh processes in balanced ABBA order:

`CONTROL -> TREATMENT -> TREATMENT -> CONTROL`

Two valid runs per arm; no scientific retry.

## Host admission

Before every constituent run require two consecutive passive samples with system free >=60% and swap <=5600 MB. No purge, unrelated process kills, swap manipulation, artificial allocations or deliberate page-cache flush.

After inference starts, resource abort if free <5% or swap >5600 MB.

## Measurements

Per run/prompt where feasible:

- generated tokens and exact IDs;
- generation wall and real tok/s;
- E2E tok/s;
- TTFT;
- MLX active after load;
- peak MLX active and active+cache where naturally available;
- minimum system free;
- peak swap;
- logical streamed B/token;
- process-read B/token diagnostic;
- cleanup invocation counts for post-embedding, per-layer, post-norm and final post-head sites.

Counters must be low overhead and identical between arms except for the intended skipped cleanup calls. Do not add timers or synchronization around cleanup sites.

## Primary causal comparison

Use contemporaneous TREATMENT/CONTROL pooled ratio.

Report:

- generation throughput ratio/change;
- E2E ratio/change;
- TTFT change;
- wall/token delta;
- peak MLX delta;
- min-free delta;
- peak-swap delta;
- exact parity;
- cleanup-count difference.

Historical S0/S1 values are contextual only, not causal denominators.

## Interpretation

`SHARED_CLEANUP_COST_MATERIAL` if treatment gives a reproducible >=5% generation improvement while preserving parity/resource gates.

`SHARED_CLEANUP_COST_SMALL` if valid treatment improves <5% but >0 within stable paired evidence.

`SHARED_CLEANUP_NO_GO` if no improvement/regression or unacceptable memory/resource effect.

No claim about SSD/materialization/Metal internals follows from this test.

## Classification

`SHARED_CLEANUP_CONSOLIDATION_001_COMPLETE` if two valid runs/arm and correctness status known.

`SHARED_CLEANUP_CONSOLIDATION_001_PARTIAL` if at least one valid run/arm exists but another constituent fails resource/correctness gates.

`SHARED_CLEANUP_CONSOLIDATION_001_INFRASTRUCTURE_INCOMPLETE` only for harness/implementation failure.

## Evidence

Store under:
`results-local/memory/shared-cleanup-consolidation-001/<run-id>/`

At minimum:
- summary.json
- implementation-audit.json
- parity.json
- host-admission.jsonl
- comparison.json
- cleanup-counts.json
- runs/

## Pi role

Pi implements/runs only. No Git, HANDOFF, ROADMAP, next-experiment execution or unrelated optimization.
