# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — full-bank expert-major is accepted end-to-end for the current Qwen3-30B-A3B Q4 M1/8GB path. Physical-I/O causality and runtime adoption are settled; next is productionization/canonicalization only.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002_EXPERT_MAJOR_RUNTIME_GO`
Next: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001`
Pi context: `/AGENTS.md` v3.33.

## Settled expert-major evidence

Physical-I/O decision:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.

Valid PACKED/SOURCE first-touch ratios:
- `0.602456`;
- `0.595950`;
- `0.581170`;
- median `0.595950` = `40.405%` lower expert-access wall.

Runtime decision:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Result:
`research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-result.md`

Evidence:
`results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`

Full-bank/runtime acceptance:
- readiness PASS, source `6144/6144`;
- full routed bank `6144` entries / `15,401,484,288 B`, complete hash/provenance PASS;
- static dry-run `18,048` accesses, zero unresolved/fallback/cache;
- three-position full 48-layer exactness PASS, identical routing and raw final-logit float32 SHA;
- process-level A/B ratios `0.794284`, `0.846718`, `0.768208`;
- median `0.794284` = `20.5716%` lower measured decode wall;
- RSS gate PASS;
- swap delta `0 MiB`;
- no unsafe pressure, SOURCE fallback or persistent expert cache.

Conclusion: expert-major is no longer an experimental candidate. It is the accepted runtime direction for this target. Do not re-run the physical-I/O or full runtime acceptance campaigns unless a regression or materially different runtime/model target appears.

## Integration discipline

`research/architecture/loom-integration-readiness-protocol-v1.md` remains mandatory.

Before future integrations:
- explicit producer/consumer contracts;
- mechanical coverage proof;
- static access dry-run;
- only then model forward/integration;
- deterministic scripts/JSON for manifest/provenance rather than broad Pi reasoning.

## Exact next step — Canonicalization 001

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-001-preregistration.md`

This is productionization, not a new scientific experiment.

Pi should:
1. recover the exact accepted builder/manifest/backend from the retained Runtime Funnel 002 evidence;
2. verify the retained full-bank artifact still passes integrity/provenance;
3. add minimal reusable expert-major builder/validator/backend code to the local working tree while preserving SOURCE and every non-I/O runtime semantic;
4. run static production checks: compile/syntax, `6144/6144`, complete mapping, retained `18,048`-access replay, zero unresolved/fallback/cache;
5. rerun only the three-position exactness regression gate;
6. run one bounded SOURCE->PACKED three-token performance/safety smoke, not another full A/B campaign.

Canonicalization GO requires exactness + static gates PASS and smoke PACKED/SOURCE wall <=`0.95`, safe RSS/swap, zero fallback/cache/unsafe pressure.

Pi may edit runtime/source code but must not commit/push or edit AGENTS/HANDOFF/ROADMAP. On GO, Pi returns changed files + concise evidence so the code can be reviewed and committed separately.
