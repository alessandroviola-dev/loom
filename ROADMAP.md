# LOOM Roadmap

Last updated: 2026-08-28
Current: `SPEC_VERIFY_FRONTIER_NOT_PROMISING`
Immediate next: `LOOM_QWEN38_PORTABILITY_READINESS_001`
Canonical context: `/AGENTS.md` v3.43.

## Frozen current 30B runtime

Qwen3-30B-A3B exact-Q4/top-8:
- backend commit `96958de`;
- sustained 3×32 `1.115874`, `1.229233`, `1.254611 tok/s`;
- production median `1.229233 tok/s`;
- expert-major/canonicalization exact and safe.

## Closed speed paths

Routing sparsity: `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`.

Lower-bit Q2/Q3 expert requantization: `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`; both technically valid but failed frozen fidelity.

DFlash: closed.

Lossless speculative verifier ceiling:
`SPEC_VERIFY_FRONTIER_NOT_PROMISING`.

Result:
`research/architecture/loom-30b-lossless-speculative-verification-ceiling-001-result.md`.

K=4 oracle ceiling final median `1.792925 tok/s` with 40.93% expert reuse and `568,641,024 B/output-token`; exactness/safety PASS. This is an upper bound only, not production speed. K=8 was INVALID.

Conclusion: do not spend current effort on a real drafter for the existing verifier. The 5 tok/s target requires a materially different architecture/runtime target.

## Current — Qwen3.8 Portability Readiness 001

Preregistration:
`research/architecture/loom-qwen38-portability-readiness-001-preregistration.md`.

Purpose: decide, before large downloads, whether LOOM can partition and execute on M1/8GB:

### Qwen3.8-27B
- dense 27B;
- reference MLX Q4 payload ~16.1 GB;
- candidate LOOM mechanism: bounded layer streaming;
- key question: one-layer + mandatory resident state <=5.5 GiB and acceptable projected full-layer bytes/token.

### Qwen3.8-Flash-Next
- reference Q4+MTP payload ~113.209 GB / 105.434 GiB;
- `qwen4_exp`, 48 layers;
- 125B main / 6B activated token;
- 51B n-gram embedding;
- 4B native MTP;
- 512 routed experts, 10 active +1 shared;
- candidate LOOM mechanisms: expert-major storage/resolver, deterministic n-gram lookup/offload, bounded shared/backbone/state residency, optional native MTP.

Readiness checkpoint constraints:
- metadata/config/index only;
- <=100 MiB network per candidate;
- no weight shards;
- no model forward;
- no package upgrades.

Outcomes:
- `QWEN38_BOTH_PORTABLE`;
- `QWEN38_FLASH_ONLY_PORTABLE`;
- `QWEN38_27B_ONLY_PORTABLE`;
- `QWEN38_NEITHER_PORTABLE`;
- `QWEN38_READINESS_INCONCLUSIVE`.

PORTABLE means static LOOM working-set/ABI feasibility only.

## After readiness

Acquire and run only candidates that pass readiness, one at a time in ranked order.

For each actual candidate:
1. exact source/artifact provenance;
2. Integration Readiness Protocol v1;
3. static resolver/streaming replay;
4. first-token correctness;
5. bounded 32-token sustained run;
6. memory/swap/safety;
7. canonicalize only if useful.

## Final model bake-off

Once the feasible Qwen3.8 candidates run locally, compare on identical M1/8GB constraints:
1. canonical `Qwen3-30B-A3B`;
2. `Qwen3.8-27B` if portable;
3. `Qwen3.8-Flash-Next` if portable.

Measure:
- sustained tok/s and TTFT;
- RAM/swap/disk;
- intelligence/quality on a frozen common LOOM eval set;
- instruction following/refusal/steerability;
- winner for raw speed;
- winner for intelligence;
- winner for combined practical use.

Do not infer the winner from external hardware/vendor benchmarks.