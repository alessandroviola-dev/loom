# LOOM Roadmap

Last updated: 2026-08-28
Current: Auto Capability Dispatch FIX1 completed with valid evidence and scientific NO_GO. Selector-first/static-protocol dispatch improved utility but did not generalize sufficiently and produced only 2/9 fully correct AUTO8 outputs.
Immediate next: validate a fail-closed post-generation Output Validator v0 on fresh RAW8 tasks before any 30B escalation work.
Canonical context: `/AGENTS.md` v3.61.

## 1. Product direction — validator-first LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> 30B selective escalation;
- future `loom-fast` -> reintroduce later through a clean runtime;
- `loom-auto` -> 8B generation, task/contract validation, then selective repair or DEEP escalation when verification fails or remains uncertain.

Pre-inference deterministic capability selector v0 is not the current production path. Do not tune it on exposed dispatch prompts.

Do not freeze 30B escalation thresholds yet.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional after initial runtime/capability optimization. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Runtime/product evidence

Compact 8B vs 30B:
- 8B utility `4/10`, wall `35.325 s`;
- 30B utility `7/10`, wall `468.867 s`;
- 30B +3 utility at +`433.541 s` waiting (~12.27x wall).

8B remains ~13 tok/s and is the latency-efficient base. 30B remains expensive and must be called only when evidence justifies it.

Historical 8B 4-bit is not reopened: the exact continuous profile resource-failed after controlled high-free-memory launch, and its KV8 rescue branch has no canonical quality result.

Legacy 4B FAST remains parked.

## 4. Capability evidence

8B capability funnel:
- strict-output ACCEPTED branch-level;
- verification-first ACCEPTED branch-level;
- calculator REJECTED.

Capability Candidate v1:
- NO_GO under frozen +2 improvement gate;
- CAP8 `7/8`, RAW8 `6/8`, 30B `7/8`;
- zero regressions;
- targeted mechanisms remain evidence, not an always-on bundle.

Capability Selector v0 isolated validation:
- GO `15/15`;
- zero NORMAL false activations;
- microsecond overhead.

## 5. Auto Capability Dispatch FIX1 — NO_GO

Result:
`research/architecture/loom-8b-auto-capability-dispatch-001-fix1-result.md`.

All 18 frozen conditions valid.

Observed:
- selector `7/9` -> gate FAIL;
- NORMAL false activations `1/3` -> gate FAIL;
- AUTO8 utility `8` vs RAW8 `6` -> +2 PASS;
- zero per-task utility regressions -> PASS;
- AUTO8 fully CORRECT `2/9` -> gate FAIL.

AUTO8 wall `58.924179 s` vs RAW8 `45.979878 s`.

Conclusion: targeted capability prompts can rescue individual contract failures, but selector-first dispatch does not generalize and does not solve semantic/incomplete outputs. Do not build DEEP escalation on this graph.

## 6. Current — 8B Output Validator v0

Preregistration:
`research/architecture/loom-8b-output-validator-v0-001-preregistration.md`.

Test:
`prompt -> RAW8 -> PASS / FAIL / UNCERTAIN`.

12 fresh tasks:
- exact JSON/CSV/restricted key:value contracts;
- three verification-rule tasks;
- three open-ended tasks that validator v0 must mark UNCERTAIN.

Validator kind/spec is supplied by benchmark metadata in v0. This isolates validator fidelity; automatic validator selection is later work.

Before inference, synthetic PASS/FAIL/UNCERTAIN fixtures must pass.

Primary gate: zero false PASS on mechanically invalid outputs. T10–T12 must all abstain as UNCERTAIN. Validator p95 must remain <5 ms.

No 30B, retries, repair, selector tuning, capability injection, memory/RAG, fine-tuning, Heretic or provider/UI.

## 7. Selective repair / 30B escalation

Only after Output Validator v0 GO, freeze a fresh end-to-end experiment:
`8B -> validator -> if PASS accept; if FAIL/UNCERTAIN use a preregistered cheap repair when applicable or call 30B`.

Measure:
- fraction of 30B calls avoided;
- final correctness/utility;
- false accepts;
- extra waiting time;
- whether 30B actually repairs validator-detected failures.

The validator should run again after any repair/30B response when a deterministic contract exists.

## 8. Further intelligence amplification

Later candidates:
- completion-aware continuation for length-stopped answers;
- structured-output repair driven by deterministic validators;
- memory/RAG;
- skills/protocol retrieval rather than static stuffing;
- tools with semantic/task-specific validators;
- planner/executor/verifier;
- domain adaptation/distillation only after system-layer gains are measured.

## 9. FAST tier

Legacy 4B llama.cpp path remains parked. Reintroduce only through a clean runtime aligned with final architecture.

## 10. Provider/UI

After execution graph validation, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 11. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 12. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block validator-first product progress.
