# LOOM DFlash Corrected Temporal Alignment Audit 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`
Classification: `NO_SYSTEMATIC_TEMPORAL_SHIFT`
Gate: `PASS`

## Purpose

Test, using only frozen target tokens and retained corrected 32k DFlash logits, whether the remaining zero top-1 compatibility is explained by a systematic neighboring-position / temporal shift.

No model forward, BF16 execution, download, E2E, retraining, remapping, or boundary-crossing comparison was performed.

## Population and method

- Frozen states at intended offset 0: 63.
- Comparisons were state-local and prompt-local only.
- Relative offsets tested by the executed audit: `-3,-2,-1,0,+1,+2,+3`.
- Corrected publisher mapping semantics `target_id = draft_row + d2t[draft_row]` were preserved.
- Retained proposal rows/logits were revalidated.
- Total valid state-local comparisons: 333.

## Results

| Offset | Valid | Representable | Top1 | Top5 | Top10 | Top50 | Top100 | Rank min | Rank median | Rank mean | Rank max |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| -3 | 36 | 29 | 0 | 1 | 2 | 6 | 12 | 2 | 251 | 798.69 | 4235 |
| -2 | 45 | 35 | 0 | 3 | 4 | 7 | 11 | 2 | 299 | 846.03 | 7140 |
| -1 | 54 | 43 | 0 | 5 | 6 | 11 | 17 | 3 | 178 | 597.47 | 4600 |
| 0 | 63 | 50 | 0 | 8 | 11 | 19 | 26 | 2 | 93.5 | 438.82 | 3510 |
| +1 | 54 | 43 | 0 | 5 | 6 | 13 | 21 | 2 | 124 | 487.44 | 2710 |
| +2 | 45 | 37 | 2 | 2 | 4 | 11 | 15 | 1 | 196 | 515.62 | 2630 |
| +3 | 36 | 29 | 2 | 2 | 2 | 8 | 11 | 1 | 155 | 757.79 | 3880 |

## Neighbor proposal matches

Four distinct source distributions matched a neighboring frozen target token, only at offsets `+2/+3`.

Per-prompt behavior:
- `+2`: P1 = 1 top1 gain, P2 = 1, P3 = 0;
- `+3`: P1 = 1 top1 gain, P2 = 1, P3 = 0.

The apparent non-zero-offset gains therefore do not reproduce across all trajectories.

## Interpretation

Offset `+2` is the descriptive top1 winner because it produces 2 exact matches, but it does not dominate offset 0 on top-k placement or median rank. Offset `+3` likewise fails consistency and distributional dominance.

Offset 0 retains the strongest aggregate directional alignment:
- best median target rank (`93.5`);
- best top5 (`8`), top10 (`11`), top50 (`19`), and top100 (`26`) counts among the tested offsets;
- no consistent non-zero shift across P1/P2/P3.

Therefore the remaining DFlash mismatch is not explained by a simple systematic temporal/off-by-N alignment error.

## Scientific consequence

Do not modify target positions, anchors, masks, or block alignment based on this audit.

The next high-leverage discriminator is to test the full 32k drafter-logit distribution of the MLX port against an authoritative publisher/reference implementation on a small stratified set of frozen states. Top1/raw-row parity alone is insufficient to exclude subtler numerical port divergence.

Evidence directory: exact timestamp was not included in the returned checkpoint text; Pi's local `results-local/research/dflash-corrected-temporal-alignment-audit-001/<UTC>/` directory remains authoritative.
