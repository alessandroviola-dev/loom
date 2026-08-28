# LOOM Roadmap

Last updated: 2026-08-28
Current: Output Validator v0 completed GO with zero false PASS on mechanically verifiable tasks and correct UNCERTAIN abstention on open-ended tasks.
Immediate next: validator-guided selective rescue using safe fence-only deterministic repair and 30B DEEP only on residual FAIL.
Canonical context: `/AGENTS.md` v3.62.

## 1. Product direction — validator-first LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> 30B selective escalation;
- future `loom-fast` -> reintroduce later through a clean runtime;
- `loom-auto` -> 8B generation, deterministic/task-specific validation, safe repair when provably semantics-preserving, then DEEP only when validation still fails.

Open-ended semantic uncertainty remains separate. Do not convert UNCERTAIN into automatic DEEP calls until a semantic-verifier path is measured.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional after initial runtime/capability optimization. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Runtime/product evidence

8B BALANCED remains roughly 13 tok/s and is the latency-efficient base.
30B DEEP remains roughly 1.4 tok/s on compact tasks with ~50 s median TTFT; it must be called only when validation evidence justifies the cost.
Historical 8B 4-bit remains closed by resource evidence; legacy 4B FAST remains parked.

## 4. Selector/capability evidence

Strict-output and verification-first remain branch-level accepted mechanisms, but selector-first end-to-end dispatch is closed as a current architecture path:
- isolated selector 15/15;
- end-to-end selector 7/9 with one NORMAL false activation;
- AUTO8 utility 8 vs RAW8 6 but only 2/9 fully correct.

Do not tune on exposed dispatch prompts.

## 5. Output Validator v0 — GO

Result:
`research/architecture/loom-8b-output-validator-v0-001-result.md`.

Observed:
- 11/11 synthetic fixtures PASS;
- 12/12 valid records;
- PASS/FAIL/UNCERTAIN 3/6/3;
- T01–T09 quality 3/3/3 CORRECT/PARTIAL/INCORRECT;
- false PASS 0;
- open-ended abstention 3/3;
- validator p95 0.758321 ms;
- 8B generation 12.986417 tok/s.

This validates fail-closed post-generation checks when validator kind/spec is already known. It does not validate automatic validator selection or general semantic correctness.

## 6. Current — Validator-Guided Selective Rescue 001

Preregistration:
`research/architecture/loom-validator-guided-selective-rescue-001-preregistration.md`.

Fresh eight-task verifiable suite.

Graph:
`8B -> validator -> PASS accept; FAIL -> fence-only safe repair if eligible -> revalidate -> residual FAIL -> one 30B -> revalidate`.

Safe repair only removes one outer Markdown code fence and must leave payload bytes untouched. No value/type/order coercion or semantic rewriting.

Measure:
- raw8 vs final quality;
- false accepts;
- safe-repair success;
- DEEP call rate and calls avoided;
- added 30B wall;
- final correctness and time per correct task.

GO requires zero false accepts, final >=6/8 CORRECT, >=+2 CORRECT vs raw8, >=2/8 DEEP calls avoided, and no unnecessary DEEP calls after PASS/successful repair.

## 7. Semantic verifier for open-ended tasks

After bounded selective rescue, separately research validation for tasks where deterministic contracts do not exist. Candidates may include:
- independent rubric/checklist generation;
- constrained self-verification with observable claims;
- small verifier model or cross-tier judge only if evidence justifies latency;
- retrieval/tool-grounded verification when external facts are involved.

Do not treat generic model confidence as sufficient.

## 8. Automatic validator/contract selection

Only after validator behavior and rescue value are established, test deriving validator kind/spec from the user request rather than benchmark metadata. This must be independent of the failed selector-v0 exposed prompt set.

## 9. Further intelligence amplification

Later candidates:
- completion-aware continuation;
- deterministic structured-output repair;
- memory/RAG;
- skills/protocol retrieval;
- tools with semantic validators;
- planner/executor/verifier;
- domain adaptation/distillation after system-layer gains are measured.

## 10. FAST tier

Legacy 4B remains parked; reintroduce only through a clean runtime.

## 11. Provider/UI

After execution graph validation, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 12. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 13. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block validator-first product progress.
