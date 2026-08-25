# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — corrected DFlash temporal-alignment audit executed for offsets -3..+3 and shows no systematic shift within that range; because persistent preregistration was -7..+7, next complete only missing ±4..±7 statically before closing the hypothesis
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001_NO_SYSTEMATIC_TEMPORAL_SHIFT_WITHIN_PM3`
Next core checkpoint: `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.5. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Still valid:
- exact target-tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen 63-state target continuation, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Mapping correction

Publisher `d2t` stores an OFFSET:
`target_id = draft_row + d2t[draft_row]`.

The old local direct-`d2t` decode has been repaired.

True support:
- `32,000` valid unique target IDs;
- exact equality with `t2d` TRUE positions;
- frozen corpus `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` remains unsupported.

Corrected top1 proposals remain `0/63` exact target matches. Historical first E2E `0/96` remains contaminated until corrected replay and is not treated as reconfirmed.

## BF16 branch

Pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control measured material internal drift while target top1 stayed `12050`; result remained `NOT_CAUSAL`.

Persistent BF16 cache:
`<external-archive>/bf16-cache/`
~33 GiB; exact P1_t01 BF16 taps/logits retained; later full replay used 0 network bytes.

BF16 tap intervention moved the 32k drafter-logit distribution materially but did not establish recovery.

## Corrected drafter target-rank audit — COMPLETE

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

For 50 representable targets:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

Conclusion: mismatch is real, but drafter target signal is non-trivial.

## Temporal alignment audit — VALID WITHIN ±3

Checkpoint:
`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

Pi classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`

Scientific review classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT_WITHIN_PM3`

Report:
`research/architecture/loom-dflash-corrected-temporal-alignment-audit-001-result.md`

Executed metrics:

| Offset | Valid | Rep. | Top1 | Top5/10/50/100 | Rank min/median/mean/max |
|---:|---:|---:|---:|---:|---:|
| -3 | 36 | 29 | 0 | 1/2/6/12 | 2 / 251 / 798.69 / 4235 |
| -2 | 45 | 35 | 0 | 3/4/7/11 | 2 / 299 / 846.03 / 7140 |
| -1 | 54 | 43 | 0 | 5/6/11/17 | 3 / 178 / 597.47 / 4600 |
| 0 | 63 | 50 | 0 | 8/11/19/26 | 2 / 93.5 / 438.82 / 3510 |
| +1 | 54 | 43 | 0 | 5/6/13/21 | 2 / 124 / 487.44 / 2710 |
| +2 | 45 | 37 | 2 | 2/4/11/15 | 1 / 196 / 515.62 / 2630 |
| +3 | 36 | 29 | 2 | 2/2/8/11 | 1 / 155 / 757.79 / 3880 |

Four proposal-neighbor matches occur only at +2/+3, split P1=1, P2=1, P3=0 for each offset. These gains are not trajectory-consistent and do not dominate offset 0 on top-k or median rank.

Offset 0 remains the strongest aggregate alignment within ±3.

Methodological correction: `/AGENTS.md` v3.4 had preregistered `-7..+7`, but the active operational Pi prompt requested only `-3..+3`. Therefore the current result cannot close the full preregistered range.

## Exact next step

Checkpoint:
`LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001`

Use retained evidence only. Compute missing offsets:
`-7,-6,-5,-4,+4,+5,+6,+7`.

For each report the same valid/representable/top1/top5/top10/top50/top100/rank metrics, proposal-neighbor matches, and per-prompt consistency. Then combine with existing ±3 results and determine whether any nonzero offset across full `-7..+7` materially and consistently dominates offset 0.

No model replay, target/BF16 forward, download, E2E, retraining/remapping, or performance work.

If full-range temporal shift is rejected, next discriminator is full 32k MLX-vs-authoritative-reference logit parity on a small stratified frozen subset.
