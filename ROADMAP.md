# LOOM Roadmap

Last updated: 2026-08-27
Current: expert-major canonical backend committed (`36414d7`)
Strategic next: `LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001`
Canonical context: `/AGENTS.md` v3.38.

## Settled 30B expert-major direction

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median PACKED/SOURCE access ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted runtime ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower decode wall.

Canonicalization Runtime Contract 002:
`EXPERT_MAJOR_CANONICALIZATION_GO` with `FORMULAIC_RESOLVER`.
`6144/6144`, `18,048` replay, hot full-manifest parse/open `0`, 3-position exactness, RSS/swap/safety PASS.

Canonical code:
`scripts/loom_30b_moe_expert_major_backend_001.py`
Commit `36414d7`.

The expert-major phase is closed. Do not reconfirm it without regression/new target.

## Current — Post-Canonical Speed Frontier 001

Preregistration:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-preregistration.md`.

Engineering objective: maximize sustained Qwen3-30B-A3B Q4 decode on M1/8GB while preserving exact outputs first. Aspirational target `>=5.0 tok/s`.

Frozen compound progression:
1. 32-token sustained canonical baseline + exclusive bottleneck attribution;
2. process-lifetime PACKED fd if current per-expert open/close is confirmed;
3. remove/restructure redundant per-expert materialization synchronization if preregistered precondition is met;
4. bounded single-expert read/allocation reduction if still material;
5. bounded one-ahead overlap if external I/O remains >=20%;
6. final 3 × 32-token sustained throughput measurement.

Each intervention must independently preserve the frozen 3-position exactness oracle, zero fallback/cache, and bounded RSS/swap. It is retained only if its minimum preregistered speed gain passes; otherwise it is reverted.

Final outcomes:
- `SPEED_5TPS_REACHED`
- `SPEED_FRONTIER_ADVANCED`
- `SPEED_FRONTIER_NO_EXACT_GAIN`
- `SPEED_FRONTIER_INCONCLUSIVE`

No quantization/quality tradeoff or speculative decoding is authorized inside this checkpoint.

## Speed Frontier 002 — only if needed

If exactness-preserving engineering remains below the desired practical speed, separately investigate:
- lower-bit expert quantization (Q3/Q2 or mixed precision) with explicit quality loss gates;
- independent speculative decoding distinct from the closed DFlash path;
- retain only options with measured quality/safety/memory benefit.

Target `5 tok/s` is aspirational, not a justification for relaxing validity.

## Next-model LOOM bake-off

After freezing the fastest accepted current 30B runtime, test whether LOOM techniques can support newer Qwen releases on the same M1/8GB.

Candidates:
1. current `Qwen3-30B-A3B` — 30B total / 3B activated MoE baseline;
2. `Qwen3.8-27B` — dense 27B, requires a different streaming/readiness strategy because all 27B parameters participate in each token;
3. `Qwen3.8-Flash-Next` — ultra-sparse architecture with large expert bank, 6B activated main parameters, N-gram embedding, and MTP; requires a new LOOM artifact/runtime contract.

Required bake-off outputs on identical local constraints:
- sustained tok/s and latency;
- RAM/swap/disk footprint;
- fixed intelligence/quality score across reasoning, coding, knowledge and instruction following;
- controllability/refusal/steerability profile;
- practical winner by speed, intelligence and combined utility.

Do not infer the local winner from vendor benchmarks alone; measure all feasible candidates locally under a matched quality/quantization budget.
