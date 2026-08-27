# LOOM Roadmap

Last updated: 2026-08-27
Current: `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`
Immediate next: `LOOM_30B_LOWER_BIT_EXPERT_SPEED_QUALITY_FRONTIER_001`
Canonical context: `/AGENTS.md` v3.41.

## Settled current 30B runtime

Canonical expert-major backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Current exact-Q4 speed baseline:
- commit `96958de`;
- 3×32-token throughput `1.115874`, `1.229233`, `1.254611 tok/s`;
- median `1.229233 tok/s`;
- exactness/safety PASS;
- persistent PACKED fd retained and committed.

Expert-major I/O/runtime/canonicalization are closed absent regression/new target.

## Why 5 tok/s needs larger levers

Top-8 Q4 traffic is `962,592,768 B/token`.
At `5 tok/s`, expert payload traffic alone would be about `4.81 GB/s` before expert compute, backbone, materialization and routing.

The exact-Q4 profile showed expert I/O `44.61%` and expert compute `26.50%` of wall before the persistent-fd improvement. Small hot-path changes therefore do not have enough headroom to reach the target alone.

## Routing Sparsity Frontier 001 — CLOSED

Result:
`research/architecture/loom-30b-routing-sparsity-speed-quality-frontier-001-result.md`.

Evidence:
`results-local/research/30b-routing-sparsity-speed-quality-frontier-001/20260827T135848Z/`.

Quality-valid points:
- tau `.95`: STRICT, `7.8757` experts/layer, `947,630,592 B/token`, `1.216703 tok/s`, `-1.02%`;
- tau `.90`: STRICT, `6.9440` experts/layer, `835,531,776 B/token`, `1.223280 tok/s`, `-0.48%`.

Aggressive points:
- tau `.80`: KL `0.113882` => fidelity FAIL;
- tau `.70`: top1 `87.5%`, KL `0.331111` => fidelity FAIL.

No eligible point met the frozen >=10% speed-gain gate. No sparsity variant was selected and no canonical code changed.

Conclusion: top-8 routing mass is too distributed for useful pruning under current quality gates. Do not spend more time on adjacent tau/fixed-top-k variants.

## Current — Lower-Bit Expert Speed/Quality Frontier 001

Preregistration:
`research/architecture/loom-30b-lower-bit-expert-speed-quality-frontier-001-preregistration.md`.

Objective: keep full top-8 routing and reduce byte/compute cost per expert using locally native lower-bit representations.

Frozen baseline:
- commit `96958de`;
- exact-Q4 median `1.229233 tok/s`;
- same retained 128-position Q4 teacher oracle.

Stage progression:
1. local MLX capability/readiness audit, no network/model forward/full build;
2. authorize only Q3 and/or Q2 if native local APIs support current group size/expert shapes;
3. fixed representative round-trip pilot;
4. sequential resumable full lower-bit banks, Q2 then Q3 where supported;
5. `6144/6144` + artifact integrity + `18,048` replay;
6. same 128-position fidelity oracle;
7. sustained 32-token test only for fidelity-valid candidates;
8. eligible candidate requires >=10% gain, USABLE fidelity and safety;
9. fastest eligible candidate gets final 3×32 + final oracle.

Candidate source is the deployed Q4 expert representation; no BF16 substitution in this checkpoint.

No routing sparsity, group-size search, mixed precision, custom kernel, speculative decoding, DFlash, Q4 rebuild or threshold rescue.

USABLE fidelity:
- top1 >=90%;
- teacher top1 in candidate top3 >=97%;
- KL <=0.10;
- finite logits.

STRICT:
- top1 >=95%;
- top3 >=99%;
- KL <=0.05.

Final classes:
- `EXPERT_QUANT_5TPS_REACHED_QUALITY_GATED`;
- `EXPERT_QUANT_FRONTIER_ADVANCED`;
- `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`;
- `EXPERT_QUANT_FRONTIER_INCONCLUSIVE`.

## Likely route after lower-bit compression

Even a 2× reduction in expert bytes is unlikely by itself to guarantee 5 tok/s because non-I/O work remains material. If Q2/Q3 produce an acceptable faster verifier, freeze the best point and then test an independent speculative-decoding mechanism.

The intended cumulative route is:

`expert-major + persistent fd + lower-bit experts + speculative/multi-token acceptance`

not repeated routing pruning.

## Next-model LOOM bake-off

After the current Qwen3-30B-A3B speed frontier is frozen, evaluate on the same M1/8GB:
1. current Qwen3-30B-A3B;
2. Qwen3.8-27B dense;
3. Qwen3.8-Flash-Next ultra-sparse MoE + N-gram embedding + MTP.

Compare:
- sustained tok/s and latency;
- RAM/swap/disk;
- intelligence/quality on a fixed LOOM eval set;
- instruction/refusal/steerability characteristics;
- best model for speed, intelligence and combined practical utility.

Each new architecture requires its own readiness contract and local measurement; do not infer the winner from vendor benchmarks alone.
