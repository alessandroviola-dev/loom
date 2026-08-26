# LOOM — 30B Cold-I/O Measurement Strategy Redesign 001 — Result

Date: 2026-08-26
Classification: `COLD_IO_MEASUREMENT_STRATEGY_SELECTED`
Local evidence: `results-local/research/30b-cold-io-measurement-strategy-redesign-001/20260826T133031Z/`

## Decision

Selected strategy: direct read of the existing packed expert-major payload using `F_GLOBAL_NOCACHE=1` together with per-FD `F_NOCACHE=1` and `F_RDAHEAD=0`, applied before any payload read and reset afterward.

This strategy removes the failed fresh-inode byte-copy preparation step entirely. It does not rely on RAM filling, swap pressure, reboot, or system-wide purge.

## Mechanism probe

A bounded 32-MiB availability/semantics probe was permitted by the preregistration.

Observed:
- `F_GLOBAL_NOCACHE` was accepted locally;
- conservative physical coverage with global+descriptor controls: `49.35%`;
- descriptor-only comparison: `57.58%`;
- hashes PASS;
- swap increase `0 B`.

Interpretation: the control is locally available and usable, but the tiny probe does **not** establish adequate coldness and is not a performance result. The write-side-cache hypothesis remains supported but is not proven as the sole cause of the failed fresh-inode protocol.

## Candidate ranking

1. **Selected:** direct existing packed payload read with `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before first read; reset global control afterward. No preparation write/read; per-trial physical coverage remains the validity authority.
2. Fresh packed subset written under `F_GLOBAL_NOCACHE` before first write. Rejected for now because copy/write introduces additional causal confounding, storage I/O and complexity.
3. `purge(8)`. Rejected because it is system-wide, operationally disruptive and vulnerable to background-I/O contamination.

## Preregistered next validation

Checkpoint: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_001`.

Workload:
- packed-only validation;
- first 64 packed experts;
- `160,432,128 B` logical payload/trial;
- 3 trials maximum;
- fresh read-only FD each trial;
- set `F_GLOBAL_NOCACHE=1`, `F_NOCACHE=1`, `F_RDAHEAD=0` before any payload read;
- three idle `iostat -Id` intervals for conservative background accounting;
- timed 4-MiB-chunk read/hash;
- persist repaired instrumentation;
- reset global control after each trial, fail closed if set/reset fails.

PASS only if all 3/3 trials satisfy:
- conservative physical coverage `>=80%`;
- payload/hash PASS;
- complete arithmetic-consistent persisted instrumentation;
- successful control set/reset;
- swap delta `<=16,000,000 B`;
- free memory `>=10%`;
- no unsafe memory-pressure event.

FAIL if any trial is below 80% or any safety/control/hash/persistence gate fails.

No model forward, network, DFlash, source-vs-packed A/B or runtime integration is authorized by this checkpoint.
