# LOOM Roadmap

Last updated: 2026-08-26
Current: `EXPERT_MAJOR_GO` from Decision Funnel 002
Strategic next: `LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001`
Canonical context: `/AGENTS.md` v3.31.

## Core 30B-on-8GB serving

External expert data-access remains the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

## Expert-major — physical-I/O decision accepted

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-002-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-002/20260826T144530Z/`.

Three disjoint 64-expert matched groups passed all physical-I/O validity gates.

Paired PACKED/SOURCE access-wall ratios:
- `0.602456`;
- `0.595950`;
- `0.581170`;
- median `0.595950` = `40.405%` lower access wall.

Read calls were reduced `576 -> 64` per group while conservative physical-byte ratios remained `0.947801`, `0.952811`, `0.945495`; all payload/hash, control, instrumentation, memory and swap gates passed.

Therefore raw expert-major data access is no longer speculative. It is the selected serving intervention for runtime validation.

## Execution model

Continue using compound preregistered funnels for strategic yes/no questions. Internal stages do not require Git/pull if outcomes, branch logic, thresholds, deterministic workload selection/fallback and bounds are frozen before execution.

## Next — Expert-major Runtime Funnel 001

Preregistration: `research/architecture/loom-30b-expert-major-runtime-funnel-001-preregistration.md`.

Question: does replacing only the external expert data-access backend with expert-major preserve exact runtime semantics and deliver enough practical end-to-end decode improvement on M1/8GB to justify canonical adoption?

Stage 0 — isolated integration:
1. inspect the current exact external serial-expert runtime and retained pack manifest;
2. select the most recent existing deterministic canonical exact-runtime workload supporting final-logit capture and decode timing;
3. build an isolated experimental adapter under `results-local/`;
4. SOURCE remains unchanged; PACKED changes only expert data-access backend/layout;
5. no persistent expert cache; one routed expert logically live at a time;
6. validate complete expert mapping before model forward.

Stage 1 — exactness:
- same forced/frozen token sequence;
- three full 48-layer decode positions;
- identical routed expert IDs/order;
- identical raw final-logit float32 SHA SOURCE vs PACKED;
- no fallback/cache/safety regression.

Valid exactness failure => `EXPERT_MAJOR_RUNTIME_NO_GO`; measurement ambiguity => INCONCLUSIVE.

Stage 2 — practical end-to-end decode:
- no artificial cold-cache manipulation;
- exactly 3 fresh-process pairs: `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`;
- one unmeasured warmup decode token then exactly three measured decode tokens per arm;
- record measured decode wall, peak RSS, swap/memory pressure and routing/backend state.

Runtime GO gates:
- Stage 1 exactness PASS;
- median `PACKED/SOURCE measured decode wall <=0.90` (>=10% improvement);
- median PACKED peak RSS <= median SOURCE +128 MiB;
- PACKED swap delta <= matched SOURCE +64 MiB in every pair;
- no unsafe pressure, persistent expert cache, fallback or incomplete evidence.

Final outcomes:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`

Hard bounds: no network/model download, no DFlash/cache-eviction experiments, no rescue repetitions, 3 exactness positions max, exactly 3 performance pairs, total runtime execution <=360 s.

## After Runtime Funnel 001

If `EXPERT_MAJOR_RUNTIME_GO`: productionize/canonicalize the expert-major backend in the repository, preserving exact acceptance evidence and then return to the next serving bottleneck.

If `EXPERT_MAJOR_RUNTIME_NO_GO`: retain expert-major physical-I/O evidence but do not adopt it in the runtime; diagnose only the measured runtime-level reason for rejection.

If `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`: repair only the specific integration/instrumentation ambiguity if a bounded one-factor remedy exists; do not reopen the already-settled physical-I/O question.

## Synchronization rule

Outside a frozen compound funnel, every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next independent WP; user pulls first.
