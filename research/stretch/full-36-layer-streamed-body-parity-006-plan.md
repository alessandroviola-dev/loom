# Stretch 006 — Full 36-Layer Streamed Body Parity — Preregistered Plan

Date: 2026-08-19
Status: **PREREGISTERED / NOT YET RUN**

## Research question

Does the bounded one-layer-at-a-time Qwen3 transformer-weight residency demonstrated by Stretch 004–005 continue across the **entire 36-transformer-block body**, while producing the same final activation as a resident 36-block control?

## Motivation

Stretch 005 (`20260819-163413`) changed only chain depth from 2 to 8 blocks and reached `EIGHT_LAYER_STREAMED_FORWARD_SCALING_PASS`:
- resident materialized delta: 675,352,572 B;
- maximum streamed one-layer materialized delta: 84,427,264 B;
- resident/streamed ratio: 7.999223710482908x;
- all streamed cycles reclaimed to the frozen tolerance;
- resident-vs-streamed max/mean absolute difference: 0.0 / 0.0;
- minimum free memory 63%; peak swap 810.5 MB.

The next preregistered factor is transformer-body depth only: 8 -> 36 blocks.

## Single changed factor vs Stretch 005

Change:
- transformer block chain length: **8 -> 36**, exactly layers `0..35`.

Preserve:
- same verified local Qwen3-8B 3-bit artifact;
- same mlx / mlx-lm / transformers versions;
- same official `mlx_lm.models.qwen3.TransformerBlock`;
- same 3-bit/group-64 quantization/load semantics;
- same deterministic batch1 / sequence4 / hidden4096 synthetic activation;
- same attention-mask semantics;
- same resident-control vs streamed-path order and computation;
- same per-layer lazy/materialization/eviction gates;
- same numerical parity formula;
- same host/runtime guardrails;
- no tokenizer, embedding lookup, final norm, LM head, KV cache, autoregressive generation, prefetch, double buffering or layer skipping.

## Frozen provenance

Stretch 005 source:
`scripts/stretch_eight_layer_streamed_forward_scaling_005.py`

Required source blob:
`8bbfff727a0131c48d4ba71edc8de485182b7fbe`

Stretch 006 is implemented as a frozen transform of that exact source rather than a manual rewrite.

Transform may change only:
1. experiment/display naming from Stretch 005 to Stretch 006;
2. layer list from `[14..21]` to `list(range(36))`;
3. output directory/classification naming;
4. resident-control size tolerance from +/-8 MiB to **+/-36 MiB**, preserving the same +/-1 MiB-per-layer scaling used by Stretch 005;
5. result-summary provenance field for the frozen Stretch 005 source.

The wrapper must assert that every expected source replacement occurs exactly once before executing the transformed program.

## Frozen subject

Artifact:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Config:
- model type `qwen3`
- hidden size 4096
- transformer layers 36
- attention heads 32
- KV heads 8
- head dim 128
- quantization 3-bit / group size 64.

Every layer must remain exactly:
- 25 tensors
- 84,427,264 B.

## Resident control

Construct all 36 official Qwen3 TransformerBlock instances, associate each exact layer-specific lazy tensor set, quantize with the frozen config, and materialize all 36 parameter sets simultaneously.

Exact header-derived transformer-body payload:

`36 * 84,427,264 = 3,039,381,504 B`

Presentation value: approximately 2.831 GiB.

Resident size gate:
- observed materialized delta must be within +/-36 MiB of 3,039,381,504 B.

Then run the frozen synthetic activation through layers 0 -> 35 and materialize the final resident activation.

## Streamed path

Using a fresh identical input in the same child process, execute layers 0 -> 35 sequentially.

For each layer:
1. sample pre-layer active memory;
2. lazy-load only the selected layer tensors;
3. construct/quantize one official Qwen3 TransformerBlock;
4. require pre-eval active delta <=32 MiB;
5. materialize block parameters;
6. require materialized delta 84,427,264 B +/-1 MiB;
7. run the real transformer-block forward and materialize output activation;
8. replace current activation;
9. delete block/weight/old-activation references;
10. GC + `mx.clear_cache()`;
11. require post-clear active delta within +/-4 MiB and cache <=4 MiB.

No cumulative residency allowance is introduced.

## Numerical parity

Compare final resident and streamed activations in float32.

Frozen metrics/gate:
- max absolute difference;
- mean absolute difference;
- resident max absolute magnitude;
- threshold `1e-5 + 1e-5 * resident_max_abs`;
- parity PASS iff max absolute difference <= threshold.

## Scaling metrics

Record:
- resident materialized raw-weight delta;
- maximum streamed one-layer materialized delta;
- resident / streamed materialized ratio;
- all 36 per-layer pre/materialized/post-clear deltas;
- maximum streamed residual active/cache;
- resident materialization/forward wall;
- streamed total materialization/forward wall;
- resident/stream MLX peak memory;
- minimum system free memory;
- peak swap;
- peak child RSS;
- disk before/after.

Structural expectation if bounded streaming continues:
- resident raw-weight delta ~3.039 GB;
- streamed raw-weight delta ~84.4 MB per cycle;
- resident/streamed raw-weight ratio near **36x**;
- no cumulative active/cache growth;
- numerical parity retained.

This expectation does not replace the explicit gates.

## Host/runtime safety

Unchanged from Stretch 005:
- launch: 3 samples each >=60% free memory;
- swap <=5600 MB;
- runtime free memory <5% => `PARTIAL_RESOURCE_FAIL`;
- runtime swap >5600 MB => `PARTIAL_RESOURCE_FAIL`;
- missing required telemetry => `TELEMETRY_FAIL`.

No guardrail weakening or manual memory purge is allowed.

## Primary PASS

`FULL_36_LAYER_STREAMED_BODY_PARITY_PASS` requires:
- source/config/version/layer provenance PASS;
- resident 36-layer materialized delta within frozen tolerance;
- all 36 streamed cycles pass lazy/materialization/eviction gates;
- resident-vs-streamed numerical parity PASS;
- no runtime safety violation.

## Interpretation boundary

A PASS would establish streamed parity for the **entire transformer-block body** of this Qwen3-8B 3-bit checkpoint with raw layer-weight residency bounded near one layer at a time.

It would still not yet constitute end-to-end LLM inference because it excludes:
- token embeddings;
- final RMSNorm;
- LM head / tied embedding projection;
- tokenizer;
- KV cache;
- autoregressive generation.

Therefore no token/s or model-quality claim is authorized from Stretch 006 alone.

## Decision after result

If PASS:
- freeze the full-body result;
- move to shared-weight policy: embeddings + final norm + LM-head/logit parity with the 36-layer streamed body;
- only afterward introduce KV cache and token generation.

If resident control resource-fails:
- classify only the frozen experiment outcome; do not lower safety guardrails;
- inspect whether a separate resident control process is scientifically required before redesign.

If streamed boundedness or parity fails:
- diagnose the first failing layer/cycle before adding components.

## Exact execution

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/stretch_full_36_layer_streamed_body_parity_006.py
python3 scripts/stretch_full_36_layer_streamed_body_parity_006.py
```

No download is expected.
