# LOOM — 30B MoE Serving/I/O Re-entry 001 — Result

Date: 2026-08-26
Checkpoint: `LOOM_30B_MOE_SERVING_IO_REENTRY_001`
Classification: `SERVING_IO_BOTTLENECK_IDENTIFIED`

## Decision

The dominant measured bottleneck of the exact Qwen3-30B-A3B Q4 external-MoE decode path on Apple M1/8GB is **external expert data-access**.

Retained evidence shows, for an exact packed 48-layer decode-equivalent path:
- expert data-access: `0.442087 s` of `0.926028 s` median wall = `47.74%`;
- 384 expert reads;
- `962,592,768 B` logical expert payload;
- expert compute: `0.004186 s`;
- routing: `0.019075 s`;
- physical token-like I/O floor: `0.481589 s/token`.

Thus expert compute and routing are not the current dominant optimization targets.

## Evidence-supported interventions

1. Full lossless expert-major contiguous storage.
   Prior retained evidence showed approximately `-0.719300 s/token (-43.72%)` and `0.608 -> 1.080` decode-equivalent tok/s without persistent expert RAM.
2. Bounded raw packed-byte cache.
   Simulation only; the prior 4-GiB global LRU caused `+2410.56 MiB` swap and remains rejected.
3. Materialization/synchronization reduction.
   An exposed `0.251202 s/token` share exists, but recoverable fraction and RAM impact remain unresolved.

## Selected experiment

Preregistered physical-I/O A/B:
- source arm: nine-range source expert reads;
- packed arm: existing lossless trace-scoped expert-major pack;
- same 384 canonical routed experts and identical payload bytes;
- five fresh `F_NOCACHE/F_RDAHEAD` repetitions per arm;
- no model forward.

PASS required all of:
- exact byte/hash equality;
- physical/counter validity;
- packed p50 access wall `<= 0.70x` source;
- packed physical bytes `<= 1.05x` source;
- read-count reduction `3456 -> 384`.

Local evidence:
`results-local/research/30b-moe-serving-io-reentry-001/20260826T122316Z/analysis.json`
