# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Capability Selector v0 remains GO. The first end-to-end RAW8 vs AUTO8 dispatch checkpoint is closed NO_GO because all 18 conditions hit a post-inference harness instrumentation bug before outputs/metrics were persisted. No capability-quality conclusion is supported. Current checkpoint is a separate mechanical FIX1 with unchanged scientific conditions.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_AUTO_CAPABILITY_DISPATCH_001_FIX1`
Pi context: `/AGENTS.md` v3.60.

## Product architecture direction

- 8B BALANCED — provisional default/primary tier;
- 30B DEEP — selective escalation where measured gain justifies latency;
- FAST — concept retained, legacy 4B parked;
- LOOM AUTO — selector -> targeted capability -> 8B -> validation -> 30B only if unresolved.

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
- `LOOM_8B_CAPABILITY_CANDIDATE_V1_NO_GO` under frozen +2 improvement gate;
- CAP8 `7/8`, RAW8 `6/8`, 30B `7/8`;
- no regressions;
- B/C remain targeted capabilities.

Capability Selector v0:
- `LOOM_CAPABILITY_SELECTOR_V0_GO`;
- 15/15 correct;
- NORMAL false activations 0/7;
- p50/p95 8 us / 218 us.

## Auto Capability Dispatch 001 — closed mechanical NO_GO

Result:
`research/architecture/loom-8b-auto-capability-dispatch-001-result.md`
Evidence:
`results-local/research/8b-auto-capability-dispatch-001/20260828T164106Z/`
Classification: `LOOM_8B_AUTO_CAPABILITY_DISPATCH_NO_GO`.

All 18 child conditions reached inference but then failed while building cleanup evidence with:
`TypeError: object of type 'int' has no len()`.

Valid conditions: `0/18` because generated output, selector labels/walls, scoring, latency and post-run evidence were not persisted.

Pre-inference provenance did pass:
- exact frozen 8B model/runtime;
- selector SHA `5ccaae77862ceb60700115487ea4db5e5bdcae330d8dcb7583d3186e6521887d`;
- failed harness `scripts/loom_8b_auto_capability_dispatch_001.py` SHA `a0346835bd927add1309ac800a9ae5c1fbffff25cb0f2307737186b526f9c460`.

This is instrumentation failure only. It does not invalidate selector/B/C capability evidence and supports no AUTO8 quality/performance claim.

## Exact next action — FIX1

Preregistration:
`research/architecture/loom-8b-auto-capability-dispatch-001-fix1-preregistration.md`.

Keep failed harness untouched. Create only:
`scripts/loom_8b_auto_capability_dispatch_001_fix1.py`.

Only authorized source-semantic delta is cleanup-evidence type normalization at the traceback site: integer cleanup count is persisted directly; collections use their length. No inference/scoring/selector/protocol/prompt/order changes.

Before inference:
1. verify original harness SHA;
2. persist exact unified diff;
3. synthetic no-model checks for integer and collection cleanup values;
4. verify selector/model/runtime provenance;
5. prove zero network/package/model mutation.

Then rerun the same frozen 18 RAW8/AUTO8 conditions once under the separate FIX1 checkpoint. No condition retries.

If a second independent harness defect appears, stop with mechanical NO_GO rather than patch again.

If valid evidence is obtained, apply the original frozen gate unchanged: all 18 valid; selector >=8/9; zero NORMAL false activations; AUTO8 >=RAW8 +2 utility; zero regressions; AUTO8 >=7/9 CORRECT; frozen selector/protocol definitions unchanged.

After FIX1 GO only, move to output validation and selective 30B escalation.
