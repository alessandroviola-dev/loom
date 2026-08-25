# LOOM — Pi Agent Protocol

Version: 3.16
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
7. Do not relax preregistered provenance/hash gates post-hoc merely because top1/top-k agrees.
8. Continuation-state provenance includes producer segmentation and KV-cache boundary.

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
- stored payload `16,220,499,968 B`;
- resident non-routed backbone `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- one local Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
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
- all `680,813,824` learned BF16 drafter params mapped;
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
- verifier/tap static interface: `16/16` PASS, no demonstrated material mismatch;
- tap transport float32-vs-BF16: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Do not reopen these without new evidence.

## BF16 bounded infrastructure — COMPLETE

Pinned available BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Remote guard source parity:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Validated guard SHA-256:
- range control `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376`;
- BF16 tap probe `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f`;
- guard test `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae`.

Hard ceilings for the causal pilot remain frozen:
- aggregate network `8 GiB`;
- aggregate requests `1,024`, retries included;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache.

BF16 cache preflight remains valid:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections verified;
- total cache `35,837,957,463 B`;
- Q4-route planning estimate 703 combined unique misses / `6,634,340,352 B`.

Actual BF16 routing may diverge.

## Representable causal state set — FROZEN

Selected states and fixed execution order:
1. P3 `P3_t01:2` — frozen Q4 target `1620`, baseline DFlash rank `2`, 64-token state;
2. P1 `P1_t32:6` — target `326`, rank `3`, 79-token state;
3. P2 `P2_t16:3` — target `994`, rank `3`, 74-token state.

No substitutions or reordering.

## First causal pilot attempt — INVALID BEFORE BF16

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` = `INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

It stopped before BF16/network because P3 Q4 final-logit provenance failed. No BF16 scientific conclusion is valid from that attempt.

## Q4 provenance reconciliation — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001` = `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`.

Root cause: deterministic producer segmentation drift.

P3 frozen producer used `63-token prefill + cached one-token decode [3889]`; invalid pilot used a fresh 64-token full-prefix forward. Inputs/model/runtime were otherwise identical. The frozen raw-float32 SHA remains authoritative.

## Q4 segmentation replay repair — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001` = `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`.

Report:
`research/architecture/loom-dflash-q4-baseline-segmentation-replay-repair-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-segmentation-replay-repair-001/20260825T132255Z/`

Recovered exact producer segmentation:
- P3: `[63,1]`; decode token `3889`; KV boundary `63`;
- P1: `[43] + 31x[1]`, then branch tokens `[1674,52245,9935,11,1187]`; KV boundary `74`;
- P2: `[57] + 15x[1]`, then branch tokens `[30130,84]`; KV boundary `72`.

Exact expected=observed raw `float32 [151936]` final-logit SHA-256:
- P1 `c3d4987ef17e295ea2a396c60e8dfb273100455059d9e829f4ef75637081c202`;
- P2 `65339a7fd91a8ef7f4cc36a36e897c3fed788cbb57466839b4b8ec3582a50a05`;
- P3 `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

All states passed exact IDs, frozen base taps, BF16-KV boundaries/offsets, selector `[0,-1]`, dtype/shape, final SHA, finite/no-expert-leak gates.

Unchanged DFlash restored the preregistered baseline:
- P1 rank `3`, proposal `3100`;
- P2 rank `3`, proposal `4057`;
- P3 rank `2`, proposal `5416`.

Zero BF16 target forwards, network bytes/requests, downloads and E2E runs.

Repair source is remote-reproducible via user commit `8a74c3a2f039a771b4f1a682cc1754e48c76e50e`:
- `scripts/loom_dflash_q4_baseline_replay_shared_001.py` — local SHA-256 `6da9e920f24e3c66ac8d37056d13e544dc70194b1d83987a5875db54590e1ea0` — Git blob `f75771e99ca8e604521094ed494422409e31e65c`;
- `scripts/loom_dflash_representable_bf16_target_causal_pilot_001.py` — local SHA-256 `2882a8168612d1a3b6d0151b1b4511d21a51c0ba90b209f145f2fd3cc64a5e2b` — Git blob `3e3639749078c6ef60b25846a6df8d1ce4a4f48f`.

The Q4 baseline provenance blocker is CLOSED.

## Next checkpoint

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002`

Goal: re-attempt the original one-factor Q4-vs-pinned-BF16 causal pilot after the purely mechanical baseline producer repair. The scientific contract is unchanged from pilot 001.

Required execution:
1. fixed order P3 -> P1 -> P2;
2. before each BF16 intervention, reproduce the exact segmented Q4 baseline with the restored producer and require all exact provenance gates;
3. teacher-force pinned BF16 verifier through the same segmented logical continuation state, preserving the same token IDs/state definition and capturing taps `[1,12,23,34,45]`, final logits/top1, routing and network/cache ledger;
4. run unchanged DFlash on exact Q4 taps and BF16 taps with IDs/positions/masks/tap order/weights/mapping frozen;
5. compare per-layer Q4-vs-BF16 taps and full 32k DFlash logits using max abs, mean abs, RMSE, rel-L2, cosine and proposal change;
6. preserve both labels per state: frozen Q4 verifier target and BF16 verifier top1;
7. report DFlash rank/top5/top10/top50/top100/top1 for frozen label under both conditions, and for BF16 label when DFlash-representable;
8. retain completed-state evidence if a later state hits the hard cap; no post-hoc state replacement.

Preregistered decision classifications remain unchanged:
- `BF16_TARGET_RECOVERY_SIGNAL`: at least 2 selected states have BF16-tap DFlash top1 equal to a representable BF16 verifier top1 while corresponding Q4-tap condition is not exact;
- `NO_USEFUL_BF16_TARGET_RECOVERY`: zero exact BF16-label recoveries and no broad decision-level/top-k improvement;
- `BF16_TARGET_EFFECT_AMBIGUOUS`: exactly one exact recovery, support/label ambiguity, or systematic non-top1 movement insufficient for the recovery gate;
- `BF16_TARGET_PILOT_NETWORK_CAP_ABORT`: hard cap stops completion; retain partial evidence and infer nothing for unexecuted states.

If any repaired Q4 baseline provenance gate fails, STOP as invalid rather than rescue.

No E2E, retraining, remapping, state substitution, tolerance relaxation or unrelated optimization.

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
