# LOOM DFlash Verifier Provenance / Tap Interface Audit 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`
Classification: `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`
Gate: `PASS`

## Result

Static contract audit passed `16/16` assertions.

Recovered tap semantics for published target-layer IDs `[1,12,23,34,45]` are compatible with the current local frozen interface:
- ordered 1-based layer IDs;
- post-block residual outputs;
- captured before final model normalization;
- current local taps retained as float32;
- no local tap cast, copy, fusion or reordering step before DFlash input.

No material target revision, config, tokenizer, position/mask, or tap-interface mismatch was demonstrated from already-local provenance.

## Remaining provenance uncertainty

The following historical details remain unpinned:
- exact Qwen verifier revision used during DFlash training;
- exact vLLM PR/revision;
- exact Speculators checkout;
- exact publisher tap-transport dtype.

These are unresolved provenance facts, not demonstrated mismatches. Under the project scientific contract they must not be treated as causal without an isolated material difference.

## Scientific interpretation

Combined with `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`, there is now no demonstrated material error in:
- local DFlash learned-weight mapping;
- drafter forward implementation;
- corrected 32k-to-target token mapping;
- target-layer indexing/order;
- local post-block tap stage;
- static verifier config/tokenizer/interface identity.

The cheapest remaining isolated interface variable is tap transport dtype. Because the local frozen taps are float32 while publisher training transport dtype is unpinned, test BF16 transport sensitivity on already-retained taps before authorizing new target-model BF16 computation.

If transport dtype does not materially recover representable-state compatibility, the next high-value causal test is a bounded representable-state Q4-target vs BF16-target hidden-state intervention.

Evidence:
`results-local/research/dflash-verifier-provenance-tap-interface-audit-001/20260825T103951Z/`

No target/BF16 forward, download, E2E, retraining, remapping, Git or project-document edit was performed by Pi.