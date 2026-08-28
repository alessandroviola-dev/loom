# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Output Validator v0 remains GO. Validator-Guided Selective Rescue 001 was scientific NO_GO at 5/8 CORRECT. The next cheap guided-repair experiment became MECHANICAL_NO_GO because hidden expected-payload/spec metadata leaked into repair input. A separate pre-guided false acceptance on `V_VERIFY_RULE` also surfaced. Current checkpoint hardens only `V_VERIFY_RULE` with model-free adversarial fixtures before any guided-repair rerun.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_VERIFY_RULE_VALIDATOR_HARDENING_001`
Pi context: `/AGENTS.md` v3.64.

## Product direction

- 8B BALANCED — provisional primary tier;
- 30B DEEP — expensive selective tier;
- FAST — concept retained, legacy 4B parked;
- LOOM AUTO — validator-first: validated acceptance, cheap repair when independently proven, DEEP only after cheaper verified paths fail.

Open-ended semantic verification and automatic validator selection remain separate unresolved tracks. LOOM Heretic remains fundamental/non-optional after initial runtime/capability optimization.

## Key evidence

### Output Validator v0 — GO
- zero false PASS on its preregistered set;
- open-ended UNCERTAIN abstention correct;
- sub-ms overhead.

### Selective Rescue 001 — NO_GO
- RAW8 2/8 CORRECT -> final 5/8;
- zero false accepts;
- fence repair 2/2;
- DEEP calls 4/8, avoided 4/8;
- only one DEEP call repaired a residual failure;
- failed only final >=6/8 gate.

### 8B Validator-Guided Repair 001 — MECHANICAL_NO_GO
Result: `research/architecture/loom-8b-validator-guided-repair-001-result.md`
Evidence: `results-local/research/8b-validator-guided-repair-001/20260828T204632Z/`

The harness passed validator spec metadata containing hidden expected-payload information into guided-repair feedback. Therefore guided-repair outputs and aggregates are invalid scientific evidence. No rerun was performed.

Independent diagnostic: T08 was accepted by `V_VERIFY_RULE` while the frozen scorer marked it PARTIAL, and that acceptance happened before guided repair. Therefore leakage does not explain it. Do not merely sanitize feedback and rerun the exposed suite.

## Exact next action — VERIFY_RULE Validator Hardening 001

Preregistration:
`research/architecture/loom-verify-rule-validator-hardening-001-preregistration.md`

Create only:
`scripts/loom_verify_rule_validator_hardening_001.py`

No model inference.

Run exactly 24 fresh model-free fixtures: 8 expected PASS and 16 adversarial expected FAIL across cheap-first, named checks, accept polarity, escalation polarity, forbidden heuristics and contradiction cases.

GO requires:
- 24/24 valid records;
- false PASS 0/16;
- PASS recall >=7/8;
- contradiction rejection 2/2;
- forbidden-heuristic rejection 2/2;
- p95 <5 ms;
- standard library only, zero network/package/model mutation.

If GO, next checkpoint will be a fresh guided-repair suite with sanitized allowlisted failure reports. Do not reuse the exposed T01–T08 tasks or any hidden validator-spec payload.
