# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — DFlash MLX/reference full-32k logit parity PASS on a stratified 6-state subset; MLX drafter port is no longer the leading explanation for corrected 0/63 top1 mismatch; next audit verifier revision/provenance and exact target-tap interface semantics statically
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001_FULL_LOGIT_REFERENCE_PARITY_PASS`
Next core checkpoint: `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

## Mission

**Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB while preserving exactness, bounded memory and reproducible evidence.

Persistent context and Pi rules live in `/AGENTS.md` v3.7. Pi executes compact local WPs; ChatGPT owns Git/project-state administration.

## Stable DFlash state

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Local tap contract: `[1,12,23,34,45]`, 1-based post-block.

Still valid:
- target-tap implementation;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Mapping correction — resolved

Publisher `d2t` is offset semantics:
`target_id = draft_row + d2t[draft_row]`.

True support:
- 32,000 valid unique target IDs;
- exact `t2d` support equality;
- frozen corpus `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` unsupported;
- corrected top1 target matches `0/63`.

Historical first E2E `0/96` is still contaminated by the old decode and is not a valid current acceptance measurement.

## Corrected target-rank signal

For 50 representable states:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

The drafter has substantial directional signal despite zero top1 compatibility.

## Temporal alignment — closed

Full preregistered `-7..+7` result:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

- 441 valid prompt-local comparisons;
- offset 0 remains strongest aggregate alignment;
- only 5 nonzero proposal-neighbor matches total (+2=2, +3=2, +4=1), none in P3;
- no nonzero offset dominates offset 0.

Do not change positions, anchors, masks, block semantics, mapping, or tap order based on temporal-shift hypotheses.

## Full-logit reference parity — COMPLETE

Checkpoint:
`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

Classification:
`FULL_LOGIT_REFERENCE_PARITY_PASS`

Report:
`research/architecture/loom-dflash-full-logit-reference-parity-001-result.md`

Evidence:
`results-local/research/dflash-full-logit-reference-parity-001/20260825T102523Z/`

Subset: best + worst corrected target-rank state from each P1/P2/P3:
- P1 best `P1_t32:6`, rank 3;
- P1 worst `P1_t16:4`, rank 2890;
- P2 best `P2_t16:3`, rank 3;
- P2 worst `P2_t01:4`, rank 3510;
- P3 best `P3_t01:2`, rank 2;
- P3 worst `P3_t01:4`, rank 1645.

Parity:
- input/tap/position/mask hashes identical `6/6`;
- argmax draft rows exact `6/6`;
- top5/top10 exact ordered parity `6/6`;
- top50 identical row sets `6/6`, with only minor order swaps;
- corrected decode parity `6/6`.

Full-vector metrics across states:
- max abs `0.003529..0.009598`;
- mean abs `0.000666..0.002038`;
- RMSE `0.000834..0.002529`;
- rel-L2 `0.000382..0.001375`;
- cosine `0.999999164..0.999999932`.

Vectors are not bitwise identical; earliest difference is at fusion, but all established numerical gates pass and decision-level outputs are unchanged.

Scientific consequence: no material MLX-port divergence explains the frozen mismatch on the stratified tested states. Remaining mechanism is upstream of drafter implementation: verifier hidden-state provenance/revision/interface, or genuine candidate/training-distribution behavior.

## BF16 branch context

Pinned currently available BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 target control changed internal states materially but target top1 stayed `12050`; narrow BF16-tap intervention moved drafter logits but did not establish recovery. Persistent cache ~33 GiB remains reusable.

Important: this narrow P1_t01 result does not prove the full frozen tap population matches the training verifier distribution.

## External publisher provenance observation

The exact DFlash model card documents:
- verifier/base `Qwen/Qwen3-30B-A3B`;
- target layers `1 12 23 34 45` in the vLLM launch and training commands;
- no exact verifier revision pinned in those commands.

Therefore exact historical verifier/tap provenance remains open even though the model name matches.

## Exact next step

Checkpoint:
`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

Static only. Determine whether our frozen hidden-state interface matches the verifier/tap pipeline actually used for DFlash training/validation.

Required:
1. recover strongest local provenance for DFlash checkpoint, speculators/vLLM lineage, verifier identity and target-layer contract;
2. distinguish plausible target revisions that changed model weights/config from metadata/tokenizer-only changes;
3. establish exact publisher tap semantics for layers `[1,12,23,34,45]`: indexing, pre/post block, residual/norm handling, dtype/cast, sequence position, serialization/order;
4. compare against local frozen tap-generation code without running target;
5. identify any unpinned version/runtime behavior capable of materially changing hidden states;
6. do not call a mismatch merely because revision is unpinned — require a demonstrated material difference.

Classifications:
- `VERIFIER_PROVENANCE_TAP_INTERFACE_MATCH`
- `TARGET_REVISION_OR_TAP_INTERFACE_MISMATCH`
- `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`
- `VERIFIER_PROVENANCE_UNRESOLVED`

No target/BF16 forward, downloads, E2E, retraining/remapping, or performance work.
