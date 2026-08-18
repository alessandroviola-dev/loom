# Coding Baseline 001 — Qwen 3.5 4B MLX

Date: 2026-08-18
Status: **PENDING CORRECTED RESCORE**

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

## Original raw result

The v1.0.0 runner reported **39.82 / 100**.

This number is preserved for auditability but is **not an official baseline score** because a scoring defect was discovered during ingestion.

Raw per-task report:

| Task | Skill | Raw points | Runner passed/total |
|---|---|---:|---:|
| T01 | generation | 15.00 / 15 | 6 / 6 |
| T02 | debugging | 6.43 / 15 | 3 / 7 |
| T03 | comprehension | 8.57 / 15 | 4 / 7 |
| T04 | refactoring | 8.57 / 15 | 4 / 7 |
| T05 | multi-file reasoning | 0.00 / 25 | 0 / 11 |
| T06 | instruction following | 1.25 / 15 | 1 / 12 |

## Scoring defect

The v1.0.0 runner regex-parsed verbose `unittest` result lines. Failing `subTest` cases emitted extra result lines and were incorrectly counted as additional tests.

Evidence from the first real run:

- T05 runner field: 11 tests, while `unittest` reported `Ran 7 tests`.
- T06 runner field: 12 tests, while `unittest` reported `Ran 7 tests`.

The denominator therefore depended on how tests failed. This violates reproducibility and invalidates the original aggregate score.

The scorer was patched in Benchmark 01 v1.0.1 so each top-level `unittest.TestCase` method counts exactly once. Prompts, fixtures, tests, expected behavior and task weights were not changed.

## Quality observations before corrected rescore

These observations are independent of the aggregate scoring bug:

- **T01 generation:** complete success, 6/6 top-level tests passed.
- **T02 debugging:** partial success; rolling-window logic remained incorrect for several cases and boolean `True` was not rejected as an invalid window size.
- **T03 comprehension:** partial success; strategy recognition was correct, but input mutation, unassigned sentinel and complexity notation/contract were answered incorrectly under the benchmark's expected schema.
- **T04 refactoring:** functional behavior partly passed, but the required `_coerce_score` helper was missing and `summarize` therefore did not satisfy the required refactoring structure.
- **T05 multi-file reasoning:** generated working tree still contained the original `NotImplementedError`, so no functional tests passed. The quality-result JSON alone cannot determine whether this came from a model failure or an adapter/output-parsing failure.
- **T06 instruction following:** generated working tree still contained the original `NotImplementedError` for most checks. The quality-result JSON alone cannot determine whether this came from a model failure or an adapter/output-parsing failure.

## Missing ingestion data

The uploaded quality-result JSON does not contain the adapter records from `run-summary.json`, so the following remain pending:

- adapter status for T01–T06;
- malformed JSON/output errors;
- raw Ollama responses;
- prompt and generation token counts;
- prompt and generation tok/s;
- wall times;
- memory, compression and swap snapshots.

## Next action

1. Pull the v1.0.1 scoring patch.
2. Rescore the exact existing run with `scripts/rescore_coding_run.py`; do **not** rerun the model.
3. Ingest the corrected score.
4. Ingest the original `run-summary.json` to classify T05/T06 as model-quality vs adapter-format failures and add speed/memory metrics.
5. Only then freeze Coding Baseline 001 as an official result.
