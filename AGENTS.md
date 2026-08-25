# LOOM — Pi Agent Protocol

Version: 3.13
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
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

Correct publisher decode:
`target_id = draft_row + d2t[draft_row]`.

Support / corrected compatibility:
- 32,000 valid unique target IDs;
- frozen `50/63` representable, `13/63` unsupported;
- corrected exact top1 remains `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` used the old decode and is not current acceptance evidence.

## Closed leading hypotheses

- temporal/off-by-N: `NO_SYSTEMATIC_TEMPORAL_SHIFT` over full `-7..+7`;
- MLX drafter implementation: `FULL_LOGIT_REFERENCE_PARITY_PASS` on 6 stratified states;
- verifier/tap static interface: `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`, contract `16/16` PASS;
- tap transport float32-vs-BF16: `NO_MATERIAL_TAP_DTYPE_EFFECT`, proposal changes `0/63`, no top-k crossings.

Do not reopen these without new evidence.

## BF16 representable-state path

Available BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected deterministic states:
- P1 `P1_t32:6`, baseline rank 3, frozen Q4 target 326, 79-token verifier prefix;
- P2 `P2_t16:3`, baseline rank 3, frozen Q4 target 994, 74-token prefix;
- P3 `P3_t01:2`, baseline rank 2, frozen Q4 target 1620, 64-token prefix.

No compute sharing across trajectories; use fresh KV state per prompt.

BF16 cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections SHA-256 verified;
- integrity failures 0;
- total BF16 cache `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route planning estimate: 703 combined unique misses / `6,634,340,352 B` missing.

Actual BF16 routing may diverge.

## BF16 network-cap guard — COMPLETE AND REMOTE-REPRODUCIBLE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Validated behavior:
- synthetic tests `6/6` PASS; compile PASS;
- exact boundary allow;
- byte/request reject occurs before `HTTPSConnection.request`;
- deterministic `NETWORK_CAP_ABORT`;
- retries counted and bounded;
- cache hits charge `0 B / 0 requests`;
- abort preserves complete/partial cache and resumability;
- real network dispatches observed `0` during validation.

Source export and payload handoff are now closed:

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-source-payload-handoff-001-result.md`

Validated remote source identities at user commit `01a5f9b`:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py` — 74,261 B — SHA-256 `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376` — Git blob `00287bc793fce8b552c55b8706a2d7f4d69be08e`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py` — 26,443 B — SHA-256 `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f` — Git blob `b2366c1c78b960e0bba224a3eb2da8efe92e7bfc`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py` — 11,741 B — SHA-256 `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae` — Git blob `8ded2333d8007abec857d20b82e891b961add69b`.

Fresh-clone source parity is established. The local-only blocker is CLOSED.

## Next checkpoint

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001`

Goal: test whether verifier precision/distribution (Q4 target state vs pinned BF16 target state) causally recovers DFlash compatibility on the three preregistered representable near-target states.

Execution order for bounded feasibility:
1. P3 `P3_t01:2`;
2. P1 `P1_t32:6`;
3. P2 `P2_t16:3`.

This order is fixed from ascending preflight-estimated missing network bytes and does not change state selection.

Hard aggregate ceilings across the whole BF16 pilot:
- network bytes: `8 GiB`;
- requests: `1,024`, retries included;
- `NETWORK_CAP_ABORT` before dispatch if the next request would exceed either cap;
- persistent cache and partial progress retained.

Required gates / measurements:
1. reproduce the Q4 baseline for each state before interpreting BF16; frozen target token and retained Q4 state must remain consistent;
2. run the pinned BF16 verifier teacher-forced only to the selected state/prefix;
3. retain BF16 taps `[1,12,23,34,45]`, target final logits/top1, routing and network/cache ledger;
4. compare Q4-vs-BF16 taps per layer: max abs, mean abs, RMSE, rel-L2, cosine;
5. run the unchanged DFlash drafter on Q4 taps and BF16 taps with identical IDs/positions/masks/tap order/weights/mapping;
6. compare full 32k DFlash logits: max abs, mean abs, RMSE, rel-L2, cosine and proposal change;
7. preserve both labels per state: frozen Q4 target token and BF16 verifier top1 token;
8. report DFlash rank/top5/top10/top50/top100/top1 for the frozen token in both conditions;
9. if BF16 verifier top1 is DFlash-representable, report the same metrics and exact proposal match for that BF16 label;
10. retain completed-state evidence even if a later state hits the network cap; do not post-hoc replace states.

Decision classifications:
- `BF16_TARGET_RECOVERY_SIGNAL`: at least 2 selected states achieve BF16-tap DFlash top1 equal to the BF16 verifier top1 (representable), while the corresponding Q4-tap condition is not exact;
- `NO_USEFUL_BF16_TARGET_RECOVERY`: zero exact BF16-label recoveries and no broad decision-level/top-k improvement;
- `BF16_TARGET_EFFECT_AMBIGUOUS`: exactly one exact recovery, label-support ambiguity, or systematic non-top1 movement insufficient for the recovery gate;
- `BF16_TARGET_PILOT_NETWORK_CAP_ABORT`: hard cap stops completion; retain partial evidence but do not infer the missing states.

If Q4 baseline replay/provenance fails, STOP as an invalid pilot rather than rescuing.

No E2E, retraining, remapping or unrelated performance optimization in this checkpoint.

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
