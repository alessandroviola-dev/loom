# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Auto Capability Dispatch FIX1 completed with valid evidence but failed its frozen scientific gate. Selector v0 did not generalize sufficiently to mixed cues and AUTO8 reached only 2/9 fully correct tasks. Current checkpoint pivots to post-generation output validation before any 30B escalation work.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_8B_OUTPUT_VALIDATOR_V0_001`
Pi context: `/AGENTS.md` v3.61.

## Product architecture direction

- 8B BALANCED — provisional default/primary tier;
- 30B DEEP — selective escalation where measured gain justifies latency;
- FAST — concept retained, legacy 4B parked;
- LOOM AUTO direction — `8B -> post-generation validator -> accept / repair / 30B escalation`, not selector-first prompt classification.

Do not freeze 30B escalation thresholds yet.

## LOOM Heretic

`LOOM_HERETIC_TECHNICAL_PAPER.md` remains fundamental/non-optional after initial runtime/capability optimization with frozen refusal/steerability and capability-preservation gates.

## Runtime evidence

8B BALANCED remains Qwen3-8B 3-bit/group64 Direct MLX, ~13 tok/s real generation.
30B DEEP remains ~1.4 tok/s on compact tasks with ~50 s median TTFT.

Historical 8B 4-bit is not a current rescue: the continuous unquantized-KV profile resource-failed after a controlled high-free-memory launch and the KV8 branch has no canonical quality result. Do not reopen from current evidence.

Legacy 4B FAST remains parked after mechanical abort.

## Key prior evidence

Compact 8B vs 30B:
- 8B utility 4/10, wall 35.325 s;
- 30B utility 7/10, wall 468.867 s;
- +3 utility cost +433.541 s (~12.27x).

8B capability funnel:
- calculator REJECTED;
- strict-output ACCEPTED branch-level;
- verification-first ACCEPTED branch-level.

Capability Candidate v1:
- NO_GO under frozen +2 improvement gate;
- CAP8 7/8, RAW8 6/8, 30B 7/8;
- B/C retained only as targeted evidence, not an always-on bundle.

Capability Selector v0 isolated set:
- GO 15/15, zero NORMAL false activations, microsecond overhead.

## Auto Capability Dispatch FIX1 result

Result:
`research/architecture/loom-8b-auto-capability-dispatch-001-fix1-result.md`
Evidence:
`results-local/research/8b-auto-capability-dispatch-001-fix1/20260828T165528Z/`
Classification: `LOOM_8B_AUTO_CAPABILITY_DISPATCH_FIX1_NO_GO`.

All 18 conditions valid.

Frozen gate:
- selector accuracy `7/9` <8/9;
- NORMAL false activations `1/3` >0;
- AUTO8 utility `8` vs RAW8 `6`: +2 PASS;
- zero utility regressions: PASS;
- AUTO8 CORRECT `2/9` <7/9.

RAW8: utility 6, C/P/I 1/4/4, E2E wall 45.979878 s.
AUTO8: utility 8, C/P/I 2/4/3, E2E wall 58.924179 s.

Selector mistakes:
- T03 VERIFY_FIRST classified STRICT_OUTPUT;
- T07 NORMAL classified VERIFY_FIRST.

Supported conclusion: selector-first/static-protocol dispatch is not reliable enough. Do not tune on these exposed tasks or use this graph as the basis for 30B escalation.

## Exact next action — Output Validator v0

Preregistration:
`research/architecture/loom-8b-output-validator-v0-001-preregistration.md`.

Create only:
`scripts/loom_8b_output_validator_v0_001.py`.

Run synthetic no-model fixtures first. Then run 12 fresh RAW8 tasks once each.

Validator kinds are explicitly supplied by benchmark metadata to isolate validator fidelity:
- exact JSON object/array;
- exact CSV;
- restricted key:value contract;
- verification-first structural rule;
- UNVERIFIABLE -> always UNCERTAIN.

Main safety objective: **zero false PASS** on mechanically invalid outputs. Open-ended T10–T12 must all abstain as UNCERTAIN.

No 30B, selector tuning, capability injection, retries/repair, calculator, 4B, network/downloads, runtime changes, memory/RAG, fine-tuning, Heretic or provider/UI.

If GO, next separately test selective repair and/or 30B escalation only for FAIL/UNCERTAIN outputs. Do not expose an unvalidated answer merely because the 8B generated it.
