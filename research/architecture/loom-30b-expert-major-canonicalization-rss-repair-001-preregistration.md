# LOOM 30B Expert-Major Canonicalization RSS Repair 001 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Repair only the canonicalization-specific RSS regression observed in `LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001`, while preserving the already accepted expert-major mechanism, exact runtime semantics and frozen adoption thresholds.

This is a bounded production regression repair, not a new mechanism experiment.

Final outcomes only:
- `EXPERT_MAJOR_CANONICALIZATION_GO`
- `EXPERT_MAJOR_CANONICALIZATION_NO_GO`
- `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`

## Frozen prior facts

Accepted mechanism/runtime:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Rejected canonical implementation:
`LOOM_30B_EXPERT_MAJOR_CANONICALIZATION_001 = EXPERT_MAJOR_CANONICALIZATION_NO_GO` solely because:
- SOURCE RSS `191,348,736 B`;
- PACKED RSS `402,259,968 B`;
- delta `+201.14 MiB` > frozen `+128 MiB` limit.

The same canonical implementation already passed:
- manifest `6144/6144`;
- `18,048`-access replay with zero unresolved/fallback/cache;
- three-position exactness;
- performance smoke ratio `0.938185866 <=0.95`;
- swap `0 MiB` and no unsafe pressure.

Do not relax any threshold.

## Stage 0 — deterministic regression attribution

No model forward initially.

Inputs:
- accepted experimental backend/runner from:
  `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/`
- failed canonical working-tree implementation:
  `scripts/loom_30b_moe_expert_major_backend_001.py`
- canonicalization evidence:
  `results-local/research/30b-expert-major-canonicalization-001/20260827T084858Z/`

Produce a compact machine-readable allocation/lifetime delta report comparing accepted experimental PACKED behavior to canonical PACKED behavior.

Inspect only directly relevant code and runtime-object lifetimes. Attribute differences among these allowed classes:
1. manifest/provenance data retained unnecessarily in the hot runtime object;
2. different file-access/mapping primitive or mapping lifetime;
3. repeated owned payload-buffer allocations versus bounded/reused single-expert storage;
4. treatment-only instrumentation/logging objects retained across accesses;
5. other directly demonstrated canonicalization-only allocation/lifetime difference.

Do not speculate broadly. Every claimed cause must point to concrete code/object-lifetime evidence.

If no canonicalization-specific memory-behavior delta can be identified from the accepted and canonical implementations: `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE` and STOP.

## Stage 1 — minimal memory-behavior repair

Apply the smallest local working-tree change that makes canonical PACKED allocation/lifetime behavior match the accepted experimental backend as closely as practical.

Allowed repair scope only:
- remove validation-only metadata from hot runtime lifetime after validation;
- restore the accepted file-access/mapping primitive/lifetime;
- restore bounded single-expert temporary-buffer behavior or equivalent bounded reuse;
- eliminate treatment-only retained instrumentation state;
- another directly demonstrated allocation/lifetime correction from Stage 0.

Forbidden:
- changing expert-major file layout;
- changing routing, expert math, quantization, dtypes, KV, scheduling or outputs;
- introducing a multi-expert cache or persistent expert payload cache;
- relaxing RSS/performance thresholds;
- changing the workload;
- adding SOURCE fallback;
- rebuilding the already valid full-bank artifact.

Keep changes minimal/localized. Preserve explicit SOURCE/PACKED backend selection and fail-closed behavior.

## Stage 2 — static production re-gate

Before model forward require:
- syntax/compile checks PASS;
- manifest `6144/6144` PASS;
- mapping uniqueness/bounds PASS;
- retained `18,048` access replay PASS;
- zero unresolved/ambiguous/invalid-range accesses;
- zero SOURCE fallback;
- zero persistent expert cache;
- full-bank artifact integrity/provenance still PASS.

Any deterministic defect introduced by the repair => `EXPERT_MAJOR_CANONICALIZATION_NO_GO` and STOP.
Missing/inaccessible environment dependency => INCONCLUSIVE.

## Stage 3 — exactness regression gate

Use the same accepted frozen workload and exactly three consecutive decode positions.

Require canonical SOURCE vs repaired canonical PACKED:
- identical routed expert IDs/order;
- mapping/hash PASS;
- identical raw final-logit float32 SHA at all three positions;
- zero fallback;
- no persistent expert cache;
- no unsafe memory pressure.

Any valid exactness mismatch => `EXPERT_MAJOR_CANONICALIZATION_NO_GO` and STOP.

## Stage 4 — single detailed RSS/performance smoke

Exactly one fresh-process matched pair, frozen order `SOURCE -> PACKED`.
Use the same accepted workload/settings:
- prefill;
- one unmeasured warmup decode token;
- exactly three measured decode tokens.

Record aggregate measured decode wall and detailed RSS milestones for both arms at minimum:
- process/backend initialized;
- model/runtime ready;
- after prefill;
- after warmup;
- after each of the three measured decode tokens;
- peak RSS.

Also record swap before/after/delta, fallback/cache status and unsafe pressure.

Frozen PASS thresholds are unchanged:
- PACKED/SOURCE aggregate decode wall `<=0.95`;
- PACKED peak RSS `<= SOURCE peak RSS +128 MiB`;
- PACKED swap delta `<= SOURCE swap delta +64 MiB`;
- no unsafe pressure;
- no fallback;
- no persistent expert cache.

If all gates PASS: `EXPERT_MAJOR_CANONICALIZATION_GO`.

If evidence is valid but RSS, performance, exactness or safety still fails: `EXPERT_MAJOR_CANONICALIZATION_NO_GO`.

INCONCLUSIVE only for genuine environment/instrumentation ambiguity.

## Hard bounds / efficiency

- no network/model download;
- reuse full-bank artifact; do not rebuild;
- no DFlash;
- no physical cold-I/O work;
- no full 3-pair runtime campaign;
- one matched smoke pair only;
- exactly three exactness positions;
- no threshold rescue;
- no broad repo/history reread;
- deterministic scripts/JSON for memory attribution where possible;
- Pi may edit the existing canonical working-tree script and directly related runtime code only;
- Pi must not commit/push or edit AGENTS/HANDOFF/ROADMAP/project decision docs.

Evidence:
`results-local/research/30b-expert-major-canonicalization-rss-repair-001/<UTC>/`
