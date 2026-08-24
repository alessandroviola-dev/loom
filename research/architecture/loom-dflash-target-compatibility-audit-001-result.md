# LOOM DFlash Target Compatibility Audit 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`
Classification: `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`
Gate: `PASS`

## Purpose

Audit the validated masked DFlash drafter against the current Qwen3-30B-A3B MLX 4-bit target, with exact target replay integrity as a hard precondition before interpreting compatibility.

## Attempt history

The first attempt stopped as `ENGINE_OR_DATA_BLOCKED` because only 45/63 immutable continuation decisions existed. No compatibility measurements were made in that attempt.

`LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS` subsequently supplied a complete provenance-safe `REBASELINED_REFERENCE`:
- historical overlap 45/45;
- 63/63 decisions complete;
- 18 new decisions explicitly labeled `REBASELINED_REFERENCE`;
- deterministic rerun PASS;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

The compatibility audit was then resumed.

## Evidence

Final raw evidence:
`results-local/research/dflash-target-compatibility-audit-001/20260824T151134Z/`

Runner:
`scripts/loom_dflash_target_compatibility_audit_001.py`

## Replay / validator gates

- frozen-reference SHA-256: PASS;
- current-target replay: 63/63 PASS;
- frozen-target control through the scoring path: 63/63 PASS;
- deterministic rerun: PASS;
- NaN/Inf: none.

Therefore the target reference and the compatibility scorer are valid for this corpus.

## Drafter versus target

Decisions scored: 63.

Top1 parity:
- `0/63` = `0%`.

First mismatch:
- state: `P1_t01`;
- proposal position: 1;
- drafter proposal token: `1778`;
- target top1 token: `12050`;
- proposed-token target rank: `23,235`;
- proposed-token target log-probability: `-40.4061`.

Target-rank distribution of drafter proposals:
- minimum: `987`;
- P50: `14,195`;
- mean: `28,621.08`;
- maximum: `146,487`.

Top-k inclusion:
- top5: `0/63`;
- top10: `0/63`;
- top50: `0/63`.

Proposal target log-probability:
- P50: `-37.3015`;
- mean: `-35.7567`.

Target top1/top2 margin:
- P50: `8.8752`;
- mean: `9.0658`.

Accepted-prefix distribution across the nine frozen states:
`[0,0,0,0,0,0,0,0,0]`

## Interpretation

This is not a narrow greedy-boundary mismatch.

The validated masked drafter proposals are structurally far from the current target distribution on the frozen corpus:
- zero top1 agreement;
- zero top50 inclusion;
- best observed proposed-token rank still 987;
- median rank 14,195;
- large target decision margins.

The corrected MLX drafter already matches an independent publisher-semantics reference on all 63 proposal decisions, while the current target and validation path reproduce the frozen target reference exactly on all 63 decisions.

Therefore the supported compatibility verdict is:

`INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`

This checkpoint does **not** establish why the incompatibility exists. In particular it does not prove that 4-bit quantization is causal.

## Next checkpoint

`LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`

Before constructing an expensive unquantized target control, audit the intended publisher target versus the local target provenance and static identity:
- exact model family/source lineage;
- architecture/config fields relevant to DFlash;
- tokenizer/vocabulary and special-token identity;
- d2t/t2d target-ID semantics;
- quantization/conversion provenance and revision information where locally recoverable.

The goal is to determine whether the local target differs from the publisher-intended `Qwen/Qwen3-30B-A3B` in any material way other than quantization/conversion. If an identity mismatch exists, localize it before a BF16 control. If static identity is compatible and quantization remains the material unresolved transformation, then design a separate isolated hidden-state/target precision control.

No model changes, no threshold changes, no memory remediation and no full E2E rerun are authorized by this result.
