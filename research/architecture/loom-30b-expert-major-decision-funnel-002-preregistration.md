# LOOM 30B Expert-Major Decision Funnel 002 — Preregistration

Date: 2026-08-26
Branch: `research/stretch-015-divergence-attribution`
Status: PREREGISTERED — not yet executed

## Decision question

Does lossless expert-major contiguous storage provide a sufficiently large, causally valid physical-I/O improvement to justify runtime integration on the current M1/8GB LOOM path?

Final outcomes only:
- `EXPERT_MAJOR_GO`
- `EXPERT_MAJOR_NO_GO`
- `EXPERT_MAJOR_INCONCLUSIVE`

This is one compound preregistered funnel. Internal stages advance automatically without intermediate Git/pull. No rule, threshold, workload rescue or branch may change after execution begins.

## Stage 0 — deterministic packed-first construction

Use retained pack manifest/layout/hash metadata only; do not read payload bytes before timing.

1. Enumerate packed expert entries in ascending physical offset.
2. Exclude the packed region/expert set used by the recent first-64 global-nocache validation and any other region explicitly recorded as recently re-touched by those validation runs.
3. From the remaining entries, select the first three non-overlapping blocks of 64 consecutive packed entries by ascending offset.
4. Each block must be physically contiguous at expert granularity: 64 adjacent expert-major payload records, `160,432,128 B` logical payload.
5. Map those exact ordered expert identities into the canonical SOURCE nine-range representation.
6. Validate from retained metadata/hashes that SOURCE and PACKED represent the same ordered logical payload bytes.
7. Require zero source-range overlap across groups and zero packed-range overlap across groups.
8. Expected read counts per group: SOURCE `576`, PACKED `64`.

If three valid 64-expert blocks cannot be built, deterministic fallback is allowed before any timing:
- try 32 consecutive packed entries per group;
- if still impossible, try 16 consecutive packed entries per group.
Use the largest size for which exactly three valid disjoint groups exist. The selected size applies to all three pairs. No other fallback is allowed.

If no size in `{64,32,16}` yields three valid groups: `EXPERT_MAJOR_INCONCLUSIVE` and STOP.

## Stage 1 — decisive paired first-touch physical-I/O A/B

Exactly three matched groups, each used once only.
Frozen arm order:
- Pair 1: `SOURCE -> PACKED`
- Pair 2: `PACKED -> SOURCE`
- Pair 3: `SOURCE -> PACKED`

For every arm:
- fresh read-only FD(s);
- fixed-ABI `F_GLOBAL_NOCACHE` protocol already established locally;
- SET `1` requires raw `0`, errno `0`;
- `F_NOCACHE=1`, `F_RDAHEAD=0` where applicable;
- three idle `iostat -Id` intervals;
- complete repaired instrumentation;
- timed exact payload read/hash;
- RESET `0` requires raw `1`, errno `0`;
- restoration verification SET `1` -> raw `0`, RESET `0` -> raw `1`, errno `0` throughout.

Every arm/repetition must independently PASS:
- conservative physical coverage `>=80%`;
- exact payload/hash PASS;
- complete arithmetic-consistent evidence;
- control set/reset/restoration PASS;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory pressure;
- SOURCE logical bytes == PACKED logical bytes within pair;
- observed read-count structure matches selected group size: SOURCE `9*N`, PACKED `N`.

Any invalid arm => `EXPERT_MAJOR_INCONCLUSIVE` and STOP. Invalid timing must not be used as performance evidence.

## Frozen decision

For each valid pair:
`paired_ratio = packed_wall / source_wall`.

Decision statistic: median of the three paired ratios.

`EXPERT_MAJOR_GO` only if all validity gates PASS and:
- median paired ratio `<=0.70`;
- packed conservative physical bytes `<=1.05x` source in every pair;
- no payload exactness regression;
- no structural read-count regression.

`EXPERT_MAJOR_NO_GO` if the comparison is valid but:
- median paired ratio `>0.70`; or
- valid evidence shows unacceptable physical-byte/read-structure regression.

No threshold relaxation.

## Bounds

- no model forward;
- no network;
- no DFlash;
- no runtime integration/edit;
- no purge/reboot/cache-thrash/RAM-fill/swap-induced eviction;
- no fresh-copy workaround;
- maximum three matched pairs;
- maximum selected group size 64 experts;
- total timed logical payload <= `962,592,768 B` if 64-expert groups are selected, proportionally lower for fallback sizes;
- fail closed on instrumentation/control ambiguity.

If final outcome is `EXPERT_MAJOR_GO`, the next phase should be one compound runtime funnel bundling isolated integration, exactness parity, safety and bounded end-to-end performance measurement.
