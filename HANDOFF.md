# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access is the dominant measured bottleneck. Expert-major packing remains promising, but cold-I/O validation is currently blocked by instrumentation reliability rather than by a negative storage-layout result.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001_PACKED_COLD_IO_PROTOCOL_UNRESOLVED`
Next: `LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001`
Pi context: `/AGENTS.md` v3.22.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. INVALID/UNRESOLVED evidence cannot support performance claims.

## DFlash

Closed as active recovery path. Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

## 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage.

## A/B 001 + coverage audit

First physical-I/O A/B was INVALID despite structural read reduction `3456 -> 384` and exact payload equality. Packed aggregate conservative physical coverage was `50.0644%` because repeated reads became resident in macOS page cache; first packed repetition reached `94.26%`, later repeats `38.61–40.20%`.

Frozen future validity gate: every accepted timed repetition must independently show >=80% conservative physical coverage.

## Cold-I/O protocol validation 001

Classification: `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`.
Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-001-result.md`.
Evidence: `results-local/research/30b-expert-major-cold-io-protocol-validation-001/20260826T125114Z/`.

Selected candidate cache-state method:
- fresh non-cloned APFS inode;
- `O_CREAT|O_EXCL` byte-copy + `fsync`;
- `F_NOCACHE/F_RDAHEAD` supplementary.

Trial 1 attempted `160,432,128 B`, but instrumentation aborted after the timed read before physical counter bytes and payload/hash validation were persisted. Trial therefore not accepted; trials 2–3 were correctly not run fail-closed. Memory remained safe (`59% -> 60%` free); swap delta `0 B`.

This is not evidence against the fresh-inode method. It is an instrumentation failure.

## Exact next step

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001`

Repair evidence persistence and validate it end-to-end with only a <=16 MiB tiny probe. Required fields: pre/post device counters, derived physical bytes, logical bytes, wall time, read count, payload/hash result, memory/swap state. Validate both normal completion and intentional failure/exception persistence. No full cold trial, model forward, network, DFlash or A/B.

Only after `COLD_IO_INSTRUMENTATION_PASS` may a new `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002` retest the fresh-inode cache-state method.
