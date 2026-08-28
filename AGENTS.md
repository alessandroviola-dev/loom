# LOOM — Pi Agent Protocol

Version: 3.43
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent rescue or post-hoc gate relaxation;
3. comparison invalid if more than intended treatment factor changes;
4. expensive/network work requires retained/resumable artifacts and pre-dispatch caps;
5. fail closed before expensive execution;
6. no performance claim from INVALID/UNRESOLVED/INCONCLUSIVE evidence;
7. do not advance from stale canonical docs except inside a fully preregistered compound funnel;
8. required gate instrumentation must persist before evidence is accepted;
9. failed frozen methods are not silently modified/rerun under the same checkpoint;
10. control/API semantics affecting validity must be established locally;
11. Integration Readiness Protocol v1 is mandatory before integration coding/model forward: `research/architecture/loom-integration-readiness-protocol-v1.md`;
12. producer/consumer compatibility must be proven mechanically before adapter coding;
13. static adapter dry-run with zero unresolved accesses and forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts are not promoted implicitly to runtime artifacts;
15. metadata/coverage/provenance checks use deterministic scripts/JSON where possible;
16. settled mechanisms are not reopened absent regression/materially different target;
17. production regressions require a new bounded preregistered repair;
18. validation-only metadata stays out of hot runtime when representable by a smaller contract;
19. accepted production code is canonical only after review and Git persistence;
20. quality-trading speed work freezes fidelity metrics/thresholds before candidate results;
21. verifier-ceiling experiments using oracle proposals are upper bounds only and never production speed;
22. large new-model downloads require a metadata-only portability/readiness gate first.

External root: `<external-archive>/`

## Frozen Qwen3-30B-A3B production baseline

Canonical backend:
`scripts/loom_30b_moe_expert_major_backend_001.py`

Current production baseline commit:
`96958de` — persistent PACKED fd.

Exact-Q4/top-8 sustained throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.

Full Q4 expert traffic:
`962,592,768 B/output-token`.

Settled/closed speed paths:
- expert-major physical I/O/runtime/canonicalization: ACCEPTED;
- exact-Q4 speed frontier: ADVANCED only via persistent fd;
- routing sparsity: `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`;
- Q2/Q3 expert requantization: `EXPERT_QUANT_FRONTIER_NO_ACCEPTABLE_GAIN`;
- DFlash: CLOSED;
- real speculative drafter on this verifier: NOT JUSTIFIED by oracle ceiling.

## Lossless Speculative Verification Ceiling 001 — CLOSED / NOT PROMISING

`LOOM_30B_LOSSLESS_SPECULATIVE_VERIFICATION_CEILING_001 = SPEC_VERIFY_FRONTIER_NOT_PROMISING`.

Result:
`research/architecture/loom-30b-lossless-speculative-verification-ceiling-001-result.md`

Evidence:
`results-local/research/30b-lossless-speculative-verification-ceiling-001/20260828T101836Z/`

Exact K=2 ceiling:
- `1.548806 tok/s`;
- `22.36%` expert-payload reuse;
- `747,325,440 B/output-token`.

Exact K=4 ceiling:
- candidate `1.776372 tok/s`;
- final 3×32: `1.792925`, `1.807852`, `1.785392 tok/s`;
- median `1.792925 tok/s`;
- `40.93%` expert reuse;
- `568,641,024 B/output-token`;
- exactness/safety PASS.

K=8: INVALID exactness; no performance evidence.

The K=4 median is only an oracle/verifier upper bound. Even with perfect proposals and zero drafter cost it is below the frozen promising threshold `2.458466 tok/s` and far below `5 tok/s`. Do not build/download a real drafter for the current verifier absent a materially new verifier architecture.

Current Qwen3-30B-A3B production comparison baseline remains `1.229233 tok/s`, not `1.792925`.

## Current checkpoint — QWEN3.8 PORTABILITY READINESS 001

`LOOM_QWEN38_PORTABILITY_READINESS_001`

Preregistration:
`research/architecture/loom-qwen38-portability-readiness-001-preregistration.md`

Purpose: before downloading large weights, determine whether LOOM can partition/execute on M1/8GB:
1. `Qwen3.8-27B` using reference `mlx-community/Qwen3.8-27B-4bit` (~16.1 GB);
2. `Qwen3.8-Flash-Next` using reference `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP` (~113.209 GB / 105.434 GiB).

Frozen external architecture facts to mechanically revalidate:
- Qwen3.8-27B is dense;
- Flash-Next is `qwen4_exp`, 48 layers, 125B main / 6B active per token, +51B n-gram embedding, +4B native MTP, 512 routed experts with 10 active +1 shared.

Readiness network cap:
- metadata/small config/index only;
- <=100 MiB per candidate;
- NO weight shard download;
- NO package upgrade;
- NO model forward.

Candidate A gate: derive dense layer-streaming contract, projected resident working set and bytes/token; require one-layer + mandatory state <=5.5 GiB and no full-model residency requirement.

Candidate B gate: derive expert-major, n-gram offload, shared/backbone/state and optional MTP contracts; require bounded active working set <=5.5 GiB, deterministic expert addressing, bounded n-gram access, and no full-artifact residency requirement.

Final outcomes:
- `QWEN38_BOTH_PORTABLE`;
- `QWEN38_FLASH_ONLY_PORTABLE`;
- `QWEN38_27B_ONLY_PORTABLE`;
- `QWEN38_NEITHER_PORTABLE`;
- `QWEN38_READINESS_INCONCLUSIVE`.

PORTABLE is a static feasibility result, not a speed/quality claim.

After readiness: acquire/run portable candidates one at a time in ranked order, then final matched bake-off on sustained tok/s/TTFT, RAM/swap/disk, intelligence/quality, instruction/refusal/steerability.