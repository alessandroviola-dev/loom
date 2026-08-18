# Coding Baseline 001 — Qwen 3.5 4B MLX

Date: 2026-08-18
Status: **QUALITY RESCORED — FULL INGESTION PENDING**

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

## Corrected quality score

The exact first-run outputs were rescored with Benchmark 01 v1.0.1 without calling Ollama again.

**Corrected score: 40.71 / 100**

| Task | Skill | Points | Tests passed |
|---|---|---:|---:|
| T01 | generation | 15.00 / 15 | 6 / 6 |
| T02 | debugging | 6.43 / 15 | 3 / 7 |
| T03 | comprehension | 8.57 / 15 | 4 / 7 |
| T04 | refactoring | 8.57 / 15 | 4 / 7 |
| T05 | multi-file reasoning | 0.00 / 25 | 0 / 7 |
| T06 | instruction following | 2.14 / 15 | 1 / 7 |

The original v1.0.0 score of **39.82 / 100** is preserved only as an auditable historical artifact because its test denominator was affected by failing subtests.

## Quality interpretation

### T01 — generation
Complete success. All six tests passed. This is strong evidence that the 4B model can produce a correct small implementation from a focused specification in strict single-shot mode.

### T02 — debugging
Partial success. Four of seven top-level tests failed. The generated fix retained incorrect rolling-window update behavior for floats, multiple windows and size-one cases, and did not reject boolean `True` as an invalid size.

### T03 — comprehension
Partial success. Four of seven tests passed. The model correctly identified the broad strategy and produced valid structured output, but it misclassified input mutation/state and the unassigned sentinel. It also returned `O(n*m)` even though the prompt explicitly required Big-O notation in terms of `len(capacities)` and `len(jobs)`; therefore this is a legitimate instruction-following miss rather than a scorer defect.

### T04 — constrained refactoring
Partial success. Four of seven tests passed. Functional behavior was partly preserved, but the required `_coerce_score` helper was absent and `summarize` did not use the required helper contract.

### T05 — multi-file reasoning
0/7. The isolated working copy still contains the original `NotImplementedError`, so no functional test passed. This cannot yet be classified as a pure model-reasoning failure because the corrected quality-result file does not contain adapter-status or raw-response information.

### T06 — implementation constraints
1/7. The isolated working copy still contains the original `NotImplementedError` for the implementation. As with T05, adapter-status/raw-response data are required before classifying the failure mechanism.

## Scoring defect history

Benchmark 01 v1.0.0 regex-parsed verbose `unittest` output. Failing `subTest` cases emitted extra result lines and were incorrectly counted as extra tests, making the denominator depend on failure shape.

Observed in the original result:
- T05 was reported as 11 tests although there are 7 top-level tests.
- T06 was reported as 12 tests although there are 7 top-level tests.

Benchmark 01 v1.0.1 fixes only the scoring mechanism. Task prompts, fixtures, tests, expected semantics and weights remain unchanged.

## What is still missing

The uploaded rescored file is a quality-result artifact, not the adapter's original `run-summary.json`. Full baseline ingestion still requires:

- adapter status for T01–T06;
- parse/output-format errors;
- raw Ollama response status;
- prompt token counts and prompt tok/s;
- generation token counts and generation tok/s;
- wall time per task and total run duration;
- memory, compression and swap snapshots.

These data are especially necessary to classify why T05 and T06 remained unimplemented.

## Next action

Ingest the original file:

`<repository-root>/results-local/coding-single-shot/20260818-203156/run-summary.json`

After that ingestion, freeze Coding Baseline 001 as the first official full quality/performance/memory reference for LOOM.
