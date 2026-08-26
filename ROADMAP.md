# LOOM Roadmap

Last updated: 2026-08-26
Current: `EXPERT_MAJOR_PHYSICAL_IO_INVALID`
Strategic next: `LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`
Canonical context: `/AGENTS.md` v3.20.

## DFlash — closed as active path

Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.
BF16 affects DFlash distributions but did not restore exact speculation on P3/P1; the preregistered >=2/3 signal became impossible. Preserve artifacts; do not reopen without a new independent mechanism.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified the dominant measured bottleneck as **external expert data-access**.
Report: `research/architecture/loom-30b-moe-serving-io-reentry-001-result.md`.

Measured decode-equivalent breakdown:
- expert access `0.442087 / 0.926028 s = 47.74%`;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

The highest-priority evidence-supported intervention is lossless expert-major contiguous storage. Large 4-GiB raw LRU remains rejected because of swap pressure.

## Expert-major A/B 001

`LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_001` produced a strong but invalid timing signal.
Report: `research/architecture/loom-30b-expert-major-physical-io-ab-001-result.md`.

Observed:
- source p50 `1.097739 s`;
- packed p50 `0.382613 s`;
- apparent ratio `0.348547`;
- reads/pass `3456 -> 384`;
- byte/hash equality PASS.

However packed physical coverage was only `50.06%`; physical/counter validity failed. No speedup claim is accepted from this run.

## Next

`LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001`

Before repeating the A/B or modifying runtime code:
1. explain the ~50% packed physical coverage from retained evidence;
2. distinguish counter semantics from cache/readahead/APFS or sampling contamination;
3. verify full 384-expert payload identity and exact logical/physical byte accounting;
4. if necessary, use only a <=100 MiB diagnostic probe;
5. decide whether the old timing can be reused and define the minimum correction for a valid A/B.

Only after this audit may a corrected physical-I/O A/B be preregistered. Only after a valid A/B PASS may expert-major packed access be integrated into the exact runtime and benchmarked end-to-end.

## Synchronization rule

A significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls the updated branch first. Micro-diagnostics may be grouped only if the canonical checkpoint does not change.
