# LOOM DFlash Masked Reference Parity 001 — Result

Date: 2026-08-24
Classification: `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`

## Purpose

Validate the repaired MLX DFlash drafter against an independently implemented publisher-semantics reference using the correct anchor/block attention mask, before making any target-compatibility claim.

## Evidence

Local raw evidence:
`results-local/research/dflash-masked-reference-parity-001/20260824T142830Z/`

Local files:
- `scripts/loom_dflash_masked_reference_parity_001.py`
- `scripts/loom_dflash_greedy_e2e_001.py`

## Mask contract

Publisher semantics independently recovered and implemented:
- base positions are strictly before the anchor;
- same-block synthetic slots are causal;
- `sample_from_anchor=False`;
- proposal slots 1–7 map through `d2t`;
- `use_cache=False` / no draft-KV carry.

An explicit independent 8×13 anchor/block visibility matrix assertion was included.

Mask assertion: **PASS**.

## Corpus

Nine frozen real target-tap states:
- P1 / P2 / P3;
- positions 1 / 16 / 32.

Seven autoregressive proposal decisions were compared per state.

Total decisions: `63`.

## MLX vs independent reference

Mapped proposal-token parity:
- `63/63`;
- first mismatch: none.

Deterministic rerun: **PASS**.

NaN/Inf: none.

Final-logit error distribution:
- max-abs distribution maximum: `0.0166407`;
- max-abs distribution mean: `0.0109135`;
- mean-abs distribution maximum: `0.00175031`;
- mean-abs distribution mean: `0.00120281`.

Top1/top2 proposal-margin statistics:
- MLX mean margin: `0.55770`;
- independent-reference mean margin: `0.55726`;
- maximum absolute margin error: `0.00708771`.

The observed numerical differences did not change any mapped proposal decision.

## Frozen target acceptance observation

Accepted-prefix distribution against the frozen target continuation:

`[0,0,0,0,0,0,0,0,0]`

This was identical for MLX and the independent reference.

This is an observation only. No full E2E target-compatibility conclusion is drawn from this checkpoint alone.

## Interpretation

The repaired MLX drafter now matches an independently implemented masked publisher-semantics reference on all required real target-tap states and all seven autoregressive proposal positions.

Therefore the previously discovered missing anchor/block mask is no longer an unresolved implementation explanation for the persistent zero frozen-prefix acceptance.

The remaining compatibility question has moved to the drafter/target interface itself. The local `Qwen3-30B-A3B-MLX-4bit` target is a hypothesis to audit, not yet a proven cause, and 4-bit quantization must not be blamed without a control that isolates it.

## Restrictions preserved

No:
- full E2E rerun;
- target forward used as a rescue/tuning loop;
- drafter-weight or target-weight changes;
- acceptance-threshold changes;
- memory/performance remediation.

## Next checkpoint

`LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001`

First gate must confirm that the current target replay reproduces the frozen target continuation before using that path to attribute drafter/target disagreement. Only after target replay integrity passes should proposal ranks/log-probabilities/top-k proximity and exact accepted-prefix behavior be characterized.

## Gate

`PASS`

Masked publisher-reference parity is established. Target/drafter compatibility remains conditional and is the next scientific question.
