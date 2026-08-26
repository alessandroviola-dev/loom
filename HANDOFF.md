# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access remains the dominant measured bottleneck. Repeated same-region cold enforcement is now rejected; first-touch behavior is strongly physical and the next direction is a non-reuse matched-payload design.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002_PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Next: `LOOM_30B_FIRST_TOUCH_NONREUSE_IO_DESIGN_001`
Pi context: `/AGENTS.md` v3.28.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. Failed/invalid/unresolved evidence cannot support performance claims. Failed frozen methods are not silently modified and rerun.

## Core 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, contingent on valid physical-I/O causality.

## Existing physical-I/O evidence

A/B 001 remains INVALID due cache contamination, although exact payload equality and structural read reduction `3456 -> 384` remain valid.

Frozen validity rule: every accepted timed repetition independently `>=80%` conservative physical coverage.

Fresh-inode byte-copy cold protocol is rejected (~21% physical coverage across three valid ~160-MiB trials). Instrumentation persistence and `F_GLOBAL_NOCACHE` control semantics are resolved.

## Global-nocache cold-I/O validation 002

Classification: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.
Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-002-result.md`.
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-002/20260826T141527Z/`.

Three repeated reads of the same first-64-expert packed region:
- T1 `96.0406%` conservative physical coverage, wall `0.251112 s`;
- T2 `25.8365%`, `0.226934 s`;
- T3 `23.9728%`, `0.228232 s`.

Payload/hash PASS 3/3; initial set/reset/restoration PASS 3/3; swap delta 0 B 3/3; minimum free memory 56%.

Interpretation: T1 establishes a strong first-touch physical-read signal, but the same pages become cache-served on T2/T3 despite correct controls. This is now a method failure, not a runner/instrumentation ambiguity. Do not keep iterating same-page eviction flags.

## Exact next step

`LOOM_30B_FIRST_TOUCH_NONREUSE_IO_DESIGN_001`

Analysis-first design of a measurement scheme that avoids page reuse. Inspect packed/source mappings and retained expert identities to determine whether multiple mutually disjoint matched payload groups can be constructed. Each repetition must compare identical logical expert bytes between source and packed while not touching payload pages used in prior repetitions. Preserve the `>=80%` conservative physical-coverage gate per arm/repetition and one-factor causality.

No full A/B, model forward, network, DFlash, runtime integration, purge/reboot/cache-thrash, swap pressure or fresh-copy workaround during design. Select one bounded validation design first.
