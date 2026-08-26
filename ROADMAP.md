# LOOM Roadmap

Last updated: 2026-08-26
Current: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE` from Runtime Funnel 001
Strategic next: `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002`
Canonical context: `/AGENTS.md` v3.32.

## Core 30B-on-8GB serving

External expert data-access remains the dominant measured bottleneck.

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`:
- median physical-I/O PACKED/SOURCE wall ratio `0.595950`;
- ~`40.405%` lower expert-access wall;
- exact payload/hash PASS;
- reads `576 -> 64` per 64-expert group;
- physical-byte, memory and swap gates PASS.

Raw expert-major I/O is accepted and should not be re-litigated.

## Runtime Funnel 001 — INCONCLUSIVE before model forward

Result: `research/architecture/loom-30b-expert-major-runtime-funnel-001-result.md`.
Evidence: `results-local/research/30b-expert-major-runtime-funnel-001/20260826T150012Z/`.

Selected workload: `LOOM_30B_MOE_REAL_RAW_CACHE_001` SOURCE control, P1 canonical sequence (`20260824T092553Z`).

The retained pack was only a 384-expert single-position/trace artifact. It could not cover the selected runtime workload's prefill and consecutive decode accesses without fallback. Stage 0 therefore stopped; no model execution occurred.

This is an artifact-readiness/process failure, not performance evidence.

## Integration Readiness Protocol v1 — mandatory

`research/architecture/loom-integration-readiness-protocol-v1.md`

Before any integration coding/model forward:
1. define producer artifact scope/coverage/provenance/ABI;
2. define consumer runtime workload/access/fallback/exactness contract;
3. mechanically prove `consumer_required_coverage ⊆ provider_available_coverage`;
4. run a static adapter/access replay with zero unresolved accesses and zero forbidden fallback;
5. only then write/run the integrated treatment;
6. use scripts/JSON rather than broad Pi reasoning for manifest/coverage checks.

Trace/benchmark artifacts are not general runtime artifacts.

## Next — Full-Bank Expert-Major Runtime Funnel 002

Preregistration: `research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-preregistration.md`.

One compound run:

### Stage 0 — compile-time readiness
- freeze the canonical workload;
- verify source model has all `6144/6144` experts and correct format/provenance;
- require >=20 GiB free destination space;
- reuse an existing full-bank pack only if a complete manifest proves compatibility.

### Stage 1 — runtime-complete full-bank artifact
If absent, build a deterministic full expert-major routed bank:
- `6144` experts;
- `2,506,752 B/expert`;
- total `15,401,484,288 B`;
- `(layer_id, expert_id) -> offset/size/hash/provenance` manifest;
- expert-granular resumability;
- full coverage/integrity verification.

### Stage 2 — static adapter compatibility
- prove required workload accesses are a subset of full-bank coverage;
- replay all retained required accesses before model forward;
- zero missing/ambiguous mapping;
- zero SOURCE fallback;
- only storage backend/layout may differ.

### Stage 3 — exactness
- same forced token sequence;
- 3 consecutive full 48-layer decode positions;
- identical routed expert order;
- identical raw final-logit float32 SHA SOURCE vs PACKED;
- no fallback/cache/safety regression.

### Stage 4 — practical runtime A/B
- no artificial cache-state manipulation;
- exactly 3 fresh-process pairs `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`;
- prefill + one unmeasured warmup + 3 measured decode tokens/arm;
- capture wall, RSS, pressure, swap, routing/backend state.

GO iff:
- artifact/static/exactness/safety PASS;
- median PACKED/SOURCE decode wall <=0.90;
- median PACKED RSS <= SOURCE +128 MiB;
- PACKED swap delta <= matched SOURCE +64 MiB;
- no fallback/persistent expert cache/unsafe pressure.

NO-GO for valid exactness/safety/performance failure. INCONCLUSIVE only for a genuine environment/resource/instrumentation blocker.

## Execution-efficiency rule

Prefer a single preregistered compound run that includes readiness/build/static validation/runtime validation. Do not return to serial integration micro-tests. Static incompatibilities must terminate before adapter/model work. Artifact builders/validators must be persisted and reused.
