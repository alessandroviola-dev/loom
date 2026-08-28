# LOOM — Pi Agent Protocol

Version: 3.64
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not commit/push/PR/edit project decision docs unless explicitly authorized.
GitHub is canonical. Active clone: `<repository-root>`.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. fail closed before expensive execution;
4. invalid/inconclusive runs support no performance claim;
5. production code requires exact review + Git persistence;
6. do not tune on exposed evaluation examples;
7. hidden ground truth/spec metadata must never enter model repair/judge inputs unless explicitly preregistered as public input.

## Product direction

**Big models. Small machines.**
- BALANCED: Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s, provisional primary tier.
- DEEP: canonical 30B, ~1.4 tok/s compact generation, selective expensive tier.
- FAST: concept retained; legacy 4B parked.
- LOOM AUTO direction: validator-first; accept only validated results, use cheap semantics-preserving/guided repair when independently validated, DEEP only after cheap paths fail.

LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Key evidence

### Output Validator v0 — GO
`research/architecture/loom-8b-output-validator-v0-001-result.md`
- zero false PASS on its preregistered mechanically-verifiable set;
- open-ended tasks abstained UNCERTAIN;
- validator p95 <1 ms.

### Validator-Guided Selective Rescue 001 — scientific NO_GO
`research/architecture/loom-validator-guided-selective-rescue-001-result.md`
- RAW8 2/8 CORRECT -> final 5/8;
- zero false accepts;
- safe fence repair 2/2;
- DEEP called 4/8, avoided 4/8;
- only one DEEP call repaired a residual failure;
- missed frozen final >=6/8 gate.

### 8B Validator-Guided Repair 001 — MECHANICAL NO_GO
Result: `research/architecture/loom-8b-validator-guided-repair-001-result.md`
Evidence: `results-local/research/8b-validator-guided-repair-001/20260828T204632Z/`
Classification: **`LOOM_8B_VALIDATOR_GUIDED_REPAIR_MECHANICAL_NO_GO`**.

Cause: guided-repair input serialized validator spec metadata containing hidden expected-payload information. This violates the no-hidden-ground-truth boundary. Guided repair outputs/aggregates are scientifically invalid; do not reuse or rescore them.

Independent diagnostic observed before guided repair: one `V_VERIFY_RULE` output (T08) was validator PASS but ground-truth PARTIAL. Leakage cannot explain that pre-guided false acceptance. Therefore do not immediately rerun guided repair with only sanitized feedback.

## Current checkpoint — VERIFY_RULE Validator Hardening 001

Preregistration:
`research/architecture/loom-verify-rule-validator-hardening-001-preregistration.md`.

Model-free checkpoint. Create only:
`scripts/loom_verify_rule_validator_hardening_001.py`.

Exactly 24 fresh deterministic/adversarial fixtures:
- 8 expected PASS;
- 16 expected FAIL covering missing cheap-first, missing checks, wrong accept/escalation polarity, forbidden heuristic, and contradictions.

PASS requires all required components positively satisfied and no contradiction. Missing evidence -> FAIL. No fuzzy semantic PASS.

Frozen GO:
- 24/24 valid;
- false PASS 0/16;
- PASS recall >=7/8;
- contradiction reject 2/2;
- forbidden-heuristic reject 2/2;
- p95 <5 ms;
- standard library only, no model/network/package mutation.

No model inference, no guided-repair rerun, no JSON/CSV/KV validator changes, no 30B.

If GO: preregister a fresh guided-repair suite using hardened VERIFY_RULE and a sanitized allowlisted failure report. The repair report may include only public/check-derived fields; never validator spec objects, hidden expected payloads, scorer labels or ground-truth answers.
