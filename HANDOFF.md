# LOOM — Active Handoff

Last updated: 2026-08-26
Status: ACTIVE — core 30B-on-8GB serving/I/O. Direct existing-packed `F_GLOBAL_NOCACHE` produced a strong cold-read signal (`95.3113%`). The prior reset failure was a runner interpretation bug; local set/reset semantics are now resolved.
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_30B_GLOBAL_NOCACHE_RESET_SEMANTICS_AUDIT_001_GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`
Next: `LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002`
Pi context: `/AGENTS.md` v3.27.

## Synchronization

After every significant checkpoint: ChatGPT updates canonical GitHub state, user pulls, then next Pi WP. Failed/invalid/unresolved evidence cannot support performance claims. Control/API semantics affecting scientific gates must be established explicitly.

## Core 30B serving/I/O

`LOOM_30B_MOE_SERVING_IO_REENTRY_001` identified external expert data-access as dominant:
- access `0.442087 / 0.926028 s = 47.74%` median wall;
- `962,592,768 B` / 384 expert reads;
- expert compute `0.004186 s`;
- routing `0.019075 s`;
- physical token-like I/O floor `0.481589 s/token`.

Priority intervention remains lossless expert-major contiguous storage, contingent on valid physical-I/O causality.

## Existing physical-I/O evidence

A/B 001 is INVALID due cache contamination, although exact payload equality and structural read reduction `3456 -> 384` remain valid.

Frozen cold timing rule: every accepted timed repetition independently `>=80%` conservative physical coverage.

Fresh-inode byte-copy protocol is rejected (~21% physical coverage across three valid ~160-MiB trials). Instrumentation persistence is repaired and PASS.

## Global-nocache validation 001

Classification remains `PACKED_GLOBAL_NOCACHE_COLD_IO_FAIL` because the preregistered 3/3 sequence terminated after T1.

T1 itself achieved:
- conservative physical coverage `95.3113%`;
- wall `0.246744 s`;
- raw/conservative physical `153,010,000 / 152,910,000 B`;
- payload/hash PASS;
- swap delta `0 B`;
- minimum free memory `59%`.

The runner stopped because RESET returned raw `1` and was incorrectly treated as failure.

## Reset semantics audit 001

Classification: `GLOBAL_NOCACHE_RESET_SEMANTICS_RESOLVED`.
Report: `research/architecture/loom-30b-global-nocache-reset-semantics-audit-001-result.md`.
Evidence: `results-local/research/30b-global-nocache-reset-semantics-audit-001/20260826T135941Z/`.

Exact local semantics:
- `F_GLOBAL_NOCACHE=55`;
- SET argument `1`: raw `0`, errno `0`, state `0 -> 1`;
- RESET argument `0`: raw `1`, errno `0`, state `1 -> 0`;
- therefore old `returned == 0` RESET predicate was wrong.

No passive GET exists locally. Reversible transactional checks on empty files produced `[0,1,0,1,0,1]` under native C, Python fcntl, and fixed-ABI C/ctypes, with no payload read.

Frozen future control protocol uses a fixed-ABI native helper with explicit errno capture: SET 1 requires raw 0; RESET 0 requires raw 1; then verify restoration transactionally with another SET 1 -> 0 / RESET 0 -> 1 pair. Any deviation fails closed.

## Exact next step

`LOOM_30B_EXPERT_MAJOR_GLOBAL_NOCACHE_COLD_IO_VALIDATION_002`

Repeat the same packed-only 3-trial validation on the first 64 experts (`160,432,128 B/trial`) with unchanged coldness/safety thresholds. The only repaired factor is correct global-nocache control semantics using the fixed-ABI helper.

PASS requires all 3/3 trials >=80% conservative physical coverage, payload/hash PASS, complete instrumentation, control set/reset/restoration PASS, swap delta <=16,000,000 B, free memory >=10%, and no unsafe pressure.

Only after PASS may physical-I/O A/B 002 be preregistered.
