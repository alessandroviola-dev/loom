# LOOM — Expert-major cold-I/O protocol validation 002

Date: 2026-08-26
Checkpoint: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`
Classification: `PACKED_COLD_IO_PROTOCOL_FAIL`

## Purpose

Retest the frozen fresh-inode cold-read method after the instrumentation repair, without changing the scientific gate.

Frozen method:
- fresh non-cloned APFS inode via `O_CREAT|O_EXCL`;
- byte-copy selected packed payload;
- `fsync` before timed read;
- `F_NOCACHE/F_RDAHEAD` supplementary only.

Frozen acceptance gate: every accepted trial must independently show >=80% conservative physical coverage, payload/hash PASS, complete instrumentation, and safe memory/swap behavior.

## Result

Evidence:
`results-local/research/30b-expert-major-cold-io-protocol-validation-002/20260826T131142Z/`

All three trials used the same `160,432,128 B` representative payload and completed with valid payloads and zero swap delta.

| Trial | Conservative physical coverage | Wall | Raw physical bytes | Outcome |
|---|---:|---:|---:|---|
| 1 | 21.7537% | 0.221453 s | 37,090,000 B | FAIL |
| 2 | 21.6914% | 0.253920 s | 37,030,000 B | FAIL |
| 3 | 20.8250% | 0.224689 s | 37,140,000 B | FAIL |

Payload validation: PASS 3/3.
Swap delta: 0 B / 0 B / 0 B.
Trials satisfying >=80% physical coverage: 0/3.

## Interpretation

The fresh-inode method is rejected under the frozen protocol. The failure is reproducible and cannot be attributed to payload mismatch, missing instrumentation, or unsafe memory/swap behavior.

A plausible working hypothesis is that preparation by byte-copy leaves a substantial fraction of the freshly written file resident in the macOS page cache, so the immediately following read is not genuinely cold. This mechanism is not yet proven and must not be treated as established fact.

The failed method must not be silently modified and rerun under the same checkpoint. The prior INVALID A/B 001 remains invalid and no packed speedup claim is accepted.

## Decision

Do not preregister physical-I/O A/B 002 yet.

Next checkpoint: `LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001`.

Goal: analysis-first redesign of the cold-I/O measurement strategy. Inspect existing evidence and local macOS mechanisms, rank only safe candidate approaches, and select one bounded validation experiment with a frozen >=80% physical-coverage gate. Avoid RAM-thrashing/swap-based eviction, model forward, network, DFlash, and full source-vs-packed A/B.
