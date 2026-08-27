# LOOM Roadmap

Last updated: 2026-08-27
Current: `EXPERT_MAJOR_CANONICALIZATION_NO_GO` from Canonicalization 001, RSS gate only
Strategic next: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RSS_REPAIR_001`
Canonical context: `/AGENTS.md` v3.34.

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

## Canonicalization 001 — NO-GO on RSS only

Result: `research/architecture/loom-30b-expert-major-canonicalization-001-result.md`.
Evidence: `results-local/research/30b-expert-major-canonicalization-001/20260827T084858Z/`.

New working-tree file:
`scripts/loom_30b_moe_expert_major_backend_001.py` (214 insertions).

Passed:
- artifact recovery/reuse;
- static manifest `6144/6144`;
- `18,048` replay with zero unresolved/ambiguous/invalid/fallback/cache;
- three-position exactness;
- performance smoke ratio `0.938185866 <=0.95`;
- swap `0 MiB`, no unsafe pressure/fallback/cache.

Failed:
- SOURCE peak RSS `191,348,736 B`;
- PACKED peak RSS `402,259,968 B`;
- delta `+201.14 MiB` > `+128 MiB` frozen gate.

This is a productionization allocation/lifetime regression, not a rejection of expert-major.

## Next — Canonicalization RSS Repair 001

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-rss-repair-001-preregistration.md`.

Goal: restore the memory behavior of the already accepted experimental backend in canonical reusable code without changing mechanism or thresholds.

Compound repair flow:
1. deterministic diff of accepted experimental vs canonical PACKED allocation/lifetime behavior;
2. smallest repair limited to demonstrated canonicalization-only memory behavior;
3. static production re-gate (`6144/6144`, `18,048`, zero unresolved/fallback/cache);
4. same three-position exactness gate;
5. one detailed SOURCE->PACKED smoke with RSS milestones.

Unchanged adoption gates:
- smoke ratio `<=0.95`;
- PACKED peak RSS `<= SOURCE +128 MiB`;
- PACKED swap delta `<= SOURCE +64 MiB`;
- exactness PASS;
- no fallback/persistent expert cache/unsafe pressure.

No full-bank rebuild, no new cache, no physical-I/O campaign, no three-pair runtime campaign, no threshold rescue.

## After RSS Repair

If `EXPERT_MAJOR_CANONICALIZATION_GO`: review the final working-tree diff, then commit/push the production backend and make it the canonical selected runtime direction before moving to the next serving bottleneck.

If `EXPERT_MAJOR_CANONICALIZATION_NO_GO`: do not silently iterate. Record the demonstrated remaining production-memory blocker and decide whether a materially different implementation approach is warranted.

If `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`: repair only the concrete environment/instrumentation blocker if bounded; do not reopen expert-major science.
