# LOOM Roadmap

Last updated: 2026-08-26
Current: `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`
Strategic next: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002`
Canonical context: `/AGENTS.md` v3.27.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, subject to valid physical-I/O causality.

## Existing I/O evidence

Expert-major A/B 001 is INVALID due cache contamination, although exact payload identity and structural read reduction `3456 -> 384` are valid.

Frozen cold timing rule: every accepted repetition independently `>=80%` conservative physical coverage.

Fresh-inode byte-copy cold protocol is rejected (~21% coverage across three valid trials). Instrumentation persistence is repaired and PASS.

## Global-nocache validation 001

Overall classification remains `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL` because only T1 executed.

T1 provided the strongest cold-read evidence so far:
- `95.3113%` conservative physical coverage;
- `0.246744 s` wall;
- `153,010,000 / 152,910,000 B` raw/conservative physical bytes;
- payload/hash PASS;
- zero swap.

Execution stopped because raw RESET return `1` was incorrectly classified as failure.

## Reset semantics audit 001 — RESOLVED

Report: `research/architecture/loom-30b-global-nocache-reset-semantics-audit-001-result.md`.
Classification: `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`.

Local semantics are now established:
- `F_GLOBAL_NOCACHE=55`;
- SET `1` returns prior state `0`, errno `0`, and enables state 1;
- RESET `0` returns prior state `1`, errno `0`, and restores state 0;
- old RESET success predicate was wrong.

No passive GET exists. Transactional verification is reproducible with a fixed-ABI native helper and no payload read.

Future protocol: SET 1 requires raw 0; RESET 0 requires raw 1; explicitly capture errno; verify restoration with a second SET/RESET transaction; fail closed on any deviation.

Validation 001 is not retroactively reclassified because its preregistered 3/3 sequence was incomplete.

## Next

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002`

1. Same packed-only first-64-expert workload: `160,432,128 B/trial`.
2. Exactly three trials maximum.
3. Same physical coverage gate `>=80%` independently per trial.
4. Same payload/hash, instrumentation, memory and swap gates.
5. Only changed factor: correct fixed-ABI global-nocache set/reset/restoration semantics.
6. No source arm, model forward, network, DFlash, runtime integration, threshold change or post-hoc strategy modification.

If validation 002 PASSes 3/3, preregister `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002` — the first valid cold source-vs-packed causal timing comparison. Only after a valid A/B 002 PASS integrate expert-major packed access into the exact runtime and measure end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
