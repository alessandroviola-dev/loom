# LOOM Roadmap

Last updated: 2026-08-28
Current: 8B Validator-Guided Repair 001 is MECHANICAL_NO_GO because hidden expected-payload/spec metadata leaked into repair feedback. A separate pre-guided `V_VERIFY_RULE` false acceptance was also observed. Immediate next: model-free hardening of `V_VERIFY_RULE` on fresh adversarial fixtures before any guided-repair rerun.
Canonical context: `/AGENTS.md` v3.64.

## 1. Product direction — validator-first LOOM AUTO

Near-term tiers:
- `loom-balanced` -> Qwen3-8B 3-bit, provisional primary;
- `loom-deep` -> expensive selective 30B;
- future `loom-fast` -> clean-runtime reintroduction later;
- `loom-auto` -> generate with 8B, validate, apply only proven cheap repairs, then DEEP only when cheaper verified paths fail.

Do not freeze general DEEP thresholds yet. Generic confidence is not validation.

## 2. Core evidence

Output Validator v0: GO, zero false PASS on its preregistered set, correct UNCERTAIN abstention, sub-ms overhead.

Validator-Guided Selective Rescue 001: NO_GO; RAW8 2/8 -> final 5/8 CORRECT, zero false accepts, 4/8 DEEP calls avoided, but final gate required >=6/8. One-shot DEEP repaired only one of four residual failures.

8B Validator-Guided Repair 001: MECHANICAL_NO_GO; guided feedback leaked hidden validator-spec/expected-payload information. Guided-repair performance from that run is invalid and must not be reused.

A `V_VERIFY_RULE` false acceptance occurred before guided repair in that run. This means feedback sanitization alone is insufficient as the immediate next step.

## 3. Current — VERIFY_RULE Validator Hardening 001

Preregistration:
`research/architecture/loom-verify-rule-validator-hardening-001-preregistration.md`

No model inference.

Exactly 24 fresh deterministic/adversarial fixtures test:
- cheap-first requirement;
- named check coverage;
- accept polarity;
- escalation polarity;
- forbidden-heuristic rejection;
- contradiction rejection.

GO requires zero false PASS on 16 expected FAIL fixtures, >=7/8 PASS recall, 2/2 contradiction rejection, 2/2 forbidden-heuristic rejection, p95 <5 ms and no external dependencies/network/model changes.

## 4. Next if validator hardening GO

Preregister a completely fresh 8B guided-repair suite.

Repair feedback must use an allowlisted schema containing only public/check-derived fields such as check ID, failure code, component/field name and observed condition. It must never serialize validator spec objects, hidden expected payloads, scorer labels or ground-truth answers.

Use fresh prompts, not the exposed guided-repair T01–T08 set.

## 5. Later selective DEEP

Only after cheap guided repair is independently validated, test:
`8B -> validator -> safe repair -> guided 8B repair -> residual FAIL -> DEEP -> revalidate`.

Measure final correctness, false accepts, DEEP call rate, DEEP repair yield and waiting cost.

## 6. Semantic verifier / automatic validator selection

Separate future research:
- semantic/open-ended verifier;
- task-specific tests/tools;
- retrieval-grounded verification where factual;
- automatic validator/contract derivation from user request on fresh data.

## 7. Other tracks

- LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.
- Historical 8B 4-bit branch remains closed by resource evidence.
- Legacy 4B FAST remains parked.
- Provider/UI follows validated execution graph.
- Qwen3.8 and new 30B speed R&D remain separate and must not block validator-first progress.
