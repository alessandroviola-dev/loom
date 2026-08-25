# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001_NO_SYSTEMATIC_TEMPORAL_SHIFT`
Strategic next: `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.6.

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

For 50 representable targets:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top1 `0/50`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`.

The drafter is mismatched at top1 but carries measurable target-directional signal.

## Temporal alignment — CLOSED

Combined result:
`NO_SYSTEMATIC_TEMPORAL_SHIFT` over the full preregistered valid range `-7..+7`.

Reports:
- `research/architecture/loom-dflash-corrected-temporal-alignment-audit-001-result.md`;
- `research/architecture/loom-dflash-temporal-alignment-range-completion-001-result.md`.

Completion evidence:
`results-local/research/dflash-temporal-alignment-range-completion-001/20260825T101610Z/`

Full-range summary:
- 441 valid prompt-local comparisons;
- offset 0: 50 representable, top1/top5/top10/top50/top100 `0/8/11/19/26`, median rank `93.5`;
- only 5 nonzero-offset proposal-neighbor matches total: +2=2, +3=2, +4=1;
- no neighbor matches in P3;
- no nonzero offset materially and consistently dominates offset 0.

Therefore temporal/off-by-N alignment is rejected as the explanation. Do not change positions, anchors, masks, block semantics, mapping, or tap order.

## Next — full 32k MLX/reference logit parity

Checkpoint:
`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

Purpose:
Resolve the remaining highest-level ambiguity: is the current MLX DFlash port numerically reproducing an authoritative publisher/reference implementation, or is there still a subtle implementation divergence hidden beneath matching raw argmax behavior?

Plan:
1. preregister a small stratified subset of frozen states across P1/P2/P3, covering near-target and poor target-rank cases;
2. reuse exact frozen taps/input IDs/positions/mask semantics;
3. run current MLX drafter and authoritative publisher/reference implementation with the same publisher weights;
4. compare full 32k logits before decode using argmax/top-k parity and vector error/cosine metrics;
5. separately verify corrected `row + d2t[row]` decode parity;
6. no target-model forward is needed.

Decision:
- strong full-logit parity -> MLX port is not the remaining explanation on tested states; diagnose published-candidate/interface/training-distribution compatibility or make an explicit DFlash salvage-vs-abandon decision;
- material full-logit divergence -> localize the first numerical divergence before any corrected E2E;
- only after port parity is established should a corrected bounded E2E be considered.

Restrictions:
- no target/BF16 target forward;
- no E2E yet;
- no retraining/remapping;
- no performance optimization;
- no download unless an exact missing authoritative reference dependency is identified and separately justified.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
