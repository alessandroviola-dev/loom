# LOOM — Pi Agent Protocol

Version: 3.37
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
19. accepted production code is canonical only after final diff review and Git persistence.

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

## Expert-major — ACCEPTED AND CANONICAL

Physical-I/O: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime: `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Accepted three-pair runtime ratios: `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall. Exactness/RSS/swap/fallback/cache gates PASS.

Canonicalization Runtime Contract 002: `EXPERT_MAJOR_CANONICALIZATION_GO`.
Result: `research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-result.md`.
Evidence: `results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/`.
Selected runtime resolver: `FORMULAIC_RESOLVER` after fixed-layout PASS (`6144`, lexicographic `48×128`, constant `2,506,752 B`, affine contiguous offsets, exact `15,401,484,288 B`).
Runtime-contract SHA-256: `ee43eaa935e957d40856898c73fe238ff626c880514a8deb9b73491567657aba`.
Static `6144/6144`, `18,048` replay, hot-manifest-open=0, 3-position exactness, RSS/swap/safety all PASS.
The one-pair canonicalization smoke ratio `0.439345978` is regression evidence only; the accepted effect estimate remains median `0.794284` from the three-pair runtime funnel.

Canonical implementation:
`scripts/loom_30b_moe_expert_major_backend_001.py`
Commit: `36414d7` (`feat: canonicalize 30B expert-major backend`).
Final reviewed local SHA-256 before commit: `b3d198308c8471832d04c79433d1c67643f30f1b1d9e2b7df0cc542b668c9ea2`.

Do not reopen expert-major physical-I/O, runtime acceptance, RSS repair, or canonicalization absent a material regression or different target/runtime.

## Current checkpoint — POST-EXPERT-MAJOR BOTTLENECK SELECTION

The expert-major phase is CLOSED.

Next scientific action: measure the canonical post-expert-major decode path and identify the new dominant serving bottleneck before selecting another intervention.

Use the canonical expert-major backend as the baseline. Do not optimize based only on the pre-expert-major decomposition because relative bottleneck shares have changed.

Preferred next categories to distinguish from measured evidence include:
- external expert access residual;
- expert payload materialization / host-to-MLX conversion;
- MLX evaluation/synchronization barriers;
- routing / dispatch;
- non-routed backbone compute;
- KV / attention / output head;
- other directly measured exclusive residual.

The next profile must be bounded, attribution-first, non-invasive, and must not reopen already-settled expert-major comparisons.
