# STREAMING-ACTIVATION-AUDIT 001 — result

Date: 2026-08-22
Classification: `STREAMING_ACTIVATION_AUDIT_001_COMPLETE`

## Question

After STREAMED-LAYER-GRADIENT 001 exposed a large first-streamed-layer penalty, identify token-level operations that appear only when any transformer layer is streamed and distinguish fixed activation work from per-streamed-layer work.

## Source-level result

S0 uses the normal resident path: embedding -> mask -> 36 resident blocks/KV updates -> norm -> LM head -> argmax/eval. It does not enter `streamed_forward` and has no streamed-stage lifecycle.

S1 enters `streamed_forward`, keeps shared stages resident, runs explicit stage-local `mx.eval` and cleanup around embedding/norm/head, and executes the full streamed lifecycle for layer 35.

Strict once-per-token non-scaling stream-specific candidates (S0=0; S1/S2/S4≈1):

- streamed-region entry/bookkeeping;
- embedding stage-local `mx.eval(h)`;
- post-embedding `gc.collect(); mx.clear_cache()` cleanup;
- norm stage-local `mx.eval(h2)`;
- post-norm cleanup;
- LM-head stage-local `mx.eval(logits)`;
- post-head final cleanup.

Per-streamed-layer operations scale exactly 1/2/4 across S1/S2/S4:

- `mx.load` + selected tensor map;
- selection-time deletion/GC;
- selected-map validation;
- transient block construction/quantization/parameter rebinding;
- `mx.eval(module.parameters())`;
- streamed block forward + `mx.eval(h2)`;
- transient module/value deletion + GC/cache clear.

The streamed arms also use a fixed manual 36-way dispatcher and 36 explicit per-block `mx.eval(h2)` calls/token; these are fixed with respect to streamed-layer count but not cleanly isolatable as a single treatment.

## Candidate ranking

1. shared-stage cleanup sequences (post-embedding, post-norm, post-head): HIGH;
2. shared-stage stage-local eval boundaries: HIGH;
3. final post-head cleanup alone: MEDIUM;
4. streamed-region bookkeeping / fixed dispatcher: LOW.

No milliseconds are assigned by this audit. It maps control flow and invocation topology only.

## Historical relevance

Prior LOOM Stretch experiments provide plausibility context:

- Stretch 025: batching 36 transformer cleanup sequences into one per transformer body produced a controlled ~3.8628x rate ratio (+286.28%) on its frozen M5/H36 path;
- Stretch 026: consolidating three shared-stage cleanup points into one final shared-path cleanup produced +14.11%;
- Stretch 027: consolidating transformer-body + final cleanup into one end-of-pass cleanup produced +8.67%.

These historical effects are not transferred causally to the current real-M1 partial-residency path, but they strongly justify cleanup cadence as the first isolated candidate.

## Decision

The next experiment is `SHARED_CLEANUP_CONSOLIDATION_001` on S1 only.

CONTROL: exact S1 streamed path.

TREATMENT: remove/defer only the post-embedding and post-norm `gc.collect()/mx.clear_cache()` cleanup sequences and retain exactly one final post-head shared-stage cleanup. Layer-35 streaming, its per-layer cleanup, all explicit eval boundaries, model math, source representation, residency and decoding stay unchanged.

This tests the fixed non-scaling cleanup component directly without touching the per-layer lifecycle.

Raw local evidence:
`results-local/memory/streaming-activation-audit-001/20260822-170803/`
