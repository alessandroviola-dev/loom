# LOOM Stretch 024 — Harness Fix2 Preregistration

Status: **READY / NOT YET RUN**

This document preserves the original Stretch 024 scientific design and records a harness-only repair after the incomplete run `20260820-155313`.

Preserved defect record:
`research/stretch/full-persistent-compute-kernel-attribution-024-harness-defect-20260820-155313.md`

## Why Fix2 is permitted

The incomplete run failed only during PROFILED parent-side telemetry aggregation:

`compute attribution incomplete: NameError: name 'args' is not defined`

The component measurements are collected by the child runtime, but the parent aggregation referenced child-local `args.num_hidden_layers` in three expressions.

This is a harness/telemetry scoping defect, not a model, correctness, memory, or performance result.

No measurements from the incomplete run are reused.

## Harness-only change

Replace only these parent-side geometry expressions:

- `ORACLE_BLOCK_COUNT * args.num_hidden_layers`
  -> `ORACLE_BLOCK_COUNT * len(HOTSET_LAYER_IDS)`
- `range(args.num_hidden_layers)` for `layer_accum`
  -> `range(len(HOTSET_LAYER_IDS))`
- `list(range(args.num_hidden_layers))` for profiled layer-ID validation
  -> `list(range(len(HOTSET_LAYER_IDS)))`.

Under the frozen H36 architecture, `len(HOTSET_LAYER_IDS) == 36`.

No profiling boundary or scientific operation changes.

## Frozen scientific architecture

- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1
- exact oracle M=5
- H36 transformer residency
- full raw-weight persistence `3,583,928,320 B`
- ordinary BF16 KV
- exact numerical and top-1 parity gates
- inherited host/resource/I-O policy
- no tokenizer/sampling/drafter/KV quantization/runtime change
- no deliberate cache purge.

## Frozen CONTROL

`scripts/stretch_five_token_h36_full_weight_persistent_variant_023_fix1.py`

Blob:
`120ad7be2f275559898bf636ca8e8fe039a56c60`

## PROFILED lineage

Base profiling helper, never canonical for execution:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled.py`
- blob `b9c233415386ce796a2331cbfd011881b844cb91`.

Preflight Fix1, used in the incomplete run:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled_fix1.py`
- blob `845b10da26a70455cd40f483cea5d313f9ac12dd`.

Canonical Fix2 PROFILED helper:
- `scripts/stretch_full_persistent_compute_attribution_024_profiled_fix2.py`
- blob `83f9e12dfa30445810ca4d39150dbcd151ad3e66`.

Fix2 carries forward Fix1's unique transformer-cycle telemetry anchor and repairs only the three parent layer-geometry references described above.

## Canonical Fix2 balanced runner

`scripts/stretch_full_persistent_compute_kernel_attribution_024_fix2.py`

Blob:
`de464c4fe5dca90c2fe110337f12e3f6424ea937`

It also carries forward the runner preflight correction that consumes `slowest_layers_by_mean_profiled_compute` rather than the nonexistent `all_layer_means` field.

## Balanced order

`CONTROL -> PROFILED -> PROFILED -> CONTROL`

A completely new four-run sequence is required.

No automatic retry. No reuse of attempt 1 CONTROL from `20260820-155313`.

## Frozen profiling boundaries

PROFILED adds explicit `mx.eval` boundaries on target blocks only for:

1. input RMSNorm
2. attention
3. residual 1
4. post-attention RMSNorm
5. gate projection
6. up projection
7. SwiGLU
8. down projection
9. residual 2.

It also measures:
- persistent-layer build/reuse wall
- per-layer cleanup wall
- transformer materialization/forward wall
- persistent shared-stage materialization/forward wall
- residual unattributed block wall.

Prompt remains unprofiled.

## Interpretation discipline

Explicit `mx.eval` boundaries perturb MLX scheduling/fusion/laziness.

Therefore:
- CONTROL throughput remains the uninstrumented reference within the new balanced sequence;
- PROFILED throughput is only instrumentation-perturbation telemetry;
- component timing/ranking is the Stretch 024 scientific output;
- PROFILED token/s must not be promoted as production performance.

## Success / failure

All four constituents must pass inherited architecture/correctness/resource gates and both PROFILED runs must contain 108 target layer profiles.

Success:
`FULL_PERSISTENT_COMPUTE_ATTRIBUTION_PASS`

Any constituent or profile failure:
`COMPUTE_ATTRIBUTION_INCOMPLETE`

No partial component ranking is accepted from an incomplete sequence.
