# LOOM Roadmap

Last updated: 2026-08-27
Current: `SPEED_FRONTIER_ADVANCED` from Post-Canonical Speed Frontier 001
Immediate next: review/commit accepted persistent-FD delta
Strategic next: `LOOM_30B_ROUTING_SPARSITY_SPEED_QUALITY_FRONTIER_001`
Canonical context: `/AGENTS.md` v3.39.

## Settled expert-major direction

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median PACKED/SOURCE first-touch ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted median ratio `0.794284` = `20.5716%` lower decode wall.

Canonicalization Runtime Contract 002:
`EXPERT_MAJOR_CANONICALIZATION_GO` with `FORMULAIC_RESOLVER`.

Canonical code before current speed delta:
`scripts/loom_30b_moe_expert_major_backend_001.py`
commit `36414d7`.

Expert-major validation is closed absent regression/new target.

## Post-Canonical Speed Frontier 001 — ADVANCED

Result:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-result.md`.
Evidence:
`results-local/research/30b-post-canonical-speed-frontier-001/20260827T131329Z/`.

Exact Stage-0 sustained baseline: `1.063941 tok/s`.

Wall attribution:
- expert file I/O `44.61%`;
- expert compute `26.50%`;
- non-expert/backbone `14.74%`;
- materialization/synchronization `11.51%`;
- routing `2.64%`.

Only persistent process-lifetime PACKED fd was retained (`+8.65%`, exact/safe).

Rejected/reverted:
- synchronization collapse `-30.38%`;
- allocation/copy reduction `+3.60%` but RSS gate fail;
- one-ahead overlap `+8.45%` but RSS gate fail.

Final exact 3×32-token throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

p50 `0.825660 s`; p95 `1.217692 s`; peak RSS `404,340,736 B`; swap `0`; exactness/safety PASS.

The accepted Stage-1 persistent-FD change remains local/uncommitted and must be reviewed/persisted before the next independent funnel.

## Why exact Q4 is unlikely to reach 5 tok/s alone

Top-8 Q4 routed expert traffic is:
`384 experts/token × 2,506,752 B = 962,592,768 B/token`.

At `5 tok/s`, expert payload traffic alone would be about `4.81 GB/s`, before expert compute, backbone, materialization and routing.

Therefore the next high-leverage speed work should reduce expert work/bytes per token rather than continue small exact-Q4 hot-path changes.

## Next — Routing Sparsity Speed/Quality Frontier 001

Preregistration:
`research/architecture/loom-30b-routing-sparsity-speed-quality-frontier-001-preregistration.md`.

Execute only after persistent-FD code is reviewed and committed.

Treatment: retain the original top-8 router decision, but execute only the smallest subset covering a frozen cumulative routing-mass threshold, then renormalize retained weights while preserving original retained expert accumulation order.

Authorized thresholds only:
- `tau=0.95`;
- `tau=0.90`;
- `tau=0.80`;
- `tau=0.70`.

No fixed-top-k or post-hoc threshold rescue.

Quality oracle frozen before candidate results:
8 prompts ×16 teacher-forced positions = 128 positions against exact Q4 teacher logits.

USABLE minimum:
- top1 agreement >=90%;
- reference top1 in candidate top3 >=97%;
- KL(reference||candidate) <=0.10 nats;
- finite logits.

STRICT:
- top1 >=95%;
- top3 inclusion >=99%;
- KL <=0.05.

Eligible variant also requires >=10% sustained speed gain over exact median `1.229233 tok/s` and memory/swap safety PASS.

Select fastest eligible point; throughput tie within 2% favors better fidelity/higher tau.

After selected sparsity, one bounded raw one-ahead overlap repair may be retried only with <=one extra raw expert payload and +32 MiB RSS bound.

Final classifications:
- `SPARSITY_5TPS_REACHED_QUALITY_GATED`;
- `SPARSITY_FRONTIER_ADVANCED`;
- `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`;
- `SPARSITY_FRONTIER_INCONCLUSIVE`.

## If still below 5 tok/s

Next frontier: lower-bit expert payload quantization (Q3/Q2 or mixed precision), under its own frozen quality gate, optionally combined only with the accepted routing-sparsity point.

This is the most direct next way to reduce the dominant byte/token cost.

## Next-model LOOM bake-off

After freezing the fastest acceptable current Qwen3-30B-A3B runtime, adapt/test on the same M1/8GB:
1. Qwen3-30B-A3B baseline;
2. Qwen3.8-27B dense;
3. Qwen3.8-Flash-Next ultra-sparse MoE + N-gram embedding + MTP.

Matched outputs:
- sustained tok/s/latency;
- RAM/swap/disk;
- fixed intelligence/quality score;
- instruction/refusal/steerability profile;
- winner for speed, intelligence and combined practical utility.

Do not infer the winner from vendor benchmarks alone; each new architecture requires its own LOOM readiness contract and local measurement.
