# LOOM 8B Output Validator v0 001 — Result

Date: 2026-08-28
Classification: **LOOM_8B_OUTPUT_VALIDATOR_V0_GO**

## Frozen provenance

- model `mlx-community/Qwen3-8B-3bit@619ded3`
- weight SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit/group64
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3; transformers 5.12.1
- Apple M1 built-in `qmv_fast`, BF16 KV, greedy, thinking OFF
- exact RAW8 baseline system message
- harness `scripts/loom_8b_output_validator_v0_001.py`
- harness SHA256 `c67aed70998ee2cac23827e486b0cdfeaf3b8c1264bd84a84e4c24e8443fdc25`
- evidence `results-local/research/8b-output-validator-v0-001/20260828T174056Z/`

## Preflight

Synthetic validator fixtures: **11/11 PASS** before model load. `V_UNVERIFIABLE` correctly returned `UNCERTAIN`.

## Task results

| Task | Validator | Decision | Quality |
|---|---|---|---|
| T01 | V_JSON_OBJECT | PASS | CORRECT |
| T02 | V_CSV | PASS | CORRECT |
| T03 | V_JSON_ARRAY | FAIL | INCORRECT |
| T04 | V_KV | FAIL | INCORRECT |
| T05 | V_JSON_OBJECT | FAIL | INCORRECT |
| T06 | V_CSV | PASS | CORRECT |
| T07 | V_VERIFY_RULE | FAIL | PARTIAL |
| T08 | V_VERIFY_RULE | FAIL | PARTIAL |
| T09 | V_VERIFY_RULE | FAIL | PARTIAL |
| T10 | V_UNVERIFIABLE | UNCERTAIN | NOT_SCORED_SEMANTICALLY |
| T11 | V_UNVERIFIABLE | UNCERTAIN | NOT_SCORED_SEMANTICALLY |
| T12 | V_UNVERIFIABLE | UNCERTAIN | NOT_SCORED_SEMANTICALLY |

Aggregate validator decisions: PASS/FAIL/UNCERTAIN = `3/6/3`.
T01–T09 model quality: CORRECT/PARTIAL/INCORRECT = `3/3/3`.

## Frozen GO gate

- 12/12 valid inference/evidence records: PASS
- all synthetic fixtures: PASS
- false PASS on mechanically invalid T01–T09 outputs: **0**
- T10–T12 UNCERTAIN: **3/3**
- frozen validator definitions: PASS
- validator p95 <5 ms: PASS
- zero network/package/model/runtime mutation: PASS

## Performance

- median TTFT: `1.499425 s`
- pooled generation: `12.986417 tok/s`
- total E2E wall: `63.297052 s`
- validator p50/p95: `0.066355 / 0.758321 ms`
- peak MLX: `3,814,648,388 B`
- peak swap: `2715.19 MiB`
- periodic cleanups: `57`, cleanup wall `3.487805 s`

## Supported interpretation

Output Validator v0 is a valid fail-closed post-generation mechanism for the frozen benchmark-supplied validator classes. Every observed PASS on T01–T09 corresponded to a CORRECT answer, no invalid answer was falsely accepted, and deliberately open-ended tasks were abstained as UNCERTAIN rather than plausibility-approved.

This does **not** prove general semantic validation or automatic validator selection. Validator kind/spec was supplied by benchmark metadata.

The result authorizes a separate selective-rescue experiment on fresh mechanically verifiable tasks. A cheap deterministic repair may be attempted only for prospectively frozen, semantics-preserving formatting defects; residual FAIL may then selectively invoke 30B DEEP. Open-ended `UNCERTAIN` tasks require a separate semantic-verifier track and are not automatically escalated in the first rescue experiment.
