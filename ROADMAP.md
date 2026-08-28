# LOOM Roadmap

Last updated: 2026-08-28
Current: Capability Selector v0 completed GO with 15/15 correct applicability decisions and zero NORMAL false activations. Immediate next is end-to-end RAW8 vs AUTO8 conditional capability dispatch on fresh mixed tasks.
Canonical context: `/AGENTS.md` v3.59.

## 1. Product direction — capability-first LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> 30B selective escalation;
- future `loom-fast` -> reintroduce later through a clean runtime;
- `loom-auto` -> selector, targeted capability, 8B execution, validation, then 30B only when unresolved.

Do not freeze 30B escalation thresholds yet.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional after initial runtime/capability optimization. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Runtime/product evidence

Compact 8B vs 30B:
- 8B utility `4/10`, wall `35.325 s`;
- 30B utility `7/10`, wall `468.867 s`;
- 30B +3 utility at +`433.541 s` waiting (~12.27x wall).

8B capability funnel:
- strict-output ACCEPTED;
- verification-first ACCEPTED;
- calculator REJECTED because correct arithmetic cannot repair a wrong model-selected expression.

Capability Candidate v1:
- NO_GO only because improvement was +1 vs frozen +2 requirement;
- CAP8 `7/8`, RAW8 `6/8`, 30B `7/8`;
- zero regressions;
- CAP8 `26.311 s` vs 30B `284.591 s` wall;
- retain B/C as targeted capabilities, not an always-on bundle.

## 4. Capability Selector v0 — GO

Result:
`research/architecture/loom-capability-selector-v0-001-result.md`.

Frozen deterministic selector over `NORMAL`, `STRICT_OUTPUT`, `VERIFY_FIRST`:
- 15/15 correct;
- per-label precision/recall/F1 `1.0000`;
- NORMAL false activations `0/7`;
- p50/p95 `8 us / 218 us`;
- no inference/network/external packages.

This validates applicability selection only.

## 5. Current — 8B Auto Capability Dispatch 001

Preregistration:
`research/architecture/loom-8b-auto-capability-dispatch-001-preregistration.md`.

Test the first end-to-end graph:
`prompt -> selector v0 -> NORMAL / STRICT_OUTPUT / VERIFY_FIRST -> 8B`
against RAW8.

Nine fresh mixed tasks:
- 3 NORMAL;
- 3 STRICT_OUTPUT;
- 3 VERIFY_FIRST.

Measure selector correctness, answer correctness/utility, regressions, TTFT, throughput, total wall, memory/swap and conditional capability cost.

Frozen GO requires selector >=8/9, zero NORMAL false activations, AUTO8 >=RAW8 +2 utility, zero per-task regressions and >=7/9 AUTO8 CORRECT.

No 30B inference or escalation thresholds in this checkpoint.

## 6. Output validation and 30B escalation

Only after AUTO8 dispatch GO, freeze validators for output/task success and test:
`prompt -> selector/capability -> 8B -> validator -> 30B only on failed/uncertain validation`.

The objective is to minimize expensive DEEP calls while preserving correctness. Do not use prompt length alone as escalation signal.

## 7. Further intelligence amplification

Later candidates:
- memory/RAG;
- skills/protocol retrieval rather than static stuffing;
- deterministic tools with semantic validators;
- planner/executor/verifier;
- domain adaptation/distillation after system-layer gains are measured.

## 8. FAST tier

Legacy 4B llama.cpp path remains parked. Reintroduce only through a clean runtime aligned with final architecture.

## 9. Provider/UI

After execution graph validation, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 10. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 11. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block capability-first product progress.
