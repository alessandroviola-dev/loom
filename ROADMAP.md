# LOOM Roadmap

Last updated: 2026-08-28
Current: Output Validator v0 remains GO. Validator-Guided Selective Rescue 001 improved final correctness from RAW8 `2/8` to `5/8` with zero false accepts and avoided DEEP on `4/8`, but missed the frozen `>=6/8` gate. Immediate next: test one cheap validator-guided 8B repair before any further 30B escalation.
Canonical context: `/AGENTS.md` v3.63.

## 1. Product direction — validator-first LOOM AUTO

Near-term tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> expensive selective 30B;
- future `loom-fast` -> clean-runtime reintroduction later;
- `loom-auto` -> 8B generation, deterministic/task-specific validation, semantics-preserving repair, cheap validator-guided repair, then DEEP only when still unresolved.

Do not treat generic model size/confidence as validation. Do not freeze general DEEP thresholds yet.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains core/non-optional after initial runtime/capability optimization. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Runtime/product evidence

- 8B BALANCED remains roughly 13 tok/s and is the latency-efficient base;
- 30B DEEP remains roughly 1.4 tok/s on compact tasks and is expensive;
- historical 8B 4-bit remains closed by resource evidence;
- legacy 4B FAST remains parked.

## 4. Selector/capability evidence

Selector-first/static-protocol dispatch is not the production direction. Branch-level strict-output/verification-first evidence remains useful, but end-to-end selector dispatch failed its scientific gate. Do not tune on exposed selector prompts.

## 5. Output Validator v0 — GO

Result:
`research/architecture/loom-8b-output-validator-v0-001-result.md`.

Key result:
- zero false PASS;
- deterministic verifiable classes safely accepted/rejected;
- open-ended tasks abstained UNCERTAIN;
- sub-ms validator overhead.

This establishes the safety primitive used by later rescue stages when validator kind/spec is known.

## 6. Validator-Guided Selective Rescue 001 — NO_GO

Result:
`research/architecture/loom-validator-guided-selective-rescue-001-result.md`.

Observed:
- RAW8 `2/8` CORRECT;
- final `5/8` CORRECT;
- zero false accepts;
- fence-only safe repair `2/2` successful;
- DEEP calls `4/8`, avoided `4/8`;
- only one of four DEEP calls produced a final validator-PASS/CORRECT rescue;
- added DEEP wall `246.346 s`.

The only failed frozen gate was final CORRECT `5/8 < 6/8`. Do not relax/retry the exposed suite.

Supported conclusion: validator-first is useful, but raw one-shot DEEP is not a universal repair strategy.

## 7. Current — 8B Validator-Guided Repair 001

Preregistration:
`research/architecture/loom-8b-validator-guided-repair-001-preregistration.md`.

Fresh eight-task verifiable suite.

Graph:
`RAW8 -> validator -> PASS accept; FAIL -> existing safe fence repair if eligible -> revalidate -> residual FAIL -> one guided 8B repair using validator failure report -> revalidate`.

No 30B inference. This isolates whether observable validator failures can be repaired cheaply before escalation.

GO requires:
- zero false accepts;
- final >=6/8 CORRECT;
- >=+2 CORRECT vs RAW8;
- at least 2 residual FAILs repaired to validator PASS + ground-truth CORRECT;
- no unnecessary repair calls;
- frozen repair prompt/template and validator definitions;
- no network/model/runtime mutation.

## 8. Later selective DEEP integration

Only after the cheap guided-repair stage is independently validated, run a new fresh end-to-end suite:
`8B -> validator -> safe repair -> guided 8B repair -> residual FAIL -> DEEP -> revalidate`.

Measure final correctness, false accepts, DEEP call rate, DEEP repair yield and waiting cost.

## 9. Semantic verifier for open-ended tasks

Separate research for outputs that cannot be checked by deterministic contracts. Candidates:
- independent rubric/checklist validation;
- constrained verification against observable claims;
- task-specific tools/tests;
- small verifier/cross-tier judge only if measured value justifies cost;
- retrieval-grounded verification for factual tasks.

Generic confidence alone is insufficient.

## 10. Automatic validator/contract selection

After validator/rescue behavior is stable, test deriving validator kind/spec from the user request on a fresh independent prompt set. Do not reuse failed selector-v0 examples.

## 11. Further intelligence amplification

Later candidates:
- completion-aware continuation;
- deterministic structured-output repair;
- memory/RAG;
- skills/protocol retrieval;
- planner/executor/verifier;
- domain adaptation/distillation after system-layer gains are measured.

## 12. FAST tier

Legacy 4B remains parked; reintroduce only through a clean runtime.

## 13. Provider/UI

After execution graph validation, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 14. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 15. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block validator-first product progress.
