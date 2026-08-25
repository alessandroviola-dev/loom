# LOOM DFlash Corrected Drafter Target Rank Audit 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`
Classification: `PASS_DIRECTIONAL_SIGNAL_PRESENT`
Gate: `COMPLETE`

## Purpose

Measure where the exact frozen target token ranks inside the unchanged DFlash 32k drafter distribution after the corrected `target_id = draft_row + d2t[draft_row]` mapping semantics.

This is drafter-side rank only. No target-model logits were recomputed.

## Evidence

Local evidence:
`results-local/research/dflash-corrected-drafter-target-rank-audit-001/20260825T094730Z/`

Retained full 32k drafter logits were reused; no replay was required. Raw argmax rows revalidated 63/63 and retained-logit SHA-256 matched prior repair evidence.

## Population

- frozen states: `63`;
- target token representable in the true 32k draft vocabulary: `50`;
- structurally unsupported: `13`;
- unsupported states were excluded from artificial rank assignment.

## Correct-target drafter ranks

Across the 50 representable states:

- minimum rank: `2`;
- median rank: `93.5`;
- mean rank: `438.82`;
- maximum rank: `3510`.

Top-k membership:

- rank 1: `0/50`;
- top-5: `8/50`;
- top-10: `11/50`;
- top-50: `19/50`;
- top-100: `26/50`.

Rank histogram:

- rank 1: `0`;
- ranks 2–5: `8`;
- ranks 6–10: `3`;
- ranks 11–50: `8`;
- ranks 51–100: `7`;
- ranks 101–1000: `17`;
- ranks 1001–10000: `7`.

Best state:
- `P3_t01`, position `2`;
- target token `1620`;
- draft row `1423`;
- rank `2`;
- probability `0.05192055`.

Worst state:
- `P2_t01`, position `4`;
- target token `2464`;
- draft row `2147`;
- rank `3510`;
- probability `4.636e-05`.

## Interpretation

The corrected drafter remains `0/50` at exact top-1 on representable target tokens, so the remaining incompatibility is real.

However, the learned distribution is not globally uninformative: 11/50 correct tokens are already top-10, 19/50 top-50, and 26/50 top-100, with median rank 93.5. This is evidence of directional target signal despite zero top-1 agreement.

Therefore the next highest-leverage cheap diagnostic is not retraining, E2E, BF16, or performance work. Before treating the issue as generic calibration/training-distribution mismatch, test whether proposal/token ranks are systematically aligned to a neighboring frozen target position (off-by-one/block-position error).

No causal explanation is established by this rank audit alone.

## Next checkpoint

`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001`

Static retained-evidence audit: compare each corrected drafter distribution/proposal against neighboring frozen target tokens within the same sequence across a preregistered relative-position window, looking for a systematic non-zero offset.
