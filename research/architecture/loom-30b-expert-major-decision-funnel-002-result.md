# LOOM 30B Expert-Major Decision Funnel 002 — Result

Date: 2026-08-26
Checkpoint: `LOOM_30B_EXPERT_MAJOR_DECISION_FUNNEL_002`
Classification: `EXPERT_MAJOR_GO`

## Decision

Lossless expert-major contiguous storage has passed the preregistered causal physical-I/O gate and is justified for isolated runtime integration testing.

Evidence: `results-local/research/30b-expert-major-decision-funnel-002/20260826T144530Z/`.

## Stage 0

PASS with the preferred size:
- 3 matched groups;
- 64 experts/group;
- `160,432,128 B` logical payload per arm/group;
- SOURCE/PACKED logical bytes matched exactly;
- zero SOURCE cross-group overlap;
- zero PACKED cross-group overlap.

## Stage 1 paired first-touch A/B

Pair 1:
- SOURCE: `100.7841%` conservative physical coverage, `0.425011 s`, `161,690,000 B`, 576 reads;
- PACKED: `95.5233%`, `0.256050 s`, `153,250,000 B`, 64 reads;
- paired wall ratio `0.602456`;
- physical-byte ratio `0.947801`.

Pair 2:
- SOURCE: `100.1233%`, `0.423898 s`, `160,630,000 B`, 576 reads;
- PACKED: `95.3986%`, `0.252622 s`, `153,050,000 B`, 64 reads;
- paired wall ratio `0.595950`;
- physical-byte ratio `0.952811`.

Pair 3:
- SOURCE: `100.8651%`, `0.425366 s`, `161,820,000 B`, 576 reads;
- PACKED: `95.3674%`, `0.247210 s`, `153,000,000 B`, 64 reads;
- paired wall ratio `0.581170`;
- physical-byte ratio `0.945495`.

Median paired wall ratio: `0.595950`, corresponding to a `40.405%` reduction in access wall versus SOURCE under the valid paired physical-I/O protocol.

All six timed arms passed:
- conservative physical coverage gate `>=80%`;
- whole-group payload/hash equality;
- expected read structure `576 -> 64` per 64-expert group;
- fixed-ABI control set/reset/restoration;
- arithmetic/instrumentation validity;
- zero swap delta;
- minimum free memory `55%`.

## Interpretation

This is the first causally valid physical-I/O performance result supporting expert-major. The speedup cannot be attributed to reduced physical-byte demand or cache contamination: PACKED read approximately `94.5–95.3%` as many conservative physical bytes as SOURCE while reducing fragmented read calls by `9x` and wall time by about `40%`.

The next question is no longer whether the storage layout helps raw expert access. It is whether replacing only the external expert data-access path with this layout preserves exact runtime semantics and produces a useful end-to-end decode improvement on the M1/8GB target without RAM/swap regression.
