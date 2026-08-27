# LOOM Roadmap

Last updated: 2026-08-27
Current: `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`
Immediate next: `LOOM_30B_LOSSLESS_SPECULATIVE_VERIFICATION_CEILING_001`
Canonical context: `/AGENTS.md` v3.42.

## Settled current 30B runtime

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Exact-Q4 speed baseline:
- commit `96958de`;
- sustained 3×32 values `1.115874`, `1.229233`, `1.254611 tok/s`;
- median `1.229233 tok/s`;
- exactness/safety PASS.

Full top-8 Q4 expert traffic is `962,592,768 B/token`.
Expert-major I/O/runtime/canonicalization are closed absent regression/new target.

## Closed speed paths

### Routing sparsity

`SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`.
Quality-valid pruning removed too little work; aggressive pruning failed fidelity. No routing variant selected.

### Q2/Q3 lower-bit experts

`EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`.
Result:
`research/architecture/loom-30b-lower-bit-expert-speed-quality-frontier-001-result.md`.

Q2:
- bank `8,153,726,976 B`;
- traffic `509,607,936 B/token`;
- top1 `84.375%`, top3 `96.094%`, KL `0.426378` => FAIL.

Q3:
- bank `11,777,605,632 B`;
- traffic `736,100,352 B/token`;
- top1 `87.500%`, top3 `100%`, KL `0.150060` => FAIL.

Both are technically supported on MLX `0.32.0`, pass complete static `6144/6144` + `18,048` replay, but neither meets frozen USABLE fidelity. No speed benchmark was allowed and no runtime code changed.

Conclusion: do not relax quality thresholds or search adjacent bit/group-size settings post hoc.

## Why speculative verification is the next question

The remaining practical baseline is still Q4 top-8 at `1.229233 tok/s`.
Further approximate byte reduction has failed quality gates, and exact hot-path work lacks enough headroom for `5 tok/s`.

The next potential multiplicative lever is producing/verifying multiple output tokens per expensive target step.

Before investing in a drafter, first measure whether the verifier itself has enough multi-token headroom under perfect proposals.

## Current — Lossless Speculative Verification Ceiling 001

Preregistration:
`research/architecture/loom-30b-lossless-speculative-verification-ceiling-001-preregistration.md`.

This is a verifier-only ceiling experiment, not production speculative decoding.

Frozen chunk sizes:
- K=2;
- K=4;
- K=8.

Oracle proposals are exact greedy Q4 continuation tokens, giving deliberately perfect acceptance so only verifier throughput is measured.

Required:
- sequential-equivalent causal/KV semantics;
- identical routed identities/order and raw float32 final-logit SHA;
- same full top-8 Q4 bank;
- zero SOURCE fallback/persistent multi-expert cache;
- no Q2/Q3, routing sparsity, DFlash, real drafter or network download.

Within a chunk/layer, one expert payload may be reused across multiple positions only when those positions route to the same expert; it must be applied independently to each row and not retained as a persistent cache.

Per K measure 32 verified output tokens and:
- tok/s;
- p50/p95;
- target chunk count;
- unique expert loads / reuse rate;
- expert bytes/output-token;
- wall attribution;
- RSS/swap/safety.

Best exact/safe K gets `3×32` confirmation.

Decision:
- median >=5 => `SPEC_VERIFY_5TPS_CEILING_REACHED`;
- median >=2.458466 but <5 => `SPEC_VERIFY_FRONTIER_PROMISING`;
- median <2.458466 => `SPEC_VERIFY_FRONTIER_NOT_PROMISING`;
- genuine execution ambiguity => INCONCLUSIVE.

Do not report oracle-ceiling tok/s as real user generation speed.

## If verifier ceiling is promising

Preregister a real lossless drafter frontier.
Candidate order:
1. zero-download n-gram/prompt-lookup where applicable;
2. if ceiling leaves enough margin, one small tokenizer-compatible Qwen-family drafter under explicit RAM/latency/download gates.

A real path must preserve canonical Q4 greedy output exactly and account for drafter overhead + actual acceptance.

## If verifier ceiling is not promising

Stop current-Qwen3 speculative work. Freeze the best 30B runtime at `1.229233 tok/s` and proceed to the planned same-hardware model bake-off:
1. Qwen3-30B-A3B;
2. Qwen3.8-27B;
3. Qwen3.8-Flash-Next.

Compare sustained tok/s, RAM/swap/disk, intelligence/quality, and instruction/refusal/steerability characteristics.
