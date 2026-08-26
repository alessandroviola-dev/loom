# LOOM Roadmap

Last updated: 2026-08-26
Current: `EXPERT_MAJOR_INCONCLUSIVE` from Decision Funnel 001
Strategic next: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002`
Canonical context: `/AGENTS.md` v3.30.

## Core 30B-on-8GB serving

External expert data-access remains the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate remains lossless expert-major contiguous storage.

## Established I/O facts

- Exact expert-major payload equality is valid.
- Structural read reduction `3456 -> 384` is valid.
- A/B 001 timing is INVALID due cache contamination.
- Every accepted timed arm requires `>=80%` conservative physical coverage.
- Fresh-inode copy cold preparation is rejected.
- Instrumentation and `F_GLOBAL_NOCACHE` semantics are resolved.
- Same-region repetition is rejected: first touch `96.0406%`, repeats `25.8365%`, `23.9728%`.

## Decision Funnel 001 — INCONCLUSIVE

Result: `research/architecture/loom-30b-expert-major-decision-funnel-001-result.md`.
Evidence: `results-local/research/30b-expert-major-decision-funnel-001/20260826T143324Z/`.

Stage 0 found three 64-expert groups with exact retained metadata and zero cross-group overlap, but canonical trace ordering did not produce contiguous packed groups. No performance timing ran. This is a design/preregistration failure only.

## Execution model

Use compound preregistered funnels for strategic yes/no questions. Internal gates do not require Git/pull if all branches, thresholds, deterministic fallback order, workload and bounds were frozen before execution. No post-hoc rescue.

## Next — Expert-major Decision Funnel 002

Preregistration: `research/architecture/loom-30b-expert-major-decision-funnel-002-preregistration.md`.

Stage 0:
1. enumerate packed expert entries by physical offset;
2. exclude regions explicitly re-touched in recent global-nocache validation;
3. select the first three disjoint contiguous packed groups;
4. map the exact same expert IDs/order to source nine-range representation;
5. validate retained hash/provenance and zero source/packed cross-group overlap;
6. deterministic group-size order `64 -> 32 -> 16`, use largest size yielding exactly 3 valid groups;
7. if none works, final `EXPERT_MAJOR_INCONCLUSIVE`.

Stage 1, automatic if Stage 0 passes:
- three first-touch matched pairs with frozen order `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`;
- each arm independently >=80% conservative physical coverage plus payload/hash, instrumentation, control, memory/swap and read-structure gates;
- primary metric `packed_wall/source_wall`; decision metric median of 3 ratios.

Final decision:
- `EXPERT_MAJOR_GO` if valid median <=0.70, packed physical bytes <=1.05x source per pair, no exactness/read regression.
- `EXPERT_MAJOR_NO_GO` if valid but median >0.70 or valid physical/read regression.
- `EXPERT_MAJOR_INCONCLUSIVE` only when a valid causal comparison cannot be established.

Bounds: no model forward/network/DFlash/runtime edits/purge/reboot/cache-thrash/RAM-fill/swap eviction/fresh-copy workaround; max 3 pairs; max 64 experts/group; total timed logical bytes <=962,592,768 B at size 64.

## After Funnel 002

If `EXPERT_MAJOR_GO`: one compound runtime funnel should bundle isolated integration, exactness parity, safety and bounded end-to-end tok/s/RSS/swap measurement.

If `EXPERT_MAJOR_NO_GO`: stop expert-major and return to the next ranked serving intervention.

If `EXPERT_MAJOR_INCONCLUSIVE`: reconsider measurement only if a materially different causal design exists; do not return to serial cache-control micro-tests.

## Synchronization rule

Outside a frozen compound funnel, every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next independent WP; user pulls first.
