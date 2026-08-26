# LOOM — 30B Expert-Major I/O Coverage Audit 001

Date: 2026-08-26
Checkpoint: `LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`
Classification: `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`

## Decision

The first expert-major physical-I/O A/B remains invalid as a cold/physical comparison. The packed arm was increasingly served from macOS file/page cache despite accepted `F_NOCACHE/F_RDAHEAD` hints.

## Exact accounting

Per pass both arms request exactly `962,592,768 B`.
Across five passes each: `4,812,963,840 B` logical bytes.

Source:
- 3,456 unique non-overlapping ranges across four files;
- total source file size `16,220,657,512 B`;
- conservative background-subtracted physical bytes `4,807,000,000 B`;
- physical coverage `99.8761%`.

Packed:
- 384 unique non-overlapping ranges covering one fully allocated `962,592,768 B` file;
- conservative background-subtracted physical bytes `2,409,580,000 B`;
- physical coverage `50.0644%`.

All 384 expert payloads remain exact: 3,456 components / `962,592,768 B`, zero byte/hash/metadata mismatches.

## Root cause

Coverage is defined as the sum of `max(0, iostat_device_bytes - 12,340,000 B idle_max)` divided by aggregate requested bytes.

Packed physical delivery by repetition fell from `907.39 MB` net (`94.26%`) on the first valid-like pass to `386.95`, `371.72`, `371.84`, and `371.68 MB` (`38.61–40.20%`) on subsequent reads.

Audit excluded duplicate/overlapping ranges, sparse allocation, APFS clone construction, counter units, trace-subset mismatch and payload mismatch. The supported cause is packed-file OS cache residency surviving the accepted cache-control hints.

## Interpretation

The prior packed timing (`p50 0.382613 s`, apparent ratio `0.348547`) is not reusable as a cold physical-I/O speedup claim. It remains only an uncontrolled application-read observation.

Structural facts that remain valid:
- exact packed/source payload equality;
- 3,456 -> 384 logical read-count reduction;
- expert-major packed representation is lossless.

## Minimum requirement before another performance claim

Every timed repetition in both arms must demonstrate at least `80%` conservative physical coverage. Any repetition below that threshold is invalid and cannot contribute to wall-time comparison.

## Next

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`

Validate a reproducible packed cold-read protocol first, with bounded diagnostic I/O and no model forward. Do not repeat the full A/B until the protocol itself passes the per-repetition physical-coverage gate.

Local evidence:
`results-local/research/30b-expert-major-physical-io-ab-001/20260826T122942Z/`

Payload validation:
`results-local/moe/trace-pack-decode-ab-001/20260824T084956Z/pack-validation.json`
