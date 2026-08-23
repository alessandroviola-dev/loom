# SELECT-TIME-GC-DEFER 001 — Result

Classification: `SELECT_TIME_GC_DEFER_001_COMPLETE`
Interpretation: `SELECT_TIME_GC_NO_GO`
Date: 2026-08-23

Raw local evidence:
`results-local/memory/select-time-gc-defer-001/20260823-180124/`

## Frozen comparison

Both arms used the promoted S1 lifecycle:
- transformer layers 0..34 persistent;
- layer 35 streamed;
- embedding/final norm/LM head persistent;
- persistent raw weights `3,499,501,056 B`;
- logical streaming `84,427,264 B/token`;
- post-forward streamed-layer GC/cache cleanup already deferred;
- exactly one final cleanup/token.

CONTROL retained the select-time `gc.collect()` after deletion/release of the full loaded-weight container.

TREATMENT kept the same deletion/ownership point but omitted only that select-time `gc.collect()`.

## Correctness

Exact token parity: PASS for preflight and all four scientific constituents.

No resource aborts.

## Pooled results

| Arm | Valid | Tokens | Gen tok/s | Wall/token | E2E tok/s | Median TTFT | Peak active | Active+cache | Min free | Peak swap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTROL | 2/2 | 384 | 8.293 | 120.577 ms | 7.141 | 1.203 s | 3.633 GB | 3.538 GB | 19% | 2185.56 MB |
| TREATMENT | 2/2 | 384 | 7.767 | 128.754 ms | 6.731 | 1.388 s | 3.633 GB | 3.538 GB | 11% | 2130.25 MB |

## Causal comparison

TREATMENT vs CONTROL:
- generation ratio `0.936489`;
- generation `-6.351%`;
- E2E `-5.752%`;
- wall/token `+8.177 ms`;
- TTFT `+15.374%`;
- peak MLX active delta `0 B`;
- peak active+cache delta `0 B`;
- free-floor delta `-8 pp`;
- peak swap delta `-55.31 MB`;
- process-read diagnostic `+362,549 B/token`.

The treatment removed exactly one select-time GC invocation per generated token while preserving weight-container deletion/ownership, logical I/O, residency, model math, eval topology and the promoted post-forward cleanup policy.

## Decision

`SELECT_TIME_GC_NO_GO`.

The select-time Python GC remains part of the promoted streamed-layer lifecycle. Removing it did not reduce the marginal streaming cost and instead regressed throughput and host free-memory headroom.

Cleanup-cadence exploration is considered exhausted for the current path unless new evidence appears:
- shared intermediate cleanup consolidation: promoted;
- streamed-layer post-forward cleanup defer: promoted;
- select-time GC removal: NO-GO;
- embedding eval removal: NO-GO;
- norm eval removal: SMALL / not promoted.

Physical SSD traffic remains unproven.

## Routing

Do not remeasure the gradient because the NO-GO treatment is not promoted. Preserve the Gradient002 lifecycle as canonical and move to the next remaining marginal mechanism. Before changing I/O or adding prefetch, inspect whether transient streamed-block construction / quantized-structure reconstruction can be isolated from parameter loading/materialization without retaining layer weights.
