# LOOM Roadmap

Last updated: 2026-08-26
Current: `PACKED_COLD_IO_PROTOCOL_FAIL`
Strategic next: `LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001`
Canonical context: `/AGENTS.md` v3.24.

## DFlash — closed

Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`. Preserve artifacts only; do not reopen absent a new independent mechanism.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, subject to valid physical-I/O causality.

## Expert-major A/B 001 — invalid

Source p50 `1.097739 s`, packed p50 `0.382613 s`, apparent ratio `0.348547`, structural reads/pass `3456 -> 384`, exact payload equality PASS. No speedup accepted because packed physical coverage was cache-contaminated.

## Coverage audit

`PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`.
Source conservative physical coverage `99.8761%`; packed aggregate `50.0644%`. First packed repetition `94.26%`; later repeats `38.61–40.20%`. Future cold timing requires >=80% conservative physical coverage on every accepted repetition.

## Instrumentation repair — PASS

`COLD_IO_INSTRUMENTATION_PASS` removed the evidence-persistence blocker. Required success-path, fail-path and fail-closed behavior are validated.

## Cold-I/O protocol validation 002 — FAIL

Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-002-result.md`.
Classification: `PACKED_COLD_IO_PROTOCOL_FAIL`.

Frozen fresh-inode byte-copy method produced only:
- T1 `21.7537%` coverage;
- T2 `21.6914%`;
- T3 `20.8250%`.

All three payloads validated; all swap deltas were 0 B; 0/3 met the frozen >=80% gate. The method is rejected.

Working hypothesis only: preparation by normal byte-copy may populate macOS page cache for the newly written inode. This is not yet proven.

## Next

`LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001`

1. Inspect retained I/O evidence and locally available macOS cache/file mechanisms.
2. Separate established facts from hypotheses about write-side cache population.
3. Rank no more than three safe candidate measurement/preparation strategies.
4. Reject RAM-fill/cache-thrash, swap-induced eviction and uncontrolled reboot dependence.
5. Select exactly one bounded validation experiment with the unchanged >=80% conservative physical-coverage criterion.
6. Define instrumentation, workload and quantitative PASS/FAIL before execution.
7. No full source-vs-packed A/B, model forward, network, DFlash or runtime integration during redesign.
8. Only after a separately preregistered cold-strategy validation PASS may physical-I/O A/B 002 be considered.
9. Only after a valid A/B 002 PASS integrate packed access into the exact runtime and benchmark end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
