# CAPABILITY 000L — Full-sequence request-boundary reclamation plan

Date frozen: 2026-08-21
Status: FROZEN / NEXT

## Purpose

Validate the combined CAPABILITY 000I + 000K boundary policy across the full captured R1->R6 request trajectory before modifying the real Pi bridge.

The combined treatment is:

1. after each HTTP response is fully complete, detach only the stale completed `GenerationBatch.Response.prompt_cache` proven in CAPABILITY 000I;
2. immediately call `mlx.core.clear_cache()` exactly once.

No other cleanup or model/runtime change is allowed.

## Scientific basis

CAPABILITY 000H proved all captured R1-R6 requests pass fresh, while sequential R2 fails because R1 leaves request-boundary state.

CAPABILITY 000I identified stale finished-response KV ownership and recovered 252 MiB active memory via targeted `prompt_cache` detach.

CAPABILITY 000K then showed that the released storage remained in MLX allocator cache. One `mx.clear_cache()` after the targeted detach reclaimed ~486 MiB allocator cache and improved R2 minimum system free memory from 5% to 11%, with exact response/tool equivalence and ~3.9 ms measured cache-clear latency.

## Frozen subject

- canonical Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- context 4096
- `prefill_step_size=512`
- thinking disabled
- exact captured R1-R6 bodies from CAPABILITY 000H
- same localhost model-server semantics and four tool definitions

Expected canonical input token counts:
- R1 1518
- R2 1573
- R3 1634
- R4 1682
- R5 1765
- R6 1820

If exact bodies/counts cannot be recovered, classify infrastructure incomplete.

## Host admission

Before each independent process:
- system free >=60% for two consecutive passive samples
- swap <=5600 MB

No purge, unrelated process kills, artificial allocations, swap manipulation or other host normalization.

## Experiment A — control

Fresh process, zero inference preflight.

Execute exact R1->R6 sequentially with natural server behavior and no boundary treatment.

Stop on hard resource abort.

This serves as a same-session control and may reproduce the known R2 boundary failure.

## Experiment B — combined boundary treatment

New fresh process with independent host admission.

Execute exact R1->R6 sequentially.

After every successfully completed response Ri:

1. prove the stale finished `GenerationBatch.Response` belongs to completed Ri and is no longer needed by an unfinished generation batch;
2. detach only `stale_response.prompt_cache`;
3. call `mx.clear_cache()` exactly once;
4. record boundary latency and memory state;
5. proceed to Ri+1.

No `gc.collect()`.

## Required boundary telemetry

For each reached request record:

- input tokens
- response/tool identity
- pre-request MLX active/cache
- request MLX peak
- minimum system free %
- peak swap
- post-response active/cache before detach
- active/cache after targeted detach
- active/cache after `mx.clear_cache()`
- system free before/after clear
- detached KV count and metadata-only bytes
- cache-clear wall ms
- total request wall time

Actual M segments/prefill/generation timing may be recorded if the harness can do so correctly and non-invasively, but **they are optional and must not gate the memory experiment**. The ~0.01 s prefill numbers from 000K are not accepted as canonical prefill timing.

## Resource policy

Hard abort after model execution begins if:
- free memory <5%
- or swap >5600 MB

No rescue.

## Semantic equivalence

For every treatment response compare against:
- control when the control reached that request;
- otherwise the canonical fresh response/evidence from CAPABILITY 000H where available.

Compare response text/bytes where deterministic, finish reason, tool-call name, tool arguments and response structure.

No semantic regression is allowed.

## Primary questions

1. Does combined detach + allocator-cache clear allow all R1-R6 to complete?
2. Does system-free memory remain safely above the 5% floor across turns?
3. Does post-boundary active + cache remain bounded rather than accumulating?
4. Does allocator-cache clear remain low-cost across all completed turns?
5. Does any semantic/tool behavior change?

## Classification

`CAPABILITY_000L_FULL_SEQUENCE_BOUNDARY_RECLAMATION_PASS`
- all R1-R6 complete under treatment
- no hard resource abort
- semantic/tool equivalence passes
- correct ownership confirmed at every detach
- no forbidden cleanup

`CAPABILITY_000L_BOUNDARY_RECLAMATION_PARTIAL_GO`
- treatment completes strictly farther than control but later hits a resource floor
- no semantic/lifecycle violation

`CAPABILITY_000L_BOUNDARY_RECLAMATION_NO_GO`
- treatment does not materially extend safe sequence, causes semantic/lifecycle regression, or incurs clearly unacceptable boundary cost

`CAPABILITY_000L_INFRASTRUCTURE_INCOMPLETE`
- exact requests, ownership evidence or valid memory measurements cannot be established

## Evidence

Store locally under:
`results-local/capability/capability-000l/<run-id>/`

At least:
- `summary.json`
- `control.json`
- `treatment.json`
- `boundary-trajectory.json`
- `response-equivalence.json`
- `ownership-evidence.json`
- `memory-samples.jsonl`
- `request-copies/`
- `logs/`

## Stop condition

Do not run real Pi or CAPABILITY 001 after this experiment. ChatGPT reviews the result first.
