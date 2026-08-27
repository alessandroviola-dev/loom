# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — Qwen3-30B-A3B expert-major runtime is accepted/canonical. Exact-Q4 baseline is `1.229233 tok/s`. Routing sparsity and Q2/Q3 lower-bit expert frontiers are closed with no acceptable gain. Current work is lossless speculative verifier-ceiling measurement.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_LOSSLESS_SPECULATIVE_VERIFICATION_CEILING_001`
Pi context: `/AGENTS.md` v3.42.

## Current accepted runtime

Backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Commit:
`96958de` — persistent process-lifetime PACKED fd.

Exact-Q4 sustained throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Full top-8 Q4 expert traffic:
`962,592,768 B/token`.

Accepted expert-major/canonicalization evidence is settled and must not be reopened absent regression/new target.

## Closed speed frontiers

### Exact-Q4 Speed Frontier 001

Advanced from Stage-0 `1.063941 tok/s` to final median `1.229233 tok/s`. Only persistent PACKED fd retained. Expert I/O remained dominant.

### Routing Sparsity Frontier 001

Final `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`.
- tau `.95`: STRICT but `1.216703 tok/s`;
- tau `.90`: STRICT but `1.223280 tok/s`;
- tau `.80/.70`: fidelity FAIL.
No selected runtime change.

### Lower-Bit Expert Frontier 001

Final `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`.
Result:
`research/architecture/loom-30b-lower-bit-expert-speed-quality-frontier-001-result.md`.
Evidence:
`results-local/research/30b-lower-bit-expert-speed-quality-frontier-001/20260827T144620Z/`.

Installed local stack: MLX `0.32.0`, mlx-lm `0.31.3`; Q2/Q3 native at group size 128.

Q2 complete bank:
- `8,153,726,976 B`;
- `509,607,936 B/token` top-8;
- top1 `84.375%`, top3 `96.094%`, KL `0.426378` => fidelity FAIL.

Q3 complete bank:
- `11,777,605,632 B`;
- `736,100,352 B/token` top-8;
- top1 `87.500%`, top3 `100%`, KL `0.150060` => fidelity FAIL.

Both passed `6144/6144` + `18,048/18,048` static replay, but no sustained speed test was permitted because USABLE fidelity failed. No tracked code changed.

Retained artifacts:
- Q2 SHA `945fb36ce6912e2be3caaa69264e44a8aa71907c189dd753b539106252bf468a`;
- Q3 SHA `bd321bb35cde48d85033c859a22a277091e8b5ad236e05f6fade2da1fcf11c87`.

Do not adopt/retest adjacent lower-bit settings or relax quality gates without a materially new hypothesis.

## Exact next step — Lossless Speculative Verification Ceiling 001

Preregistration:
`research/architecture/loom-30b-lossless-speculative-verification-ceiling-001-preregistration.md`.

Question: if the canonical Q4 verifier receives perfect future-token proposals, can it verify multiple tokens per target step fast enough to justify a real drafter?

This is an upper-bound experiment only. Oracle throughput must not be described as user-visible production speed.

Frozen K values:
- 2;
- 4;
- 8.

For each K:
- proposals are exact known greedy Q4 continuation tokens;
- target chunk verification must be causal/KV-equivalent to sequential decode;
- final logits/routing/token IDs must be exact against sequential reference;
- same top-8 Q4 experts and quantization;
- no real drafter/network/DFlash/Q2/Q3/sparsity;
- same expert may be loaded once per layer/chunk only if required at multiple positions, then independently applied to each corresponding row;
- no persistent expert cache.

Measure one 32-output-token ceiling run per valid K, then final `3×32` on best K.

Decision:
- >=5 tok/s => `SPEC_VERIFY_5TPS_CEILING_REACHED`;
- >=2.458466 and <5 => `SPEC_VERIFY_FRONTIER_PROMISING`;
- <2.458466 => `SPEC_VERIFY_FRONTIER_NOT_PROMISING`;
- genuine runtime ambiguity only => INCONCLUSIVE.

## After ceiling

If promising: next checkpoint is a real lossless drafter frontier; start zero-download (n-gram/prompt lookup if applicable), then consider one small tokenizer-compatible Qwen-family drafter only if the ceiling justifies it.

If not promising: freeze current 30B speed frontier and move to the planned Qwen3.8-27B / Qwen3.8-Flash-Next bake-off or another verifier architecture.
