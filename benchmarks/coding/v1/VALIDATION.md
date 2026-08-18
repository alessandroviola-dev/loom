# Coding Benchmark 01 — Validation Record

Date: 2026-08-18
Current version: 1.0.1
Status: PATCHED — scoring defect corrected; existing first run requires deterministic rescore

## Original v1.0.0 validation

A private local reference implementation was created for each task solely to validate the benchmark fixtures and tests. Reference solutions are intentionally **not committed** to the repository so they cannot leak into future model or agent runs.

The original benchmark suite passed all functional tests:

- Overall reference score: **100 / 100**
- Top-level unittest methods: **41 / 41 passed**

Per task:

| Task | Top-level tests | Reference score |
|---|---:|---:|
| T01 — generation | 6 / 6 | 15 / 15 |
| T02 — debugging | 7 / 7 | 15 / 15 |
| T03 — comprehension | 7 / 7 | 15 / 15 |
| T04 — refactoring | 7 / 7 | 15 / 15 |
| T05 — multi-file reasoning | 7 / 7 | 25 / 25 |
| T06 — instruction constraints | 7 / 7 | 15 / 15 |

## Critical scoring defect discovered after first real model run

The v1.0.0 runner inferred test totals by regex-parsing verbose `unittest` output. Failing `subTest` cases can emit additional result lines even though `unittest` still counts the enclosing test method only once.

Consequence: the denominator could grow when subtests failed. In the first real Qwen run, for example, T05 and T06 were reported as 11 and 12 tests even though `unittest` reported `Ran 7 tests` for each task. This made the score outcome-dependent and therefore invalid as a reproducible metric.

The first reported **39.82 / 100** score is retained as an historical raw result but is **not an official LOOM baseline score**.

## v1.0.1 patch

The runner now discovers and executes each top-level `unittest.TestCase` method independently. A top-level test counts exactly once and is considered failed if any assertion, error, unexpected success, or subtest failure occurs inside it.

This guarantees:

- stable denominator independent of failures;
- exactly 6 top-level tests for T01;
- exactly 7 top-level tests for each T02–T06;
- exactly 41 top-level tests overall;
- no prompt, fixture, expected behavior, task weight, or test semantics changed.

The benchmark manifest patch version was incremented from `1.0.0` to `1.0.1` because only the scoring implementation changed.

A rescoring utility exists at `scripts/rescore_coding_run.py` so existing model outputs can be rescored without generating new answers.

## Freeze rule

The task prompts, fixtures, tests, weights and semantics remain frozen. Critical benchmark defects may be patched in place only when documented here and accompanied by a patch-version increment. Any semantic benchmark change requires a new benchmark version.
