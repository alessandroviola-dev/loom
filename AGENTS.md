# LOOM — Pi Agent Protocol

Version: 3.7
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. WP prompts must contain only the active delta.

## Role split

Pi owns local execution only: inspect targeted local code/evidence, implement the minimum authorized WP change, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, research result documents, `HANDOFF.md`, `ROADMAP.md`, and checkpoint administration.

Pi must NOT run Git, edit AGENTS/HANDOFF/ROADMAP, push/open/merge PRs, or create project documentation unless explicitly authorized.

## Scientific rules

1. Read this file first, then only files/evidence relevant to the active WP.
2. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
3. Distinguish fact, inference, hypothesis and unverified limit.
4. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
5. STOP on scientific ambiguity, destructive actions, missing required artifacts, or explicit stop gates.
6. Do not optimize memory/performance while the active scientific blocker is unresolved unless required for feasibility.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Expensive-run retention

Before any materially expensive network/compute run, create a retention plan identifying cost, expensive intermediates, exact storage, hashes/provenance and resumability/cache behavior.

External LOOM root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Persistent research artifacts:
`<external-archive>/artifacts/`

Operational Q4 target remains on internal SSD.

## Mission / stable target

Mission: **Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB with exactness, bounded memory and reproducible evidence.

Local target:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable anatomy:
- 48 MoE layers; 128 experts/layer; top-k 8;
- stored payload 16,220,499,968 B;
- resident non-routed backbone 819,015,680 B;
- routed bank 15,401,484,288 B;
- one local Q4 expert 2,506,752 B;
- BF16 KV 98,304 B/token.

Stable runtime invariants:
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- expert-major contiguous disk access preferred;
- 4-GiB raw global LRU rejected due swap/slowdown.

