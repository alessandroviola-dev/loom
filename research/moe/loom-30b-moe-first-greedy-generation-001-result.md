# LOOM — 30B MoE First Greedy Generation 001 — Result

Date: 2026-08-24
Classification: `LOOM_30B_MOE_FIRST_GREEDY_GENERATION_001_PASS`
Run: `20260824T081701Z`
Raw evidence: `results-local/moe/first-greedy-generation-001/20260824T081701Z/`

## Result

The full-capacity `Qwen3-30B-A3B-MLX-4bit` target produced its first real autoregressive output on the Apple M1 / 8 GB reference machine using the resident non-expert backbone, BF16 KV cache, and source-external serial routed experts with zero expert cache/prefetch/DFlash.

Prompt: `Quanto fa 2+2? Rispondi solo con il numero.`

Formatted prompt: 28 tokens.
Generated token IDs: `[19, 151645]`.
Decoded output: `4` followed by canonical EOS.

The generation was deterministic in the short rerun.

## Performance

Prefill:
- wall: 18.666122750 s;
- 28 prompt tokens;
- 1.500043709 prompt tok/s.

Decode:
- one measured autoregressive decode step after the prefill-emitted first token;
- wall: 1.545350791 s;
- 0.647102267 decode tok/s.

E2E:
- 20.281761667 s;
- 0.098610763 output tok/s for the two generated token IDs including EOS.

Decode timing attribution:
- attention/shared: 0.163348212 s;
- expert reads: 1.044226996 s;
- MLX reconstruction: 0.040544777 s;
- expert compute: 0.197101287 s;
- aggregation: 0.012058625 s.

The measured decode step is therefore dominated by source-external expert reading.

## Expert traffic

Per decode token:
- useful expert bytes: 962,592,768 B;
- selected experts: 384 (`48 layers × 8`);
- source component reads: 3,456 (`384 × 9`).

This is the exact zero-expert-cache traffic baseline.

The current source-layout decode read wall is ~1.044 s, materially above the device-verified ~0.4816 s zero-cache storage-only reference measured with expert-sized contiguous accesses. This does not prove the difference is entirely layout/read-call overhead, but it creates a direct runtime hypothesis worth testing.

## KV / memory

BF16 KV:
- after prefill: 2,752,512 B;
- after final generated token: 2,850,816 B;
- growth: 98,304 B/token.

Memory:
- peak MLX: 923,521,032 B;
- peak RSS: 861,634,560 B (`ru_maxrss`; sampled peak 858,587,136 B);
- swap: 922.12 -> 922.12 MiB;
- memory pressure: PASS;
- progressive memory growth: NO;
- final routed expert residency: 0 / 0 B;
- ownership gate: PASS.

## Routing reuse

The short two-position generation trace produced 768 routed selections and a consecutive-token same-layer expert reuse ratio of 0.2786458333.

Counterfactual perfect previous-token retention and whole-run layer-local union both yield 828,481,536 B/token for this very short trace, a 13.932291667% traffic reduction from the 962,592,768 B zero-cache baseline.

This trace is too short to design a production cache policy. A longer deterministic generation trace is required before cache sizing/policy conclusions.

## Decision

PASS establishes that real autoregressive generation with advancing BF16 KV and source-external experts is correct and memory-stable on M1 8 GB.

However:
1. zero-cache decode is only ~0.647 tok/s;
2. expert source reads account for ~1.044 s of the ~1.545 s decode step;
3. the current source layout requires 3,456 component `pread` calls/token;
4. existing expert-major packing has already proven a lossless 9->1 range transformation but has not yet been measured on the real decode hot path;
5. the two-position routing trace is insufficient for cache policy design.

Therefore the next high-leverage experiment should compare source 9-range access against a minimal trace-scoped expert-major packed access on an otherwise identical decode step, without building the full 14.344 GiB pack. After the layout cost is isolated, collect a longer real generation routing trace for cache simulation.
