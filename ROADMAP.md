# LOOM Roadmap

Last updated: 2026-08-28
Current: Capability Selector v0 remains GO. First end-to-end RAW8-vs-AUTO8 dispatch attempt is closed NO_GO because a post-inference harness cleanup-evidence type bug prevented all 18 conditions from becoming valid scientific evidence.
Immediate next: execute separate mechanical `LOOM_8B_AUTO_CAPABILITY_DISPATCH_001_FIX1` with unchanged scientific condition and one authorized instrumentation fix.
Canonical context: `/AGENTS.md` v3.60.

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
- calculator REJECTED.

Capability Candidate v1:
- NO_GO under frozen +2 improvement gate;
- CAP8 `7/8`, RAW8 `6/8`, 30B `7/8`;
- zero regressions;
- B/C retained as targeted capabilities.

## 4. Capability Selector v0 — GO

Result:
`research/architecture/loom-capability-selector-v0-001-result.md`.

Frozen deterministic selector:
- 15/15 correct;
- per-label precision/recall/F1 `1.0000`;
- NORMAL false activations `0/7`;
- p50/p95 `8 us / 218 us`.

## 5. Auto Capability Dispatch 001 — MECHANICAL INVALID

Result:
`research/architecture/loom-8b-auto-capability-dispatch-001-result.md`.

Classification:
`LOOM_8B_AUTO_CAPABILITY_DISPATCH_NO_GO`.

All `18/18` child conditions reached inference but then failed while the experimental harness constructed cleanup evidence:
`TypeError: object of type 'int' has no len()`.

Outputs, selector labels/timing, scores and performance evidence were not persisted. Therefore valid conditions = `0/18` and no AUTO8 quality/performance conclusion is allowed.

Model/runtime/selector provenance passed before inference. The original checkpoint remains closed; do not silently repair/reclassify it.

## 6. Current — Auto Capability Dispatch FIX1

Preregistration:
`research/architecture/loom-8b-auto-capability-dispatch-001-fix1-preregistration.md`.

Keep original failed harness unchanged. Create separate fix1 harness with exactly one allowed semantic change: cleanup-evidence normalization for integer count versus event collection.

Before any inference, persist failed-vs-fix1 diff and run synthetic no-model tests for both cleanup value shapes.

If preflight passes, execute the original frozen 18 RAW8/AUTO8 conditions once. No retries.

If a second independent harness defect appears, stop with mechanical NO_GO instead of accumulating patches.

Original scientific gate remains unchanged:
- all 18 valid;
- selector >=8/9;
- NORMAL false activations 0/3;
- AUTO8 >= RAW8 +2 utility;
- zero regressions;
- AUTO8 >=7/9 CORRECT;
- selector/protocol definitions unchanged.

## 7. Output validation and 30B escalation

Only after a valid AUTO8 dispatch GO, freeze validators for output/task success and test:
`prompt -> selector/capability -> 8B -> validator -> 30B only on failed/uncertain validation`.

Objective: minimize expensive DEEP calls while preserving correctness. Do not use prompt length alone as escalation signal.

## 8. Further intelligence amplification

Later candidates:
- memory/RAG;
- skills/protocol retrieval rather than static stuffing;
- deterministic tools with semantic validators;
- planner/executor/verifier;
- domain adaptation/distillation after system-layer gains are measured.

## 9. FAST tier

Legacy 4B llama.cpp path remains parked. Reintroduce only through a clean runtime aligned with final architecture.

## 10. Provider/UI

After execution graph validation, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 11. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 12. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block capability-first product progress.
