# LOOM 30B MoE Expert Pack 001 — Result

Date: 2026-08-23
Classification: `LOOM_30B_MOE_EXPERT_PACK_001_PASS`
Run ID: `20260823T204053Z`

## Proven result

A deterministic expert-major derived format was built and validated for layers 0 and 15 of `Qwen3-30B-A3B-MLX-4bit`.

- Layers packed: 0 and 15.
- Experts packed: 256.
- Useful expert bytes packed: 641,728,512 B.
- Per-layer pack: 320,864,256 B.
- Components validated: 2,304.
- Bytes validated: 641,728,512 B.
- Hash mismatches: 0.
- Byte mismatches: 0.
- Metadata mismatches: 0.

Each routed expert is reduced from 9 source data ranges to one contiguous 2,506,752 B packed data range with 100% useful/span efficiency. Top-k=8 therefore drops from 72 source data reads to 8 packed reads, with no byte amplification.

This proves lossless, independently addressable expert-major storage for both an ordinary layer and a shard-boundary layer.

## Important benchmark caveat

The reported packed/source read throughput of roughly 14–15 GB/s and the resulting ~66 ms 48-layer zero-cache I/O-only extrapolation must NOT be treated as physical SSD performance evidence.

The benchmark used `os.pread`; the CACHE_MINIMIZED mode set Darwin `F_NOCACHE`, but the tested files had already been created/read in the same workflow. The observed throughput is far above plausible physical storage throughput for the reference machine and is consistent with filesystem/page-cache or memory-resident service. `F_NOCACHE` prevents/controls file-system caching for an FD but does not by itself prove that already resident pages were absent before measurement.

Therefore:
- pack correctness: PASS;
- read-call geometry reduction: PASS;
- physical-storage throughput/latency: UNVALIDATED;
- ~66 ms/token extrapolation: NON-CANONICAL pending a physically grounded I/O checkpoint.

## Storage projection

Projected full 48-layer expert pack:
- binary expert payload: 15,401,484,288 B (14.344 GiB);
- estimated manifests: 66,227,400 B;
- total: ~14.405 GiB.

Observed free SSD space during the run: 63.251 GiB. Full repack is storage-feasible, but is not yet justified as the next action because physical I/O behavior remains unvalidated.

## Decision

Do not build the complete 14.3 GiB expert pack yet.

Next checkpoint: `LOOM_30B_MOE_PHYSICAL_IO_001`.

It must establish a defensible physical/cold-ish storage baseline that cannot be confused with page-cache or memory bandwidth, while preserving the proven 9->1 expert packing geometry.

Only after that checkpoint should LOOM decide between:
1. full expert-bank repack;
2. one-layer external-expert execution;
3. stronger cache/amortization/storage redesign.

Raw local evidence:
`results-local/moe/expert-pack-001/20260823T204053Z/`
