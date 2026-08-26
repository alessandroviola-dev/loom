# LOOM Roadmap

Last updated: 2026-08-26
Current: `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`
Strategic next: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`
Canonical context: `/AGENTS.md` v3.21.

## DFlash — closed

Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.
BF16 did not restore exact speculation on P3/P1; preregistered >=2/3 became impossible. Preserve artifacts only.

## Core 30B-on-8GB serving

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified **external expert data-access** as the dominant measured bottleneck.
Report: `research/architecture/loom-30b-moe-serving-io-reentry-001-result.md`.

Measured decode-equivalent breakdown:
- expert access `0.442087 / 0.926028 s = 47.74%`;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage.

## Expert-major A/B 001 — invalid

Report: `research/architecture/loom-30b-expert-major-physical-io-ab-001-result.md`.
Observed source p50 `1.097739 s`, packed p50 `0.382613 s`, apparent ratio `0.348547`, reads/pass `3456 -> 384`, byte/hash equality PASS.

No speedup claim accepted because packed physical coverage was only `50.06%`.

## Coverage audit 001

Report: `research/architecture/loom-30b-expert-major-io-coverage-audit-001-result.md`.
Classification: `PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`.

Both arms request exactly `962,592,768 B/pass`.
Source conservative physical coverage `99.8761%`; packed `50.0644%`.
Packed first repetition reached `94.26%`; subsequent repeats fell to `38.61–40.20%` because packed-file macOS cache residency survives `F_NOCACHE/F_RDAHEAD` hints.

Payload identity and structural read reduction remain valid. Previous packed timing cannot be reused as cold physical-I/O evidence.

## Next

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`

Before A/B 002:
1. validate a reproducible packed cold-read/cache-state protocol with bounded diagnostic I/O;
2. do not rely on `F_NOCACHE/F_RDAHEAD` alone;
3. require >=80% conservative physical coverage independently on every accepted packed trial;
4. reject methods that induce unsafe RAM/swap pressure;
5. no model forward, network, DFlash or runtime optimization.

Only after protocol PASS preregister `LOOM_30B_EXPERT_MAJOR_PHYSICAL_IO_AB_002`. Only after a valid A/B PASS integrate expert-major packed access into the exact runtime and measure end-to-end tok/s.

## Synchronization rule

Every significant checkpoint must be committed to AGENTS/HANDOFF/ROADMAP/result docs before the next scientific WP; user pulls first.
