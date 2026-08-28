# LOOM Roadmap

Last updated: 2026-08-28
Current: 8B Capability Candidate v1 completed NO_GO under its frozen promotion gate. Strict-output and verification-first remain accepted targeted capabilities; calculator remains rejected. Immediate next is zero-inference capability-selector validation.
Canonical context: `/AGENTS.md` v3.58.

## 1. Product direction — capability-first LOOM AUTO

Near-term active tiers:
- `loom-balanced` -> optimized 8B, provisional default;
- `loom-deep` -> 30B selective escalation;
- future `loom-fast` -> reintroduce later through a clean runtime;
- `loom-auto` -> capability selection, 8B execution, validation, then 30B only when unresolved.

Do not freeze 30B escalation thresholds yet.

## 2. LOOM Heretic — fundamental

`LOOM_HERETIC_TECHNICAL_PAPER.md` is core/non-optional after initial runtime/capability optimization. Freeze refusal/steerability and capability-preservation gates before edits.

## 3. Compact 8B vs 30B evidence

8B utility `4/10`, wall `35.325 s`.
30B utility `7/10`, wall `468.867 s`.
30B gained +3 utility at +`433.541 s` waiting (~12.27x wall).

## 4. 8B capability amplification funnel

Accepted:
- strict-output protocol;
- verification-first protocol.

Rejected:
- current calculator flow, because correct arithmetic does not repair wrong model-selected expressions/semantics.

## 5. Capability Candidate v1 — NO_GO

Result:
`research/architecture/loom-8b-capability-candidate-v1-001-result.md`.

CAP8:
- utility `7/8`;
- 3/4 CORRECT;
- zero regressions;
- total wall `26.311 s`.

RAW8:
- utility `6/8`.

30B:
- utility `7/8`;
- total wall `284.591 s`.

Candidate gate failed only the preregistered `>=+2` improvement requirement: CAP8 improved by `+1`. Do not relax/retry the gate. The result does not invalidate the separately accepted B/C mechanisms; retain them as targeted conditional capabilities rather than an always-on promoted bundle.

## 6. Current — Capability Selector v0

Preregistration:
`research/architecture/loom-capability-selector-v0-001-preregistration.md`.

Test exact deterministic rules for three labels on 15 unseen mixed/adversarial prompts:
- `NORMAL`;
- `STRICT_OUTPUT`;
- `VERIFY_FIRST`.

No model inference. Measure selector accuracy, confusion matrix, precision/recall/F1, false activations and microsecond-level wall.

If GO, proceed to separate end-to-end conditional dispatch with 8B. If NO_GO, keep capabilities explicitly invoked and do not tune on the same prompt set.

## 7. End-to-end conditional dispatch

Only after selector GO, test:
`prompt -> selector -> NORMAL/accepted protocol -> 8B`
against raw 8B on fresh mixed tasks. Measure quality delta, false activation cost and latency overhead. This remains separate from 30B escalation thresholds.

## 8. 30B escalation / LOOM AUTO

After capability selection and 8B validation are established, add validation-driven 30B escalation. Use 30B only for residual failures/uncertainty where measured quality gain justifies latency.

## 9. Further intelligence amplification

Later candidates:
- memory/RAG;
- skills/protocol retrieval rather than static stuffing;
- deterministic tools with semantic validators;
- planner/executor/verifier;
- domain adaptation/distillation after system-layer gains are measured.

## 10. FAST tier

Legacy 4B llama.cpp path remains parked. Reintroduce only through a clean runtime aligned with final architecture.

## 11. Provider/UI

After execution graph validation, expose LOOM through a local OpenAI-compatible provider usable by Pi and a proper chat UI.

## 12. Mandatory Heretic integration

After initial runtime/capability optimization, execute the Heretic-inspired behavioral/steerability track with preservation gates and decide per-tier application from evidence.

## 13. Separate R&D

Qwen3.8 and materially new 30B speed work remain separate and must not block capability-first product progress.
