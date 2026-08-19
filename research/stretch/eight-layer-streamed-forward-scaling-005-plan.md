# Stretch 005 — Eight-Layer Streamed Forward Scaling — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Does the exact resident-vs-streamed Qwen3 micro-forward parity demonstrated by Stretch 004 continue across a longer eight-layer chain while streamed raw-weight residency remains approximately one transformer layer at a time instead of growing with chain depth?

## Motivation

Stretch 004 (`20260819-162454`) established for layers 18+19:
- resident materialized delta exactly 168,854,528 B = 2 layer payloads;
- streamed materialized delta approximately one 84,427,264-byte layer at a time;
- eviction within frozen tolerance after each streamed layer;
- final resident vs streamed output max/mean absolute difference 0.0;
- classification `TWO_LAYER_STREAMED_FORWARD_PARITY_PASS`.

The next factor is chain depth only.

## Single changed factor vs Stretch 004

Change:
- transformer block chain length: **2 -> 8 consecutive layers**.

Freeze all other experimental properties:
- same local Qwen3-8B 3-bit artifact;
- same MLX/MLX-LM/transformers versions;
- same official `mlx_lm.models.qwen3.TransformerBlock` implementation;
- same 3-bit/group-64 quantization path;
- same synthetic deterministic activation generation;
- batch size 1;
- sequence length 4;
- hidden size 4096;
- same causal mask semantics;
- same no-tokenizer/no-embedding/no-KV/no-LM-head boundary;
- same resident-control vs streamed-path comparison;
- same per-layer lazy/materialization/eviction gates;
- same numerical parity formula;
- same host/runtime guardrails.

No prefetch, double buffering, layer skipping or model-quality evaluation is added.

## Frozen layer chain

Exactly eight consecutive layers:

`[14, 15, 16, 17, 18, 19, 20, 21]`

Rationale:
- includes the already validated layers 18 and 19;
- extends both before and after them;
- every layer in Stretch 001 has identical 25-tensor / 84,427,264-byte payload, so this is a clean depth-scaling probe.

No automatic expansion to more layers is allowed from this plan.

## Frozen provenance

Stretch 004 runner:
`scripts/stretch_two_layer_streamed_micro_forward_parity_004.py`

Required Stretch 004 blob:
`426423c9d9b7bd7bd1c6a3620197ad5212c678e6`

Stretch 002 helper runner:
`scripts/stretch_single_layer_mlx_materialization_002.py`

Required Stretch 002 blob:
`e7bd6bf4c61b44664c0c8421bf230b938509e4ef`

Subject artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Expected environment:
- mlx 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1.

## Frozen config

- model type `qwen3`
- hidden size 4096
- 36 transformer layers
- 32 attention heads
- 8 KV heads
- head dim 128
- quantization 3-bit / group size 64.

Every selected layer must match:
- 25 tensors
- 84,427,264 B.

## Resident control

Construct eight independent official Qwen3 TransformerBlock instances for layers 14..21, quantize each with the frozen config, associate exact layer-specific lazy weights, then materialize all eight parameter sets simultaneously.

Resident expected raw-weight materialization:

`8 * 84,427,264 = 675,418,112 B`

Frozen resident-size tolerance:
+/- 8 MiB.

Then execute the deterministic activation through all eight resident blocks in order and materialize the final resident output.

Record:
- resident base active memory;
- resident pre-eval active memory;
- resident post-materialization active memory;
- materialization delta;
- resident materialization wall;
- eight-layer forward wall;
- resident peak MLX memory.

After the resident output is materialized, delete all resident block/weight references, run GC + `mx.clear_cache()`, and retain only the final resident output needed for parity.

## Streamed path

Using a fresh identical synthetic activation in the same MLX child process:

For each layer 14..21:
1. sample pre-layer active memory;
2. lazy-load only that layer's weights;
3. construct and quantize one official Qwen3 TransformerBlock;
4. record pre-eval active memory;
5. materialize that block's parameters;
6. record post-materialization active memory;
7. execute the block on the current activation and materialize the output;
8. replace the current activation with the new output;
9. delete block/weight/old-activation references;
10. run GC + `mx.clear_cache()`;
11. record post-clear active/cache memory.

The child process remains alive for all eight cycles.

## Per-layer streamed gates

For every streamed layer:
- pre-eval active delta <=32 MiB;
- materialized delta must match 84,427,264 B within +/-1 MiB;
- post-clear active delta relative to the cycle's pre-layer state within +/-4 MiB;
- post-clear cache <=4 MiB.

Failure classifications preserve Stretch 004 semantics:
- `EAGER_FULL_FILE_LOAD_SUSPECTED`
- `STREAMED_MATERIALIZATION_SIZE_MISMATCH`
- `STREAMED_EVICTION_INCONCLUSIVE`.

## Numerical parity gate

Compare final resident and streamed outputs in float32.

Record:
- max absolute difference;
- mean absolute difference;
- resident max absolute magnitude;
- threshold `1e-5 + 1e-5 * resident_max_abs`.

Parity PASS requires:
`max_abs_diff <= threshold`.

If not:
`NUMERICAL_PARITY_FAIL`.

## Scaling metrics

Primary scaling evidence:
- resident materialized raw-weight delta;
- maximum streamed per-layer materialized delta;
- ratio `resident_materialized_delta / max_streamed_materialized_delta`;
- maximum post-clear streamed residual active/cache;
- resident forward wall;
- total streamed materialization wall;
- total streamed forward wall;
- system min free memory / peak swap.

Expected structural outcome if bounded streaming scales:
- resident raw-weight delta approximately 8 layer payloads (~644.13 MiB);
- streamed per-cycle raw-weight delta approximately 1 layer payload (~80.52 MiB);
- residency ratio near 8x, without cumulative per-layer active/cache growth.

This expected ratio is a preregistered structural expectation, not a guaranteed PASS criterion beyond the explicit byte gates.

## Host/runtime safety

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

`EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS` requires:
- source/config/version/layer-provenance preflights PASS;
- resident eight-layer materialized delta within +/-8 MiB of 675,418,112 B;
- all eight streamed layers satisfy lazy/materialization/eviction gates;
- numerical parity passes;
- no runtime safety violation.

## Interpretation boundary

A PASS would establish that actual Qwen3 transformer computation can scale from two to eight consecutive blocks with resident-vs-streamed numerical parity while raw weight residency remains bounded near one block at a time.

A PASS still does NOT prove end-to-end streamed LLM inference. This experiment excludes:
- embeddings;
- final norm;
- LM head;
- tokenizer;
- KV cache;
- autoregressive token generation;
- the remaining 28 transformer layers;
- prefetch/double buffering.

## Decision after result

If PASS:
- freeze the scaling result;
- next consider a full 36-transformer-block body parity experiment with the same tiny activation before adding shared weights/KV/token generation.

If parity fails:
- diagnose the earliest divergence before expanding depth.

If boundedness fails:
- inspect exact layer/cycle and activation residency rather than changing multiple runtime factors.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_eight_layer_streamed_forward_scaling_005.py
python3 scripts/stretch_eight_layer_streamed_forward_scaling_005.py
```

No download is expected.