## DFlash stable chain

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Target: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]` 1-based post-block under the current local contract.

Still valid:
- target-tap interface implementation;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward path;
- frozen target continuation 45/45 historical overlap and 63/63 token reference;
- frozen target SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 branch

Pinned currently available upstream BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control showed material routing/tap/logit drift while Q4 and BF16 target top1 both remained `12050`; result `NOT_CAUSAL`.

Persistent BF16 cache retains ~33 GiB and exact P1_t01 BF16 taps/logits. Later full replay used 0 network bytes.

Q4->BF16 taps materially move the 32k drafter-logit distribution (rel-L2 `0.215100`, cosine `0.977013`) but did not establish recovery. This was only a narrow P1_t01 intervention and does not prove the broader frozen tap population is distribution-compatible with the drafter's training verifier.

## Mapping semantics — RESOLVED

Publisher `d2t` is an offset:
`target_id = draft_row + d2t[draft_row]`.

`t2d` is BOOL support over 32,000 selected verifier tokens. The former local direct-`d2t[row]` decode was repaired in 8 paths.

Correct support:
- 32,000 valid unique target IDs;
- exact equality with TRUE `t2d` positions;
- frozen support `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` remains unsupported;
- corrected top1 target matches remain `0/63`.

Historical first E2E `0/96` remains contaminated until corrected replay and is not a valid current acceptance measurement.

## Corrected drafter target ranks

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

For 50 representable targets:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

The drafter carries non-trivial target-directional signal despite zero exact top1 compatibility.

## Temporal alignment — CLOSED

Combined full preregistered range `-7..+7` classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

Facts:
- 441 valid prompt-local comparisons;
- offset 0 strongest aggregate alignment: 50 representable; top1/top5/top10/top50/top100 `0/8/11/19/26`; median rank `93.5`;
- only 5 nonzero neighbor top1 matches total: +2=2, +3=2, +4=1;
- none in P3;
- no nonzero offset dominates offset 0.

Do NOT alter positions, anchors, masks, block alignment, mapping or tap ordering based on temporal-shift hypotheses.

## Full-logit MLX/reference parity — COMPLETE

`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`.

Report:
`research/architecture/loom-dflash-full-logit-reference-parity-001-result.md`

Evidence:
`results-local/research/dflash-full-logit-reference-parity-001/20260825T102523Z/`

Subset: deterministic best/worst corrected target-rank state from each P1/P2/P3 (`6` total).

Input parity:
- input/tap/position/mask hashes identical `6/6`.

Decision-level output parity:
- argmax draft row `6/6` exact;
- ordered top5 `6/6` exact;
- ordered top10 `6/6` exact;
- top50 row sets `6/6` identical with only minor tolerated ordering swaps;
- corrected `row + d2t[row]` decode `6/6` exact.

Full-vector numerical range across states:
- max abs `0.003529..0.009598`;
- mean abs `0.000666..0.002038`;
- RMSE `0.000834..0.002529`;
- relative-L2 `0.000382..0.001375`;
- cosine `0.999999164..0.999999932`.

Established gates max_abs <= `0.025`, mean_abs <= `0.004`: PASS all 6.

Full float32 vectors are not bitwise identical; earliest non-bitwise differences begin at fusion. They are not material and do not explain the frozen mismatch.

Scientific consequence: the MLX drafter port is exonerated as the remaining practical cause on the stratified tested states. Residual mismatch is now upstream of drafter implementation: verifier/tap provenance, historical target/runtime interface, or genuine candidate/training-distribution behavior.

## External publisher facts already established

Published model card for this exact drafter:
- verifier/base model named `Qwen/Qwen3-30B-A3B`;
- data preparation and vLLM launch use that unqualified model name;
- target-layer IDs documented as `1 12 23 34 45`;
- training command likewise uses `--verifier-name-or-path Qwen/Qwen3-30B-A3B` and `--target-layer-ids 1 12 23 34 45`;
- documented commands do NOT pin an exact verifier revision.

Qwen target repository history shows the currently pinned `ad44e77...` commit is a later repository commit; exact training-time verifier revision remains unproven. Do not assume revision equivalence merely from model name.

## Next checkpoint

`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001`

Goal: statically determine whether the frozen target hidden-state interface is historically and semantically compatible with the verifier/tap pipeline used to train/validate the published DFlash candidate.

Required direction:
1. recover the strongest possible DFlash training provenance from already-local checkpoint/config/code/metadata: speculators version, vLLM integration/PR lineage if retained, model/checkpoint timestamps, verifier name, target-layer IDs, mask/position conventions;
2. recover target-repository revision history/provenance already available locally and compare model-weight/config/tokenizer/chat-template identities across plausible training-time revisions; distinguish weight changes from metadata-only changes;
3. inspect authoritative publisher target-layer extraction semantics for `1,12,23,34,45`: exact indexing convention, pre/post-block location, normalization/residual handling, dtype/cast, sequence position and serialization/order;
4. compare that contract against the local frozen tap-generation path without running the target;
5. identify any unpinned runtime/version behavior capable of changing hidden states/tap semantics;
6. do not infer a mismatch from an unpinned revision unless a material file/interface difference is demonstrated.

Classification:
- `VERIFIER_PROVENANCE_TAP_INTERFACE_MATCH`
- `TARGET_REVISION_OR_TAP_INTERFACE_MISMATCH`
- `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`
- `VERIFIER_PROVENANCE_UNRESOLVED`

If a material mismatch is found: STOP before repair or target execution.
If no material static mismatch is found: next decision should isolate target-state distribution/precision on a small representable subset before any E2E.

Restrictions:
- static audit first;
- no target-model forward;
- no BF16 forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance work.

## WP contract

```text
LOOM WP <id>
Goal: ...
Change: minimum active delta
Gates: correctness + stops
Evidence: results-local/.../<UTC>/
Return: decisive metrics only
STOP
```

Original model files are immutable. Raw evidence stays under `results-local/`; expensive retained artifacts may additionally live under the declared external storage root.
