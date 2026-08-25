# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — corrected DFlash target-rank audit COMPLETE; exact target remains 0/50 top1 on representable states, but 11/50 are top10, 19/50 top50 and 26/50 top100; directional signal exists, so next test systematic temporal/position alignment using retained evidence only
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001_PASS_DIRECTIONAL_SIGNAL_PRESENT`
Next core checkpoint: `LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.4. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

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

Publisher `d2t` stores an OFFSET, not an absolute target ID:
`target_id = draft_row + d2t[draft_row]`.

The old local direct-`d2t` decode was repaired in `LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`.

True support:
- `32,000` valid unique target IDs;
- exact equality with `t2d` TRUE positions;
- frozen corpus: `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` remains unsupported.

Corrected top1 proposals still match target `0/63`; therefore the mapping bug was material but not the principal cause of incompatibility.

Historical first E2E `0/96` remains contaminated until replayed with corrected decode and is not currently treated as reconfirmed.

## BF16 branch

Pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 target control showed material internal drift while target top1 stayed `12050`; result remained `NOT_CAUSAL`.

Persistent BF16 cache:
`<external-archive>/bf16-cache/`
~33 GiB; exact P1_t01 BF16 taps/logits retained; later full replay used 0 network bytes.

BF16 tap intervention moved the 32k drafter-logit distribution materially but did not establish proposal recovery.

## Corrected drafter target-rank audit — COMPLETE

Checkpoint:
`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

Classification:
`PASS_DIRECTIONAL_SIGNAL_PRESENT`

Report:
`research/architecture/loom-dflash-corrected-drafter-target-rank-audit-001-result.md`

Evidence:
`results-local/research/dflash-corrected-drafter-target-rank-audit-001/20260825T094730Z/`

No replay was needed: retained full 32k drafter logits were reused and hashes/argmax rows revalidated.

Population:
- 50 representable target tokens;
- 13 unsupported target tokens, excluded from rank assignment.

Ranks over the 50 representable states:
- min `2`;
- median `93.5`;
- mean `438.82`;
- max `3510`.

Top-k:
- top1 `0/50`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`.

Histogram:
- 2–5: 8;
- 6–10: 3;
- 11–50: 8;
- 51–100: 7;
- 101–1000: 17;
- 1001–10000: 7.

Best state:
`P3_t01`, target `1620`, draft row `1423`, rank `2`, probability `0.05192055`.

Worst state:
`P2_t01`, target `2464`, draft row `2147`, rank `3510`, probability `4.636e-05`.

## Scientific interpretation

The remaining zero top1 compatibility is real, but the drafter is not globally unrelated to the frozen target distribution. More than half of the representable targets are already in top100, and over one fifth are in top10.

Before calling this a generic calibration/training-distribution mismatch, test a cheaper and more specific mechanism: a systematic off-by-one / block-position alignment error between DFlash proposal positions and the frozen target continuation.

## Exact next step

Checkpoint:
`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

Static retained-evidence audit only.

Required:
1. stay within each frozen prompt/sequence;
2. compare each corrected top1 proposal against target tokens at relative offsets `-7..+7` around the intended position (`0`);
3. never cross sequence boundaries;
4. for representable neighbor target tokens, compute their ranks in the retained 32k drafter logits;
5. report valid-state count, top1 match count and rank summaries for each offset;
6. identify whether any non-zero offset consistently dominates offset 0;
7. no model replay unless retained evidence is unexpectedly insufficient.

Restrictions:
- no target/BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance work.
