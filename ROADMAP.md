# LOOM Roadmap

Last updated: 2026-08-27
Current: `EXPERT_MAJOR_CANONICALIZATION_GO` from Runtime Contract 002
Strategic next: final local backend review/commit, then return to the next measured 30B serving bottleneck
Canonical context: `/AGENTS.md` v3.36.

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

Expert-major is accepted. Do not repeat physical-I/O/full-runtime acceptance absent a materially different runtime or regression.

## Productionization path

Canonicalization 001:
- static/exactness/performance PASS;
- RSS NO-GO because hot PACKED process carried validation-manifest allocation history.

RSS Repair 001:
- identified full `6144 × 9` manifest parsing as the production-only RSS contaminant;
- live resolver metadata reduced by `41,066,169 B`;
- result INCONCLUSIVE because allocator histories still differed.

Runtime Contract 002 moved full validation entirely out of the hot process.

## Canonicalization Runtime Contract 002 — GO

Result:
`research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-result.md`.

Evidence:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/`.

Selected `FORMULAIC_RESOLVER` because the accepted bank proves:
- 6144 lexicographically ordered expert records;
- constant `2,506,752 B` expert size;
- contiguous affine placement;
- exact total `15,401,484,288 B`.

Runtime contract SHA-256:
`ee43eaa935e957d40856898c73fe238ff626c880514a8deb9b73491567657aba`.

Production gates:
- offline full validation PASS (`6144` payloads / `55,296` source components);
- runtime resolver `6144/6144` PASS;
- `18,048` access replay PASS;
- zero unresolved/ambiguous/invalid/fallback/cache;
- hot runtime full-manifest opens/parses `0`;
- 3-position routing/raw float32-logit exactness PASS.

One-pair production-regression smoke:
- SOURCE `4.379309374 s`;
- PACKED `1.924031958 s`;
- ratio `0.439345978 <=0.95` PASS;
- SOURCE peak RSS `432,537,600 B`;
- PACKED peak RSS `305,020,928 B`;
- PACKED delta `-127,516,672 B` PASS;
- matched swap gate PASS;
- zero fallback/cache/unsafe pressure.

Do not treat `0.439345978` as a new effect estimate. The accepted performance estimate remains the three-pair runtime-funnel median `0.794284`.

## Immediate next — persist accepted production code

Local working-tree implementation:
`scripts/loom_30b_moe_expert_major_backend_001.py`.

It is accepted by the canonicalization gates but not yet stored in Git.

Next actions:
1. review exact final file/diff and file hash;
2. reject accidental scope expansion, hidden fallback/cache, ephemeral hard-coded paths, unsafe offset/range behavior, or maintainability defects;
3. if review PASS, commit/push the production backend;
4. update AGENTS/HANDOFF/ROADMAP to mark implementation persisted;
5. profile the post-expert-major runtime and select the next dominant serving bottleneck from measured evidence.

No additional expert-major benchmark should be run merely to reconfirm already accepted results.
