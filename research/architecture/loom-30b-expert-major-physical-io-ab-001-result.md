# LOOM — 30B Expert-Major Physical-I/O A/B 001 — Result

Date: 2026-08-26
Checkpoint: `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001`
Classification: `EXPERT_MAJOR_PHYSICAL_IO_INVALID`

## Observed timing signal

Source arm:
- p50 `1.097739 s`;
- p95 `1.116585 s`;
- `3456` reads/pass (`17280` total);
- effective throughput `874.539 MB/s`.

Packed expert-major arm:
- p50 `0.382613 s`;
- p95 `0.552228 s`;
- `384` reads/pass (`1920` total);
- effective throughput `2275.084 MB/s`.

Observed packed/source p50 wall ratio: `0.348547`.
Observed physical-bytes ratio: `0.501265`.

Exact expert byte/hash validation: PASS.

## Why the benchmark is invalid

The preregistered PASS gate required valid physical-I/O counters and packed physical bytes no greater than `1.05x` source under a genuinely comparable cold-read protocol.

Packed physical coverage was only `50.06%`; therefore physical/counter validity failed. The large wall-time improvement cannot yet be causally attributed to expert-major layout because the packed arm may have benefited from cache/readahead or counter-semantics effects.

The structural read-count reduction `3456 -> 384` is real, and payload equality passed, but the `0.348547x` timing result is not accepted as a scientific performance result until the coverage discrepancy is explained.

## Next checkpoint

`LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`

Diagnostic only. Before repeating any full A/B, determine exactly why packed physical coverage is ~50%, whether the prior timing can be recovered under corrected counter semantics, and the minimum correction required for a valid A/B.

No model forward, network, DFlash, or runtime optimization is justified before this audit.

Local evidence:
`results-local/research/30b-expert-major-physical-io-ab-001/20260826T122942Z/`
