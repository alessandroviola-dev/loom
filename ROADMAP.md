# LOOM Roadmap

Last updated: 2026-08-26
Current: `COLD_IO_INSTRUMENTATION_PASS`
Strategic next: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`
Canonical context: `/AGENTS.md` v3.23.

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

Candidate method: fresh non-cloned APFS inode using `O_CREAT|O_EXCL` byte-copy + `fsync`, with `F_NOCACHE/F_RDAHEAD` supplementary.

The first `160,432,128 B` trial could not be classified because instrumentation raised a post-read `KeyError` before required physical-counter and payload-validation evidence was persisted. The method itself remained unclassified.

## Cold-I/O instrumentation repair 001 — PASS

Report: `research/architecture/loom-30b-cold-io-instrumentation-repair-001-result.md`.
Classification: `COLD_IO_INSTRUMENTATION_PASS`.

Root cause repaired: `row.update()` referenced `row['payload_validation']` before insertion.

Validation:
- success-path persistence PASS;
- intentional failure persistence PASS;
- fail-closed incomplete-evidence gate PASS;
- probe `16,777,216 B`;
- swap delta `0 B`.

This removes the instrumentation blocker only; no cache-state or performance claim follows from this PASS.

## Next

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`

1. Retest the unchanged fresh-inode method with repaired fail-safe instrumentation.
2. At most three independent fresh-inode trials using the same representative packed subset scale (`160,432,128 B`, unless an exact bounded mechanical adjustment is required).
3. Every accepted trial must independently satisfy >=80% conservative physical coverage, payload/hash PASS, complete instrumentation and safe memory/swap behavior.
4. Do not run a full source-vs-packed A/B, model forward, network, DFlash or runtime optimization.
5. Only `PACKED_COLD_IO_PROTOCOL_PASS` allows preregistration of `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002`.
6. Only after a valid A/B 002 PASS integrate packed access into the exact runtime and measure end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
