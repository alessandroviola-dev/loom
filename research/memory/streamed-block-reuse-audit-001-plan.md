# STREAMED-BLOCK-REUSE-AUDIT 001 — Frozen Plan

Status: FROZEN
Date: 2026-08-23

## Goal

Determine whether the current per-token streamed transformer-layer path contains a cleanly isolatable **transient block / quantized-structure reconstruction** cost that can be removed by reusing a weightless module structure, while preserving:
- exact model math;
- exact token output;
- identical layer residency;
- identical streamed weight bytes;
- identical source/load behavior;
- identical materialization and forward semantics;
- no persistence of layer-35 weight arrays between tokens.

This is an implementation/source audit only. Do not optimize or benchmark performance yet.

## Current promoted lifecycle

Use the canonical Gradient002/S1 lifecycle:
- layers 0..34 persistent;
- layer 35 streamed;
- embedding/final norm/LM head persistent;
- shared intermediate cleanup consolidated;
- embedding/norm/head explicit evals retained;
- select-time `gc.collect()` retained;
- streamed-layer post-forward `gc.collect()/mx.clear_cache()` omitted/deferred;
- transient layer module/value deletion retained;
- exactly one final post-head cleanup/token.

`SELECT_TIME_GC_DEFER 001` was NO-GO, so select-time GC must remain.

## Scientific question

For each generated token, identify exactly which operations in the layer-35 path are:

1. **STRUCTURE_CONSTRUCTION** — architecture/module object creation independent of the current weight values;
2. **QUANTIZED_STRUCTURE_SETUP** — quantized module conversion/configuration independent of current weight values, if any;
3. **PARAMETER_BINDING** — attaching selected streamed weight arrays to the structure;
4. **PARAMETER_MATERIALIZATION** — `mx.eval(module.parameters())` or equivalent;
5. **FORWARD**;
6. **OWNERSHIP_RELEASE** — deletion/detachment of current streamed weight arrays;
7. **SOURCE_LOAD_SELECTION** — `mx.load`, dictionary/slice selection and related source work.

Determine whether categories 1 and/or 2 can be performed once per process/prompt and reused across tokens **without retaining current or previous layer weights**.

## Mandatory source inspection

Trace actual call graph from the current local runners/helpers. At minimum inspect:
- `scripts/loom_streamed_layer_gradient_002.py`;
- `scripts/loom_streamed_layer_cleanup_defer_001.py`;
- proven helpers they actually call;
- Qwen/MLX module construction and quantization/rebinding code used by layer 35.

Do not infer behavior from filenames.

For each relevant function/block record:
- source file;
- function/class;
- approximate line/range;
- operation;
- invocation count per streamed layer/token;
- whether it depends on current weight values;
- whether it creates MLX arrays;
- whether it can hold references to streamed weights;
- whether it is safe to retain after a token;
- whether it is cleanly isolatable in a future A/B.

## Reference-lifetime proof

If reusable structure appears feasible, prove the ownership/lifetime requirements needed so that after each token:
- no layer-35 weight array from that token remains referenced;
- no selected-weight dictionary remains referenced;
- no loaded full-weight container remains referenced;
- persistent raw-weight accounting remains `3,499,501,056 B` for S1;
- next token must still execute the same `84,427,264 B` logical streamed weight path;
- no effective caching/residency promotion occurs.

Distinguish Python object persistence from MLX weight-array persistence.

## Future A/B candidate

If safe reuse is possible, define the smallest future one-factor CONTROL/TREATMENT:

CONTROL:
- canonical current S1; construct transient block/quantized structure each token.

TREATMENT:
- construct only the weight-independent reusable structure once;
- each token performs identical load/select, current-weight binding, parameter materialization, forward and current-weight detachment/release;
- no layer weight survives across tokens.

Do not implement or run this A/B in the audit.

## Counter validation

If static source inspection cannot establish counts/lifetimes, a short counter/reference-identity harness is allowed.

Allowed:
- integer counters;
- Python object IDs;
- weakrefs/reference checks where appropriate;
- short canonical prompt;
- exact token parity check.

Forbidden:
- performance timing as scientific evidence;
- profiler;
- extra `mx.eval`/`mx.synchronize`;
- changing residency;
- caching weights;
- prefetch;
- buffering;
- source I/O redesign.

## Classification

`STREAMED_BLOCK_REUSE_AUDIT_001_COMPLETE`
if the reconstruction/binding/materialization lifecycle is mapped and a safe future A/B is either identified or ruled out with evidence.

`STREAMED_BLOCK_REUSE_AUDIT_001_UNRESOLVED`
if ownership/lifetime cannot be proven cleanly.

`STREAMED_BLOCK_REUSE_AUDIT_001_INFRASTRUCTURE_INCOMPLETE`
only if actual source/helper provenance cannot be recovered.

## Evidence

Store under:
`results-local/memory/streamed-block-reuse-audit-001/<run-id>/`

At minimum:
- `summary.json`
- `source-map.json`
- `lifetime-map.json`
- `candidate-ab.json`
- optional `counter-events.jsonl`
- optional `parity.json`

## Return

Return only:
1. classification;
2. exact current layer-35 lifecycle map;
3. table of reconstruction/binding/materialization operations;
4. which operations are weight-independent;
5. reusable structure feasible YES/NO;
6. exact references that would need clearing after each token;
7. proof that weights would not become persistent;
8. smallest future one-factor A/B if feasible;
9. counter validation used YES/NO;
10. parity if counters used;
11. strongest supported conclusion;
12. evidence directory;
13. files created/modified.

No Git, no HANDOFF/ROADMAP, no optimization, no prefetch, no buffering, no range-I/O redesign, no OUTCORE-BLOCK, no next experiment execution.
