# LOOM — Pi Agent Protocol

Version: 3.35
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
18. validation-only metadata/provenance must not remain in the hot runtime process when it can be proven offline and represented by a smaller runtime contract.

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

All payload/hash, physical-byte, read-structure, memory and swap gates PASS. Raw expert-major physical-I/O causality is settled.

## Full-Bank Runtime Funnel 002 — ACCEPTED

`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Result: `research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-result.md`
Evidence: `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`

Accepted evidence:
- readiness PASS: source `6144/6144`, disk gate PASS;
- full bank PASS: `6144` entries, `15,401,484,288 B`, full hash/provenance PASS;
- static dry-run PASS: `18,048` accesses, `0` unresolved/fallback/cache;
- exactness PASS: 3 full 48-layer decode positions, identical routing and raw final-logit float32 SHA;
- runtime ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall;
- RSS gate PASS; swap delta `0 MiB`; no unsafe pressure/fallback/persistent expert cache.

Decision: full-bank expert-major remains the accepted runtime direction. Do not re-run full physical-I/O or runtime acceptance testing absent a materially different target/runtime.

## Canonicalization 001 — NO-GO, RSS ONLY

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001 = EXPERT_MAJOR_CANONICALIZATION_NO_GO`.

Result: `research/architecture/loom-30b-expert-major-canonicalization-001-result.md`
Evidence: `results-local/research/30b-expert-major-canonicalization-001/20260827T084858Z/`
Working-tree file: `scripts/loom_30b_moe_expert_major_backend_001.py`.

Passed static/exactness/performance; failed only RSS: SOURCE `191,348,736 B`, PACKED `402,259,968 B`, delta `+201.14 MiB` > frozen `+128 MiB` gate.

## Canonicalization RSS Repair 001 — INCONCLUSIVE

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RSS_REPAIR_001 = EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`.

Result: `research/architecture/loom-30b-expert-major-canonicalization-rss-repair-001-result.md`
Evidence: `results-local/research/30b-expert-major-canonicalization-rss-repair-001/20260827T104738Z/`

Concrete finding:
- PACKED alone parsed the full `6144 × 9` validation manifest in the runtime process;
- compacting resolver metadata removed `41,066,169 B` of live Python objects, but allocator high-water RSS remained;
- SOURCE and PACKED therefore had non-equivalent allocator histories and the one-pair RSS/performance comparison was inadmissible.

Still PASS:
- artifact integrity/provenance;
- `6144/6144`;
- `18,048` replay, zero unresolved/fallback/cache;
- 3-position exactness;
- swap `0 MiB`, no unsafe pressure.

Informative only, not accepted as decision evidence: smoke ratio `0.869104911`; post-prefill/decode RSS was lower for PACKED, but peak comparison was contaminated by startup allocator history.

## Current checkpoint — CANONICALIZATION RUNTIME CONTRACT 002

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002`

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-preregistration.md`

Purpose: move full manifest/provenance validation completely out of the hot runtime process and give PACKED only a minimal prevalidated resolver contract.

Frozen resolver selection:
1. offline validate full accepted artifact/manifest;
2. if the manifest proves fixed-size contiguous lexicographic `(layer,expert)` placement, use `FORMULAIC_RESOLVER` with deterministic offset computation and a tiny provenance contract;
3. otherwise use `COMPACT_INDEX_RESOLVER` with only runtime-required per-expert fields;
4. no other representation or threshold change.

Then:
- minimally repair the existing canonical working-tree backend;
- static `6144/6144` + `18,048` replay, zero unresolved/fallback/cache;
- prove hot PACKED child does not parse full validation manifest/provenance trees;
- same 3-position exactness;
- exactly one fresh-process SOURCE->PACKED RSS/performance smoke after offline preflight validator has exited.

Unchanged GO gates:
- PACKED/SOURCE decode wall `<=0.95`;
- PACKED peak RSS `<= SOURCE +128 MiB`;
- PACKED swap delta `<= SOURCE +64 MiB`;
- exactness PASS;
- no fallback/cache/unsafe pressure.

Pi may edit the existing canonical script and directly related reusable helper code only. Pi must not commit/push or edit project decision docs.
