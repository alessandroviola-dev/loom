# LOOM — Expert-major cold-I/O protocol validation 001

Date: 2026-08-26
Checkpoint: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`
Classification: `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`

## Result

Candidate cache-state method selected: fresh non-cloned APFS inode created with `O_CREAT|O_EXCL`, byte-copy, and `fsync`; `F_NOCACHE/F_RDAHEAD` supplementary only.

The scientific protocol did not complete because instrumentation aborted after the first timed read before physical-counter and payload-validation evidence was persisted.

Observed trial state:
- trial 1: timed read attempted, but physical counters were not persisted; not accepted;
- trials 2–3: not run, correctly fail-closed;
- logical payload attempted: `160,432,128 B`;
- physical bytes: unavailable/not persisted;
- free memory: `59% -> 60%`;
- swap delta: `0 B`;
- payload/hash validation: unavailable/not persisted.

No cold-I/O performance or >=80% physical-coverage claim is accepted from this checkpoint.

## Interpretation

This is an instrumentation failure, not evidence that the fresh-inode cache-state method fails. Do not repeat the full protocol until evidence capture is made fail-safe.

## Next

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001`

Repair/validate persistence of pre/post device counters, logical-byte accounting, payload/hash validation, wall time, read count, and memory/swap state using only a tiny bounded synthetic/representative probe. No full 160 MiB trial, no model forward, no network, no A/B.

Only after instrumentation PASS may `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002` retest the selected fresh-inode method.

Local evidence: `results-local/research/30b-expert-major-cold-io-protocol-validation-001/20260826T125114Z/`.
