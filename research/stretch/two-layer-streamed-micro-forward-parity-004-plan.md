# Stretch 004 — Two-Layer Streamed Micro-Forward Parity — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Can two real consecutive Qwen3 transformer blocks be executed with one-layer-at-a-time weight residency and produce a numerically equivalent output to a resident two-layer control, while retaining the bounded-memory behavior demonstrated by Stretch 001–003?

## Motivation

Stretch 001 proved exact layer-addressable safetensors I/O.
Stretch 002 proved one layer can remain lazy, materialize to exactly 84,427,264 B, and be reclaimed.
Stretch 003 proved the same materialize/evict cycle repeats across layers 18 and 19 in one MLX process with no observed active/cache accumulation.

Stretch 004 introduces actual transformer computation for the first time.

## Frozen subject

Artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Config:
- model type `qwen3`
- hidden size 4096
- 36 layers
- 32 attention heads
- 8 KV heads
- head dim 128
- quantization 3-bit / group size 64.

Environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

Stretch 002 helper source blob required:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef`.

## Implementation provenance

Use the installed `mlx_lm.models.qwen3.TransformerBlock` class from mlx-lm 0.31.3 rather than reimplementing Qwen3 math.

The official v0.31.3 block performs:
- input RMSNorm;
- self attention with Q/K normalization + RoPE;
- residual add;
- post-attention RMSNorm;
- SwiGLU MLP;
- residual add.

The quantized block is transformed with `mlx.nn.quantize` using the local model's frozen 3-bit/group-64 config before loading the layer-specific weights, matching the official mlx-lm load path.

Record the installed Qwen3 source SHA-256 at runtime for provenance.

## Frozen input

Synthetic deterministic activation only; no tokenizer or embedding lookup.

- batch size: 1
- sequence length: 4
- hidden size: 4096
- deterministic values from `sin(arange(N) / 97)` cast to bfloat16
- attention mask generated with official `create_attention_mask`.

This isolates transformer-block correctness from tokenizer/embedding/shared-weight concerns.

## Resident control

Materialize layers 18 and 19 simultaneously using the same real Qwen3 `TransformerBlock` implementation and exact quantized weights.

Then compute:
`x -> layer18 -> layer19 -> resident_output`.

Record:
- pre-eval active memory;
- active memory after both layer parameter sets are materialized;
- two-layer materialization wall;
- two-layer forward wall.

Expected resident weight-materialization delta:
approximately `2 * 84,427,264 B`, tolerance +/-2 MiB.

## Streamed path

In the same child process, using a fresh copy of the same deterministic input:

1. lazy-load only layer 18 weights;
2. construct/quantize exact Qwen3 block 18;
3. materialize block 18;
4. run block 18 forward and materialize its activation output;
5. delete block-18 weight references, GC and clear MLX cache while preserving the activation;
6. lazy-load only layer 19 weights;
7. construct/quantize exact block 19;
8. materialize block 19;
9. run block 19 forward;
10. delete block-19 weights and clear cache.

Per streamed layer:
- pre-eval active delta <=32 MiB;
- materialized weight delta must match 84,427,264 B within +/-1 MiB;
- post-clear active delta relative to that cycle's pre-layer state must remain within +/-4 MiB (activation replacement allowance);
- post-clear MLX cache <=4 MiB.

## Numerical parity gate

Compare final resident and streamed outputs in float32.

Record:
- max absolute difference;
- mean absolute difference;
- resident max absolute magnitude;
- frozen threshold `1e-5 + 1e-5 * resident_max_abs`.

Primary parity PASS requires max absolute difference <= threshold.

## Host / runtime safety

Host launch gate:
- 3 samples;
- each >=60% free memory;
- swap <=5600 MB.

Runtime:
- free memory <5% => `PARTIAL_RESOURCE_FAIL`;
- swap >5600 MB => `PARTIAL_RESOURCE_FAIL`;
- missing telemetry => `TELEMETRY_FAIL`.

No guardrail weakening.

## Primary PASS

`TWO_LAYER_STREAMED_FORWARD_PARITY_PASS` requires:
- exact config/provenance preflights;
- resident two-layer materialization near expected size;
- both streamed cycles satisfy lazy/materialization/eviction gates;
- numerical output parity passes;
- no safety violation.

Other diagnostic classifications include:
- `EAGER_FULL_FILE_LOAD_SUSPECTED`
- `RESIDENT_CONTROL_SIZE_MISMATCH`
- `STREAMED_MATERIALIZATION_SIZE_MISMATCH`
- `STREAMED_EVICTION_INCONCLUSIVE`
- `NUMERICAL_PARITY_FAIL`
- runtime/safety/harness failures.

Harness/runtime defects are not evidence against the architecture.

## Explicit exclusions

Stretch 004 does NOT:
- construct the full 36-layer Qwen model;
- load tokenizer or embedding weights;
- run final model norm or LM head;
- create KV cache;
- generate tokens;
- claim end-to-end streamed inference;
- add prefetch/double buffering;
- test layer skipping.

## Decision after result

If PASS: preregister the next experiment as a longer streamed block chain before adding embeddings/KV/token generation. The next expansion must preserve resident numerical control and explicit memory accounting.

If numerical parity fails: diagnose block loading/quantization/mask semantics before expanding.

If resource boundedness fails: inspect exact activation/weight residency rather than adding more layers.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_two_layer_streamed_micro_forward_parity_004.py
python3 scripts/stretch_two_layer_streamed_micro_forward_parity_004.py
```

No download is expected.