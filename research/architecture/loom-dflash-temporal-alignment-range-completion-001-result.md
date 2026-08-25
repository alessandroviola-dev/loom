# LOOM DFlash Temporal Alignment Range Completion 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001`
Classification: `NO_SYSTEMATIC_TEMPORAL_SHIFT`
Gate: `PASS`

## Purpose

Complete the preregistered DFlash temporal-alignment audit over the full relative-offset range `-7..+7`, using only retained corrected 32k drafter logits and frozen prompt-local target continuations.

No model forward, BF16 execution, download, E2E, retraining, remapping, or cross-trajectory comparison was performed.

## New offsets completed

| Offset | Valid | Representable | Top1 | Top5 | Top10 | Top50 | Top100 | Rank min | Rank median | Rank mean | Rank max |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| -7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — | — |
| -6 | 9 | 7 | 0 | 0 | 0 | 0 | 1 | 69 | 242 | 334.86 | 738 |
| -5 | 18 | 13 | 0 | 0 | 0 | 2 | 3 | 18 | 219 | 801.69 | 4183 |
| -4 | 27 | 21 | 0 | 0 | 2 | 5 | 7 | 7 | 150 | 789.76 | 5217 |
| +4 | 27 | 21 | 1 | 2 | 3 | 7 | 8 | 1 | 354 | 945.10 | 10412 |
| +5 | 18 | 15 | 0 | 2 | 2 | 5 | 5 | 3 | 344 | 705.47 | 3996 |
| +6 | 9 | 7 | 0 | 0 | 0 | 0 | 2 | 95 | 287 | 1162.71 | 6545 |
| +7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — | — |

New state-local comparisons: `108`.
Full `-7..+7` comparison total: `441`.

## Full-range interpretation

The intended offset `0` remains stronger than every nonzero offset on aggregate directional metrics:
- representable states at offset 0: `50`;
- top1/top5/top10/top50/top100: `0/8/11/19/26`;
- median target-row rank: `93.5`.

Corrected-proposal neighbor matches over all nonzero offsets total only `5`:
- `+2`: 2 matches, one in P1 and one in P2;
- `+3`: 2 matches, one in P1 and one in P2;
- `+4`: 1 match, in P2;
- no nonzero-offset match in P3.

No nonzero offset dominates offset 0 on the preregistered combination of exact-match, top-k placement, median-rank behavior, and cross-trajectory consistency.

Therefore a systematic temporal / off-by-N alignment error is rejected over the full valid `-7..+7` range.

## Scientific consequence

Do not alter target positions, anchors, masks, block alignment, mapping, or tap ordering based on temporal-shift hypotheses.

The next high-leverage discriminator is a small stratified full-32k numerical parity audit between the validated MLX DFlash port and an authoritative publisher/reference implementation using the same frozen input evidence. This should distinguish residual port divergence from genuine drafter/target-distribution incompatibility.

Evidence:
`results-local/research/dflash-temporal-alignment-range-completion-001/20260825T101610Z/`
