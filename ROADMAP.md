# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001_NO_SYSTEMATIC_TEMPORAL_SHIFT_WITHIN_PM3`
Strategic next: `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.5.

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

Publisher `d2t` is an offset. Correct decode:
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

## Corrected drafter rank signal

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

For the 50 representable target tokens:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top1 `0/50`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`.

The drafter is mismatched at top1 but carries substantial target-directional signal.

## Temporal alignment audit — partial preregistered range

Checkpoint:
`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

Scientific classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT_WITHIN_PM3`.

Report:
`research/architecture/loom-dflash-corrected-temporal-alignment-audit-001-result.md`

Executed offsets `-3..+3` show:
- offset 0 has strongest aggregate top-k placement and best median target rank `93.5`;
- +2 and +3 each yield 2 descriptive top1 neighbor matches, but both lose to offset 0 on top-k/median rank;
- gains at +2/+3 occur in P1/P2 but not P3;
- no systematic temporal shift is supported within ±3.

Methodological note: persistent preregistration in AGENTS v3.4 was `-7..+7`, while the active Pi prompt executed only `-3..+3`. Full-range closure therefore requires a cheap retained-evidence completion for missing offsets only.

## Next — temporal alignment range completion

Checkpoint:
`LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001`

Static only:
1. compute missing offsets `-7,-6,-5,-4,+4,+5,+6,+7`;
2. use the exact same retained corrected 32k logits and frozen per-trajectory targets;
3. never cross trajectory boundaries;
4. report valid/representable counts, top1, top5/10/50/100, rank min/median/mean/max;
5. report proposal-neighbor exact matches and per-prompt consistency;
6. merge with existing `-3..+3` metrics;
7. determine whether any nonzero offset over full `-7..+7` materially and consistently dominates offset 0.

Decision:
- full-range nonzero dominance -> investigate positional/block alignment before E2E;
- no full-range dominance -> close temporal shift and run a small stratified full-32k MLX-vs-authoritative-reference logit parity audit;
- only after numerical port parity is established should remaining mismatch be attributed to candidate/training/interface distribution.

Restrictions:
- no model forward;
- no target/BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance work.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
