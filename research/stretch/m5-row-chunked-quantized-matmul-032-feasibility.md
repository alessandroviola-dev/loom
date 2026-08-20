# Stretch 032 candidate — M5 row-chunked quantized-matmul feasibility

Date: 2026-08-20  
Status: **NO-GO — diagnostic only; no Stretch 032 ABBA created or run.**

## Question and boundary

With the frozen global oracle block `M=5`, can every eligible Qwen3 quantized linear be evaluated as `2 + 2 + 1` input rows (three `mx.quantized_matmul` calls plus `mx.concatenate`) faster than one monolithic `M=5` call?

This artifact is a real-weight microbenchmark, not a scientific constituent. It does not change the M5 geometry, model, gates, or canonical implementation. It may decide only whether a separately preregistered Stretch 032 ABBA is warranted.

## Frozen diagnostic environment

- Apple M1 / 8 GB; canonical literal launcher `results-local/mlx/venv-mlx-lm-0.31.3/bin/python`.
- Child provenance: `sys.prefix` matched that venv; mlx/mlx-metal `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`.
- Real checkpoint: `results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`, SHA-256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`.
- Qwen3 config: hidden `4096`, intermediate `12288`, 36 layers, 32 attention heads, 8 KV heads, head dimension `128`.
- Quantization: packed real weights, BF16 scales/biases, affine `bits=3`, `group_size=64`.
- Scope: only the selected layer-0 projection payload tensors were retained/materialized (`84,410,376 B` active after setup); no model module or full model was constructed.

The installed `mlx_lm.models.qwen3` source confirms the projection definitions: q `4096→4096`, k/v `4096→1024`, o `4096→4096`, gate/up `4096→12288`, and down `12288→4096`. Safetensors headers confirmed the following exact real packed geometries:

| Projection | K → N | packed weight U32 | scales/biases BF16 | output at M5 |
|---|---:|---:|---:|---:|
| q_proj | 4096 → 4096 | 4096 × 384 | 4096 × 64 | 1 × 5 × 4096 |
| k_proj | 4096 → 1024 | 1024 × 384 | 1024 × 64 | 1 × 5 × 1024 |
| v_proj | 4096 → 1024 | 1024 × 384 | 1024 × 64 | 1 × 5 × 1024 |
| o_proj | 4096 → 4096 | 4096 × 384 | 4096 × 64 | 1 × 5 × 4096 |
| gate_proj | 4096 → 12288 | 12288 × 384 | 12288 × 64 | 1 × 5 × 12288 |
| up_proj | 4096 → 12288 | 12288 × 384 | 12288 × 64 | 1 × 5 × 12288 |
| down_proj | 12288 → 4096 | 4096 × 1152 | 4096 × 192 | 1 × 5 × 4096 |

## Method

One deterministic BF16 input of shape `1 × 5 × K` was constructed per input width and reused unchanged by both sides.

- **CONTROL:** one affine `mx.quantized_matmul(..., transpose=True, group_size=64, bits=3, mode="affine")` over M5.
- **TREATMENT:** slices of the same rows `2`, `2`, and `1`; three identical qmatmuls; then `mx.concatenate(axis=1)`.
- Exactness was checked before timing using the actual outputs.
- Each side received 40 excluded warmup iterations. Timed work used 60 interleaved `CONTROL → CHUNKED → CHUNKED → CONTROL` cycles: 120 synchronized samples per side/projection. Each sample timed only construction through `mx.eval(output)`.
- No deliberate cache purge occurred between sides or projections. Peak memory was reset only as a telemetry counter after warmup, not to evict cache/data.

## Exactness

All seven outputs had equal top-level shape and bit-exact equality: `max_abs_diff = 0.0`, `mean_abs_diff = 0.0`. Chunking deliberately changes supplied row shape/call count, but this probe did **not** observe a numerical change. This does not identify the internal MLX kernel name; it establishes only the observed output behavior on these shapes and real layer-0 payloads.

## Timings

Values are median milliseconds `[p25, p75]`; ratio is `chunked / monolithic`. Each total is synchronized wall across 120 samples.

| Projection | M5 monolithic ms | 2+2+1 ms | Ratio | total control / chunked s |
|---|---:|---:|---:|---:|
| q_proj | 1.4616 [1.2642, 1.5332] | 1.5532 [1.3409, 1.6807] | 1.062675 | 0.170768 / 0.182566 |
| k_proj | 0.7299 [0.7125, 0.7519] | 0.8602 [0.8417, 0.8798] | 1.178569 | 0.088086 / 0.103633 |
| v_proj | 0.7339 [0.7168, 0.7536] | 0.8705 [0.8450, 0.9010] | 1.186259 | 0.088062 / 0.106623 |
| o_proj | 1.5442 [1.5215, 1.5794] | 1.6850 [1.6624, 1.7228] | 1.091189 | 0.187267 / 0.204961 |
| gate_proj | 2.4000 [2.2553, 2.4619] | 2.5487 [2.4214, 2.6286] | 1.061970 | 0.284509 / 0.304940 |
| up_proj | 2.2836 [2.2014, 2.3888] | 2.4394 [2.3756, 2.5827] | 1.068221 | 0.276444 / 0.298807 |
| down_proj | 2.4717 [2.4248, 2.6079] | 2.6240 [2.5545, 2.7770] | 1.061597 | 0.306169 / 0.322367 |

Chunking is slower for every projection; the extra dispatches plus concatenate are not offset by the M2/M1 row shapes on this M1 / 3-bit workload.

## Diagnostic weighted estimate

Stretch 028's perturbed component telemetry is used only for an admission estimate, never as a scientific result. Applying the measured gate/up/down ratios to its corresponding MLP component times yields an estimated **loss** of `0.0185683 s/block`: `-5.3249%` of the valid Stretch 031 M5 median block wall (`0.3487060 s`) and `-4.1291%` of the Stretch 028 transformer-compute time. Applying the mean q/k/v/o result to the whole Stretch 028 attention bucket is knowingly an optimistic bound because attention includes non-projection work; it is also negative (`-0.0127831 s/block`). The MLP-plus-attention upper-bound loss is `-8.9908%` of the Stretch 031 M5 median block wall.

## Upstream context

MLX issue [#3553](https://github.com/ml-explore/mlx/issues/3553), retrieved 2026-08-20, reports a shape-dependent M=3 cost step on an M4 Pro with **4-bit** group-64 workloads, particularly large asymmetric MLP shapes. It explicitly warns the behavior is shape/hardware dependent. This probe measures the required different case: Apple M1, actual Qwen3-8B 3-bit affine payloads, M5 versus 2+2+1. The local evidence contradicts the proposed speedup.

## Decision

`STRETCH_032_ROW_CHUNKED_FEASIBILITY_NO_GO`.

Correctness is diagnostically acceptable, but performance is uniformly worse and the conservative MLP-only estimate fails the `>=5%` upside gate in the wrong direction. Therefore:

- do **not** create a Stretch 032 preregistration or ABBA;
- do **not** retry this measurement or try `1+1+…` / `3+2`; those are separate factors;
- keep monolithic M5 quantized matmul canonical;
- choose a new, independently preregistered compute factor before any further scientific run.

## Evidence

- Runner: `scripts/stretch_m5_row_chunked_quantized_matmul_032_feasibility.py`
- Parent summary: `results-local/stretch/m5-row-chunked-quantized-matmul-032-feasibility/20260820-185103/summary.json`
- Child evidence: `results-local/stretch/m5-row-chunked-quantized-matmul-032-feasibility/20260820-185103/child-summary.json`
