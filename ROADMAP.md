# LOOM Roadmap

Last updated: 2026-08-25
Current checkpoint: `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001_FULL_LOGIT_REFERENCE_PARITY_PASS`
Strategic next: `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical persistent context: `/AGENTS.md` v3.7.

## Stable DFlash chain

Still valid:
- target tap interface `[1,12,23,34,45]` under current local semantics;
- exact B7 wavefront verifier;
- complete 680,813,824-param BF16 drafter port;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward;
- frozen 63-state target continuation;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Resolved output mapping

Publisher `d2t` is an offset. Correct decode:
`target_id = draft_row + d2t[draft_row]`.

True support:
- 32,000 valid unique target IDs;
- frozen support `50/63` representable, `13/63` unsupported;
- corrected exact top1 target matches remain `0/63`.

Historical first E2E `0/96` remains contaminated by the old decode and must not be treated as current acceptance evidence.

## Corrected directional signal

For 50 representable states:
- target rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

The candidate is not random/unrelated; residual mismatch remains substantial.

## Temporal alignment — CLOSED

Full preregistered `-7..+7` classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

Offset 0 remains strongest aggregate alignment. Only 5 nonzero proposal-neighbor matches exist across 441 valid comparisons, none in P3. Do not change positions/anchors/masks/block semantics/mapping/tap order based on off-by-N hypotheses.

## Completed — full 32k MLX/reference parity

Checkpoint:
`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

Classification:
`FULL_LOGIT_REFERENCE_PARITY_PASS`

Report:
`research/architecture/loom-dflash-full-logit-reference-parity-001-result.md`

Evidence:
`results-local/research/dflash-full-logit-reference-parity-001/20260825T102523Z/`

Stratified 6-state subset: best/worst corrected target-rank example from each P1/P2/P3.

Results:
- identical input/tap/position/mask hashes `6/6`;
- exact argmax rows `6/6`;
- exact ordered top5/top10 `6/6`;
- identical top50 row sets `6/6`;
- exact corrected decode `6/6`;
- rel-L2 range `0.000382..0.001375`;
- cosine range `0.999999164..0.999999932`;
- max abs range `0.003529..0.009598`;
- mean abs range `0.000666..0.002038`.

Non-bitwise differences begin at fusion but are numerically immaterial under established gates and do not change decisions.

Decision: the current MLX drafter implementation is not the leading explanation for the corrected frozen mismatch. Move upstream to verifier/tap provenance and training-interface compatibility.

## BF16 context

Current pinned upstream BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

A narrow P1_t01 Q4->BF16 intervention changed target/tap internals materially but did not recover the proposal. This does not establish distribution parity for the 50 representable frozen states.

Persistent ~33 GiB BF16 cache remains available if a later isolated representable-state test is justified.

## External publisher clue

The exact DFlash model card documents verifier `Qwen/Qwen3-30B-A3B` and target-layer IDs `1 12 23 34 45`, but its shown training/vLLM commands do not pin a verifier revision. Thus model-name identity alone does not close historical verifier/tap provenance.

## Next — verifier provenance / tap interface audit

Checkpoint:
`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

Static audit, no target execution.

Purpose:
Determine whether the frozen target hidden states supplied to an otherwise-correct DFlash drafter are semantically and historically equivalent to the verifier hidden-state stream used during publisher training/validation.

Required:
1. recover DFlash checkpoint/config/runtime provenance already present locally;
2. reconstruct plausible Qwen target revision lineage and distinguish weight/config changes from tokenizer/docs/metadata-only commits;
3. establish authoritative training-time tap semantics for `[1,12,23,34,45]`: indexing, exact stage, residual/norm, dtype, positions and ordering;
4. compare against the local frozen tap extraction contract;
5. identify any runtime/version-dependent semantic difference;
6. require a material demonstrated difference before classifying mismatch.

Decision:
- demonstrated target revision/tap mismatch -> stop and preregister a single repair/replay;
- static match -> next isolate target-state precision/distribution using the smallest representable subset, then decide whether corrected E2E is justified;
- unresolved provenance -> decide whether the missing historical artifact is worth retrieving before further DFlash investment.

Restrictions:
- no target/BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance optimization.

## Later order

1. `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`;
2. if mismatch found, repair/replay only that mechanism;
3. if static interface matches, isolate representable-state target precision/distribution;
4. corrected bounded E2E only after a useful compatibility mechanism or acceptance signal exists;
5. if candidate remains incompatible, explicitly stop DFlash salvage and return to LOOM's 30B-on-8GB serving/I/O path.

## Token-efficient workflow

Pi reads `/AGENTS.md`; WP prompts carry only the active delta. Pi executes local work; ChatGPT owns scientific/Git state.
