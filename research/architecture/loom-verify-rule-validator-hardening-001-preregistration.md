# LOOM VERIFY_RULE Validator Hardening 001 — Preregistration

Date: 2026-08-28
Status: PREREGISTERED

## Purpose

Model-free hardening of `V_VERIFY_RULE` after one false acceptance was observed before guided repair. Do not tune on exposed model outputs.

Create only:
`scripts/loom_verify_rule_validator_hardening_001.py`

No model inference, network, external packages, or changes to JSON/CSV/KV validators.

## Frozen rule

PASS only if every required component is positively satisfied and no contradiction exists.

Check families:
- cheap/fast method explicitly first when required;
- every named verification family present;
- accept/use-fast only when required checks pass;
- escalate only when checks fail or material uncertainty remains;
- any forbidden decision heuristic must be absent;
- contradiction guard: accepting on failed checks or reversing escalation polarity forces FAIL.

Missing evidence means FAIL. No fuzzy semantic PASS.

## Fresh fixture set

Exactly 24 deterministic fixtures defined in the new harness, never shown to a model:
- 8 expected PASS;
- 16 expected FAIL:
  - 3 missing cheap-first;
  - 3 missing a required check family;
  - 3 wrong/missing accept polarity;
  - 3 wrong/missing escalation polarity;
  - 2 forbidden-heuristic cases;
  - 2 contradiction cases.

Cover three generic families: SQL syntax/schema, code tests/type-check, extraction required-fields/types/totals. Do not copy exposed T01–T08 model outputs.

Persist evidence under:
`results-local/research/verify-rule-validator-hardening-001/<timestamp>/`

Record expected/predicted result, check booleans, matched cues, contradiction flags and wall time. Aggregate confusion matrix, PASS precision/recall/F1, false PASS/FAIL, p50/p95.

## Frozen GO gate

GO only if:
1. 24/24 records valid;
2. false PASS = 0/16;
3. PASS recall >=7/8;
4. contradiction cases rejected 2/2;
5. forbidden-heuristic cases rejected 2/2;
6. p95 <5 ms;
7. standard library only; zero network/package/model mutation.

Classifications:
- `LOOM_VERIFY_RULE_VALIDATOR_HARDENING_GO`
- `LOOM_VERIFY_RULE_VALIDATOR_HARDENING_NO_GO`
- `LOOM_VERIFY_RULE_VALIDATOR_HARDENING_MECHANICAL_NO_GO`

If GO, the next guided-repair experiment must use fresh tasks and a sanitized allowlisted failure-report schema. No validator-spec object, hidden expected payload, scorer label or ground-truth answer may be serialized into repair input.
