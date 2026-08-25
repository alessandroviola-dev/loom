# LOOM — Pi Agent Protocol

Version: 3.9
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

Before materially expensive network/compute work, define retention, provenance, resumability, cache behavior and hard cost/stop gates.

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

Correct support:
- 32,000 valid unique target IDs;
- exact equality with TRUE `t2d` support;
- frozen targets `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` unsupported;
- corrected exact top1 remains `0/63`.

The old direct-`d2t[row]` decode was a local mechanical bug and has been repaired. Historical E2E `0/96` remains contaminated and is not current acceptance evidence.

## Corrected directional signal

For 50 representable states:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`, top10 `11/50`, top50 `19/50`, top100 `26/50`;
- top1 `0/50`.

The drafter is mismatched at top1 but carries non-trivial target signal.

## Temporal alignment — CLOSED

Full preregistered `-7..+7` classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

Offset 0 remains strongest; no nonzero offset consistently dominates. Do NOT alter positions, anchors, masks, block semantics, mapping or tap order based on shift hypotheses.

## MLX/reference full-logit parity — COMPLETE

`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`.

Report:
`research/architecture/loom-dflash-full-logit-reference-parity-001-result.md`

Six stratified states show:
- identical input/tap/position/mask hashes `6/6`;
- exact argmax and ordered top5/top10 `6/6`;
- identical top50 sets `6/6`;
- corrected decode exact `6/6`;
- rel-L2 <= `0.001375`, cosine >= `0.999999164`.

The MLX drafter port is not the practical cause of the frozen mismatch on tested states.

## Verifier provenance / tap interface — COMPLETE

`LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001` = `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`.

Report:
`research/architecture/loom-dflash-verifier-provenance-tap-interface-audit-001-result.md`

Static contract `16/16` PASS.

Compatible semantics:
- `[1,12,23,34,45]` = ordered 1-based post-block residual outputs;
- pre-final-norm;
- local frozen taps float32 with no cast/copy/fusion/reordering;
- no material target revision/config/tokenizer/tap-interface mismatch demonstrated.

Still historically unpinned: exact training-time Qwen revision, vLLM revision/PR, Speculators checkout, publisher tap-transport dtype. Unpinned provenance is not itself evidence of mismatch.

## Tap transport BF16 sensitivity — COMPLETE

`LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001` = `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Report:
`research/architecture/loom-dflash-tap-transport-bf16-sensitivity-001-result.md`

Evidence:
`results-local/research/dflash-tap-transport-bf16-sensitivity-001/20260825T105437Z/`

One-factor intervention: retained float32 taps vs exact `float32 -> bfloat16 -> float32` round trip immediately before drafter input.

Results:
- baseline replay PASS: `9/9` retained full-logit numeric parity; argmax/provenance/hash gates PASS;
- proposal changes `0/63`;
- logit movement: max abs `0.011943`, mean abs `0.001128`, RMSE `0.001457`, rel-L2 `0.000671`, cosine `0.999999776`;
- representable-target mean rank `438.96 -> 438.72`;
- rank improved/unchanged/worsened `11/32/7`;
- no top-k boundary crossings;
- top5/top10/top50/top100 unchanged `8/11/19/26`;
- exact matches remain `0/50`;
- P1/P2/P3 each `0/21` proposal changes with unchanged top-k counts.

Conclusion: tap transport dtype is non-causal for the frozen mismatch. Do not use tap dtype as a rescue mechanism.

## BF16 target context

Currently available upstream BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control showed material routing/tap/logit drift while target top1 stayed `12050`; result `NOT_CAUSAL`. P1_t01 is outside DFlash support, so it cannot test exact proposal recovery.

Persistent BF16 cache retains ~33 GiB and exact P1_t01 BF16 taps/logits. A later P1_t01 drafter probe showed Q4->BF16 taps materially move drafter logits (rel-L2 `0.215100`, cosine `0.977013`). This does not answer representable-target recovery.

## Next checkpoint

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001`

Goal: before any new expensive target computation/download, define the smallest informative representable-state Q4-target vs BF16-target causal pilot and quantify cache/network exposure.

Static/preflight only.

Required direction:
1. from the existing 50 representable states, deterministically select one near-target state per P1/P2/P3: lowest corrected baseline target rank within each prompt, tie-break by state ID;
2. identify the exact minimal verifier prefix/state reproduction needed for each selected state and whether work can be shared within each prompt trajectory;
3. audit the persistent BF16 cache manifest/integrity: dense assets, routed experts, hashes/size, resumability, and current disk availability;
4. using retained Q4 routing traces, report selected-state expert cache hits/misses as an **estimate only**; explicitly note BF16 routing may diverge and therefore exact future misses are unknowable without execution;
5. inspect existing on-demand BF16 fetch/cache code and determine whether a later pilot can enforce a hard network-byte/request cap and stop cleanly before exceeding it;
6. propose a concrete later pilot contract: selected states, retained artifacts, maximum network/compute exposure, abort gates, and decisive comparison metrics (BF16-vs-Q4 taps, drafter 32k movement, correct-target rank/top-k/top1);
7. do not download or execute the target in this preflight.

Classifications:
- `BF16_TARGET_PILOT_READY`
- `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`
- `BF16_TARGET_PILOT_NOT_FEASIBLE`
- `BF16_TARGET_PREFLIGHT_AMBIGUOUS`

Restrictions:
- no target forward;
- no BF16 target forward;
- no downloads;
- no E2E;
- no retraining/remapping;
- no performance optimization.

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