# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — full preregistered DFlash temporal-alignment range `-7..+7` is CLOSED with `NO_SYSTEMATIC_TEMPORAL_SHIFT`; offset 0 remains strongest aggregate alignment; next discriminate MLX-port error vs genuine candidate/interface mismatch by full-32k logit parity against authoritative reference on a small frozen subset
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001_NO_SYSTEMATIC_TEMPORAL_SHIFT`
Next core checkpoint: `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.6. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Still valid:
- target-tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen 63-state target continuation, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Mapping correction — resolved

Publisher `d2t` stores an OFFSET:
`target_id = draft_row + d2t[draft_row]`.

Local direct-`d2t` decode was repaired in 8 decode/analysis paths.

True support:
- `32,000` valid unique target IDs;
- exact equality with `t2d` TRUE positions;
- frozen corpus `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` unsupported.

Corrected top1 target matches remain `0/63`. Historical first E2E `0/96` remains contaminated until corrected replay and is not treated as reconfirmed.

## BF16 branch

Pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 target control showed material internal drift while target top1 stayed `12050`; result `NOT_CAUSAL`.

Persistent BF16 cache:
`<external-archive>/bf16-cache/`
~33 GiB; exact P1_t01 BF16 taps/logits retained; later full replay used 0 network bytes.

Q4->BF16 taps materially move the 32k drafter-logit distribution but did not establish recovery.

## Corrected drafter rank signal

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

For 50 representable targets:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

The remaining mismatch is serious but not equivalent to random/unrelated output.

## Temporal alignment — CLOSED

Combined checkpoints:
- `LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`;
- `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001`.

Final classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

Reports:
- `research/architecture/loom-dflash-corrected-temporal-alignment-audit-001-result.md`;
- `research/architecture/loom-dflash-temporal-alignment-range-completion-001-result.md`.

Range-completion evidence:
`results-local/research/dflash-temporal-alignment-range-completion-001/20260825T101610Z/`

Missing offsets completed:
- -7: no valid comparison;
- -6: 9 valid / 7 representable, T1/T5/T10/T50/T100 `0/0/0/0/1`, median rank 242;
- -5: 18/13, `0/0/0/2/3`, median 219;
- -4: 27/21, `0/0/2/5/7`, median 150;
- +4: 27/21, `1/2/3/7/8`, median 354;
- +5: 18/15, `0/2/2/5/5`, median 344;
- +6: 9/7, `0/0/0/0/2`, median 287;
- +7: no valid comparison.

Full-range facts:
- 441 valid prompt-local comparisons over all executable offsets;
- offset 0 remains stronger: 50 representable; T1/T5/T10/T50/T100 `0/8/11/19/26`; median rank `93.5`;
- only 5 corrected-proposal neighbor matches across all nonzero offsets: +2=2, +3=2, +4=1;
- matches occur only in P1/P2, none in P3;
- no nonzero offset dominates offset 0 on exact match, top-k, median rank, and cross-prompt consistency.

Scientific consequence: reject a simple off-by-N temporal/block-position explanation. Do not change positions, anchors, masks, block alignment, mapping, or tap ordering.

## Exact next step

Checkpoint:
`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

Goal:
Determine whether the remaining DFlash mismatch comes from the MLX port itself or from the published candidate/interface distribution.

Use a small preregistered stratified frozen subset across P1/P2/P3, including near-target and poor-rank examples. Feed exactly the same frozen target taps/input IDs/positions/mask semantics to both the current MLX drafter and an authoritative publisher/reference implementation using the same publisher weights.

Compare BEFORE decode:
- full 32k logits;
- argmax row;
- top-k rows;
- max/mean absolute error;
- RMSE;
- relative-L2;
- cosine similarity;
- exact/bitwise or justified numerical tolerance status.

Then verify corrected `row + d2t[row]` target-token decode parity separately.

Decision:
- full-logit parity -> MLX port exonerated for tested states; remaining mismatch is candidate/interface/distribution behavior and next scientific decision is salvage vs abandon / interface-history investigation;
- material parity failure -> STOP and localize first numerical divergence before E2E.

Restrictions:
- no target-model forward;
- no BF16 target forward;
- no E2E;
- no retraining/remapping;
- no performance work;
- no download unless a precise missing authoritative reference dependency is identified and separately authorized.
