# STREAMING-ATTRIBUTION 001 — result

Date: 2026-08-22
Classification: `STREAMING_ATTRIBUTION_001_PARTIAL`
Bottleneck classification: `ATTRIBUTION_UNRESOLVED`

## Scope

This experiment instrumented the exact MEMORY-FRONTIER 001 F1/H32 partial-residency path without changing model math. F1 keeps transformer layers 0..31 persistent and streams layers 32..35 plus embedding, final norm and LM head.

Exact token parity was preserved against the canonical F0/F1 prefix.

## Scientific runs

Two fresh admitted F1 runs generated 32 greedy unknown tokens each.

- run 1: 18.942 s, 1.689 tok/s, TTFT 3.286 s, peak MLX 2,752,856,248 B, minimum free 17%, peak swap 1054.62 MB
- run 2: 18.628 s, 1.718 tok/s, TTFT 3.384 s, peak MLX 2,752,856,248 B, minimum free 17%, peak swap 1046.94 MB

Token-path logical streamed traffic was 882,255,872 B/generated token. The larger 909,826,368 B/token run-level number includes one required prefill pass.

Darwin process-read diagnostics were ~370.3 MB/token and ~342.9 MB/token in the two instrumented runs. These are diagnostics only and are not claimed physical SSD traffic.

## Traced intervals

Because MLX execution is asynchronous, host enqueue intervals and later materialization/synchronization overlap. The categories below are therefore not additive wall-time shares.

Across both runs:

- source access host wall: 0.787 s total, 12.298 ms/token mean
- tensor reconstruction host wall: 0.189 s, 2.952 ms/token
- materialization/sync wall: 15.359 s, 239.978 ms/token
- streamed-forward wall: 3.923 s, 61.303 ms/token
- cleanup/orchestration wall: 12.048 s, 188.248 ms/token
- persistent-forward wall: 5.168 s, 80.746 ms/token
- unclassified wall: 0.089 s, 1.387 ms/token

No GPU-kernel-duration or additive percentage claim is made.

## Stage hotspots

Largest observed stage wall/token:

1. LM head — 134.538 ms/token; 272,269,312 logical B/token; materialization/sync largest local category
2. embedding — 131.814 ms/token; 272,269,312 logical B/token; materialization/sync largest local category
3. layer 32 — 58.229 ms/token
4. layer 33 — 51.856 ms/token
5. layer 35 — 50.219 ms/token
6. layer 34 — 50.164 ms/token
7. final norm — 27.946 ms/token

Embedding + LM head account for 544,538,624 B/token of F1 logical streaming, about 61.7% of the 882,255,872 B/token token-path total.

## Instrumentation limitation

Pooled instrumented throughput was ~1.703 tok/s versus historical uninstrumented F1 2.527 tok/s, a ~32.6% lower rate. No contemporaneous uninstrumented control was run, so this cannot be isolated as pure tracing overhead.

Therefore the observed materialization/synchronization intervals, although the largest traced component and concentrated strongly in embedding/LM-head handling, do not justify a primary bottleneck classification.

Classification remains `ATTRIBUTION_UNRESOLVED`.

## Strongest supported conclusion

The current F1 design repeatedly streams two very large shared stages — embedding and LM head — in addition to four transformer layers. Those two shared stages dominate the logical streamed-byte budget and are also the two largest observed traced stage hotspots. This is sufficient to justify a one-factor shared-stage residency experiment, but not to claim that physical SSD I/O or materialization is definitively the primary bottleneck.

Physical SSD traffic proven: **NO**.

## Evidence

Raw local evidence:
`results-local/memory/streaming-attribution-001/20260822-160948/`

Local implementation:
`scripts/loom_streaming_attribution_001.py`
