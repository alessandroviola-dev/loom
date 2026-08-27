# LOOM Roadmap

Last updated: 2026-08-27
Current: `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE` from RSS Repair 001
Strategic next: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002`
Canonical context: `/AGENTS.md` v3.35.

## Settled 30B expert-major direction

Raw physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median PACKED/SOURCE access-wall ratio `0.595950`, or `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Accepted runtime evidence:
- full bank `6144/6144`, `15,401,484,288 B`;
- full hash/provenance PASS;
- static replay `18,048` accesses, zero unresolved/fallback/cache;
- 3-position exactness PASS;
- runtime ratios `0.794284`, `0.846718`, `0.768208`, median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS, swap `0 MiB`, no unsafe pressure/fallback/persistent expert cache.

Expert-major is the accepted runtime mechanism. Do not repeat settled physical-I/O or full runtime acceptance testing.

## Canonicalization 001

`EXPERT_MAJOR_CANONICALIZATION_NO_GO` on RSS only.
Working-tree implementation: `scripts/loom_30b_moe_expert_major_backend_001.py`.

It already passed `6144/6144`, `18,048` replay, exactness and performance smoke; initial RSS delta was `+201.14 MiB` vs frozen `+128 MiB` limit.

## RSS Repair 001 — INCONCLUSIVE measurement

Result: `research/architecture/loom-30b-expert-major-canonicalization-rss-repair-001-result.md`.
Evidence: `results-local/research/30b-expert-major-canonicalization-rss-repair-001/20260827T104738Z/`.

Root cause established:
- PACKED alone parsed the complete 6144×9 validation manifest in its runtime process;
- resolver compaction removed `41,066,169 B` live Python metadata;
- allocator high-water remained after release;
- SOURCE/PACKED startup histories therefore differed, invalidating the peak-RSS comparison.

Still valid PASS evidence:
- artifact/provenance;
- `6144/6144`;
- `18,048` replay;
- three-position exactness;
- zero fallback/cache;
- swap `0 MiB`, no unsafe pressure.

Informative only: runtime ratio `0.869104911`; PACKED RSS after prefill/warmup/measured tokens was below SOURCE, but the peak statistic is inadmissible due allocator-history divergence.

## Next — Canonicalization Runtime Contract 002

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-preregistration.md`.

Goal: remove validation-only metadata from the hot runtime entirely.

Compound flow:
1. offline preflight validates full bank + full manifest;
2. deterministic resolver choice:
   - preferred `FORMULAIC_RESOLVER` if manifest proves fixed-size contiguous lexicographic layout;
   - frozen fallback `COMPACT_INDEX_RESOLVER` if not;
3. hot PACKED runtime loads only the tiny runtime contract/resolver, never the full validation manifest/provenance tree;
4. static `6144/6144` + `18,048` replay and explicit proof no full-manifest load in hot child;
5. same 3-position exactness;
6. one fresh-process `SOURCE -> PACKED` smoke after preflight validator exits.

Unchanged gates:
- smoke ratio `<=0.95`;
- PACKED peak RSS <= SOURCE +128 MiB;
- PACKED swap delta <= SOURCE +64 MiB;
- exactness PASS;
- no fallback/persistent cache/unsafe pressure.

No full-bank rebuild, no new cache, no physical-I/O campaign, no 3-pair runtime campaign, no threshold rescue.

## After Runtime Contract 002

If `EXPERT_MAJOR_CANONICALIZATION_GO`: review working-tree diff and generated runtime contract, then commit/push production backend and make it canonical before moving to the next serving bottleneck.

If `EXPERT_MAJOR_CANONICALIZATION_NO_GO`: record the demonstrated production blocker; do not silently iterate or relax thresholds.

If `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`: repair only a new concrete environment/instrumentation blocker if bounded; do not reopen settled expert-major science.
