# LOOM — STREAMED-LAYER-CLEANUP-DEFER 001 — Result

Date: 2026-08-22
Classification: `STREAMED_LAYER_CLEANUP_DEFER_001_COMPLETE`
Interpretation: `STREAMED_LAYER_CLEANUP_COST_MATERIAL`

Raw local evidence:
`results-local/memory/streamed-layer-cleanup-defer-001/20260822-180629/`

## Frozen comparison

Both arms used the promoted cleanup-consolidated S1 residency:
- transformer layers 0..34 persistent;
- transformer layer 35 streamed;
- embedding/final norm/LM head persistent;
- persistent raw weights `3,499,501,056 B`;
- logical streamed transformer traffic `84,427,264 B/token`;
- post-embedding/post-norm shared cleanup absent;
- embedding/norm/head eval boundaries retained;
- final post-head cleanup retained.

CONTROL retained layer-35 post-forward cleanup.

TREATMENT changed only the layer-35 post-forward cleanup cadence:
- select-time cleanup unchanged;
- load/select/reconstruction/materialization/forward/eval unchanged;
- transient deletion/release unchanged;
- omitted exactly one post-forward `gc.collect()` and one `mx.clear_cache()` per generated token;
- relied on the already-existing final post-head cleanup.

Exact token parity passed in preflight and every scientific prompt/run.

## Balanced ABBA result

| Arm | Valid | Tokens | Generation wall | Gen tok/s | Wall/token | E2E tok/s | Median TTFT | Peak active B | Observed active+cache B | Min free | Peak swap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTROL | 2/2 | 384 | 54.881 s | 6.997 | 142.918 ms | 6.135 | 1.274 s | 3,633,031,420 | 3,537,569,528 | 18% | 1990.56 MB |
| TREATMENT | 2/2 | 384 | 46.698 s | 8.223 | 121.610 ms | 7.101 | 1.203 s | 3,633,031,420 | 3,537,569,528 | 17% | 1964.75 MB |

Causal TREATMENT vs CONTROL:
- generation ratio `1.1752x`;
- generation **+17.522%**;
- E2E **+15.750%**;
- wall/token **-21.308 ms (-14.910%)**;
- TTFT **-5.566%**;
- peak active delta `0 B`;
- observed peak active+cache delta `0 B`;
- free-floor delta `-1 pp`;
- peak swap delta `-25.81 MB`;
- process-read diagnostic delta `-15,424 B/token`.

No resource aborts.

## Interpretation

Deferring only the streamed layer's post-forward cleanup materially improves the real-M1 streamed-layer lifecycle while preserving exact model output and the measured S1 memory envelope.

The removed `21.308 ms/token` is about `54.64%` of the historical ~39 ms/layer marginal reference from STREAMED-LAYER-GRADIENT 001, but that comparison is descriptive only because the historical gradient used the older lifecycle.

This experiment does **not** isolate whether the saved wall comes from Python GC, the MLX allocator, Metal scheduling, CPU work, I/O, or another internal subsystem. Physical SSD traffic remains unproven.

## Decision

Promote the deferred post-forward streamed-layer cleanup policy for further marginal-lifecycle research.

Before testing a different per-layer mechanism, remeasure the `S0/S1/S2/S4` real-M1 gradient under this new cleanup policy. The key question is whether the S1 gain scales across multiple streamed layers without unacceptable transient memory/cache accumulation.
