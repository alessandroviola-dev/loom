# LOOM — Active Handoff

Last updated: 2026-08-27
Status: ACTIVE — full-bank expert-major runtime remains ACCEPTED; first canonical production implementation failed only the frozen RSS gate. A bounded canonicalization RSS-repair checkpoint is preregistered.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_RSS_REPAIR_001`
Pi context: `/AGENTS.md` v3.34.

## Settled expert-major evidence

Physical-I/O:
`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002 = EXPERT_MAJOR_GO`.
Median first-touch PACKED/SOURCE access ratio `0.595950` = `40.405%` lower expert-access wall. Exactness/read-structure/physical-byte/memory/swap gates PASS.

Runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.
Evidence: `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`.

Accepted full-bank/runtime facts:
- `6144/6144` experts;
- `15,401,484,288 B` full bank;
- full hash/provenance PASS;
- `18,048` static accesses, zero unresolved/fallback/cache;
- 3-position full-runtime exactness PASS;
- A/B ratios `0.794284`, `0.846718`, `0.768208`; median `0.794284` = `20.5716%` lower measured decode wall;
- RSS PASS, swap `0 MiB`, no unsafe pressure/fallback/persistent cache.

Do not reopen physical-I/O/runtime acceptance.

## Canonicalization 001 result

`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001 = EXPERT_MAJOR_CANONICALIZATION_NO_GO`.
Result: `research/architecture/loom-30b-expert-major-canonicalization-001-result.md`.
Evidence: `results-local/research/30b-expert-major-canonicalization-001/20260827T084858Z/`.

Working-tree code:
`scripts/loom_30b_moe_expert_major_backend_001.py` — new, 214 lines.

PASS:
- accepted artifact recovery/reuse;
- canonical code integration;
- manifest `6144/6144`;
- `18,048` access replay, zero unresolved/ambiguous/invalid/fallback/cache;
- 3-position routing and raw float32-logit SHA exactness;
- smoke SOURCE `4.463661583 s`, PACKED `4.187744208 s`, ratio `0.938185866 <=0.95`;
- swap `0 MiB`, no unsafe pressure/fallback/persistent cache.

FAIL only:
- SOURCE RSS `191,348,736 B`;
- PACKED RSS `402,259,968 B`;
- delta `+201.14 MiB` > frozen `+128 MiB` gate.

Interpretation: productionization allocation/lifetime regression. Accepted mechanism/runtime direction remains intact.

## Exact next step — Canonicalization RSS Repair 001

Preregistration:
`research/architecture/loom-30b-expert-major-canonicalization-rss-repair-001-preregistration.md`.

One bounded repair funnel:
1. compare accepted experimental PACKED backend/runner against the failed canonical script and emit a concrete allocation/lifetime delta report;
2. apply only the smallest demonstrated canonicalization memory-behavior correction;
3. static re-gate: compile, `6144/6144`, `18,048` accesses, zero unresolved/fallback/cache;
4. same 3-position exactness regression;
5. one detailed fresh-process `SOURCE -> PACKED` smoke pair with RSS milestones.

Allowed repair classes are only demonstrated productionization differences: retained validation metadata, file-access/mapping lifetime, temporary payload-buffer allocation/lifetime, treatment-only retained instrumentation, or another directly evidenced canonicalization-only memory delta.

Forbidden: expert-major layout/mechanism changes, routing/math/dtype/KV/scheduling changes, multi-expert cache, SOURCE fallback, full-bank rebuild, threshold relaxation.

Frozen GO thresholds remain:
- runtime smoke ratio `<=0.95`;
- PACKED peak RSS `<= SOURCE +128 MiB`;
- PACKED swap delta `<= SOURCE +64 MiB`;
- exactness PASS;
- no unsafe pressure/fallback/persistent cache.

Pi may edit the existing uncommitted canonical script and directly related runtime code only. Pi must not commit/push or edit decision docs.
