# LOOM Roadmap

Last updated: 2026-08-26
Current: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`
Strategic next: `LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`
Canonical context: `/AGENTS.md` v3.26.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck:
- `0.442087 / 0.926028 s = 47.74%` median wall;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, subject to valid physical-I/O causality.

## Existing I/O evidence

Expert-major A/B 001 is INVALID because repeated packed trials were cache-contaminated, although structural read reduction `3456 -> 384` and exact payload identity remain valid.

Frozen cold timing rule: every accepted timed repetition independently >=80% conservative physical coverage.

Fresh-inode byte-copy protocol is rejected after three valid ~160-MiB trials around 21% coverage. Instrumentation persistence is repaired and PASS.

Measurement redesign selected direct existing-packed reads with `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0`.

## Global-nocache validation 001 — protocol FAIL, coldness signal positive

Report: `research/architecture/loom-30b-expert-major-global-nocache-cold-io-validation-001-result.md`.
Classification: `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL`.

T1 achieved:
- `95.3113%` conservative physical coverage;
- `0.246744 s` wall;
- `153,010,000 B` raw / `152,910,000 B` conservative physical bytes;
- payload/hash PASS;
- control set PASS;
- swap delta 0 B;
- minimum free memory 59%.

This is the strongest evidence so far that the selected direct global-nocache approach can produce a genuinely physical packed read.

However post-trial reset of `F_GLOBAL_NOCACHE` returned `1` and the runner treated it as failure. The preregistered protocol therefore failed closed and T2/T3 were not run.

Do not reinterpret the return code post hoc. Do not rerun the large validation until local set/reset semantics and restoration verification are established.

## Next

`LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001`

1. Inspect exact runner/API call path and local constants.
2. Establish raw set/reset return-value and errno/exception semantics on this system.
3. Determine whether control state can be queried directly; otherwise define a minimal safe behavioral verification.
4. Use at most a tiny <=16 MiB probe only if required to resolve semantics.
5. Persist raw calls, returns, errors and final restoration evidence.
6. Select exactly one fail-safe control protocol if resolved.
7. No full 160-MiB validation, source arm, model forward, network, DFlash or performance claim.

Only after `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED` may another preregistered global-nocache cold-I/O validation be run. Only after that validation passes may physical-I/O A/B 002 be preregistered. Only after a valid A/B 002 PASS integrate packed access into the exact runtime and measure end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
