# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. Same-page cold enforcement is rejected. Decision Funnel 001 stopped INCONCLUSIVE at Stage 0 because trace-order groups were not packed-contiguous; no timing ran. A corrected packed-first compound funnel is preregistered.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002`
Pi context: `/AGENTS.md` v3.30.

## Synchronization

Normal rule: significant checkpoint -> ChatGPT updates GitHub -> user pulls -> next independent Pi WP.

Exception: a fully preregistered compound funnel may traverse internal stages automatically without intermediate Git/pull. All branches, thresholds, workload/fallback order and bounds must be frozen before execution.

## Core 30B serving/I/O

External expert data-access remains the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage.

## Physical-I/O evidence

- A/B 001 INVALID due cache contamination; exact payload equality and structural read reduction `3456 -> 384` remain valid.
- Valid timed arms require `>=80%` conservative physical coverage.
- Fresh-inode copy cold method rejected (~21% coverage).
- Instrumentation and `F_GLOBAL_NOCACHE` set/reset semantics are resolved.
- Repeated same packed pages: first touch `96.0406%`, then `25.8365%` / `23.9728%`; same-page cold enforcement rejected.

## Decision Funnel 001

Classification: `EXPERT_MAJOR_INCONCLUSIVE`.
Result: `research/architecture/loom-30b-expert-major-decision-funnel-001-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-001/20260826T143324Z/`.

Stage 0 identified 3 x 64-expert groups (`160,432,128 B/arm`) with zero source/packed cross-group overlap and retained metadata/hash PASS. No timed reads ran.

Failure reason: groups were selected in canonical trace order and those groups were not contiguous in packed physical order. This is a preregistration/design failure, not evidence against expert-major.

## Exact next step — Decision Funnel 002

Preregistration: `research/architecture/loom-30b-expert-major-decision-funnel-002-preregistration.md`.

Stage 0 now selects from packed physical order first, excludes recently re-touched regions, then maps the exact same expert IDs/order into SOURCE. Deterministic group-size fallback is frozen `64 -> 32 -> 16`; largest size yielding exactly three valid disjoint groups is used.

Stage 1 automatically executes 3 first-touch matched pairs with order `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`. Every arm independently requires >=80% conservative physical coverage, exact payload/hash, full instrumentation, valid controls, safe memory/swap and expected read structure.

Final outcomes only:
- `EXPERT_MAJOR_GO`: valid median paired `packed/source <=0.70`, packed physical bytes <=1.05x source per pair, no regression.
- `EXPERT_MAJOR_NO_GO`: valid comparison but insufficient performance or valid physical/read regression.
- `EXPERT_MAJOR_INCONCLUSIVE`: valid causal measurement cannot be established.

No human/Git synchronization inside Funnel 002. If GO, the next phase should be one compound runtime funnel bundling isolated integration + exactness parity + safety + bounded end-to-end performance.
