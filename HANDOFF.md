# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — expert-major is accepted, canonicalized, reviewed and committed. Next is post-expert-major bottleneck selection from fresh canonical-runtime measurements.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_POST_EXPERT_MAJOR_BOTTLENECK_SELECTION`
Pi context: `/AGENTS.md` v3.37.

## Expert-major phase — CLOSED

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE access ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted three-pair ratios: `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall. Exactness, RSS, swap, fallback and cache gates PASS.

Canonical productionization:
`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002 = EXPERT_MAJOR_CANONICALIZATION_GO`.
Result: `research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-result.md`.
Evidence: `results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/`.

Selected resolver: `FORMULAIC_RESOLVER`.
Fixed-layout PASS: 6144 expert records, lexicographic `48×128`, constant `2,506,752 B`, contiguous affine offsets, exact `15,401,484,288 B` bank.
Runtime contract SHA-256: `ee43eaa935e957d40856898c73fe238ff626c880514a8deb9b73491567657aba`.
Static `6144/6144`, `18,048` replay, hot manifest opens/parses `0`, 3-position exactness, RSS/swap/safety all PASS.
Canonicalization smoke ratio `0.439345978` is regression evidence only; accepted performance estimate remains median `0.794284` from the three-pair funnel.

Canonical implementation:
`scripts/loom_30b_moe_expert_major_backend_001.py`
Commit: `36414d7` — `feat: canonicalize 30B expert-major backend`.
Reviewed pre-commit SHA-256: `b3d198308c8471832d04c79433d1c67643f30f1b1d9e2b7df0cc542b668c9ea2`.
Remote presence verified after push.

Do not reopen expert-major validation/canonicalization absent a material regression or materially different target/runtime.

## Exact next step — post-expert-major bottleneck profile

The old pre-expert-major decomposition is no longer sufficient for prioritization because expert access has changed materially.

Next work must profile the canonical expert-major decode path and rank exclusive wall-time contributors, distinguishing at minimum:
- residual packed expert access;
- payload materialization / NumPy-to-MLX conversion;
- MLX eval/synchronization barriers;
- routing/dispatch;
- non-routed backbone compute;
- attention/KV/output path;
- directly measured residual/other.

Requirements:
- attribution-first, non-invasive;
- deterministic existing workload where possible;
- no new optimization during the profiling checkpoint;
- no full expert-major A/B reconfirmation;
- bounded token/runtime cost;
- final output should identify the single next intervention candidate or return INCONCLUSIVE if attribution is not separable.
