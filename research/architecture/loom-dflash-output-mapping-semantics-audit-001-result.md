# LOOM DFlash Output Mapping Semantics Audit 001 — Result

Date: 2026-08-25
Checkpoint: `LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001`
Classification: `CONVERSION_OR_DECODE_SEMANTICS_BUG`
Gate: `COMPLETE`

## Local audit result

Pi established from the publisher tensors retained locally that:
- the 32,000 -> 17,018 collapse exists in the raw publisher `d2t` tensor itself;
- MLX was decoding proposals as `d2t[argmax(draft_logits)]`;
- raw `d2t` has 17,018 unique values, 14,982 repeated rows and 6,098 collided values;
- `t2d` is BOOL over the 151,936-wide verifier vocabulary with exactly 32,000 true IDs and a materially different apparent support set;
- no local tensor-conversion mismatch was found.

Local evidence:
`results-local/research/dflash-output-mapping-semantics-audit-001/20260825T091537Z/`

Pi stopped at `MAPPING_INTEGRITY_ANOMALY` because the exact mapping-generation/runtime semantics were not retained locally.

## Scientific review — authoritative semantics recovered

The ambiguity was resolved against public upstream implementation evidence.

The exact model card for `RedHatAI/Qwen3-30B-A3B-speculator.dflash` documents training with:
`--draft-vocab-size 32000`.

Current `vllm-project/speculators` vocabulary-generation code defines reduced-vocabulary `d2t` as an OFFSET, not an absolute target-token ID:

`draft_to_target = selected_token_ids - arange(draft_vocab_size)`

with the explicit invariant:

`target_token_id = draft_idx + draft_to_target[draft_idx]`.

The same generator builds `t2d` as a BOOL mask with the selected target-token IDs set true. Therefore, for a valid 32k reduced vocabulary:
- `t2d.sum() == 32000`;
- the true target support is the 32,000 selected IDs;
- repeated numeric values inside the offset tensor are legal and do NOT imply repeated target-token IDs.

Current vLLM DFlash loading/inference confirms the same semantics. The checkpoint tensor `d2t` is loaded as `draft_id_to_target_id`, and logits are expanded with:

`base = arange(draft_vocab_size)`
`targets = base + draft_id_to_target_id`
`logits_new[:, targets] = logits`.

Thus the effective target token associated with drafter row `j` is:

`j + d2t[j]`

not:

`d2t[j]`.

Upstream evidence reviewed:
- `vllm-project/speculators` commit `2aec948e43b0313e61aa639c7c8e150a8f1a2929`, `src/speculators/train/vocab_mapping.py`;
- same commit, `scripts/build_vocab_mapping.py`;
- `vllm-project/vllm` commit `d9fbe526c0787eb5e6dd1e3e4d9b88848d21bc6b`, `vllm/model_executor/models/qwen3_dflash.py`;
- published RedHatAI model card training command.

Caveat: these public code revisions are authoritative current implementation evidence, not proof of the exact historical training-runtime commit. However all three independent signals — model card, local `t2d` cardinality and upstream generation/decode code — agree on the offset semantics.

## Consequences

The previous interpretation `d2t = drafter-index -> absolute target-token ID` is wrong.

Therefore these earlier conclusions are invalidated pending corrected replay:
- `17,018` unique effective target support;
- `14,982` duplicate target-token rows;
- `6,098` collided effective target IDs;
- `30/63` representable vs `33/63` unsupported;
- P1_t01 token `12050` classified unsupported;
- decoded proposal token IDs and target ranks computed using direct `d2t[argmax]`;
- the `0/63` compatibility interpretation insofar as it depends on those decoded token IDs;
- the `0/96` E2E acceptance result is now suspect because the same wrong target-token decode may have been used.

The underlying 32k drafter logits, learned weights, tap interface, attention-mask repair and numerical forward parity are not automatically invalidated. The contamination is specifically the draft-row -> target-token decode semantics and all downstream metrics that depend on it.

The prior BF16 tap intervention also needs reinterpretation: its finding that Q4->BF16 taps materially move the 32k drafter-logit distribution remains valid, but the reported proposal target token/rank under the wrong decode must be recomputed.

## Next checkpoint

`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

Goal: mechanically implement and prove the authoritative mapping semantics `target_id = draft_row + d2t[draft_row]`, then recompute the frozen 63-state support/proposal compatibility from already-retained evidence where possible before any new expensive execution.

Restrictions:
- no retraining;
- no BF16 forward;
- no target-model rerun unless proven necessary;
- no E2E until corrected 63-state compatibility is known;
- preserve all drafter math/taps/mask/weights unchanged;
- repair only mapping decode semantics.
