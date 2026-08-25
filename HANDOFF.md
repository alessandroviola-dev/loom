# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — DFlash offset-decode repair COMPLETE; true support is 32,000 unique target IDs, frozen support is 50/63 representable and 13/63 unsupported, but corrected top1 compatibility remains 0/63; next quantify correct-target rank inside drafter distribution
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001_MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`
Next core checkpoint: `LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi execution rules live in `/AGENTS.md` v3.3. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

## Stable DFlash work

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Target taps: `[1,12,23,34,45]`.

Still-valid:
- target tap interface;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen 63-state target continuation, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 branch

Pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control measured material target hidden/router/logit drift while target top1 stayed `12050`.

Persistent external BF16 cache:
`<external-archive>/bf16-cache/`
~33 GiB; later complete P1_t01 replay used 3,470 HDD hits / 0 network bytes.

BF16 tap probe established a still-valid distribution-level fact: Q4->BF16 taps move the 32k drafter logits materially (rel-L2 `0.215100`, cosine `0.977013`). Old decoded proposal IDs/ranks from direct `d2t` interpretation are superseded.

## Mapping semantics correction — RESOLVED

Authoritative upstream semantics:
- `d2t` is an offset, not an absolute target-token ID;
- true token for draft row `j`: `j + d2t[j]`;
- `t2d` is BOOL mask over the 32,000 selected target IDs;
- vLLM reconstructs `arange(32000) + draft_id_to_target_id` before scattering logits into target vocab.

Local MLX had used direct `d2t[row]`, classified `CONVERSION_OR_DECODE_SEMANTICS_BUG`.

Authoritative references:
- `vllm-project/speculators` commit `2aec948e43b0313e61aa639c7c8e150a8f1a2929`;
- `vllm-project/vllm` commit `d9fbe526c0787eb5e6dd1e3e4d9b88848d21bc6b`.

## Corrected decode repair — COMPLETE

Checkpoint:
`LOOM_DFLASH_D2T_OFFSET_DECODE_REPAIR_001`

Classification:
`MECHANICAL_DECODE_REPAIR_PASS_COMPATIBILITY_STILL_ZERO`

Report:
`research/architecture/loom-dflash-d2t-offset-decode-repair-001-result.md`

Evidence:
`results-local/research/dflash-d2t-offset-decode-repair-001/20260825T093731Z/`

Mechanical change:
- 8 decode/analysis scripts repaired;
- all now use `draft_row + d2t[draft_row]`;
- drafter weights/logits/taps/mask/anchor unchanged.

Mapping invariants PASS:
- 32,000 rows;
- 32,000 reconstructed target IDs;
- all valid;
- all unique;
- exact equality with TRUE positions of `t2d`;
- true support cardinality `32,000`.

Frozen 63 corrected support:
- representable `50/63` (`79.37%`);
- unsupported `13/63` (`20.63%`);
- P1_t01 target `12050` still unsupported.

Corrected proposals:
- retained raw argmax unchanged `63/63`;
- old->corrected decoded token differs `63/63`;
- corrected target matches `0/63`;
- P1_t01 corrected proposal `8747`, target `12050`.

Superseded conclusions:
- support `17,018` -> false, true support `32,000`;
- `30/63 representable / 33/63 unsupported` -> false, corrected `50/63 / 13/63`;
- old numeric proposal IDs -> false.

Result that survives:
- frozen exact top1 compatibility remains `0/63` after correct decoding.

Unavailable in this repair:
- target-distribution top5/top10/top50;
- proposal rank under target logits;
because full frozen target logits were not retained. No target forward was run.

Historical first E2E `0/96` remains contaminated until mechanically replayed with correct decode; do not treat it as reconfirmed yet.

## Scientific interpretation

The decode bug was real and important but is not the principal explanation for DFlash failure.

13/63 states remain impossible because the trained draft vocabulary contains only 32,000 of 151,936 target tokens. More decisively, **all 50 representable frozen target tokens are still wrong at drafter top1**.

Therefore another compatibility mechanism remains in the learned drafter/interface/distribution.

## Exact next step

Checkpoint:
`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001`

Goal:
Measure where each exact frozen target token ranks inside the unchanged 32k DFlash drafter distribution for the 50 representable states.

Priority:
1. map each representable target token to its unique corrected draft row;
2. reuse retained full 32k drafter logits if available;
3. otherwise replay only the unchanged drafter on frozen taps;
4. report target-row rank/probability/logit/top-k and aggregate rank distribution;
5. keep 13 unsupported states separate;
6. no target-model/BF16/E2E work.

Interpretation:
- target tokens frequently near top -> directional alignment exists despite 0/63 top1;
- target tokens rank poorly -> remaining incompatibility is much deeper and DFlash salvage becomes less attractive.
