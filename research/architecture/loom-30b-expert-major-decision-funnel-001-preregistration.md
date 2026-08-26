# LOOM 30B Expert-Major Decision Funnel 001 — Preregistration

Date: 2026-08-26
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Decision question

Does lossless expert-major contiguous storage provide a sufficiently large, causally valid physical-I/O improvement to justify runtime integration on the current M1/8GB LOOM path?

Final outcomes:
- `EXPERT_MAJOR_GO`
- `EXPERT_MAJOR_NO_GO`
- `EXPERT_MAJOR_INCONCLUSIVE`

This is a compound preregistered funnel. Internal stages may advance automatically without ChatGPT/Git synchronization because all branches, gates and budgets are frozen in advance. Any scientific rule change requires a new checkpoint.

## Established evidence

- External expert data-access is the dominant measured serving bottleneck: `0.442087 / 0.926028 s = 47.74%` median wall.
- Exact payload equality and structural read reduction `3456 -> 384` are already established for the full canonical trace.
- Repeated reads of the same packed pages cannot be kept cold reliably: first touch ~96% physical, later same-region reads ~24–26%.
- `F_GLOBAL_NOCACHE` set/reset semantics and instrumentation are resolved.
- Every accepted timed arm must independently show `>=80%` conservative physical coverage.

## Stage 0 — offline feasibility / construction

No payload reads unless required by retained hashes/metadata.

Construct at least three mutually disjoint matched groups from retained canonical expert identities.
Preferred group size: 64 expert payloads = `160,432,128 B` logical payload per arm/group.

For every group:
- source and packed represent exactly the same ordered logical expert payload bytes;
- source ranges for one repetition do not overlap source ranges used by another repetition;
- packed ranges for one repetition do not overlap packed ranges used by another repetition;
- exact retained hashes/metadata validate equality;
- expected logical bytes are identical between arms;
- expected read calls are source `9 x experts`, packed `1 x experts`.

If three valid matched non-reuse groups cannot be constructed, STOP => `EXPERT_MAJOR_INCONCLUSIVE`.

## Stage 1 — single decisive first-touch paired physical-I/O A/B

Exactly three matched groups, each used once only.
Pair order is frozen before timing and alternates to reduce order bias: `SOURCE->PACKED`, `PACKED->SOURCE`, `SOURCE->PACKED`.
No group/pages are reused in another repetition.

Per arm:
- fresh read-only FD(s);
- established fixed-ABI `F_GLOBAL_NOCACHE` control protocol;
- `F_NOCACHE=1`, `F_RDAHEAD=0` where applicable;
- three idle `iostat -Id` intervals before timing;
- complete repaired instrumentation;
- exact payload/hash validation;
- swap/memory capture;
- control restoration verification.

Frozen validity gates for every arm/repetition:
- conservative physical coverage `>=80%`;
- exact payload/hash PASS;
- complete arithmetic-consistent evidence;
- control set/reset/restoration PASS;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory pressure;
- logical bytes source == packed;
- expected structural read-count pattern preserved.

If any arm is invalid under these gates, STOP => `EXPERT_MAJOR_INCONCLUSIVE`.

## Frozen causal performance decision

Primary statistic: paired wall-time ratio `packed_wall / source_wall` for each of the 3 matched groups.
Primary decision statistic: median of the 3 paired ratios.

`EXPERT_MAJOR_GO` only if all validity gates PASS and:
- median paired wall-time ratio `<=0.70`;
- packed conservative physical bytes are `<=1.05x` matched source physical bytes in every pair;
- no exactness/read-structure regression.

`EXPERT_MAJOR_NO_GO` if the comparison is valid but the median paired wall-time ratio is `>0.70`, or a valid measurement shows expert-major introduces an unacceptable physical-byte/read-structure regression.

No threshold relaxation after seeing results.

## Bounds

- no model forward;
- no network;
- no DFlash;
- no runtime integration/edit in this funnel;
- no purge/reboot/cache-thrash/RAM-fill/swap-induced eviction;
- no fresh-copy workaround;
- maximum three matched pairs;
- expected timed logical payload <= `962,592,768 B` total across both arms for 3 x 64-expert pairs;
- fail closed on instrumentation/control ambiguity.

If final outcome is `EXPERT_MAJOR_GO`, the next phase may bundle runtime integration + exactness + bounded end-to-end benchmark into one separately preregistered compound WP rather than returning to micro-test iteration.
