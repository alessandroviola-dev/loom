# Stretch 003 — Two-Layer Repeated Bounded Residency — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can the verified single-layer lazy-load/materialize/evict behavior from Stretch 002 repeat across two different consecutive transformer layers **inside the same MLX process** without active/cache memory accumulating between cycles?

## Motivation

Stretch 001 established clean layer addressability for the local Qwen3-8B 3-bit artifact:
- 36 transformer layers;
- each layer exactly 84,427,264 B / 25 tensors;
- exact selective one-layer disk I/O works.

Stretch 002 (`20260819-155641`) established for layer 18:
- pre-eval active delta 0 B;
- post-eval active delta exactly 84,427,264 B;
- post-clear active/cache delta 0/0 B;
- classification `SINGLE_LAYER_MLX_EVICTION_PASS`.

The next prerequisite is repeated bounded residency rather than a one-off load.

## Frozen provenance

Source helper/runner:
`scripts/stretch_single_layer_mlx_materialization_002.py`

Required Stretch 002 source blob:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef`

Subject artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1

## Probe layers

Exactly two consecutive layers:
- layer 18
- layer 19

Each must independently match:
- 25 tensors
- 84,427,264 B header-derived payload.

No automatic expansion to more layers is allowed from this plan.

## Same-process sequence

One MLX child process performs:

1. establish MLX active/cache baseline;
2. `mx.load()` safetensors;
3. retain only lazy arrays for layer 18 and delete the full returned tensor dictionary;
4. measure pre-eval MLX memory;
5. `mx.eval()` layer 18 arrays;
6. measure materialized memory;
7. delete layer-18 references, GC, `mx.clear_cache()`, measure recovery;
8. repeat steps 2–7 for layer 19 **without terminating the child process**;
9. return both cycle records.

This is a raw-weight residency experiment only.

## Explicit exclusions

Stretch 003 does NOT:
- construct the Qwen3 model object;
- run attention/MLP/transformer forward computation;
- create activations or residual streams;
- create tokenizer or KV cache;
- generate tokens;
- download or modify model files;
- test quality or numerical equivalence.

## Frozen gates

Host launch gate inherited from Stretch 002:
- 3 samples;
- each >=60% free memory;
- swap <=5600 MB.

Runtime safety:
- free memory <5% => `PARTIAL_RESOURCE_FAIL`;
- swap >5600 MB => `PARTIAL_RESOURCE_FAIL`;
- missing telemetry => `TELEMETRY_FAIL`.

For each layer cycle:
- pre-eval active delta must be <=32 MiB, otherwise `EAGER_FULL_FILE_LOAD_SUSPECTED`;
- post-eval active delta must match 84,427,264 B within +/-1 MiB, otherwise `MATERIALIZATION_SIZE_MISMATCH`;
- post-clear active delta <=1 MiB;
- post-clear cache delta <=1 MiB.

## Primary PASS

`TWO_LAYER_BOUNDED_RESIDENCY_PASS` requires both layer 18 and layer 19 to satisfy all materialization and eviction gates in the same process.

If both materialize but either fails the eviction tolerance:
`TWO_LAYER_MATERIALIZATION_PASS_EVICTION_INCONCLUSIVE`.

Harness/runtime/provenance failures must not be interpreted as evidence against layer streaming.

## Interpretation boundary

A PASS would establish repeated bounded raw-weight residency across two layers. It would still **not** prove end-to-end streamed transformer inference.

Only after a PASS should LOOM preregister a small sequential-forward prototype that includes actual transformer-layer computation and numerical comparison against a resident control.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_two_layer_bounded_residency_003.py
python3 scripts/stretch_two_layer_bounded_residency_003.py
```

No model download is expected.
