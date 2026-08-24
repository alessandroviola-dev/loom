# LOOM DFlash Target Identity Audit 001 — Result

Date: 2026-08-24
Checkpoint: `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`
Classification: `IDENTITY_MATCH_EXCEPT_QUANTIZATION`
Gate: `PASS`

## Purpose

Determine whether the local `Qwen3-30B-A3B-MLX-4bit` target differs materially from the DFlash publisher-intended `Qwen/Qwen3-30B-A3B` in architecture, tokenizer or token mapping before attributing the observed DFlash incompatibility to precision/quantization effects.

## Result

Intended target:
`Qwen/Qwen3-30B-A3B`

Local target provenance:
`Qwen/Qwen3-30B-A3B-MLX-4bit`, revision `4e2776a4…`

Identity checks:
- DFlash-relevant architecture/config parity: PASS;
- first config mismatch: none;
- tokenizer parity: PASS;
- special-token parity: PASS;
- vocabulary parity: PASS;
- `d2t` / `t2d` audit: PASS;
- all mapped/support token IDs are valid;
- literal inverse is not applicable because `d2t` is an I64 duplicate scatter map and `t2d` is BOOL.

Quantization/conversion delta:
- MLX affine 4-bit;
- group size 128;
- 386 weight/scales/biases triplets.

Unresolved provenance:
- exact original unquantized revision unavailable locally;
- publisher tokenizer byte snapshot unavailable locally.

## Interpretation

No material non-quantization architecture, tokenizer, vocabulary, special-token or mapping mismatch was found.

This eliminates the main static/token-semantic identity alternatives for the extreme incompatibility measured in `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`.

The remaining material transformation is the MLX 4-bit conversion/quantization path. This makes target hidden-state / precision drift the leading hypothesis, but it is **not yet causal evidence** against quantization.

A separate independent unquantized target control is required before any causal conclusion.

## Next

Run a bounded preflight for an isolated unquantized target hidden-state/logit control on the same frozen prefixes/taps. The preflight must determine exact upstream weight provenance, required artifacts/storage and whether the control can reuse LOOM's external-expert execution without requiring full-model residency. Do not blindly download the full unquantized model or run full E2E.

## Evidence

`results-local/research/dflash-target-identity-audit-001/20260824T155624Z/`

Local runner:
`scripts/loom_dflash_target_identity_audit_001.py`

## Gate

`PASS — IDENTITY_MATCH_EXCEPT_QUANTIZATION`
