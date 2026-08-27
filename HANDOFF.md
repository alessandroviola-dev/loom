# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — expert-major is accepted, canonicalized, reviewed and committed. Current work is a bounded exactness-preserving speed frontier targeting the fastest practical Qwen3-30B-A3B decode on M1/8GB.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001`
Pi context: `/AGENTS.md` v3.38.

## Expert-major phase — CLOSED

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted three-pair ratios: `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall. Exactness/RSS/swap/fallback/cache PASS.

Canonicalization:
`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002 = EXPERT_MAJOR_CANONICALIZATION_GO`.
Selected `FORMULAIC_RESOLVER`; `6144/6144`, `18,048` replay, hot full-manifest opens `0`, 3-position exactness, RSS/swap/safety PASS.

Canonical implementation:
`scripts/loom_30b_moe_expert_major_backend_001.py`
Commit: `36414d7`.
Reviewed SHA-256: `b3d198308c8471832d04c79433d1c67643f30f1b1d9e2b7df0cc542b668c9ea2`.

Do not reopen expert-major validation absent regression/new target.

## Current — Post-Canonical Speed Frontier 001

Preregistration:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-preregistration.md`.

Goal: maximize sustained decode throughput of the canonical Qwen3-30B-A3B Q4 runtime while preserving exact semantics first. Aspirational engineering target: `>=5.0 tok/s`.

Compound flow:
1. fresh canonical 32-token sustained baseline + attribution;
2. persistent PACKED file descriptor if per-expert open/close remains in hot path;
3. collapse redundant expert materialization/synchronization if its frozen precondition is met;
4. bounded one-expert allocation/copy reduction if still material;
5. bounded one-ahead overlap if residual external expert I/O remains >=20%;
6. final 3 × 32-token sustained measurement and exactness/safety decision.

Treatments are cumulative only when exactness/safety PASS and the preregistered minimum gain is met. Rejected treatments are reverted before continuing.

Final classes:
- `SPEED_5TPS_REACHED`
- `SPEED_FRONTIER_ADVANCED`
- `SPEED_FRONTIER_NO_EXACT_GAIN`
- `SPEED_FRONTIER_INCONCLUSIVE`

No quantization loss, speculative decoding, DFlash, full-bank rebuild, cache/eviction experiments or threshold rescue in this checkpoint.

## After exact speed frontier

If throughput remains materially below 5 tok/s, next speed work may separately test lower-bit expert quantization and/or an independent speculative-decoding mechanism with explicit quality gates.

After the Qwen3-30B-A3B speed frontier is frozen, run a same-hardware model bake-off against:
- `Qwen3.8-27B` — dense model, separate streaming/readiness design required;
- `Qwen3.8-Flash-Next` — ultra-sparse MoE + N-gram embedding + MTP, separate LOOM adaptation required.

Bake-off dimensions:
- sustained tok/s;
- RAM/swap;
- intelligence/quality using a fixed LOOM evaluation set;
- instruction-following/refusal/steerability behavior.
