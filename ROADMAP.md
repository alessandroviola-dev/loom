# LOOM Roadmap

Last updated: 2026-08-26
Current: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Strategic next: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_001`
Canonical context: `/AGENTS.md` v3.29.

## Core 30B-on-8GB serving

External expert data-access is the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority candidate remains lossless expert-major contiguous storage.

## What is already established

- Expert-major exact payload equality is valid.
- Structural read reduction `3456 -> 384` on the canonical full trace is valid.
- A/B 001 timing is INVALID due cache contamination.
- Accepted physical-I/O timing requires each arm/repetition independently `>=80%` conservative physical coverage.
- Fresh-inode copy cold preparation is rejected.
- Instrumentation and `F_GLOBAL_NOCACHE` control semantics are resolved.
- Same-region global-nocache repetition is rejected: first touch `96.0406%`, then `25.8365%` and `23.9728%`.

Therefore stop iterating same-page eviction variants.

## New execution model

Use preregistered compound funnels to answer strategic questions in one Pi execution. Internal stages do not require Git/pull if all branch logic, gates, workload and bounds were frozen before execution. No post-hoc rescue or threshold changes.

## Next — Expert-major Decision Funnel 001

Preregistration: `research/architecture/loom-30b-expert-major-decision-funnel-001-preregistration.md`.

Final outcomes:
- `EXPERT_MAJOR_GO`
- `EXPERT_MAJOR_NO_GO`
- `EXPERT_MAJOR_INCONCLUSIVE`

Stage 0:
1. Construct at least three mutually disjoint matched source/packed first-touch groups.
2. Prefer 64 experts / `160,432,128 B` per arm/group.
3. Exact ordered logical payload equality required.
4. No source or packed payload page reuse across repetitions.
5. If impossible, stop INCONCLUSIVE.

Stage 1, automatic if Stage 0 passes:
1. Exactly 3 matched pairs with frozen order `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`.
2. Each arm independently requires >=80% conservative physical coverage plus exact payload/hash, complete instrumentation, successful controls, swap delta <=16,000,000 B, free memory >=10%, no unsafe pressure.
3. Primary metric: paired `packed_wall/source_wall`; decision metric = median of three paired ratios.
4. GO if valid median <=0.70, packed physical bytes <=1.05x source per pair, no exactness/read-structure regression.
5. NO-GO if comparison is valid but median >0.70 or a valid physical-byte/read-structure regression makes the layout unattractive.
6. INCONCLUSIVE if a valid causal comparison cannot be established.

Bounds: no model forward, network, DFlash, runtime edits, purge/reboot/cache-thrash/RAM-fill/swap eviction/fresh-copy workaround; max 3 matched pairs; timed logical payload <=962,592,768 B total.

## After the funnel

If `EXPERT_MAJOR_GO`: run one separately preregistered compound runtime phase bundling minimal integration, exactness parity and bounded end-to-end performance measurement.

If `EXPERT_MAJOR_NO_GO`: stop expert-major integration and return to the next ranked serving bottleneck/intervention.

If `EXPERT_MAJOR_INCONCLUSIVE`: redesign measurement only if a materially different valid method exists; do not return to serial eviction micro-tests.

## Synchronization rule

Outside a frozen compound funnel, every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next independent WP; user pulls first.
