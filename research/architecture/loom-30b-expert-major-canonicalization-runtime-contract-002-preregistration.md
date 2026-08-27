# LOOM 30B Expert-Major Canonicalization Runtime Contract 002 — Preregistration

Date: 2026-08-27
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Purpose

Finish canonicalization of the already accepted full-bank expert-major backend by removing validation-manifest parsing from the hot PACKED runtime process and replacing it with a minimal prevalidated runtime contract/resolver, while preserving all settled semantics and frozen adoption thresholds.

This is a bounded productionization repair, not a new mechanism experiment.

Final outcomes only:
- `EXPERT_MAJOR_CANONICALIZATION_GO`
- `EXPERT_MAJOR_CANONICALIZATION_NO_GO`
- `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE`

## Frozen facts

Accepted runtime mechanism:
`LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002 = EXPERT_MAJOR_RUNTIME_GO`.

Prior canonicalization:
- static `6144/6144` PASS;
- `18,048` access replay PASS;
- three-position exactness PASS;
- performance smoke PASS;
- first canonicalization failed RSS only;
- RSS Repair 001 became INCONCLUSIVE because PACKED alone parsed the full 6144×9 validation manifest in-process, contaminating allocator high-water.

Do not relax thresholds or reopen expert-major I/O/runtime science.

## Stage 0 — offline runtime-contract derivation

NO model forward. Use the existing valid full-bank artifact and full manifest only in an offline/preflight process.

Inputs:
- full bank:
  `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/fullbank/experts.bin`
- full validation manifest:
  `results-local/research/30b-expert-major-fullbank-runtime-funnel-002/20260826T152602Z/fullbank/manifest.json`
- working-tree canonical script:
  `scripts/loom_30b_moe_expert_major_backend_001.py`

First mechanically validate full artifact/manifest integrity and provenance.

Then test the preferred fixed-layout invariant from retained metadata:
- exactly `6144` expert records;
- deterministic lexicographic `(layer_id, expert_id)` order for `48 × 128` identities;
- constant payload size `2,506,752 B`;
- entry offsets form one contiguous affine sequence with no gaps/overlap;
- total bank size exactly `15,401,484,288 B`.

### Frozen resolver branch

If ALL fixed-layout invariants PASS:
- select `FORMULAIC_RESOLVER`;
- runtime offset is derived deterministically from `(layer_id, expert_id)` and the frozen record size/base offset;
- emit a small machine-readable runtime contract containing only fields required to prove/use that layout: format version, source model/revision identity, bank path identity or relative contract binding, expert/layer counts, expert byte size, total bank size, base offset, full-manifest digest/provenance root, full-bank integrity identity, resolver mode.

If ANY fixed-layout invariant fails:
- select frozen fallback `COMPACT_INDEX_RESOLVER`;
- generate a compact runtime index containing exactly one entry per `(layer_id, expert_id)` with only runtime-required fields: offset, size, and minimal integrity/provenance identity;
- do not include the 9 source-component records or validation-only provenance trees in runtime memory.

No other resolver representation is allowed.

Persist the generated runtime contract/index and its digest under this checkpoint evidence directory.

If neither deterministic representation can be generated and validated from the accepted artifact: `EXPERT_MAJOR_CANONICALIZATION_INCONCLUSIVE` and STOP.

## Stage 1 — minimal canonical runtime repair

Edit only the existing canonical backend and directly required reusable helper code.

Requirements:
- full validation manifest is NEVER parsed by the hot PACKED runtime process;
- PACKED runtime loads only the Stage-0 runtime contract/resolver;
- SOURCE backend remains unchanged;
- fail closed on incompatible contract, bank size/identity mismatch, invalid `(layer,expert)`, offset/range violation, or resolver corruption;
- no SOURCE fallback;
- no persistent expert payload cache;
- one routed expert logically live at a time;
- routing, expert math, quantization, dtypes, KV, scheduling/synchronization and output computation unchanged;
- validation/full provenance remains available through the offline validator, not hot runtime state.

Do not rebuild the full bank.

## Stage 2 — static production gate

Before model forward require:
- syntax/compile checks PASS;
- offline full-manifest/full-bank validation PASS;
- runtime contract/index validation PASS;
- `6144/6144` resolver coverage PASS;
- uniqueness/bounds PASS;
- retained `18,048` access replay through the repaired canonical PACKED backend PASS;
- zero unresolved/ambiguous/invalid-range accesses;
- zero SOURCE fallback;
- zero persistent expert cache;
- deterministic evidence that the hot PACKED process does not parse/load the full validation manifest or its 9-component provenance lists.

Any deterministic repair defect => `EXPERT_MAJOR_CANONICALIZATION_NO_GO` and STOP.
Genuine missing/inaccessible artifact/environment dependency => INCONCLUSIVE.

## Stage 3 — exactness regression gate

Use the same accepted frozen workload and exactly three consecutive decode positions.

Require canonical SOURCE vs repaired canonical PACKED:
- identical routed expert IDs/order;
- mapping/hash/integrity contract PASS;
- identical raw final-logit float32 SHA at all three positions;
- zero fallback;
- no persistent expert cache;
- no unsafe memory pressure.

Any valid exactness mismatch => `EXPERT_MAJOR_CANONICALIZATION_NO_GO` and STOP.

## Stage 4 — one admissible fresh-process RSS/performance smoke

Run offline/preflight full-manifest validation BEFORE launching either timed runtime child. That validator process must exit before SOURCE/PACKED runtime measurement begins.

Then exactly one fresh-process matched pair, frozen order `SOURCE -> PACKED`.

For BOTH arms:
- launch from the same parent/harness state after preflight has completed;
- fresh child process;
- same model/workload/runtime settings;
- prefill;
- one unmeasured warmup decode token;
- exactly three measured decode tokens;
- no artificial cache/allocator normalization, purge, reboot, RAM-fill, or eviction.

PACKED child may load only its minimal runtime contract/resolver as part of the treatment. It must not parse the full validation manifest.

Record RSS at minimum:
- child startup;
- backend initialized;
- model/runtime ready;
- after prefill;
- after warmup;
- after each measured token;
- peak RSS.

Also record decode wall, swap before/after/delta, fallback/cache status and unsafe pressure.

### Frozen PASS thresholds

- PACKED/SOURCE aggregate decode wall `<=0.95`;
- PACKED peak RSS `<= SOURCE peak RSS +128 MiB`;
- PACKED swap delta `<= SOURCE swap delta +64 MiB`;
- exactness PASS;
- no unsafe pressure;
- no fallback;
- no persistent expert cache.

If all gates PASS: `EXPERT_MAJOR_CANONICALIZATION_GO`.

If valid evidence shows performance/RSS/safety/exactness failure: `EXPERT_MAJOR_CANONICALIZATION_NO_GO`.

INCONCLUSIVE only for genuine environment/instrumentation ambiguity preventing an admissible decision.

## Hard bounds / efficiency

- no network/model download;
- no DFlash;
- no full-bank rebuild;
- no physical cold-I/O work;
- no 3-pair runtime campaign;
- one matched smoke pair only;
- exactly three exactness positions;
- deterministic scripts/JSON for all validation/contract generation;
- no broad repo/history reread;
- no threshold rescue;
- Pi may edit the existing canonical script and directly related reusable helper code only;
- Pi must not commit/push or edit AGENTS/HANDOFF/ROADMAP/project decision docs.

Evidence:
`results-local/research/30b-expert-major-canonicalization-runtime-contract-002/<UTC>/`
