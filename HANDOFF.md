# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access remains the dominant measured bottleneck. Direct existing-packed `F_GLOBAL_NOCACHE` produced the strongest cold-read signal so far, but the preregistered validation failed closed on reset semantics.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001_PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Next: `LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`
Pi context: `/AGENTS.md` v3.26.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. Failed/invalid/unresolved evidence cannot support performance claims. Return-value semantics that affect a gate must be established explicitly rather than assumed.

## Core 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, contingent on valid physical-I/O causality.

## Prior I/O findings

Expert-major A/B 001 is INVALID because repeated packed trials were cache-contaminated. Structural read reduction `3456 -> 384` and exact payload identity remain valid.

Frozen future timing gate: every accepted repetition independently >=80% conservative physical coverage.

Fresh-inode byte-copy protocol is rejected after three valid ~160-MiB trials at only ~21% physical coverage. Instrumentation persistence repair is PASS.

The redesigned strategy uses direct reads of the existing packed payload with `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before any payload read.

## Global-nocache cold-I/O validation 001

Classification: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.
Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-001-result.md`.
Evidence: `results-local/research/30b-expert-major-global-nocache-cold-io-validation-001/20260826T134143Z/`.

Trial 1:
- conservative physical coverage `95.3113%`;
- wall `0.246744 s`;
- raw physical `153,010,000 B`;
- conservative physical `152,910,000 B`;
- payload/hash PASS;
- control set PASS;
- swap delta `0 B`;
- minimum free memory `59%`.

Coldness itself passed strongly. The protocol failed because the post-trial `F_GLOBAL_NOCACHE` reset returned `1`, which the runner classified as reset failure. Per the frozen fail-closed protocol, T2/T3 were not executed.

Current interpretation: the direct global-nocache mechanism remains promising; the blocker is exact control/reset semantics, not physical coverage. Do not assume return `1` means either success or failure without direct evidence.

## Exact next step

`LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`

Inspect the exact local runner/API behavior for `F_GLOBAL_NOCACHE` set/reset. Determine raw return and error semantics, whether state can be directly queried, and how to verify safe restoration. No full 160-MiB trial or performance benchmark. A tiny <=16 MiB behavioral probe is allowed only if necessary. Resolve one fail-safe control protocol before another cold-I/O validation attempt.
