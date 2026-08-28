# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Output Validator v0 completed GO. Deterministic post-generation validation produced zero false PASS on mechanically verifiable tasks and abstained on open-ended tasks. Current checkpoint is validator-guided selective rescue with safe fence-only repair and 30B escalation only on residual FAIL.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_VALIDATOR_GUIDED_SELECTIVE_RESCUE_001`
Pi context: `/AGENTS.md` v3.62.

## Product architecture direction

- 8B BALANCED — provisional default/primary tier;
- 30B DEEP — selective escalation where measured gain justifies latency;
- FAST — concept retained, legacy 4B parked;
- LOOM AUTO direction — validator-first for mechanically verifiable tasks: `8B -> validate -> safe deterministic repair -> selective 30B -> revalidate`.

Open-ended semantic uncertainty is not solved by validator v0 and remains a separate future verifier track.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Runtime evidence

8B BALANCED remains Qwen3-8B 3-bit/group64 Direct MLX, roughly 13 tok/s real generation.
30B DEEP remains roughly 1.4 tok/s on compact tasks with about 50 s median TTFT.
Historical 8B 4-bit continuous profile remains closed by resource evidence; legacy 4B FAST remains parked.

## Relevant prior capability evidence

Selector-first/static protocol dispatch is not the production direction:
- selector isolated GO 15/15;
- end-to-end FIX1 selector 7/9, NORMAL false activation 1/3;
- AUTO8 utility improved 6 -> 8 but only 2/9 fully CORRECT.

Do not tune on exposed selector/dispatch prompts.

## Output Validator v0 — GO

Result:
`research/architecture/loom-8b-output-validator-v0-001-result.md`
Evidence:
`results-local/research/8b-output-validator-v0-001/20260828T174056Z/`
Classification: `LOOM_8B_OUTPUT_VALIDATOR_V0_GO`.

Observed:
- synthetic fixtures 11/11 PASS;
- 12/12 valid records;
- PASS/FAIL/UNCERTAIN = 3/6/3;
- T01–T09 C/P/I = 3/3/3;
- false PASS = 0;
- open-ended T10–T12 UNCERTAIN = 3/3;
- validator p50/p95 = 0.066355/0.758321 ms;
- median TTFT = 1.499425 s;
- pooled generation = 12.986417 tok/s;
- total 8B E2E wall = 63.297052 s.

Supported conclusion: benchmark-supplied deterministic validators can safely accept or reject the tested contract classes and abstain rather than invent semantic confidence. This does not yet solve automatic validator selection or open-ended semantic verification.

## Exact next action — Validator-Guided Selective Rescue 001

Preregistration:
`research/architecture/loom-validator-guided-selective-rescue-001-preregistration.md`.

Create only:
`scripts/loom_validator_guided_selective_rescue_001.py`.

Run eight fresh mechanically verifiable tasks.

Per task:
1. canonical RAW8 once;
2. frozen validator;
3. if PASS: accept and never call 30B;
4. if FAIL and the only defect is one outer Markdown fence: remove that fence only, preserving interior bytes, and revalidate;
5. if still FAIL/ineligible: call canonical 30B DEEP once on the original prompt;
6. revalidate DEEP output;
7. unresolved FAIL remains unresolved; no retries.

Frozen GO:
- valid evidence for all required model calls;
- zero false acceptance;
- repair limited to exact fence-only transformation;
- final CORRECT >=6/8 and >=RAW8 +2;
- at least 2/8 DEEP calls avoided;
- no DEEP call after accepted 8B/repaired output;
- validator/repair p95 <5 ms;
- no model/runtime/package/network mutation.

Open-ended UNCERTAIN tasks are explicitly excluded here. They need separate semantic-verifier research after this bounded rescue checkpoint.
