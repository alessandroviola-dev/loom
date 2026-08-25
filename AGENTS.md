# LOOM — Pi Agent Protocol

Version: 3.15
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. WP prompts carry only the active delta.

## Role split

Pi owns targeted local execution: inspect relevant local code/evidence, implement the minimum authorized WP change, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, research result documents, `HANDOFF.md`, `ROADMAP.md`, and checkpoint administration.

Pi must NOT run Git, edit AGENTS/HANDOFF/ROADMAP, push/open/merge PRs, or create project documentation unless explicitly authorized.

## Scientific rules

1. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
2. Distinguish fact, inference, hypothesis and unverified limit.
3. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
4. STOP on scientific ambiguity, destructive actions, missing required artifacts, or explicit stop gates.
5. No memory/performance optimization while the active scientific blocker is unresolved unless required for feasibility.
6. Before expensive network/compute work define retention, resumability and hard cost/stop gates. Network caps must be enforced before dispatch.
7. Do not relax a preregistered provenance/hash gate post-hoc merely because top1 or top-k agrees.
8. For continuation-state provenance, producer segmentation and KV-cache boundary are part of the frozen state contract.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

External LOOM root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Persistent artifacts:
`<external-archive>/artifacts/`

## Mission / stable target

Mission: **Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB with exactness, bounded memory and reproducible evidence.

Operational Q4 target:
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
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Still valid:
- exact target-tap implementation;
- exact B7 wavefront verifier;
- all 680,813,824 learned BF16 drafter params mapped;
- publisher attention-mask repair;
- deterministic/finite 32k drafter forward;
- frozen target continuation 63/63, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- correct publisher decode `target_id = draft_row + d2t[draft_row]`;
- frozen support `50/63` representable, `13/63` unsupported;
- corrected exact DFlash top1 `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` used old decode and is not current acceptance evidence.

Closed leading hypotheses:
- temporal/off-by-N: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter implementation: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- verifier/tap static interface: static contract `16/16` PASS, no demonstrated material mismatch;
- tap transport float32-vs-BF16: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Do not reopen these without new evidence.

## BF16 bounded infrastructure — COMPLETE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Remote source parity:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Validated source SHA-256:
- range control `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376`;
- BF16 tap probe `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f`;
- guard test `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae`.

Hard ceilings for any future BF16 pilot retry remain frozen:
- aggregate network `8 GiB`;
- aggregate requests `1,024`, retries included;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache.

## Representable BF16 pilot state set — FROZEN

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected states:
- P1 `P1_t32:6`, baseline DFlash rank 3, frozen Q4 verifier target 326, 79-token state prefix;
- P2 `P2_t16:3`, baseline DFlash rank 3, frozen Q4 verifier target 994, 74-token state prefix;
- P3 `P3_t01:2`, baseline DFlash rank 2, frozen Q4 verifier target 1620, 64-token state prefix.

Fixed eventual pilot order remains P3 -> P1 -> P2. No substitutions.

## First causal pilot attempt — INVALID BEFORE BF16

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` stopped before BF16/network:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-001-result.md`

P3 Q4 top1 remained `1620`, but final-logit raw-array SHA mismatched. No BF16 state executed; network remained `0 B / 0 requests / 0 retries`.

No BF16 recovery/non-recovery conclusion is valid from that attempt.

## Q4 baseline provenance reconciliation — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001` = `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`.

Report:
`research/architecture/loom-dflash-q4-baseline-provenance-reconciliation-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-provenance-reconciliation-001/20260825T130903Z/`

P3 expected final-logit SHA-256:
`58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

Invalid-pilot observed SHA-256:
`97cde5dd60c4c270152b65d5dee734c9f68b80a392a77522b0de0eba297cd52e`.

Both hashes are contiguous raw `float32` final-logit vector bytes, shape `[151936]`; this is not serialization/hash semantics.

Root cause:
- frozen P3 producer = 63-token prefill + cached one-token decode `[3889]`;
- invalid-pilot producer = fresh 64-token full-prefix forward.

Inputs/model/config/tokenizer/runtime/source identities match. Both paths are deterministic.

Original segmentation exactly restores the expected SHA; full-prefix replay exactly restores the observed SHA.

Earliest divergence:
- tap layer 1, anchor position `[0,63]`;
- positions `0..62` exact;
- all five taps first differ at the anchor;
- router logits/weights differ at anchor across all 48 layers;
- router IDs diverge at layer 1.

Final hidden drift:
- max abs `0.01266575`;
- mean abs `0.00067455`;
- RMSE `0.00098518`;
- rel-L2 `0.00032064`;
- cosine `0.9999999505`.

Final-logit drift:
- max abs `0.00692338`;
- mean abs `0.00144157`;
- RMSE `0.00172441`;
- rel-L2 `0.00037988`;
- cosine `0.9999999411`;
- top1 remains `1620`;
- ordered top10 parity exact.

The frozen expected SHA remains authoritative. The exact P3 provenance contract includes IDs, segmentation `[63,1]`, cached BF16-KV boundary, selector `[0,-1]`, float32 shape `[151936]`, and raw-byte SHA.

## Next checkpoint

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001`

Goal: mechanically repair the causal-pilot Q4 baseline producer so it reproduces the original frozen continuation producer segmentation and exact provenance before any BF16/network retry.

Q4-only. No BF16 and no network.

Required direction:
1. change only pilot/shared baseline replay code necessary to reproduce the frozen continuation execution segmentation; no model/math changes;
2. recover each selected state's original frozen producer segmentation/KV boundary from frozen evidence/code rather than assuming all states use `[prefix-1,1]`;
3. for P3 explicitly reproduce the known `[63-token prefill, 1-token cached decode]` contract and require exact final-logit SHA `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`;
4. determine and replay the exact original segmentation for P1 `P1_t32:6` and P2 `P2_t16:3` from frozen provenance;
5. for P1/P2/P3 verify exact token IDs, segment boundaries, cache semantics, anchor selector, dtype/shape and expected raw-array SHA commitments;
6. require exact final-logit raw-byte SHA equality for all three states; where frozen tap/router/final-hidden commitments exist, verify them too;
7. rerun unchanged DFlash baseline on the exact restored Q4 taps and verify the preregistered corrected target ranks remain P1=3, P2=3, P3=2 and proposals/labels are consistent with frozen evidence;
8. prove zero real network/BF16 execution;
9. instrumentation/mechanical code changes only; do not modify frozen evidence or relax hashes/tolerances.

Classifications:
- `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`
- `Q4_BASELINE_SEGMENTATION_REPAIR_FAIL`
- `Q4_BASELINE_SEGMENTATION_REPAIR_AMBIGUOUS`

If PASS, the same preregistered P3 -> P1 -> P2 BF16 causal pilot may be re-authorized under the unchanged `8 GiB / 1,024 request` aggregate cap.

Restrictions:
- no BF16 target forward;
- no real network/downloads;
- no E2E;
- no retraining/remapping;
- no state replacement;
- no tolerance/hash relaxation;
- no unrelated performance optimization;
- no Git/docs edits.

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
