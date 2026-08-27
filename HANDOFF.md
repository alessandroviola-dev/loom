# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — full-bank expert-major runtime and canonical production design are ACCEPTED. Canonicalization Runtime Contract 002 = GO. Final local backend file awaits review/commit before moving to the next serving bottleneck.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002_GO_AWAITING_CODE_REVIEW`
Pi context: `/AGENTS.md` v3.36.

## Settled expert-major evidence

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE access ratio `0.595950` = `40.405%` lower expert-access wall.

Full-bank runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Evidence: `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`.

Accepted runtime facts:
- full bank `6144/6144`, `15,401,484,288 B`;
- full hash/provenance PASS;
- `18,048` static accesses, zero unresolved/fallback/cache;
- three-position exactness PASS;
- A/B ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS, swap `0 MiB`, no unsafe pressure/fallback/persistent cache.

This three-pair result remains the accepted practical performance estimate.

## Canonicalization history

Canonicalization 001 failed only its frozen RSS gate (`+201.14 MiB` vs `+128 MiB`).

RSS Repair 001 identified that PACKED alone parsed the full 6144-entry × 9-component validation manifest in the hot process. Resolver compaction removed `41,066,169 B` live Python metadata, but allocator high-water made that comparison inadmissible.

This led to the runtime-contract design: validation/provenance offline, tiny resolver in the hot process.

## Canonicalization Runtime Contract 002 — GO

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RUNTIME_CONTRACT_002 = EXPERT_MAJOR_CANONICALIZATION_GO`.

Result:
`research/architecture/loom-30b-expert-major-canonicalization-runtime-contract-002-result.md`.

Evidence:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/`.

Selected resolver: `FORMULAIC_RESOLVER`.

Fixed-layout invariant PASS:
- `6144` records;
- lexicographic `48 × 128` expert order;
- constant `2,506,752 B` payload;
- contiguous affine offsets;
- exact bank size `15,401,484,288 B`.

Runtime contract:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/20260827T115816Z/runtime-contract.json`
SHA-256 `ee43eaa935e957d40856898c73fe238ff626c880514a8deb9b73491567657aba`.

Static production gate PASS:
- offline validation: `6144` payload hashes + `55,296` source-component provenance hashes;
- resolver coverage `6144/6144`;
- `18,048` replay;
- zero unresolved/ambiguous/invalid-range/fallback/cache;
- hot PACKED runtime recorded zero full-manifest opens/parses and no 9-component provenance trees.

Exactness regression PASS on the same three frozen positions; routed expert order and raw float32 final-logit SHA identical.

Bounded canonicalization smoke PASS:
- SOURCE `4.379309374 s`;
- PACKED `1.924031958 s`;
- ratio `0.439345978`;
- SOURCE peak RSS `432,537,600 B`;
- PACKED peak RSS `305,020,928 B`;
- PACKED peak delta `-127,516,672 B`;
- swap delta SOURCE `+987.37 MiB`, PACKED `-8.00 MiB`;
- zero fallback/cache/unsafe pressure.

The smoke ratio is only regression evidence; do not use it as a replacement performance estimate.

## Exact next step — final local code review

The accepted implementation is still local/uncommitted:
`scripts/loom_30b_moe_expert_major_backend_001.py`.

Before committing:
1. capture the exact final file/diff and SHA without editing it;
2. review minimality, explicit SOURCE/PACKED separation, formulaic offset bounds, fail-closed paths, no hidden SOURCE fallback, no persistent cache, no hard-coded ephemeral evidence path dependency, and runtime-contract validation;
3. if review PASS, commit/push the production backend;
4. update canonical docs to state code is persisted;
5. then identify the next measured serving bottleneck rather than reopening expert-major validation.

No additional runtime/scientific funnel is needed unless the code review reveals a material defect.
