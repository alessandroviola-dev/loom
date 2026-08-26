# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access remains the dominant measured bottleneck. Fresh-inode cold preparation failed; a new direct-existing-packed `F_GLOBAL_NOCACHE` measurement strategy has been selected but is not yet validated.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001_COLD_IO_MEASUREMENT_STRATEGY_SELECTED`
Next: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001`
Pi context: `/AGENTS.md` v3.25.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. INVALID/UNRESOLVED evidence cannot support performance claims. Failed frozen methods cannot be silently modified and rerun under the same checkpoint.

## DFlash

Closed as active recovery path. Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

## 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, contingent on valid physical-I/O causality.

## Previous physical-I/O evidence

A/B 001 was INVALID despite structural read reduction `3456 -> 384` and exact payload equality because packed coverage was cache-contaminated.

Coverage audit established source conservative physical coverage `99.8761%`, packed aggregate `50.0644%`; first packed repetition `94.26%`, later `38.61–40.20%`. Future timing requires >=80% conservative physical coverage on every accepted repetition.

Instrumentation repair is PASS and no longer a blocker.

Fresh-inode byte-copy protocol validation 002 is `PACKED_COLD_IO_PROTOCOL_FAIL`: three valid 160,432,128-B trials produced `21.7537%`, `21.6914%`, `20.8250%` coverage. Payload/hash PASS 3/3; swap 0 B. Method rejected.

## Measurement strategy redesign 001

Classification: `COLD_IO_MEASUREMENT_STRATEGY_SELECTED`.
Report: `research/architecture/loom-30b-cold-io-measurement-strategy-redesign-001-result.md`.
Evidence: `results-local/research/30b-cold-io-measurement-strategy-redesign-001/20260826T133031Z/`.

A permitted 32-MiB mechanism probe showed:
- `F_GLOBAL_NOCACHE` is accepted locally;
- global+descriptor coverage `49.35%` vs descriptor-only `57.58%`;
- hashes PASS;
- swap increase 0 B.

This probe establishes availability only, not adequate coldness.

Selected strategy:
- direct read of existing packed payload, avoiding preparation write/read;
- fresh read-only FD each trial;
- `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before any payload read;
- reset global control afterward;
- physical coverage remains the per-trial validity gate.

`purge(8)` rejected as system-wide/disruptive. Fresh-copy-under-global-nocache deferred because it adds write/copy confounding.

## Exact next step

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001`

Packed-only validation on first 64 packed experts (`160,432,128 B/trial`), exactly three trials maximum. Each trial must use a fresh read-only FD, set global/per-FD nocache controls before first payload read, capture three idle iostat intervals, perform timed 4-MiB-chunk read/hash with repaired instrumentation, then reset global control.

PASS only if 3/3 independently achieve >=80% conservative physical coverage, payload/hash PASS, complete consistent instrumentation, successful control set/reset, swap delta <=16,000,000 B, free memory >=10%, and no unsafe pressure.

No full source-vs-packed A/B, model forward, network, DFlash or runtime integration until this validation passes.
