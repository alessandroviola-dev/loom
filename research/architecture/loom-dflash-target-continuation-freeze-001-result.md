# LOOM DFlash Target Continuation Freeze 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001`
Classification: `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`
Gate: `PASS`

## Purpose

Remove the immutable-data blocker that prevented Gate A of `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001` from running, without circularly generating the missing continuation decisions through the compatibility replay/scoring path itself.

## Recovery result

Historical recovery was attempted first.

Result:
`NOT_RECOVERED_INCOMPLETE_P1_P2_P3_T32`

The existing frozen corpus remained incomplete at 45/63 required target continuation decisions. Each of `P1_t32`, `P2_t32`, and `P3_t32` lacked six continuation tokens.

## Rebaselined reference

Because a complete provenance-valid historical corpus was not recovered, a new reference was generated through the independent validated target-oracle path.

Baseline type:
`REBASELINED_REFERENCE`

The same nine exact frozen P1/P2/P3 states were retained.

Before accepting any new decisions, the oracle was required to reproduce every historical frozen decision already available.

Historical-overlap gate:
- existing historical decisions: 45;
- exact matches: 45/45;
- first mismatch: none.

Only after that gate passed were the 18 previously missing decisions accepted as new `REBASELINED_REFERENCE` data.

Final corpus:
- states: 9 exact frozen states;
- continuation decisions: 63/63 complete;
- historical decisions preserved: 45;
- newly supplied rebaselined decisions: 18.

The 18 new decisions are explicitly not represented as historical observations.

## Determinism / validity

- deterministic rerun: PASS;
- NaN/Inf: none.

## Frozen artifact

Canonical reference artifact SHA-256:

`0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`

Raw evidence:
`results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/`

Provenance:
`results-local/research/dflash-target-continuation-freeze-001/20260824T145202Z/provenance.json`

Local runner:
`scripts/loom_dflash_target_continuation_freeze_001.py`

Additional evidence JSON artifacts are stored in the same evidence directory.

## Interpretation

The previous compatibility-audit blocker is removed.

The new complete reference is scientifically usable because:
1. it was not generated through the later compatibility replay/scoring path;
2. the independent oracle exactly reproduces all 45 historical frozen decisions;
3. the complete 63-decision artifact is deterministic, finite, provenance-recorded and content-hashed;
4. the 18 newly supplied decisions remain explicitly labeled as rebaselined reference data.

This checkpoint makes no drafter/target compatibility claim and no causal claim about 4-bit quantization.

## Next

Resume `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`.

First verify the frozen artifact hash and run Gate A against the complete 63-decision reference. Require exact current-target replay and validation-control recovery before interpreting any drafter proposal statistics.

If replay/control passes, characterize validated DFlash proposals under exact target-prefix conditioning using top1 parity, target rank, log-probability, top-k inclusion, target margins and accepted-prefix distribution.

Do not rerun full E2E and do not change target, drafter, weights, mapping, acceptance rules or memory/performance variables.