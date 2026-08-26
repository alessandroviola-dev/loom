# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — expert-major physical-I/O causality is now validated with `EXPERT_MAJOR_GO`; next is one compound isolated runtime integration/exactness/performance funnel.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002_EXPERT_MAJOR_GO`
Next: `LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001`
Pi context: `/AGENTS.md` v3.31.

## Synchronization

Normal rule: significant checkpoint -> ChatGPT updates GitHub -> user pulls -> next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull when all outcomes, branches, thresholds, workload selection/fallback and hard bounds are frozen before execution.

## Core 30B serving/I/O

External expert data-access is the dominant measured bottleneck:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

## Expert-major physical-I/O decision

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-002-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-002/20260826T144530Z/`.

Stage 0 constructed 3 disjoint matched 64-expert groups (`160,432,128 B/arm/group`) with exact SOURCE/PACKED logical payload identity and zero cross-group overlap.

All six first-touch physical-I/O arms were valid. Paired PACKED/SOURCE wall ratios:
- Pair 1 `0.602456`;
- Pair 2 `0.595950`;
- Pair 3 `0.581170`;
- median `0.595950` = `40.405%` lower access wall.

Physical-byte ratios were `0.947801`, `0.952811`, `0.945495`; read calls were `576 SOURCE -> 64 PACKED` per group. Payload/hash, controls, instrumentation and safety all PASS; zero swap delta; minimum free memory 55%.

Conclusion: expert-major raw external-expert I/O is causally validated and worth runtime integration testing. Do not reopen physical cold-cache methodology unless a new independent issue appears.

## Exact next step — Runtime Funnel 001

Preregistration: `research/architecture/loom-30b-expert-major-runtime-funnel-001-preregistration.md`.

One compound funnel answers whether expert-major should become the canonical runtime backend.

Stage 0: build an isolated one-factor expert-major data-access adapter under `results-local/`, preserving the SOURCE baseline and every non-I/O runtime factor.

Stage 1: full 48-layer exactness on three frozen decode positions. Require identical routed experts and raw final-logit float32 SHA SOURCE vs PACKED, no fallback/cache/safety regression.

Stage 2: practical runtime benchmark, not artificial coldness. Three fresh-process matched pairs with frozen order `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`; each arm has one unmeasured warmup decode token then three measured decode tokens.

Runtime GO requires:
- Stage 1 exactness PASS;
- all validity/safety gates PASS;
- median `packed measured decode wall / source measured decode wall <=0.90`;
- median PACKED peak RSS no more than 128 MiB above SOURCE;
- PACKED swap delta no more than matched SOURCE +64 MiB in every pair;
- no persistent expert cache or backend fallback.

Hard cap: 360 s total runtime execution, no network/download, no DFlash, no rescue repetitions.

Final outcomes only:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.
