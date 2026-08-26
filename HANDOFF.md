# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. External expert data-access remains the dominant measured bottleneck. Expert-major packing is still structurally promising, but the fresh-inode cold-read protocol has now failed reproducibly and must be replaced before a valid physical-I/O A/B.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_EXPERT_MAJOR_COLD_IO_PROTOCOL_VALIDATION_002_PACKED_COLD_IO_PROTOCOL_FAIL`
Next: `LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001`
Pi context: `/AGENTS.md` v3.24.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. INVALID/UNRESOLVED evidence cannot support performance claims. Failed frozen methods cannot be silently modified and rerun under the same checkpoint.

## DFlash

Closed as active recovery path. Final report: `research/architecture/loom-dflash-bf16-causal-decision-001-result.md`.

## 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, contingent on valid physical-I/O causality.

## A/B 001 + coverage audit

First physical-I/O A/B was INVALID despite structural read reduction `3456 -> 384` and exact payload equality. Packed aggregate conservative physical coverage was `50.0644%`; first packed repetition reached `94.26%`, later repeats `38.61–40.20%`, consistent with macOS page-cache residency.

Frozen future timing gate: every accepted repetition must independently show >=80% conservative physical coverage.

## Instrumentation repair

`LOOM_30B_COLD_IO_INSTRUMENTATION_REPAIR_001` = `COLD_IO_INSTRUMENTATION_PASS`.
Success/failure persistence and fail-closed missing-field behavior are validated; instrumentation is no longer the blocker.

## Cold-I/O protocol validation 002

Classification: `PACKED_COLD_IO_PROTOCOL_FAIL`.
Report: `research/architecture/loom-30b-expert-major-cold-io-protocol-validation-002-result.md`.
Evidence: `results-local/research/30b-expert-major-cold-io-protocol-validation-002/20260826T131142Z/`.

Frozen method:
- fresh non-cloned APFS inode;
- `O_CREAT|O_EXCL` byte-copy;
- `fsync`;
- `F_NOCACHE/F_RDAHEAD` supplementary.

Three valid `160,432,128 B` trials:
- T1 coverage `21.7537%`, wall `0.221453 s`, raw physical `37,090,000 B`;
- T2 `21.6914%`, `0.253920 s`, `37,030,000 B`;
- T3 `20.8250%`, `0.224689 s`, `37,140,000 B`.
Payload/hash PASS 3/3; swap delta 0 B 3/3. Zero trials met >=80% coverage.

The method is therefore rejected. A plausible but unproven hypothesis is that byte-copy preparation itself leaves the fresh file resident in cache; this is not yet an established causal fact.

## Exact next step

`LOOM_30B_COLD_IO_MEASUREMENT_STRATEGY_REDESIGN_001`

Analysis-first redesign of how to obtain/measure genuinely physical cold reads on macOS. Inspect retained evidence and local mechanisms, rank at most three safe candidate strategies, reject RAM-thrashing/swap/reboot-dependent approaches, and select one bounded validation experiment with the existing >=80% per-trial conservative physical-coverage gate. No full A/B, model forward, network, DFlash, or runtime integration during redesign.
