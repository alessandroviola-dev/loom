# CAPABILITY 001 — pre-run frozen-suite audit result

Date: 2026-08-21
Classification: `CAPABILITY_001_INFRASTRUCTURE_INCOMPLETE`
Issue: `FROZEN_TASK_COUNT_MISMATCH`

## Result

The mandatory pre-science audit found that the frozen CAPABILITY 001 specification declares 12 tasks but defines only 11 authoritative task identities:

- C01, C02, C03, C04, C05, C06;
- G01, G02, G03;
- E01, E02.

Count: **11 = 6 coding + 3 Git + 2 experimental-reasoning tasks**.

No model task was run, so this result contains no model-quality evidence and consumes no scientific task attempt.

## Sources inspected locally

- `research/capability/capability-001-frozen-spec.md`
- `research/capability/capability-001-context-amendment.md`
- `research/capability/capability-001-runtime-admission.md`
- `benchmarks/coding/v1/manifest.json`
- `benchmarks/coding/v1/README.md`
- `benchmarks/coding/v1/VALIDATION.md`

No twelfth task was found.

## Local evidence

`results-local/capability/capability-001/capability-001-audit-20260821-205727/`

Created locally:

- `frozen-suite-audit.json`
- `summary.json`

No canonical source file was modified by the audit.

## Resolution

The clerical count mismatch is corrected by:

`research/capability/capability-001-task-count-amendment.md`

The amendment freezes the canonical baseline at **11 tasks** while leaving every task identity, prompt, fixture, scorer, runtime setting and safety rule unchanged.