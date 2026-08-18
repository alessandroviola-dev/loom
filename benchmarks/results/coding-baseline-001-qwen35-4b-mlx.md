# Coding Baseline 001 — Qwen 3.5 4B MLX

Date: 2026-08-18
Status: **QUALITY + RUN SUMMARY INGESTED; RAW FAILED OUTPUTS PENDING**

## Configuration

- Benchmark: LOOM Coding Benchmark 01
- Original run benchmark version: 1.0.0
- Corrected scorer version: 1.0.1
- Model: `qwen3.5:4b-mlx`
- Runtime: Ollama
- Backend: MLX
- Mode: `single_shot`
- Context: 4096
- Reference hardware: Apple M1 / 8 GB unified memory
- Local run id: `20260818-203156`

## Score interpretation

The original v1.0.0 runner reported **39.82 / 100**, but that value is invalid because the original scorer over-counted failing subtests.

The exact same generated working tree was deterministically rescored with the corrected v1.0.1 scorer:

- **Artifact score: 40.71 / 100**
- **Delivery-adjusted strict single-shot score: 30.00 / 100**

The artifact score measures whatever files were present in the isolated working tree after the run. It is not the correct end-to-end score when an adapter/output-format failure leaves starter files untouched.

The delivery-adjusted score is the primary strict single-shot quality metric: a task contributes points only if the model output was successfully parsed and written by the adapter. Under the original run, T04, T05 and T06 all failed JSON parsing and therefore count as zero for strict delivery.

## Corrected per-task quality

| Task | Skill | Artifact score | Tests | Adapter | Strict delivered score |
|---|---|---:|---:|---|---:|
| T01 | generation | 15.00 / 15 | 6 / 6 | written | 15.00 |
| T02 | debugging | 6.43 / 15 | 3 / 7 | written | 6.43 |
| T03 | comprehension | 8.57 / 15 | 4 / 7 | written | 8.57 |
| T04 | refactoring | 8.57 / 15 | 4 / 7 | **failed JSON parse** | 0.00 |
| T05 | multi-file reasoning | 0.00 / 25 | 0 / 7 | **failed JSON parse** | 0.00 |
| T06 | instruction following | 2.14 / 15 | 1 / 7 | **failed JSON parse** | 0.00 |
| **Total** |  | **40.71 / 100** |  | 3/6 written | **30.00 / 100** |

## Adapter failure classification

The run summary resolves the previous ambiguity:

- **T01:** `written`.
- **T02:** `written`.
- **T03:** `written`.
- **T04:** `failed` — `JSONDecodeError: Invalid control character at line 1 column 340`.
- **T05:** `failed` — `JSONDecodeError: Expecting ',' delimiter at line 1 column 584`.
- **T06:** `failed` — `JSONDecodeError: Expecting ',' delimiter at line 1 column 1493`.

Therefore T04–T06 are end-to-end instruction/output-format failures. Their starter files remained in the working tree; any tests passed by those starter files cannot be credited to Qwen in strict single-shot mode.

The raw Ollama API files for T04–T06 are still required to determine whether the underlying code content was otherwise useful and merely escaped/serialized incorrectly, or whether the generated code itself was also wrong.

## Successful-task inference performance

The original adapter recorded complete Ollama metrics for T01–T03 before the old telemetry path failed to retain metrics for JSON-parse failures.

| Task | Prompt tokens | Prompt tok/s | Output tokens | Generation tok/s | API wall time |
|---|---:|---:|---:|---:|---:|
| T01 | 301 | 151.511 | 98 | 16.549 | 12.613 s |
| T02 | 406 | 165.932 | 118 | 15.917 | 9.976 s |
| T03 | 390 | 222.342 | 50 | 15.724 | 5.056 s |

Weighted across the three fully recorded successful tasks:

- prompt tokens: 1,097;
- weighted prompt throughput: **177.29 tok/s**;
- output tokens: 266;
- weighted generation throughput: **16.11 tok/s**.

This strongly suggests the earlier isolated **4.36 prompt tok/s** result was not representative of normal prompt processing for this model/runtime configuration.

The full benchmark process lasted approximately **91.25 s** from run start to finish. T04–T06 elapsed approximately 19.61 s, 13.54 s and 24.76 s respectively, but their per-token Ollama metrics are absent from the old run summary because the original adapter stored metrics only after successful JSON extraction.

## Memory / swap behavior

Before the run, with no model reported by `ollama ps`:

- PhysMem: 7551 MB used;
- compressed: 1027 MB;
- unused: 79 MB;
- swap used: **885.69 MB**;
- memory-pressure free percentage: 61%.

After T01:

- Ollama model resident: 4.1 GB, 100% GPU;
- swap used: **1983.31 MB**;
- memory-pressure free percentage: 17%.

During subsequent tasks the resident size reported by Ollama increased:

- T02: 4.2 GB;
- T03: 4.4 GB;
- T04: 4.5 GB;
- T05: 4.7 GB;
- T06/final: 4.8 GB.

Peak observed swap usage was **2486.94 MB** after T05. Final swap usage was **2403.44 MB**, an increase of about **1517.75 MB** versus the beginning of the run.

Interpretation: Qwen 3.5 4B MLX is computationally responsive on the M1/8 GB, but sustained multi-task execution creates meaningful memory pressure and swap activity. The increasing Ollama resident-size report across tasks should be investigated in later controlled memory experiments rather than assumed to be model-weight growth.

## Quality observations

- **T01 generation:** complete success.
- **T02 debugging:** partial; rolling-window update logic remained wrong and boolean `True` was not rejected as an invalid size.
- **T03 comprehension:** partial; strategy recognition succeeded but mutation semantics, unassigned sentinel and the requested complexity representation were wrong.
- **T04:** cannot be scored as model code quality from the working tree because delivery failed before the generated file was written.
- **T05:** same; strict score is zero due failed delivery.
- **T06:** same; strict score is zero due failed delivery.

## Adapter defects discovered from this run

Two instrumentation/scoring issues were found and patched after the first run:

1. **v1.0.0 scorer subtest-counting defect** — patched in benchmark v1.0.1.
2. **Adapter telemetry/delivery accounting defect** — the old adapter:
   - recorded task metrics only after successful JSON parsing;
   - allowed untouched starter files to receive artifact points after adapter failure;
   - hard-coded benchmark version 1.0.0;
   - provided no per-task progress output.

The adapter is now hardened to:

- save metrics before output parsing;
- preserve raw API responses;
- report `artifact_score` separately from `delivery_adjusted_score`;
- count failed delivery tasks as zero in the strict end-to-end score;
- load benchmark version from the manifest;
- print task progress.

## Remaining ingestion

To fully close Coding Baseline 001, inspect the preserved raw Ollama responses:

- `raw/T04-api.json`
- `raw/T05-api.json`
- `raw/T06-api.json`

This will determine whether malformed JSON was merely a transport/escaping failure or accompanied by incorrect generated code.

After that analysis, freeze Coding Baseline 001 and proceed to agentic-mode design.