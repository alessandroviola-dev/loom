# LOOM Roadmap

Last updated: 2026-08-26
Current: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Strategic next: `LOOM_30B_FIRST_TOUCH_NONREUSE_IO_DESIGN_001`
Canonical context: `/AGENTS.md` v3.28.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, subject to valid physical-I/O causality.

## Existing I/O evidence

Expert-major A/B 001 remains INVALID due cache contamination, although exact payload identity and structural read reduction `3456 -> 384` are valid.

Frozen physical-I/O timing rule: every accepted arm/repetition independently `>=80%` conservative physical coverage.

Fresh-inode byte-copy cold protocol is rejected. Instrumentation persistence and global-nocache set/reset semantics are resolved.

## Global-nocache validation 002 — FAIL

Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-002-result.md`.
Classification: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.

Repeated reads of the same 160,432,128-B packed region:
- T1 `96.0406%` coverage;
- T2 `25.8365%`;
- T3 `23.9728%`.

Payload/hash PASS 3/3; control set/reset/restoration PASS 3/3; swap delta 0 B; minimum free memory 56%.

Conclusion: first touch can be predominantly physical, but subsequent touches of the same pages are cache-served despite correct controls. Repeated-same-page cold enforcement is rejected. Do not spend more runs on additional eviction/control variants of this method.

## Next

`LOOM_30B_FIRST_TOUCH_NONREUSE_IO_DESIGN_001`

1. Inspect packed layout, source ranges, trace/expert identities and determine how many mutually disjoint matched source/packed payload groups exist.
2. Design repetitions so each uses payload pages not used by prior repetitions.
3. Within each matched pair, source and packed must represent exactly the same logical expert bytes; only storage layout/read fragmentation may differ.
4. Quantify overlap, offsets/ranges, unique bytes and expected cache/RAM interaction before execution.
5. Preserve `>=80%` conservative physical coverage independently for every arm/repetition.
6. Rank at most two designs; select exactly one bounded validation protocol before any full A/B.
7. No full A/B, model forward, network, DFlash, runtime integration, purge/reboot dependence, cache-thrash/RAM-fill, swap pressure or fresh-copy workaround during design.
8. Only after the non-reuse design passes a separately preregistered coverage validation may `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002` be considered.
9. Only after a valid A/B 002 PASS integrate expert-major access into the exact runtime and benchmark end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
