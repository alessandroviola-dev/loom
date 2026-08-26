# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — expert-major physical-I/O is accepted; Runtime Funnel 001 stopped before model forward because a trace-scoped 384-expert pack was incorrectly treated as a runtime-capable provider artifact. Integration Readiness Protocol v1 is now mandatory.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001_EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`
Next: `LOOM_30B_EXPERT_MAJOR_FULLBANK_RUNTIME_FUNNEL_002`
Pi context: `/AGENTS.md` v3.32.

## Core decision already settled

External expert data-access is the dominant measured bottleneck (`47.74%` of prior decode-equivalent wall).

`LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002` = `EXPERT_MAJOR_GO`:
- three valid paired physical-I/O ratios `0.602456`, `0.595950`, `0.581170`;
- median `0.595950` = `40.405%` lower access wall;
- exact payload/hash PASS;
- reads `576 -> 64` per 64-expert group;
- safe memory/swap.

Do not reopen raw physical-I/O causality.

## Runtime Funnel 001 result

Classification: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.
Result: `research/architecture/loom-30b-expert-major-runtime-funnel-001-result.md`.
Evidence: `results-local/research/30b-expert-major-runtime-funnel-001/20260826T150012Z/`.

Selected workload: `LOOM_30B_MOE_REAL_RAW_CACHE_001` SOURCE control, P1 canonical sequence (`20260824T092553Z`).

Stage 0 manifest precheck failed:
- provider pack = 384 experts from a different single decode position;
- consumer runtime requires prefill + consecutive decode accesses;
- no-fallback coverage impossible.

No model forward, exactness, timing, RSS or swap benchmark ran.

Root cause: artifact scope mismatch. A benchmark/trace-scoped artifact was implicitly promoted toward runtime use without a producer/consumer compatibility contract.

## New mandatory programming/integration discipline

Protocol: `research/architecture/loom-integration-readiness-protocol-v1.md`.

Before integration coding/model forward:
1. producer artifact contract must declare scope, coverage, model revision, format/ABI, dtype/quantization, mapping and hashes;
2. consumer runtime contract must declare workload/phases/required accesses/exactness/fallback/memory expectations;
3. deterministic checker must prove `consumer_required_coverage ⊆ provider_available_coverage`;
4. static adapter dry-run must resolve every frozen access exactly once with zero forbidden fallback;
5. only then may adapter coding/model forward begin;
6. Pi must use deterministic scripts/JSON for these checks rather than broad repo reasoning.

Benchmark/trace-scoped packs cannot be treated as general runtime artifacts.

## Exact next step — Full-Bank Runtime Funnel 002

Preregistration: `research/architecture/loom-30b-expert-major-fullbank-runtime-funnel-002-preregistration.md`.

This remains one compound run rather than serial micro-tests.

Stage 0: compile-time provider/consumer contract, prove all source experts available and >=20 GiB destination free space.

Stage 1: build/reuse a runtime-complete full routed-bank pack:
- `6144/6144` experts;
- `2,506,752 B` each;
- total `15,401,484,288 B`;
- deterministic `(layer, expert)` mapping;
- per-entry offset/size/hash/provenance;
- resumable build;
- complete integrity verification.

Stage 2: static compatibility + access replay; zero missing mappings/fallback before model forward.

Stage 3: exactness on 3 forced decode positions; identical routed order and raw float32 final-logit SHA SOURCE vs PACKED.

Stage 4: exactly 3 practical fresh-process A/B pairs; one warmup + 3 measured decode tokens/arm; no artificial cold-cache controls.

Runtime GO requires exactness/safety PASS and median PACKED/SOURCE measured decode wall <=0.90, median PACKED RSS <= SOURCE +128 MiB, matched swap delta <= SOURCE +64 MiB, no fallback/cache/unsafe pressure.

Final outcomes only:
- `EXPERT_MAJOR_RUNTIME_GO`
- `EXPERT_MAJOR_RUNTIME_NO_GO`
- `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`.
