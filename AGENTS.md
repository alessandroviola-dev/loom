# LOOM — Pi Agent Protocol

Version: 3.40
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
19. accepted production code is canonical only after review and Git persistence;
20. quality-trading speed work must freeze fidelity metrics/thresholds before candidate results are observed.

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
- routed expert payload/token at top-8 = `384 × 2,506,752 = 962,592,768 B`;
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
Base canonicalization commit: `36414d7`.

Do not reopen expert-major validation absent regression or a new model/runtime.

## Post-Canonical Speed Frontier 001 — ADVANCED AND PERSISTED

`LOOM_30B_POST_CANONICAL_SPEED_FRONTIER_001 = SPEED_FRONTIER_ADVANCED`.

Result:
`research/architecture/loom-30b-post-canonical-speed-frontier-001-result.md`
Evidence:
`results-local/research/30b-post-canonical-speed-frontier-001/20260827T131329Z/`

Stage-0 exact sustained baseline: `1.063941 tok/s`.
Ranked wall attribution:
- expert file I/O `44.61%`;
- expert compute `26.50%`;
- non-expert/backbone `14.74%`;
- materialization/synchronization `11.51%`;
- routing `2.64%`.

Treatment results:
- persistent process-lifetime PACKED fd: `+8.65%`, exact/safe, RETAINED;
- synchronization collapse: `-30.38%`, reverted;
- allocation/copy reduction: `+3.60%` signal but RSS +151,879,680 B > +32 MiB, reverted;
- one-ahead overlap: `+8.45%` signal but RSS +162,676,736 B > +32 MiB, reverted.

Final 3×32-token exact throughput:
`1.115874`, `1.229233`, `1.254611 tok/s`; median `1.229233 tok/s`.
p50 `0.825660 s`; p95 `1.217692 s`; peak RSS `404,340,736 B`; swap `0`; exactness PASS.

Persistent-FD implementation reviewed and persisted:
- file: `scripts/loom_30b_moe_expert_major_backend_001.py`;
- validated file SHA-256: `6bb4cfd46f7ea9f1f54d680ef146b84f85a3475377511dfcc89eb18a4733a4e1`;
- Git commit: `96958de` (`perf: keep packed expert file descriptor open`).

This commit is the exact-Q4 speed baseline for subsequent work.

Remaining dominant bottleneck: expert file I/O. At top-8 Q4, `5 tok/s` would require about `4.81 GB/s` expert payload traffic alone, before compute/backbone/materialization. Exact-Q4 micro-optimization is therefore not expected to reach 5 tok/s by itself.

## Current checkpoint — ROUTING SPARSITY SPEED/QUALITY FRONTIER 001

`LOOM_30B_ROUTING_SPARSITY_SPEED_QUALITY_FRONTIER_001`

Preregistration:
`research/architecture/loom-30b-routing-sparsity-speed-quality-frontier-001-preregistration.md`

Purpose: reduce expert bytes/compute per token by dynamically executing the smallest subset of the original top-8 experts that covers a frozen fraction of router mass, under fidelity gates frozen before candidate results.

Frozen baseline:
- code commit `96958de`;
- exact-Q4 sustained median `1.229233 tok/s`;
- top-8 routed expert semantics are the teacher/reference.

Frozen routing-mass variants only:
- `tau=0.95`;
- `tau=0.90`;
- `tau=0.80`;
- `tau=0.70`.
No other threshold/fixed-top-k rescue is allowed.

Quality oracle: 8 fixed prompts ×16 teacher-forced continuation positions = 128 positions, frozen from the exact Q4 teacher before candidate results.

USABLE fidelity requires all:
- reference top-1 agreement >=90%;
- reference top-1 in candidate top-3 >=97%;
- mean KL(reference||candidate) <=0.10 nats;
- no NaN/Inf.

STRICT requires >=95% top1, >=99% top3 inclusion, KL <=0.05.

Only quality-valid variants with >=10% speed gain and safety PASS are eligible. Select the fastest eligible variant; tie within 2% favors fidelity/higher tau.

After selecting sparsity, one bounded raw-payload one-ahead overlap repair is allowed only if residual expert I/O remains >=20%, with one raw expert maximum extra residency and +32 MiB RSS bound.

Final 3×32-token decision classes:
- `SPARSITY_5TPS_REACHED_QUALITY_GATED`;
- `SPARSITY_FRONTIER_ADVANCED`;
- `SPARSITY_FRONTIER_NO_ACCEPTABLE_GAIN`;
- `SPARSITY_FRONTIER_INCONCLUSIVE`.

No expert quantization change, model download, full-bank rebuild, DFlash, or threshold rescue in this checkpoint.

## Strategic next after sparsity frontier

If still materially below 5 tok/s, next high-leverage frontier is lower-bit expert payload quantization (Q3/Q2 or mixed precision) under a separate frozen quality gate, optionally combined only with the selected sparsity point.

After the current 30B speed frontier is frozen, run the planned same-hardware bake-off against Qwen3.8-27B and Qwen3.8-Flash-Next using matched speed/memory/quality/steerability evaluation.
