# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — DFlash output-mapping semantics resolved: local MLX decode treated publisher `d2t` offsets as absolute token IDs; prior support/compatibility conclusions depending on that decode are contaminated; next repair decode mechanically and recompute frozen 63-state compatibility
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_OUTPUT_MAPPING_SEMANTICS_AUDIT_001_CONVERSION_OR_DECODE_SEMANTICS_BUG`
Next core checkpoint: `LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi execution rules live in `/AGENTS.md` v3.2. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

## Stable DFlash facts

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Target taps: `[1,12,23,34,45]`.

Still-valid mechanical/numerical work:
- target tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- deterministic/finite drafter forward path;
- frozen target continuation 63/63, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 precision branch

Pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control measured material target hidden/router/logit drift while target top1 stayed `12050`. Exact BF16 taps/logits are retained externally.

Persistent cache:
`<external-archive>/bf16-cache/`
~33 GiB, including 3,470 routed expert entries; a later complete P1_t01 replay used 0 network bytes.

BF16 tap probe showed Q4->BF16 taps materially move the 32k drafter-logit distribution (rel-L2 `0.215100`, cosine `0.977013`). That distribution-level observation remains valid. Proposal-token/rank interpretations using the old decode must be recomputed.

## Output mapping semantics — RESOLVED

Pi local evidence:
`results-local/research/dflash-output-mapping-semantics-audit-001/20260825T091537Z/`

Pi found:
- raw publisher `d2t` length 32,000;
- only 17,018 unique numeric `d2t` values;
- `t2d` is BOOL length 151,936 with exactly 32,000 true IDs;
- MLX proposal decode used `d2t[argmax(draft_logits)]` directly;
- no tensor-conversion difference from publisher checkpoint.

Pi initially classified `MAPPING_INTEGRITY_ANOMALY` because authoritative runtime-generation semantics were absent locally.

ChatGPT scientific review recovered authoritative upstream semantics:
- exact RedHatAI model card trains with `--draft-vocab-size 32000`;
- current `vllm-project/speculators` mapping generator stores `d2t` as an OFFSET:
  `d2t = selected_target_ids - arange(32000)`;
- true target token for row `j` is `j + d2t[j]`;
- `t2d` is the BOOL mask of those 32,000 selected target IDs;
- current vLLM Qwen3 DFlash inference computes `targets = arange(32000) + draft_id_to_target_id` before scattering logits into the verifier vocabulary.

Therefore checkpoint classification is:
`CONVERSION_OR_DECODE_SEMANTICS_BUG`.

Report:
`research/architecture/loom-dflash-output-mapping-semantics-audit-001-result.md`

Authoritative code references:
- `vllm-project/speculators` commit `2aec948e43b0313e61aa639c7c8e150a8f1a2929`, `src/speculators/train/vocab_mapping.py`;
- `vllm-project/vllm` commit `d9fbe526c0787eb5e6dd1e3e4d9b88848d21bc6b`, `vllm/model_executor/models/qwen3_dflash.py`.

## Contaminated conclusions

Do not currently rely on conclusions derived from direct `d2t[argmax]` as an absolute target token ID:
- 17,018 effective support;
- 30/63 representable vs 33/63 unsupported;
- P1_t01 `12050` unsupported;
- proposal target IDs/ranks based on that decode;
- `0/63` compatibility conclusion insofar as it uses those IDs;
- first E2E `0/96` acceptance is suspect if the same decode path was used.

The underlying 32k drafter logits and forward math are not invalidated by this finding.

## Exact next step

Checkpoint:
`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

Goal:
mechanically repair only row->target decode to `target_id = row + d2t[row]`, prove exact authoritative semantics, and recompute the 63 frozen-state support/proposal compatibility using retained evidence where possible.

Priority order:
1. identify every local code path that interprets `d2t` as absolute IDs;
2. repair only decode semantics;
3. prove 32,000 true target IDs equal the `t2d` support exactly;
4. recompute 63-state support/proposals/ranks from retained logits/artifacts if available;
5. if a drafter-only replay is required, keep target/BF16 untouched;
6. do NOT run E2E until corrected 63-state compatibility is reviewed.

No retraining, no BF16 forward, no target-model regeneration unless separately proven necessary.
