# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — full-bank expert-major runtime remains ACCEPTED. Canonicalization RSS Repair 001 isolated the remaining issue to validation-manifest parsing/allocator history in the hot PACKED process. A runtime-contract repair is preregistered.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002`
Pi context: `/AGENTS.md` v3.35.

## Settled expert-major evidence

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE access ratio `0.595950` = `40.405%` lower expert-access wall.

Runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Evidence: `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`.

Accepted runtime facts:
- full bank `6144/6144`, `15,401,484,288 B`;
- full hash/provenance PASS;
- `18,048` static accesses, zero unresolved/fallback/cache;
- three-position full-runtime exactness PASS;
- A/B ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS, swap `0 MiB`, no unsafe pressure/fallback/persistent cache.

Do not reopen physical-I/O/runtime acceptance.

## Canonicalization 001

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001 = EXPERT_MAJOR_CANONICALIZATION_NO_GO` only on RSS.

Working-tree code:
`scripts/loom_30b_moe_expert_major_backend_001.py`.

Passed manifest/replay/exactness/performance. Failed RSS: SOURCE `191,348,736 B`, PACKED `402,259,968 B`, delta `+201.14 MiB` > frozen `+128 MiB` gate.

## RSS Repair 001 result

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RSS_REPAIR_001 = EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`.
Result: `research/architecture/loom-30b-expert-major-canonicalization-rss-repair-001-result.md`.
Evidence: `results-local/research/30b-expert-major-canonicalization-rss-repair-001/20260827T104738Z/`.

Concrete root cause:
- PACKED hot process parsed the complete 6144-entry validation manifest with 9 source components per expert;
- compacting to resolver-only fields reduced Python live metadata by `41,066,169 B`;
- allocator high-water remained even after those objects were released;
- SOURCE did not perform equivalent parsing, so the one-pair peak-RSS comparison had divergent allocator history and is not admissible.

Still PASS:
- full-bank integrity/provenance;
- `6144/6144`;
- `18,048` replay, zero unresolved/ambiguous/invalid/fallback/cache;
- 3-position exactness;
- swap `0 MiB`, no unsafe pressure.

Informative but not accepted: SOURCE `4.742729167 s`, PACKED `4.121929209 s`, ratio `0.869104911`. After prefill/warmup/measured tokens PACKED RSS was not elevated, reinforcing that the remaining issue is startup validation/allocator lifetime rather than expert payload caching.

## Exact next step — Canonicalization Runtime Contract 002

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-preregistration.md`.

Goal: separate complete artifact/provenance validation from hot runtime allocation.

Stage 0 offline/preflight:
- validate existing full bank + full manifest in a separate process;
- test fixed-layout invariant: 6144 records, lexicographic `(layer,expert)`, constant `2,506,752 B`, contiguous affine offsets, exact total size;
- if PASS use frozen `FORMULAIC_RESOLVER` and emit a tiny runtime provenance contract;
- otherwise use frozen `COMPACT_INDEX_RESOLVER` with only minimal runtime fields;
- no other resolver branch.

Stage 1:
- minimally repair existing working-tree canonical backend;
- hot PACKED process must never parse the full validation manifest/provenance trees;
- SOURCE unchanged; no fallback/cache; fail closed.

Stage 2:
- compile/static gates;
- full offline validation PASS;
- runtime contract PASS;
- `6144/6144` resolver coverage;
- `18,048` replay, zero unresolved/fallback/cache;
- prove full validation manifest is not loaded in hot PACKED runtime.

Stage 3:
- same 3-position exactness regression.

Stage 4:
- full-manifest validator runs and exits before runtime children;
- exactly one fresh-process pair `SOURCE -> PACKED`;
- one warmup + 3 measured decode tokens;
- detailed RSS milestones.

Frozen GO thresholds unchanged:
- runtime ratio `<=0.95`;
- PACKED peak RSS <= SOURCE +128 MiB;
- PACKED swap <= SOURCE +64 MiB;
- exactness PASS;
- no unsafe pressure/fallback/persistent cache.

Pi may edit the existing uncommitted canonical script and directly related reusable helper code only. Pi must not commit/push or edit decision docs.
