# LOOM Validator-Guided Selective Rescue 001 — Result

Date: 2026-08-28
Status: **COMPLETE / SCIENTIFIC NO_GO**
Classification: **`LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_NO_GO`**

## Frozen gate result

The checkpoint was mechanically valid and passed every frozen safety/efficiency gate except final correctness:
- all required model calls valid: PASS;
- false acceptance: `0`: PASS;
- safe repair restricted to frozen outer-fence removal: PASS;
- final CORRECT `5/8` vs required `>=6/8`: **FAIL**;
- improvement vs RAW8: `5/8` vs `2/8`, `+3`: PASS;
- 30B calls avoided: `4/8`: PASS;
- no unnecessary 30B after PASS/successful repair: PASS;
- validator/repair p95 <5 ms: PASS;
- zero forbidden mutation/network activity: PASS.

Evidence:
`results-local/research/validator-guided-selective-rescue-001/20260828T175816Z/`

Harness SHA after scoring reconciliation:
`9e6e14490be233c905b790b63a13da912ef0e88e9b1449c77b2b564287ca6073`

## Observed task outcomes

| Task | RAW8 | First validation / repair | DEEP | Final source | Final quality |
|---|---|---|---|---|---|
| T01 | INCORRECT | FAIL -> fence repair PASS | no | SAFE_REPAIR | CORRECT |
| T02 | INCORRECT | FAIL / repair ineligible | PASS | 30B_PASS | CORRECT |
| T03 | CORRECT | PASS | no | 8B_PASS | CORRECT |
| T04 | PARTIAL | FAIL / repair ineligible | FAIL | UNRESOLVED | INCORRECT |
| T05 | INCORRECT | FAIL -> fence repair PASS | no | SAFE_REPAIR | CORRECT |
| T06 | CORRECT | PASS | no | 8B_PASS | CORRECT |
| T07 | PARTIAL | FAIL / repair ineligible | FAIL | UNRESOLVED | INCORRECT |
| T08 | PARTIAL | FAIL / repair ineligible | FAIL | UNRESOLVED | INCORRECT |

RAW8 C/P/I: `2/3/3`.
Final C/P/I: `5/0/3`.
Safe repair attempts/successes: `2/2`.
30B calls: `4/8`; avoided: `4/8`.

## Runtime / cost

- 8B wall: `38.656 s`;
- added 30B wall: `246.346 s`;
- recovered child-pipeline wall: `337.068 s`;
- time per final-CORRECT: `67.414 s`;
- 8B median TTFT / pooled generation: `1.527 s / 12.546 tok/s`;
- 30B median TTFT / pooled generation: `37.743 s / 1.407 tok/s`;
- validator p50/p95: `0.0678 / 0.1850 ms`;
- repair p50/p95: `0.0005 / 0.0088 ms`;
- peak MLX: `3,829,508,732 B`;
- peak swap: `2820 MB`.

## Supported interpretation

The validator-first architecture remains supported because every accepted result was ground-truth correct and half of the DEEP calls were avoided. Fence-only repair is useful and extremely cheap.

However, raw one-shot 30B escalation repaired only one of four residual failures. T04 still violated the exact boolean contract (`enabled=no` instead of required `enabled=false`), while T07/T08 remained incomplete relative to the frozen verification-rule components. Therefore the frozen end-to-end gate is not met.

Do not relax the `6/8` gate or rescore exposed tasks. Do not treat a larger model as sufficient repair by itself.

## Next scientific question

Test one new factor before DEEP: a single **validator-guided 8B repair** on fresh mechanically verifiable tasks. The repair receives the original request, failed answer, and deterministic validator failure report, then is revalidated. No 30B inference in that checkpoint. This isolates whether observable failure information can cheaply repair the 8B before escalation.
