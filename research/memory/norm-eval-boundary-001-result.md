# LOOM — NORM-EVAL-BOUNDARY 001 — Result

Date: 2026-08-22
Classification: `NORM_EVAL_BOUNDARY_001_COMPLETE`
Interpretation: `NORM_EVAL_COST_SMALL`

## Frozen comparison

Both arms used cleanup-consolidated S1:
- transformer layers 0..34 persistent;
- layer 35 streamed;
- embedding/final norm/LM head persistent;
- persistent raw weights 3,499,501,056 B;
- logical streamed transformer traffic 84,427,264 B/token;
- post-embedding eval retained;
- post-embedding cleanup absent;
- layer-35 lifecycle/cleanup unchanged;
- post-norm cleanup absent;
- LM-head eval retained;
- final post-head cleanup retained.

CONTROL retained the explicit final-norm `mx.eval(h2)`.

TREATMENT removed/deferred only that final-norm eval. No replacement synchronization/materialization boundary was added.

Balanced order: `CONTROL -> TREATMENT -> TREATMENT -> CONTROL`.

## Correctness

- CONTROL parity: PASS
- TREATMENT parity: PASS
- exact canonical S0 token IDs preserved in preflight and all four scientific constituents
- resource aborts: none

## Pooled results

CONTROL:
- 2/2 valid
- 384 generated tokens
- 54.835 s generation wall
- 7.003 tok/s
- 142.799 ms/token
- E2E 6.153 tok/s
- median TTFT 1.240 s
- peak MLX 3,537,250,032 B
- minimum free 21%
- peak swap 1746.50 MB

TREATMENT:
- 2/2 valid
- 384 generated tokens
- 54.420 s generation wall
- 7.056 tok/s
- 141.719 ms/token
- E2E 6.194 tok/s
- median TTFT 1.225 s
- peak MLX 3,537,250,032 B
- minimum free 22%
- peak swap 1718.19 MB

## Causal effect

TREATMENT / CONTROL:
- generation ratio 1.007620x
- generation change **+0.762%**
- E2E change **+0.667%**
- wall/token delta **-1.080 ms**
- wall/token reduction 0.756%
- TTFT change -1.198%
- peak MLX delta 0 B
- minimum-free delta +1 pp
- peak swap delta -28.31 MB

The treatment removed exactly one final-norm eval invocation per generated token. All other topology remained frozen.

## Decision

The effect is positive but below the predeclared 5% material threshold. Therefore final-norm eval removal is **not promoted** into the canonical cleanup-consolidated S1 baseline.

Together with `EMBED_EVAL_BOUNDARY_001_NO_GO`, this closes the obvious shared-stage eval-boundary axis. The successful fixed-activation change remains shared cleanup consolidation; the explicit embedding/norm/head evaluation boundaries remain frozen unless future evidence independently reopens them.

The next scalable target is the measured marginal streamed-transformer lifecycle, historically about 38–39 ms/token per additional streamed layer after activation.

Physical SSD traffic remains unproven.

Raw local evidence:
`results-local/memory/norm-eval-boundary-001/20260822-175311/`
