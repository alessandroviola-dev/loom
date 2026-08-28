# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Capability Selector v0 completed GO with perfect classification on 15 unseen mixed/adversarial prompts. Strict-output and verification-first remain accepted targeted capabilities; calculator remains rejected; Capability Candidate v1 remains NO_GO under its frozen always-on promotion gate. Current checkpoint is first end-to-end conditional 8B capability dispatch.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_AUTO_CAPABILITY_DISPATCH_001`
Pi context: `/AGENTS.md` v3.59.

## Product architecture direction

- 8B BALANCED — provisional default/primary tier;
- 30B DEEP — selective escalation where measured gain justifies latency;
- FAST — concept retained, legacy 4B parked;
- LOOM AUTO — selector -> conditional capability -> 8B -> validation -> 30B only if unresolved.

Do not freeze 30B escalation thresholds yet.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional after initial runtime/capability optimization, with frozen refusal/steerability and capability-preservation gates.

## Key evidence

Compact 8B vs 30B:
- 8B utility `4/10`, wall `35.325 s`;
- 30B utility `7/10`, wall `468.867 s`;
- +3 utility cost +`433.541 s` (~12.27x wall).

8B capability funnel:
- calculator REJECTED;
- strict-output ACCEPTED;
- verification-first ACCEPTED.

Capability Candidate v1:
- classification `LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO`;
- CAP8 `7/8`, RAW8 `6/8`, required improvement +2 but observed +1;
- no regressions;
- CAP8 matched 30B `7/8` with `26.311 s` vs `284.591 s` wall;
- keep B/C targeted; do not promote always-on CAP8 or relax the frozen gate.

## Capability Selector v0 result

Result:
`research/architecture/loom-capability-selector-v0-001-result.md`
Evidence:
`results-local/research/capability-selector-v0-001/20260828T163136Z/evidence.json`
Classification: **`LOOM_CAPABILITY_SELECTOR_V0_GO`**.

Frozen deterministic selector labels:
- `NORMAL`;
- `STRICT_OUTPUT`;
- `VERIFY_FIRST`.

Observed:
- accuracy `15/15`;
- confusion matrix perfectly diagonal: NORMAL 7, STRICT_OUTPUT 4, VERIFY_FIRST 4;
- precision/recall/F1 for every label `1.0000`;
- NORMAL false activations `0/7`;
- selector wall p50 `8 us`, p95 `218 us`;
- standard-library-only `python3 -I`, no model inference/network/package mutation.

This is selector/applicability evidence only, not answer-quality evidence.

## Exact next action — 8B Auto Capability Dispatch 001

Preregistration:
`research/architecture/loom-8b-auto-capability-dispatch-001-preregistration.md`.

Create only:
`scripts/loom_8b_auto_capability_dispatch_001.py`.

Run 9 fresh mixed tasks under two conditions each:
1. RAW8 baseline;
2. AUTO8 = exact selector v0 chooses NORMAL / exact accepted strict-output / exact accepted verification-first.

Mix:
- 3 NORMAL;
- 3 STRICT_OUTPUT;
- 3 VERIFY_FIRST.

Frozen GO gate:
- all 18 inferences valid;
- selector >=8/9 expected labels;
- NORMAL false activations 0/3;
- AUTO8 utility >= RAW8 +2;
- zero per-task utility regressions;
- AUTO8 >=7/9 CORRECT;
- unchanged selector/protocol definitions.

No 30B inference in this checkpoint. No calculator, 4B, network/downloads, runtime changes, selector tuning, capability rewriting, retries, memory/RAG, fine-tuning, Heretic, provider/UI or production integration.

If GO: next design/validate output validators and selective 30B escalation. If NO_GO: preserve evidence and diagnose independently; do not tune on the same prompts.
