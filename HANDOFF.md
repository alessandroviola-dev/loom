# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB path resumed. External expert data-access is the dominant measured bottleneck. First expert-major physical-I/O A/B showed a strong timing signal but is scientifically INVALID because packed physical coverage was only 50.06%.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001_EXPERT_MAJOR_PHYSICAL_IO_INVALID`
Next: `LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`
Pi context: `/AGENTS.md` v3.20.

## Protocol state

Canonical synchronization discipline is restored: after every significant scientific checkpoint, ChatGPT updates GitHub state and the user pulls before the next Pi WP. Do not advance from stale AGENTS/HANDOFF/ROADMAP.

## DFlash

Closed as active recovery path.
Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.
BF16 changes DFlash distributions but failed exact recovery on P3 and P1; preregistered >=2/3 signal became impossible, so P2/E2E were not run.

## 30B serving/I/O re-entry

Report: `research/architecture/loom-30b-moe-serving-io-reentry-001-result.md`.
Classification: `SERVING_IO_BOTTLENECK_IDENTIFIED`.

Dominant measured bottleneck: external expert data-access.
- data-access `0.442087 s` of `0.926028 s` median wall = `47.74%`;
- 384 reads, `962,592,768 B` expert payload;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention: lossless expert-major contiguous storage, subject to valid physical-I/O causality.

## Expert-major physical-I/O A/B 001

Report: `research/architecture/loom-30b-expert-major-physical-io-ab-001-result.md`.
Classification: `EXPERT_MAJOR_PHYSICAL_IO_INVALID`.
Evidence: `results-local/research/30b-expert-major-physical-io-ab-001/20260826T122942Z/`.

Observed:
- source p50/p95 `1.097739 / 1.116585 s`;
- packed p50/p95 `0.382613 / 0.552228 s`;
- apparent wall ratio `0.348547`;
- read count `3456 -> 384` per pass;
- effective throughput `874.539 -> 2275.084 MB/s`;
- byte/hash equality PASS.

Invalidity:
- packed physical coverage `50.06%`;
- physical/counter validity FAIL.

Therefore the apparent timing gain is not accepted yet. Read-count reduction and payload identity are valid structural facts only.

## Exact next step

`LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`

Diagnostic-only audit of the ~50% packed physical coverage. Reconstruct logical/physical byte accounting and counter semantics; distinguish cache/readahead/APFS/counter-scope causes; verify all 384 payloads. Only if retained evidence is insufficient, permit a <=3-expert / <=100 MiB probe. No full A/B, model forward, network, DFlash, or runtime optimization.
