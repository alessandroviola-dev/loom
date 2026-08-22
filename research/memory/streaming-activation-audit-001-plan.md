# STREAMING-ACTIVATION-AUDIT 001 — plan

Date: 2026-08-22
Status: FROZEN / RUN PENDING

## Goal

Identify the exact control-flow/lifecycle work that is executed once per generated token when the streamed-transformer set changes from empty (S0) to non-empty (S1+), without yet changing runtime behavior.

STREAMED-LAYER-GRADIENT 001 measured a highly structured system-level cost:

- S0 wall/token: 71.315 ms
- S1: 171.824 ms
- S2: 210.287 ms
- S4: 288.737 ms

A descriptive two-component fit is:

`wall/token ≈ 71.315 ms + 61.284 ms * I(streaming active) + 39.007 ms * streamed_layers`

with `R² ≈ 0.999993` on the four pooled points.

The ~61 ms activation term is not yet assigned to an internal mechanism. This audit must identify candidate once-per-token operations before any optimization A/B is designed.

## Scope

Use the exact local implementation underlying:
- `scripts/loom_streamed_layer_gradient_001.py`
- `scripts/loom_shared_stage_residency_001.py`
- proven Stretch streaming helpers they reuse.

No model benchmark is required unless a tiny no-science counter/dry-run is necessary to verify invocation counts. Do not run a new performance treatment.

## Mandatory source audit

Compare S0 and S1 execution paths for one generated token and enumerate every operation that exists only when the streamed-layer set is non-empty.

At minimum inspect for:
- loader/context setup or teardown;
- safetensors/file open, lookup, indexing or handle lifecycle;
- per-token creation/destruction of dictionaries/modules/parameter containers;
- `mx.eval` / `mx.synchronize` or equivalent materialization boundaries;
- allocator/cache cleanup including `mx.clear_cache`;
- Python GC or explicit object release;
- parameter detach/rebind/reset;
- KV/cache handling differences;
- stream-region pre/post hooks;
- once-per-token bookkeeping or tracing/counters;
- any branch that executes once per token regardless of streamed-layer count.

Separately enumerate operations that execute once per streamed transformer layer.

## Invocation-count verification

For each candidate operation classify:
- `S0_COUNT_PER_TOKEN`
- `S1_COUNT_PER_TOKEN`
- `S2_COUNT_PER_TOKEN`
- `S4_COUNT_PER_TOKEN`

Prefer static/control-flow proof. If ambiguous, add temporary low-overhead counters in a local audit harness, not timers and not artificial synchronization.

Counters must preserve exact token output if inference is used.

## Candidate ranking

Rank once-per-token streaming-activation candidates by plausibility using only:
- invocation topology;
- whether the operation can plausibly block/materialize/flush substantial MLX work;
- prior LOOM evidence about that operation if available;
- whether its count matches the observed one-time activation structure.

Do not infer duration from source code alone.

For each candidate state whether a future one-factor A/B can isolate it without changing model math.

## Required output classes

Choose one:

`STREAMING_ACTIVATION_AUDIT_001_COMPLETE`
if the S0/S1 control-flow difference is mapped and at least one scientifically isolatable once-per-token candidate is identified.

`STREAMING_ACTIVATION_AUDIT_001_UNRESOLVED`
if the control-flow map is complete but no once-per-token candidate can be isolated cleanly.

`STREAMING_ACTIVATION_AUDIT_001_INFRASTRUCTURE_INCOMPLETE`
only if local source/helper provenance cannot be recovered sufficiently.

## Evidence

Store local evidence under:
`results-local/memory/streaming-activation-audit-001/<run-id>/`

At minimum:
- `summary.json`
- `source-map.json`
- `invocation-counts.json`
- `candidate-ranking.json`
- optional exact-token evidence if a counter run is needed.

## Pi role

Pi performs source/runtime inspection and minimal counter validation only. Pi must not:
- optimize code;
- change streaming semantics;
- run prefetch/buffering/range-I/O experiments;
- update Git/HANDOFF/ROADMAP;
- propose the next experiment beyond ranking isolatable candidates.
