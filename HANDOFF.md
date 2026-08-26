# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access remains the dominant measured bottleneck. Expert-major packing remains promising; the prior cold-I/O blocker was instrumentation reliability and is now repaired/validated.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001_COLD_IO_INSTRUMENTATION_PASS`
Next: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`
Pi context: `/AGENTS.md` v3.23.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. INVALID/UNRESOLVED evidence cannot support performance claims.

## DFlash

Closed as active recovery path. Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

## 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage.

## A/B 001 + coverage audit

First physical-I/O A/B was INVALID despite structural read reduction `3456 -> 384` and exact payload equality. Packed aggregate conservative physical coverage was `50.0644%` because repeated reads became resident in macOS page cache; first packed repetition reached `94.26%`, later repeats `38.61–40.20%`.

Frozen future validity gate: every accepted timed repetition must independently show >=80% conservative physical coverage.

## Cold-I/O protocol validation 001

Classification: `PACKED_COLD_IO_PROTOCOL_UNRESOLVED`.
Candidate cache-state method remains unchanged:
- fresh non-cloned APFS inode;
- `O_CREAT|O_EXCL` byte-copy + `fsync`;
- `F_NOCACHE/F_RDAHEAD` supplementary.

The first `160,432,128 B` trial was not accepted because instrumentation failed after the timed read before required physical-counter and payload-validation evidence was persisted. This did not reject the cache-state method.

## Cold-I/O instrumentation repair 001

Classification: `COLD_IO_INSTRUMENTATION_PASS`.
Report: `research/architecture/loom-30b-cold-io-instrumentation-repair-001-result.md`.
Evidence: `results-local/research/30b-cold-io-instrumentation-repair-001/20260826T130155Z/`.

Root cause: `row.update()` indexed `row['payload_validation']` before the update inserted it, raising `KeyError` post-read/pre-persistence.

Validated repair:
- success-path persistence PASS;
- intentional fail-path persistence PASS;
- fail-closed missing-field gate PASS;
- probe bytes `16,777,216 B`;
- swap delta `0 B`.

This validates evidence capture only; it does not establish cache coldness or any performance claim.

## Exact next step

`LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002`

Retest the unchanged fresh-inode method with repaired instrumentation. Use at most three independent bounded fresh-inode trials around the same `160,432,128 B` representative packed subset. Every accepted trial must independently show >=80% conservative physical coverage, payload/hash PASS, complete internally consistent instrumentation, and safe memory/swap behavior.

No full source-vs-packed A/B, model forward, network, DFlash or runtime optimization. Only after `PACKED_COLD_IO_PROTOCOL_PASS` may physical-I/O A/B 002 be preregistered.
