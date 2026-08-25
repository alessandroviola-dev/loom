# LOOM — Pi Agent Protocol

Version: 3.6
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

## Expensive-run retention rule

Before any materially expensive network/compute run, create a retention plan identifying cost, expensive intermediates, exact storage, hashes/provenance and resumability/cache behavior. A run is not complete if required expensive artifacts were only transient.

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
Taps: `[1,12,23,34,45]` 1-based post-block.

Still valid:
- target tap interface;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block mask repaired;
- deterministic/finite 32k drafter forward path;
- frozen target continuation 45/45 historical overlap and 63/63 token reference;
- frozen target SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

## BF16 precision branch

Pinned upstream BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

P1_t01 Q4->BF16 control showed material routing/tap/logit drift while Q4 and BF16 target top1 both remained `12050`; result `NOT_CAUSAL`.

Persistent BF16 cache retains ~33 GiB and exact P1_t01 BF16 taps/logits. Later full replay used 0 network bytes.

Q4->BF16 taps materially move the 32k drafter-logit distribution (rel-L2 `0.215100`, cosine `0.977013`) but did not establish recovery.

## DFlash mapping semantics — RESOLVED

Publisher `d2t` is an offset:
`target_id = draft_row + d2t[draft_row]`.

`t2d` is BOOL support over the 32,000 selected verifier tokens. Current vLLM reconstructs the same `arange(32000) + draft_id_to_target_id` mapping.

The former local direct-`d2t[row]` decode was a mechanical bug and has been repaired in 8 decode/analysis paths.

Correct support invariants:
- 32,000 rows;
- 32,000 valid unique target IDs;
- exact equality with TRUE `t2d` positions;
- frozen support `50/63` representable, `13/63` unsupported;
- P1_t01 target `12050` remains unsupported.

Corrected top1 matches remain `0/63`. Historical first E2E `0/96` remains contaminated until corrected replay; no E2E is authorized yet.

## Corrected drafter target-rank audit — COMPLETE

`LOOM_DFLASH_CORRECTED_DRAFTER_TARGET_RANK_AUDIT_001` = `PASS_DIRECTIONAL_SIGNAL_PRESENT`.

Evidence:
`results-local/research/dflash-corrected-drafter-target-rank-audit-001/20260825T094730Z/`

For 50 representable targets:
- rank min / median / mean / max: `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`;
- top10 `11/50`;
- top50 `19/50`;
- top100 `26/50`;
- rank1 `0/50`.

Conclusion: zero top1 is real, but the drafter carries substantial directional signal.

## Temporal alignment — CLOSED

`LOOM_DFLASH_CORRECTED_TEMPORAL_ALIGNMENT_AUDIT_001` plus `LOOM_DFLASH_TEMPORAL_ALIGNMENT_RANGE_COMPLETION_001` close the preregistered full relative-offset range `-7..+7`.

Final classification:
`NO_SYSTEMATIC_TEMPORAL_SHIFT`.

Reports:
- `research/architecture/loom-dflash-corrected-temporal-alignment-audit-001-result.md`
- `research/architecture/loom-dflash-temporal-alignment-range-completion-001-result.md`

Range-completion evidence:
`results-local/research/dflash-temporal-alignment-range-completion-001/20260825T101610Z/`

Full-range facts:
- total valid prompt-local comparisons: `441`;
- offset 0 remains strongest aggregate alignment: 50 representable; top1/top5/top10/top50/top100 `0/8/11/19/26`; median rank `93.5`;
- all nonzero corrected-proposal neighbor matches total only `5`: +2=2, +3=2, +4=1;
- those matches occur only in P1/P2; none in P3;
- no nonzero offset dominates offset 0 on exact-match, top-k, median-rank, and cross-trajectory consistency criteria.

Do NOT alter positions, anchors, masks, block alignment, mapping, or tap ordering based on temporal-shift hypotheses.

## Next checkpoint

`LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001`

Goal: distinguish residual MLX-port numerical divergence from genuine drafter/target-distribution incompatibility by comparing the entire 32k drafter-logit vector against an authoritative publisher/reference implementation on a small stratified set of already-frozen states.

Required direction:
1. choose a small preregistered stratified subset from existing frozen states, including near-target and poor-rank examples across P1/P2/P3;
2. use exactly the same frozen target taps/input IDs/positions/mask semantics and publisher weights;
3. compare MLX vs authoritative reference BEFORE any target-token decode: full 32k logits, argmax draft row, top-k rows, max/mean absolute error, RMSE, relative-L2, cosine, and tolerance/bitwise status where meaningful;
4. separately verify corrected `row + d2t[row]` decode parity after logit comparison;
5. if full-logit parity passes, treat the remaining frozen mismatch as candidate/interface/distribution behavior rather than MLX port error;
6. if parity fails materially, STOP and localize the first numerical divergence before any E2E.

Restrictions:
- no target-model forward;
- no BF16 target forward;
- no downloads unless a precise missing authoritative local reference dependency is identified and separately authorized;
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
