# LOOM DFlash Target Compatibility Audit 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`
Classification: `ENGINE_OR_DATA_BLOCKED`
Gate: `BLOCKED`

## Purpose

Audit the validated masked DFlash drafter against the current Qwen3-30B-A3B MLX 4-bit target, with exact target replay integrity as the hard first gate.

## Evidence

Local raw evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T144106Z/`

Files:
- `precondition.json`
- `provenance.json`

## Precondition result

The audit did not run target replay or compatibility scoring because the frozen continuation corpus is incomplete.

Available immutable frozen target decisions:
- `45/63` required decisions.

Missing data:
- `P1_t32`: 6 continuation tokens missing;
- `P2_t32`: 6 continuation tokens missing;
- `P3_t32`: 6 continuation tokens missing.

Each `*_t32` state therefore has only one of the seven required frozen continuation decisions available.

## Measurements not authorized

Because Gate A could not establish replay integrity, the following were not measured:
- current-target replay parity;
- frozen-continuation validation control;
- drafter/target top1 parity;
- target ranks of proposed tokens;
- top-k hit rates;
- proposed-token log-probabilities;
- target margins;
- accepted-prefix distribution.

## Root conclusion

Gate A cannot establish target replay integrity without immutable seven-token frozen continuations for all nine states.

The compatibility verdict remains `CONDITIONAL`.

Do not create the missing 18 historical decisions by simply running the same current target/scoring path that the replay gate is intended to validate; that would make the replay proof circular.

## Next checkpoint

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`

Recover an existing pre-audit continuation artifact if one exists locally and has usable provenance. If none exists, create a new explicitly rebaselined seven-token continuation corpus with an independent already-validated target oracle path, not the later compatibility scoring/replay path.

The freeze checkpoint must:
1. preserve the same nine frozen prefixes/states;
2. verify the already-existing historical first continuation token before extending each state;
3. generate/freeze seven target tokens per state with the independent oracle;
4. deterministic rerun PASS;
5. hash/provenance the complete 63-token artifact;
6. clearly label newly generated decisions as a new reference baseline rather than pretending they were historically frozen.

Only after this artifact exists may `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` be rerun.

## Gate

`BLOCKED — FROZEN_CONTINUATION_CORPUS_INCOMPLETE`
