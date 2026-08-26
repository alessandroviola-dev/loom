# LOOM Roadmap

Last updated: 2026-08-26
Current: `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`
Strategic next: `LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001`
Canonical context: `/AGENTS.md` v3.22.

## DFlash — closed

Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`. Preserve artifacts only; do not reopen absent a new independent mechanism.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage.

## Expert-major A/B 001 — invalid

Source p50 `1.097739 s`, packed p50 `0.382613 s`, apparent ratio `0.348547`, structural reads/pass `3456 -> 384`, exact payload equality PASS. No speedup accepted because packed physical coverage was contaminated by cache residency.

## Coverage audit 001

Classification: `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`.
Source conservative physical coverage `99.8761%`; packed aggregate `50.0644%`. First packed repetition `94.26%`; later repeats `38.61–40.20%`. macOS page cache survives `F_NOCACHE/F_RDAHEAD` hints.

Future cold timing requires >=80% conservative physical coverage independently on every accepted repetition.

## Cold-I/O protocol validation 001 — unresolved

Classification: `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`.
Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-001-result.md`.

Candidate method selected: fresh non-cloned APFS inode using `O_CREAT|O_EXCL` byte-copy + `fsync`, with `F_NOCACHE/F_RDAHEAD` supplementary.

The first `160,432,128 B` trial was not accepted because instrumentation aborted after the timed read before physical counters and payload/hash validation were persisted. Trials 2–3 were not run. Swap delta was `0 B`; no unsafe memory pressure was observed.

This does not reject the method; it blocks interpretation.

## Next

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001`

Before another cold-read protocol trial:
1. make all required evidence persistence fail-safe;
2. validate pre/post physical counters, logical bytes, wall time, read count, payload/hash result and memory/swap state;
3. use only a <=16 MiB tiny probe;
4. verify both success and intentional failure/exception paths persist sufficient diagnostic evidence;
5. no full 160 MiB trial, model forward, network, DFlash or A/B.

Only after `COLD_IO_INSTRUMENTATION_PASS` run `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`. Only after cold protocol PASS preregister physical-I/O A/B 002. Only after a valid A/B PASS integrate packed access into the exact runtime and measure end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
