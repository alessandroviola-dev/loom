# LOOM — Pi Agent Protocol

Version: 3.36
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
12. producer/consumer compatibility must be proven mechanically before adapter coding: `consumer_required_coverage ⊆ provider_available_coverage`;
13. static adapter dry-run with zero unresolved accesses and zero forbidden fallback must PASS before model forward;
14. benchmark/trace-scoped artifacts must not be promoted implicitly to general runtime artifacts;
15. metadata/coverage/provenance checks should use deterministic scripts/JSON rather than broad Pi reasoning;
16. once a mechanism is accepted by causal + runtime funnels, do not reopen settled validation during productionization unless a canonicalization regression appears;
17. canonicalization regressions may be repaired only in a new preregistered checkpoint with original acceptance thresholds unchanged and only the demonstrated production regression in scope;
18. validation-only metadata/provenance must not remain in the hot runtime process when it can be proven offline and represented by a smaller runtime contract;
19. accepted production code is not canonical in Git until its final working-tree diff is reviewed and committed; do not confuse scientific/productionization GO with repository persistence.

External root: `<external-archive>/`
BF16 cache: `<external-archive>/bf16-cache/`

## Mission / stable 30B target

Mission: **Big models. Small machines.** Practical ~27B/32B local AI on Apple M1/8GB.
Q4 target: `results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable facts:
- 48 MoE layers, 128 experts/layer, top-k 8;
- routed identities `48 × 128 = 6144`;
- payload `16,220,499,968 B`;
- resident non-routed `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- raw 4-GiB global LRU rejected.

## DFlash — CLOSED

Final: `BF16_TARGET_RECOVERY_SIGNAL_NOT_MET_EARLY_STOP`. Do not reopen absent a new independent mechanism.

## Expert-major physical-I/O — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.

Valid first-touch PACKED/SOURCE ratios: `0.602456`, `0.595950`, `0.581170`; median `0.595950` = `40.405%` lower expert-access wall.

Raw expert-major physical-I/O causality is settled.

## Full-Bank Runtime Funnel 002 — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Result: `research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-result.md`
Evidence: `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`

Accepted runtime evidence:
- full bank `6144/6144`, `15,401,484,288 B`;
- full hash/provenance PASS;
- `18,048` static accesses, zero unresolved/fallback/cache;
- 3-position full-runtime exactness PASS;
- runtime ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS; swap `0 MiB`; no unsafe pressure/fallback/persistent expert cache.

This remains the accepted practical performance estimate.

## Canonicalization history

Canonicalization 001: `EXPERT_MAJOR_CANONICALIZATION_NO_GO` on RSS only.
RSS Repair 001: `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE` because PACKED alone parsed the full `6144 × 9` validation manifest in-process, contaminating allocator high-water.

These did not revoke the accepted mechanism/runtime direction.

## Canonicalization Runtime Contract 002 — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002 = EXPERT_MAJOR_CANONICALIZATION_GO`.

Result:
`research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-result.md`

Evidence:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/`

Selected resolver: `FORMULAIC_RESOLVER`.

Fixed-layout contract PASS:
- 6144 records;
- lexicographic `48 × 128` order;
- constant `2,506,752 B` expert size;
- contiguous affine offsets;
- total bank `15,401,484,288 B`.

Runtime contract:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/runtime-contract.json`
SHA-256: `ee43eaa935e957d40856898c73fe238ff626c880514a8deb9b73491567657aba`.

Static production gate PASS:
- offline full validation `6144` payloads / `55,296` source components;
- resolver `6144/6144`;
- `18,048` replay;
- zero unresolved/ambiguous/invalid/fallback/cache;
- hot PACKED process opens/parses full validation manifest `0` times.

Exactness PASS at all 3 frozen positions with identical routing and raw float32 final-logit SHA.

Bounded canonicalization smoke PASS:
- SOURCE `4.379309374 s`;
- PACKED `1.924031958 s`;
- ratio `0.439345978 <=0.95`;
- SOURCE peak RSS `432,537,600 B`;
- PACKED peak RSS `305,020,928 B`;
- PACKED delta `-127,516,672 B`;
- swap SOURCE `+987.37 MiB`, PACKED `-8.00 MiB`, frozen matched gate PASS;
- zero fallback/cache/unsafe pressure.

The single smoke is only a production-regression check; do not replace the accepted three-pair runtime estimate with it.

## Current checkpoint — FINAL CODE REVIEW / COMMIT

The canonical implementation currently exists only in the local working tree:
`scripts/loom_30b_moe_expert_major_backend_001.py`.

It has productionization GO but is not yet persisted in Git.

Next exact action:
1. inspect the final local file/diff without modifying it;
2. review for accidental scope expansion, hidden fallback/cache, unsafe paths, hard-coded ephemeral evidence paths, and maintainability;
3. if review PASS, commit/push this implementation with canonical docs;
4. only then move to the next serving bottleneck.

Do not run another scientific/runtime funnel unless code review exposes a material implementation defect requiring a new bounded checkpoint.
