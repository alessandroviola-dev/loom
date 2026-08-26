# LOOM 30B Expert-Major Runtime Funnel 001 — Result

Date: 2026-08-26
Checkpoint: `LOOM_30B_EXPERT_MAJOR_RUNTIME_FUNNEL_001`
Classification: `EXPERT_MAJOR_RUNTIME_INCONCLUSIVE`

## Decision

The funnel stopped at Stage 0 before any model forward. This is an **artifact-scope / integration-readiness failure**, not evidence against expert-major runtime performance.

Selected canonical workload:
- `LOOM_30B_MOE_REAL_RAW_CACHE_001` SOURCE control;
- P1 canonical sequence (`20260824T092553Z`).

Preflight result:
- retained expert-major pack covers 384 experts from a different single decode position;
- selected runtime workload requires expert coverage across prefill and consecutive decode positions;
- no-fallback manifest coverage therefore failed;
- no model forward, exactness run, timing pair, RSS or swap benchmark was executed.

Evidence:
`results-local/research/30b-expert-major-runtime-funnel-001/20260826T150012Z/`

## Root cause

The physical-I/O experiments validated a **trace-scoped benchmark artifact**, but the runtime funnel attempted to consume it as though it were a runtime-complete backend artifact. The pack format itself remains validated; its coverage scope was insufficient for the consumer workload.

This mismatch should have been detectable before integration work from producer/consumer manifests alone.

## Required process correction

Adopt `research/architecture/loom-integration-readiness-protocol-v1.md` before another runtime integration attempt.

Key rule: no integration coding or model forward until a compile-time artifact contract proves `consumer_required_coverage ⊆ provider_available_coverage` and the adapter ABI can resolve every frozen access without fallback.

For canonical/general expert-major runtime adoption, prefer a full routed-bank artifact covering all `48 × 128 = 6144` expert identities rather than reusing a trace-scoped 384-expert benchmark pack.
