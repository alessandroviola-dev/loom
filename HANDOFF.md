# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access is the dominant measured bottleneck. Expert-major packing remains structurally promising, but the first physical-I/O A/B is invalid because repeated packed reads were increasingly served from macOS cache.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_IO_COVERAGE_AUDIT_001_PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`
Next: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`
Pi context: `/AGENTS.md` v3.21.

## Synchronization

After each significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. Do not advance from stale project docs.

## DFlash

Closed as active recovery path. Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

## 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` = `SERVING_IO_BOTTLENECK_IDENTIFIED`.
Report: `research/architecture/loom-30b-moe-serving-io-reentry-001-result.md`.

Dominant bottleneck: external expert data-access.
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` payload / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

## Expert-major A/B 001

`EXPERT_MAJOR_PHYSICAL_IO_INVALID`.
Observed source p50 `1.097739 s`, packed p50 `0.382613 s`, apparent ratio `0.348547`, reads/pass `3456 -> 384`, payload equality PASS. Timing not accepted because packed physical coverage was only ~50%.

## Coverage audit 001

`PACKED_COVERAGE_CACHE_CONTAMINATION_IDENTIFIED`.
Report: `research/architecture/loom-30b-expert-major-io-coverage-audit-001-result.md`.

Exact logical bytes/pass both arms: `962,592,768 B`.
Source conservative physical coverage: `99.8761%`.
Packed conservative physical coverage: `50.0644%`.

Packed first valid-like repetition reached `94.26%`; later repeats only `38.61–40.20%`. All 384 payloads are byte/hash exact, with no duplicate/overlap/sparse/clone/counter explanation. Supported cause: packed-file OS/page-cache residency survives accepted `F_NOCACHE/F_RDAHEAD` hints.

Therefore previous packed timing is not a valid cold-I/O speedup claim. Structural read reduction `3456 -> 384` remains valid.

Frozen future validity rule: every timed repetition in either arm must independently show >=80% conservative physical coverage; otherwise reject that repetition.

## Exact next step

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_001`

Validate a bounded, reproducible method for obtaining genuinely physical packed reads before rerunning the full A/B. No model forward/network/runtime optimization. PASS requires repeated packed trials >=80% conservative physical coverage without unsafe RAM/swap pressure. Only after PASS may A/B 002 be preregistered.
