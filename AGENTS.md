# LOOM — Pi Agent Protocol

Version: 3.38
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

Pi reads this file as persistent context. WP prompts carry only the active delta.

## Roles / synchronization protocol

Pi: local inspection/execution, minimum authorized changes, bounded tests, `results-local/` evidence, mechanical self-repair only.
ChatGPT: scientific direction, Git/GitHub, result docs, HANDOFF/ROADMAP.
Pi must not Git commit/push/PR/edit project decision docs unless explicitly authorized.

After every significant scientific checkpoint, ChatGPT updates canonical GitHub state and the user pulls before the next independent Pi WP.

A fully preregistered compound funnel may traverse internal stages without intermediate Git/pull only when question, outcomes, branches, quantitative gates, workload/fallback order, resource bounds and fail-closed behavior are frozen before execution.

## Core rules

1. one-factor comparisons; deterministic inputs; exact provenance;
2. no silent scientific rescue or post-hoc gate relaxation;
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
13. static adapter dry-run with zero unresolved accesses and zero forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts must not be promoted implicitly to general runtime artifacts;
15. metadata/coverage/provenance checks should use deterministic scripts/JSON rather than broad Pi reasoning;
16. settled mechanisms are not reopened absent regression or materially different target/runtime;
17. production regressions require a new bounded preregistered repair with original thresholds unchanged;
18. validation-only metadata/provenance stays out of the hot runtime when representable by a smaller runtime contract;
19. accepted production code is canonical only after review and Git persistence.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable current target

Mission: **Big models. Small machines.** Practical large open-weight AI on Apple M1/8GB.
Current Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable current facts:
- Qwen3-30B-A3B: 48 MoE layers, 128 experts/layer, top-k 8;
- routed identities `48 × 128 = 6144`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- DFlash path closed;
- raw 4-GiB global LRU rejected.

## Expert-major — ACCEPTED, CANONICAL, CLOSED

Physical-I/O: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime: `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted three-pair runtime ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower decode wall. Exactness/RSS/swap/fallback/cache gates PASS.

Canonicalization Runtime Contract 002: `EXPERT_MAJOR_CANONICALIZATION_GO` with `FORMULAIC_RESOLVER`.
Static `6144/6144`, `18,048` replay, hot-manifest-open=0, 3-position exactness, RSS/swap/safety PASS.

Canonical implementation:
`scripts/loom_30b_moe_expert_major_backend_001.py`
Commit: `36414d7` (`feat: canonicalize 30B expert-major backend`).
Reviewed SHA-256: `b3d198308c8471832d04c79433d1c67643f30f1b1d9e2b7df0cc542b668c9ea2`.

Do not reopen expert-major validation absent regression or a new model/runtime.

## Current checkpoint — POST-CANONICAL SPEED FRONTIER 001

`LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001`

Preregistration:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-preregistration.md`

Goal: maximize sustained decode throughput of the canonical Qwen3-30B-A3B Q4 runtime while preserving exact semantics first. Aspirational target: `>=5.0 tok/s`.

Compound stages:
1. sustained 32-token canonical baseline + bounded attribution;
2. persistent PACKED fd if per-expert open/close remains in the hot path;
3. materialization/synchronization collapse if preregistered precondition is met;
4. bounded single-expert allocation/copy reduction if still justified;
5. bounded one-ahead overlap if residual external I/O remains >=20%;
6. final 3 × 32-token sustained measurement.

Each treatment is retained only if it passes exactness/safety and its frozen minimum speed-gain gate; otherwise it is reverted before the next stage.

Final outcomes:
- `SPEED_5TPS_REACHED`
- `SPEED_FRONTIER_ADVANCED`
- `SPEED_FRONTIER_NO_EXACT_GAIN`
- `SPEED_FRONTIER_INCONCLUSIVE`

No quantization change, model-quality tradeoff, DFlash, full-bank rebuild, cache/eviction work, or threshold rescue in this checkpoint.

## Strategic next after speed frontier — next-model bake-off

After freezing the fastest accepted Qwen3-30B-A3B runtime, evaluate whether LOOM can adapt to newer open-weight candidates:
- Qwen3.8-27B (dense 27B);
- Qwen3.8-Flash-Next (ultra-sparse MoE with N-gram embedding and MTP).

The later bake-off must compare on the same local hardware and quantization-quality budget:
- sustained tok/s;
- practical memory/swap;
- intelligence/quality on a fixed LOOM eval set;
- instruction-following/refusal/steerability characteristics.

Do not assume architecture portability: the dense 27B and Flash-Next require separate readiness contracts before model execution.
