# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — 8B Capability Candidate v1 completed NO_GO under its frozen gate despite matching 30B utility on the fresh four-task set. Strict-output and verification-first remain accepted targeted capabilities; calculator remains rejected. Current checkpoint tests capability applicability with a zero-inference deterministic selector.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_CAPABILITY_SELECTOR_V0_001`
Pi context: `/AGENTS.md` v3.58.

## Product architecture direction

- 8B BALANCED — provisional default/primary tier;
- 30B DEEP — selective escalation where measured gain justifies latency;
- FAST — concept retained, legacy 4B parked;
- LOOM AUTO — capability selection -> 8B -> validation -> 30B only if unresolved.

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

## Capability Candidate v1 result

Result:
`research/architecture/loom-8b-capability-candidate-v1-001-result.md`
Evidence:
`results-local/research/8b-capability-candidate-v1-001/20260828T161543Z/`
Classification: `LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO`.

Gate:
- CAP8 utility `7/8` >=6: PASS;
- CAP8 improvement `+1` vs RAW8 `6/8`, required +2: FAIL;
- zero regressions: PASS;
- 3/4 CORRECT: PASS;
- provenance/evidence: PASS.

30B also scored `7/8`; CAP8 total wall `26.311 s` vs 30B `284.591 s`, so 30B cost +`258.280 s` / `10.82x` with no utility gain on this set.

Do not reinterpret this as CAP8 GO. The frozen gate remains closed. Also do not discard B/C: there was no integration regression and prior branch-level acceptance remains valid. Treat them as targeted conditional capabilities rather than an always-on bundle.

## Exact next action — Capability Selector v0

Preregistration:
`research/architecture/loom-capability-selector-v0-001-preregistration.md`.

Create only:
`scripts/loom_capability_selector_v0_001.py`.

No model inference. Apply the exact frozen deterministic rules to 15 unseen mixed/adversarial prompts and report accuracy, confusion matrix, per-label precision/recall/F1, NORMAL false activations, and p50/p95 selector wall.

Classification only:
- `LOOM_CAPABILITY_SELECTOR_V0_GO`;
- `LOOM_CAPABILITY_SELECTOR_V0_NO_GO`.

If GO, next checkpoint is separate end-to-end 8B conditional dispatch. If NO_GO, keep B/C explicitly invoked and do not tune selector rules on the same prompts.

Calculator, 4B recovery, 30B thresholds, memory/RAG, provider/UI, fine-tuning and Heretic are outside this checkpoint.
