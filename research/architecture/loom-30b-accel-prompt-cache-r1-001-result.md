# LOOM 30B Acceleration Prompt Cache R1 001 — Result

Date: 2026-08-30
Classification: **`LOOM_30B_ACCEL_PROMPT_CACHE_R1_MECHANICAL_NO_GO`**

## Summary

R1 stopped before inference exactly as required by its fail-closed wrapper-provenance rule.

The previously frozen Prompt Cache 001 wrapper was found and its recorded SHA256 matched the observed SHA256, but the wrapper itself hard-codes the two mechanical conditions that R1 was preregistered to change. Therefore the R1 contract is internally unexecutable while also requiring that wrapper to remain unchanged.

No inference or scientific measurement occurred. This result carries no new performance evidence and does not change the diagnostic-only status of Prompt Cache 001.

## Evidence

Evidence root:
`results-local/research/30b-accel-prompt-cache-r1-001/20260830T105237Z/`

Mechanical blocker artifact:
`results-local/research/30b-accel-prompt-cache-r1-001/20260830T105237Z/mechanical-blocker.json`

## Frozen wrapper verification

Path:
`results-local/research/30b-accel-prompt-cache-001/20260830T120000Z/prompt_cache_runner.py`

Recorded SHA256 = observed SHA256:
`1c62f4ab53e0c31bf3c725991d1f87a3f81cd75ab91d6da2e1b05bf8a499ba5e`

Wrapper provenance therefore passed.

## Mechanical incompatibility

The verified unchanged wrapper:
- hard-codes `-n 8`, while R1 requires `-n 24`;
- hard-codes exact-string validation, while R1 requires the frozen semantic validator;
- hard-codes Prompt Cache 001 classification/evidence handling.

R1 simultaneously required reuse of that wrapper unchanged and prohibited creating a replacement wrapper during R1.

Using the wrapper unchanged would violate the R1 recovery contract. Editing or replacing it would violate the R1 wrapper-freeze rule. Therefore execution correctly stopped before opening the model.

## Mutation / execution status

No:
- model inference;
- model/source/runtime mutation;
- build/rebuild;
- package action;
- Git action by Pi.

## Interpretation

This is a preregistration/harness compatibility defect, not a cache or model result.

Prompt Cache 001 remains `MECHANICAL_NO_GO` with strong diagnostic-only cache evidence. R1 adds no acceleration evidence.

## Exact next step

Preregister R2 with the same scientific experiment and gates, but explicitly authorize a one-time research-wrapper derivation before inference:
1. begin from the verified Prompt Cache 001 wrapper SHA256 above;
2. create a separate R2 wrapper without modifying the frozen parent;
3. permit only the R1 mechanical deltas plus R2 evidence/experiment identifiers;
4. synthetic-test the new wrapper without opening the GGUF;
5. freeze and record the new wrapper SHA256 before the first model invocation;
6. forbid any wrapper edit after inference begins.

No scientific threshold or prompt change is justified by this mechanical failure.
