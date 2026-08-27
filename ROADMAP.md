# LOOM Roadmap

Last updated: 2026-08-27
Current: `EXPERT_MAJOR_RUNTIME_GO` from Full-Bank Runtime Funnel 002
Strategic next: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001`
Canonical context: `/AGENTS.md` v3.33.

## Core 30B-on-8GB serving

Expert-major contiguous external-expert storage is now accepted both causally and at full runtime level for the current Qwen3-30B-A3B Q4 M1/8GB path.

## Settled physical-I/O decision

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.

PACKED/SOURCE physical-I/O ratios:
- `0.602456`;
- `0.595950`;
- `0.581170`;
- median `0.595950` = `40.405%` lower expert-access wall.

Exact payload/hash, physical bytes, read structure, memory and swap gates all PASS. Do not reopen this question absent a new independent regression/target.

## Settled runtime decision

`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Result:
`research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-result.md`

Evidence:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`

Accepted full-bank/runtime evidence:
- readiness: `6144/6144` source expert identities PASS;
- full bank: `6144` entries, `15,401,484,288 B`, complete hash/provenance PASS;
- static dry-run: `18,048` accesses, zero unresolved/fallback/cache;
- exactness: three consecutive full 48-layer decode positions, identical routing and raw final-logit float32 SHA;
- practical A/B ratios: `0.794284`, `0.846718`, `0.768208`;
- median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS;
- swap delta `0 MiB`;
- no unsafe memory pressure, fallback or persistent expert cache.

Therefore the expert-major full-bank backend is the selected runtime direction for this target.

## Integration Readiness Protocol

`research/architecture/loom-integration-readiness-protocol-v1.md` remains mandatory for future runtime integrations.

Key rule: predictable artifact/runtime incompatibilities must fail at offline contract/static-dry-run time, before adapter/model execution.

## Next — Expert-Major Canonicalization 001

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-001-preregistration.md`

Goal: productionize the already accepted experimental implementation into minimal reusable canonical repository code without re-running settled scientific campaigns.

Frozen stages:
1. recover the exact accepted Runtime Funnel 002 builder/manifest/backend and verify retained full-bank integrity;
2. add minimal reusable builder/validator/backend interface to the local working tree, preserving SOURCE and all non-I/O semantics;
3. static production gate: compile/syntax, `6144/6144` manifest, mapping uniqueness/bounds, retained `18,048`-access replay, zero unresolved/fallback/cache;
4. exactness regression: same three accepted decode positions, identical routed expert order + raw float32 final-logit SHA;
5. one bounded fresh-process SOURCE->PACKED performance/safety smoke with one warmup + three measured decode tokens.

Canonicalization GO requires all static/exactness gates PASS and smoke PACKED/SOURCE decode wall <=`0.95`, PACKED RSS <= SOURCE +128 MiB, PACKED swap <= SOURCE +64 MiB, no unsafe pressure/fallback/cache.

This smoke is only a regression guard; it must not be treated as a new estimate of the already accepted runtime effect.

## After Canonicalization GO

Review and commit the production code and reusable tooling, preserving the accepted full-bank artifact as an external/local runtime asset rather than storing the 15.4-GB payload in Git.

Then re-profile the canonical 30B runtime and select the next dominant serving bottleneck. Do not optimize expert data-access further unless the new profile shows it remains dominant after canonicalization.

## Efficiency rule

Use compound funnels for strategic questions, deterministic offline gates for compatibility/provenance, and reuse accepted artifacts/evidence. Do not return to serial micro-tests or repeat settled A/B campaigns during productionization.
