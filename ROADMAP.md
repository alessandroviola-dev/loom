# LOOM Roadmap

Last updated: 2026-08-26
Current: `COLD_IO_MEASUREMENT_STRATEGY_SELECTED`
Strategic next: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001`
Canonical context: `/AGENTS.md` v3.25.

## DFlash — closed

Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`. Preserve artifacts only; do not reopen absent a new independent mechanism.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, subject to valid physical-I/O causality.

## Existing I/O evidence

Expert-major A/B 001 is INVALID because repeated packed trials were cache-contaminated, although structural read reduction `3456 -> 384` and exact payload identity are valid.

Frozen cold timing rule: every accepted timed repetition must independently show >=80% conservative physical coverage.

Instrumentation repair is PASS.

Fresh-inode byte-copy cold protocol is FAIL: `21.7537%`, `21.6914%`, `20.8250%` coverage on three valid 160,432,128-B trials; payload/hash PASS; swap 0 B. Do not modify/rerun it post hoc.

## Measurement strategy redesign 001 — SELECTED

Report: `research/architecture/loom-30b-cold-io-measurement-strategy-redesign-001-result.md`.
Classification: `COLD_IO_MEASUREMENT_STRATEGY_SELECTED`.

Tiny permitted 32-MiB probe:
- `F_GLOBAL_NOCACHE` accepted locally;
- global+descriptor coverage `49.35%`;
- descriptor-only `57.58%`;
- hashes PASS;
- no swap increase.

The probe establishes mechanism availability only; it does not establish adequate coldness or performance.

Selected next strategy: read the existing packed payload directly with `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` set before any payload read, using a fresh read-only FD and resetting global control after the trial. This removes fresh-copy/write preparation from the measurement path.

`purge(8)` rejected as system-wide/disruptive. Fresh-copy-under-global-nocache is deferred because it adds causal confounding.

## Next

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001`

1. Packed-only, first 64 packed experts, `160,432,128 B/trial`.
2. Exactly 3 trials maximum.
3. Fresh read-only FD each trial.
4. Set `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before first payload read; fail closed on control failure.
5. Capture three idle `iostat -Id` intervals and repaired full instrumentation.
6. Timed 4-MiB-chunk read/hash; persist evidence; reset global control after each trial.
7. PASS only if all 3/3 trials independently satisfy >=80% conservative physical coverage, payload/hash PASS, complete consistent instrumentation, control set/reset PASS, swap delta <=16,000,000 B, free memory >=10%, and no unsafe pressure.
8. FAIL if any trial is below 80% or any safety/control/hash/persistence gate fails.
9. No source arm, model forward, network, DFlash or runtime integration in this validation.

Only after `PACKED_GLOBAL_NOCACHE_COLD_IO_PASS` preregister physical-I/O A/B 002. Only after valid A/B 002 PASS integrate expert-major packed access into the exact runtime and measure end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
