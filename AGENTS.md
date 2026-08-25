# LOOM — Pi Agent Protocol

Version: 3.8
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. WP prompts carry only the active delta.

## Role split

Pi owns targeted local execution: inspect relevant local code/evidence, implement the minimum authorized WP change, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

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

## Storage / expensive-run rule

Before materially expensive network/compute work, define retention, provenance, resumability and cache behavior.

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

Stable target facts:
- 48 MoE layers; 128 experts/layer; top-k 8;
- stored payload 16,220,499,968 B;
- resident non-routed backbone 819,015,680 B;
- routed bank 15,401,484,288 B;
- one local Q4 expert 2,506,752 B;
- BF16 KV 98,304 B/token;
- external serial-expert math/full final logits exact;
- one routed expert logically live at a time;
- expert-major contiguous disk access preferred;
- 4-GiB raw global LRU rejected due swap/slowdown.

## DFlash stable chain

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier/target: `Qwen/Qwen3-30B-A3B`
Target taps: `[1,12,23,34,45]`.

Validated and still usable:
- exact target-tap implementation;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward;
- frozen target continuation 63/63, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## Mapping semantics — RESOLVED

Publisher `d2t` is an offset:
`target_id = draft_row + d2t[draft_row]`.

Correct support invariants:
- 32,000 draft rows;
- 32,000 valid unique target IDs;
- exact equality with TRUE `t2d` support;
- frozen targets: `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` unsupported;
- corrected exact top1 compatibility remains `0/63`.

The old direct-`d2t[row]` decode was a local mechanical bug and has been repaired in 8 paths. Historical E2E `0/96` remains contaminated and is not current acceptance evidence.

## Corrected target-rank signal

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

For 50 representable states:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- top1 `0/50`.

The drafter is mismatched at top1 but carries non-trivial target-directional signal.

## Temporal alignment — CLOSED

Full preregistered offset range `-7..+7` classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

- 441 valid prompt-local comparisons;
- offset 0 remains strongest aggregate alignment;
- only 5 nonzero neighbor top1 matches total (+2=2, +3=2, +4=1), none in P3;
- no nonzero offset dominates offset 0.

Do NOT alter positions, anchors, masks, block semantics, mapping or tap order based on temporal-shift hypotheses.

## MLX/reference full-logit parity — COMPLETE

`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`.

Report:
`research/architecture/loom-dflash-full-logit-reference-parity-001-result.md`

Evidence:
`results-local/research/dflash-full-logit-reference-parity-001/20260825T102523Z/`

Six stratified states (best/worst corrected target rank from each P1/P2/P3):
- identical input/tap/position/mask hashes `6/6`;
- argmax rows exact `6/6`;
- ordered top5/top10 exact `6/6`;
- top50 row sets identical `6/6`;
- corrected decode exact `6/6`;
- rel-L2 `0.000382..0.001375`;
- cosine `0.999999164..0.999999932`;
- established max/mean absolute-error gates pass all 6.

Non-bitwise differences start at fusion but are numerically immaterial. The MLX drafter port is not the practical cause of the frozen mismatch on tested states.

## Verifier provenance / tap interface — COMPLETE

`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001` = `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`.

Report:
`research/architecture/loom-dflash-verifier-provenance-tap-interface-audit-001-result.md`

Evidence:
`results-local/research/dflash-verifier-provenance-tap-interface-audit-001/20260825T103951Z/`

Static contract: `16/16` assertions PASS.

Recovered compatible semantics:
- target IDs `[1,12,23,34,45]` are ordered 1-based post-block residual outputs;
- taps are pre-final-norm;
- local frozen taps are float32 with no tap cast/copy/fusion/reordering step;
- no material target revision/config/tokenizer/tap-interface mismatch was demonstrated.

Still unpinned:
- exact training-time Qwen verifier revision;
- exact vLLM PR/revision;
- exact Speculators checkout;
- publisher tap-transport dtype.

Unpinned provenance is NOT itself evidence of mismatch.

## BF16 target context

Currently available upstream BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control showed material target routing/tap/logit drift while target top1 stayed `12050`; result `NOT_CAUSAL`. Persistent BF16 cache retains ~33 GiB and exact P1_t01 BF16 taps/logits.

A later drafter probe showed Q4->BF16 taps materially move the 32k drafter distribution (rel-L2 `0.215100`, cosine `0.977013`) but P1_t01 is unsupported, so this does not answer whether BF16 target states recover compatibility on representable targets.

## Next checkpoint

`LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001`

Goal: isolate the remaining cheap interface variable before new target computation: does BF16 transport quantization of the already-frozen taps materially improve DFlash compatibility?

One-factor intervention:
- baseline = exact retained float32 frozen taps;
- intervention = the same taps elementwise round-tripped `float32 -> bfloat16 -> float32` immediately before drafter input;
- keep input IDs, positions, masks, tap ordering, target states, drafter weights/math and corrected mapping unchanged.

Required direction:
1. use retained frozen taps only; no target execution;
2. run unchanged drafter for all 63 states under the single BF16-transport intervention;
3. verify baseline replay against retained logits/argmax;
4. for all states report proposal changes and 32k-logit movement;
5. for the 50 representable targets compare correct-row rank and top5/top10/top50/top100 membership baseline vs intervention;
6. report exact target matches and per-prompt consistency;
7. do not call isolated rank movement a recovery signal without broad/decision-level improvement.

Classifications:
- `TAP_BF16_TRANSPORT_RECOVERY_SIGNAL`
- `NO_MATERIAL_TAP_DTYPE_EFFECT`
- `TAP_DTYPE_SENSITIVITY_AMBIGUOUS`

If no material recovery: next checkpoint is a bounded representable-state Q4-target vs BF16-target hidden-state precision/distribution control, with cache/network preflight before expensive execution.

Restrictions:
- no target-model forward;
- no BF16 target forward;
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