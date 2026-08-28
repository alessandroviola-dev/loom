# LOOM — Active Handoff

Last updated: 2026-08-28
Status: ACTIVE — Qwen3-30B-A3B speed frontier frozen at exact production median `1.229233 tok/s`. Oracle speculative verification reached only `1.792925 tok/s` median at exact K=4 and is NOT PROMISING for a real drafter. Current work is Qwen3.8 portability readiness before large downloads.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_QWEN38_PORTABILITY_READINESS_001`
Pi context: `/AGENTS.md` v3.43.

## Frozen Qwen3-30B-A3B baseline

Backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Commit:
`96958de`.

Production exact-Q4/top-8 throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Do not substitute oracle ceiling results for production speed.

Closed unsuccessful speed paths:
- routing sparsity: no acceptable gain;
- Q2/Q3 expert requantization from deployed Q4: fidelity fail;
- DFlash: closed;
- real speculative drafter: not justified by verifier ceiling.

## Lossless Speculative Verification Ceiling 001 — CLOSED

Result:
`research/architecture/loom-30b-lossless-speculative-verification-ceiling-001-result.md`

Evidence:
`results-local/research/30b-lossless-speculative-verification-ceiling-001/20260828T101836Z/`

K=2 exact:
- `1.548806 tok/s`;
- 22.36% expert reuse;
- `747,325,440 B/output-token`.

K=4 exact:
- selected;
- final 3×32 `1.792925`, `1.807852`, `1.785392 tok/s`;
- median `1.792925 tok/s`;
- p50/p95 `0.557813 / 0.596685 s`;
- 40.93% reuse;
- `568,641,024 B/output-token`;
- final exactness/SHA and safety PASS.

K=8 INVALID exactness and was not performance tested.

Final classification:
`SPEC_VERIFY_FRONTIER_NOT_PROMISING`.

Interpretation: even perfect proposals and zero drafter overhead leave insufficient verifier headroom for the 5 tok/s target. Freeze current verifier speed work unless a materially different verifier architecture appears.

## Current — Qwen3.8 Portability Readiness 001

Preregistration:
`research/architecture/loom-qwen38-portability-readiness-001-preregistration.md`.

Candidates:
1. `Qwen/Qwen3.8-27B`, reference MLX `mlx-community/Qwen3.8-27B-4bit`, published payload ~16.1 GB;
2. `Qwen/Qwen3.8-Flash-Next`, reference MLX `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP`, published payload ~113.209 GB / 105.434 GiB.

Flash-Next architecture to revalidate mechanically:
- `qwen4_exp`;
- 48 layers;
- 125B main / 6B active per token;
- +51B n-gram embedding;
- +4B native MTP;
- 512 routed experts, 10 active +1 shared.

This checkpoint is metadata/static readiness only:
- network <=100 MiB per candidate;
- no safetensor shard download;
- no package upgrade;
- no model forward.

For dense 27B, derive layer-streaming working set and bytes/token.
For Flash-Next, derive expert-major + deterministic n-gram offload + shared/backbone/state + optional MTP contracts.

Portable gate requires bounded active working set <=5.5 GiB, resolved tensor/identity ABI, no full-model residency requirement, no hidden remote runtime dependency.

Final outcome decides which model(s) deserve actual weight acquisition and execution next.

After actual local execution, final bake-off dimensions are:
- sustained tok/s and TTFT;
- RAM/swap/disk;
- frozen intelligence/quality set;
- instruction following/refusal/steerability;
- practical winner by speed, intelligence and combined utility.