# LOOM — Direct MLX Coding Benchmark 001 Result

Date: 2026-08-19
Run: `20260819-125647`
Status: **COMPLETE — QUALITY DIAGNOSTIC REQUIRED BEFORE PI**

## Frozen condition

- model `mlx-community/Qwen3-8B-3bit`
- verified local artifact, 3-bit / group size 64
- isolated `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- Direct MLX / `stream_generate`
- one loaded model process for T01–T06
- Qwen3 `enable_thinking=False`
- `max_kv_size=4096`
- unquantized KV
- max 2048 generated tokens per task
- exact frozen Coding Benchmark 01 v1.0.1 prompts
- exact frozen adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- exact frozen scorer blob `754e9a6506968d2b191bff57997710591efe8133`
- one attempt per task; no retry, salvage, repair, test feedback or manual intervention
- safety abort: free memory <5% OR swap >5600 MB

## Preflight

- disk free before: 40.638 GiB
- version lock: PASS
- model SHA256: PASS
- frozen adapter/scorer blobs: PASS
- frozen benchmark v1.0.1 / 6 tasks: PASS
- frozen prompts T01–T06: PASS
- safety preflight: free 75%, swap 1339.00 MB

## Runtime / safety

All six tasks ran sequentially in one loaded Direct MLX process.

Observed:
- peak sampled process RSS: 594.546875 MB
- peak observed swap: **1683.38 MB**
- minimum observed free memory: **14%**
- disk free after: 40.637 GiB
- classification: **COMPLETE**

This establishes full-session workload stability for this exact Direct MLX profile under the frozen LOOM safety thresholds. Parent/child RSS remains diagnostic only; system-wide free memory and swap are the safety signals.

## Per-task generation / delivery

| Task | Delivery | Prompt tokens | Generation tokens | Generation t/s |
|---|---:|---:|---:|---:|
| T01 | written | 276 | 86 | 16.228876984424666 |
| T02 | written | 374 | 125 | 16.440325850547953 |
| T03 | failed | 359 | 117 | 16.483912055630125 |
| T04 | failed | 486 | 237 | 16.257104019718145 |
| T05 | failed | 501 | 244 | 16.231839856178276 |
| T06 | failed | 331 | 255 | 16.391045126757284 |

Structured delivery: **2/6**.

## Frozen quality result

- artifact score: **38.57/100**
- delivery-adjusted score: **27.86/100**
- structured delivery: **2/6**
- classification: **COMPLETE**

Primary preregistered quality metric: delivery-adjusted score.

## Canonical interpretation

> Direct MLX solves the resource problem for the Qwen3 8B/3-bit profile on the reference M1/8 GB machine: the full six-task coding session completed with 14% minimum free memory and 1683.38 MB peak swap. However, the first full quality result is not yet evidence of a clear practical upgrade: delivery-adjusted quality is 27.86/100 and only 2/6 tasks satisfied the frozen structured-delivery contract.

The run is scientifically valid and complete. Delivery failures are model/profile quality evidence, not runtime failures.

## Comparison boundary

Existing historical 4B/Q2 results can be used descriptively, but runtime/model/quantization conditions differ. Do not claim a causal parameter-count or quantization effect from raw score differences.

Do not authorize Pi integration solely from `COMPLETE`. First inspect T03–T06 raw outputs, frozen adapter errors, and scorer task points to determine whether failures are primarily protocol/delivery or semantic/code-quality failures.

## Required next step

Run a read-only diagnostic over:
`results-local/mlx/coding-benchmark-001/20260819-125647/benchmark-summary.json`

Recover per task:
- adapter error;
- raw output prefix / JSON structure;
- scorer points and tests passed;
- whether artifact points come from untouched fixture/base files when delivery failed.

No model rerun or prompt/parser change is authorized for this diagnostic.