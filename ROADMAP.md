# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001_PASS_DIRECTIONAL_SIGNAL_PRESENT`
Strategic next: `LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.4.

## Stable DFlash chain

Still valid:
- target tap interface `[1,12,23,34,45]`;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Resolved mapping semantics

Publisher `d2t` stores an offset. Correct decode:
`target_id = draft_row + d2t[draft_row]`.

Mechanical repair completed:
- true target support `32,000`;
- frozen support `50/63` representable, `13/63` unsupported;
- corrected top1 target matches remain `0/63`;
- P1_t01 target remains unsupported.

Historical first E2E `0/96` remains contaminated until corrected replay and is not currently a valid acceptance measurement.

## BF16 precision branch

P1_t01 Q4->BF16 control showed substantial target-internal drift but unchanged target top1 `12050`; result `NOT_CAUSAL`.

Persistent ~33 GiB BF16 cache and exact P1_t01 taps/logits are retained externally.

BF16 target taps materially move drafter logits but did not establish recovery.

## Completed — corrected drafter target-rank audit

Checkpoint:
`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

Classification:
`PASS_DIRECTIONAL_SIGNAL_PRESENT`

Report:
`research/architecture/loom-dflash-corrected-drafter-target-rank-audit-001-result.md`

Evidence:
`results-local/research/dflash-corrected-drafter-target-rank-audit-001/20260825T094730Z/`

Retained 32k drafter logits reused; no replay.

For the 50 representable target tokens:
- rank min / median / mean / max: `2 / 93.5 / 438.82 / 3510`;
- top1 `0/50`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`.

Best state: `P3_t01`, target `1620`, rank `2`, probability `0.05192055`.
Worst state: `P2_t01`, target `2464`, rank `3510`, probability `4.636e-05`.

## Strategic interpretation

The remaining mismatch is serious but not equivalent to a random/unrelated drafter. Correct-target mass/rank is frequently non-trivial even though exact top1 agreement is zero.

Before considering retraining, calibration, another BF16 sweep, or abandonment, test a cheaper specific hypothesis: the drafter output may be systematically aligned to the wrong neighboring token position within the DFlash block/continuation.

## Next — corrected temporal alignment audit

Checkpoint:
`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

Purpose:
Determine whether a consistent relative-position shift explains part of the zero top1 compatibility.

Static retained-evidence audit:
1. use each frozen sequence independently;
2. preregister relative offsets `-7..+7`, with `0` the intended target position;
3. compare corrected proposal top1 against each valid neighboring frozen target token;
4. compute neighbor-token drafter ranks where the neighbor token is in 32k support;
5. report valid counts, exact proposal matches and rank summaries by offset;
6. no cross-sequence comparisons;
7. identify whether any non-zero offset materially dominates offset 0.

Decision:
- strong non-zero-offset concentration -> investigate/repair positional alignment before any E2E;
- no systematic shift -> temporal alignment is not explanatory; next diagnosis returns to training/interface/distribution compatibility;
- only after a supported mechanism may a corrected bounded E2E be authorized.

Restrictions:
- no target/BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no memory/performance optimization.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
