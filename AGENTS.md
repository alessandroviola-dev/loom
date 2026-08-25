# LOOM — Pi Agent Protocol

Version: 3.11
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

## BF16 target context

Available BF16 verifier revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Prior P1_t01 Q4->BF16 materially changed routing/taps/logits but P1_t01 target `12050` is outside DFlash support, so it cannot test representable-target recovery.

Persistent BF16 cache is reusable.

## Representable BF16 target preflight — COMPLETE

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-control-preflight-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z/`

Selected states:
- P1 `P1_t32:6`, rank 3, frozen target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, frozen target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, frozen target 1620, 64-token prefix.

No compute sharing across trajectories.

BF16 cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections SHA-256 verified;
- integrity failures 0;
- dense 3,082,218,423 B;
- experts 32,755,649,797 B;
- total 35,837,957,463 B;
- free external disk 1,152.25 GiB.

Q4-routing planning estimate only; BF16 routing may diverge:
- P1 misses 315 / 2,972,712,960 B;
- P2 misses 507 / 4,784,652,288 B;
- P3 misses 13 / 122,683,392 B;
- combined unique misses 703 / 6,634,340,352 B.

Pilot ceiling: hard `8 GiB` total network and `1,024` requests, with `NETWORK_CAP_ABORT` before dispatch.

## BF16 network cap guard — VALIDATED LOCALLY

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-001-result.md`

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-001/20260825T121354Z/`

Validated local working-tree files:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py`.

Results:
- synthetic tests `6/6` PASS; compile PASS;
- exact boundary allow PASS;
- byte/request rejects occur before `HTTPSConnection.request` and emit deterministic `NETWORK_CAP_ABORT`;
- retry reservations counted exactly once; 2 attempts = 10 B / 2 requests with one bounded retry;
- cache hits cost 0 B / 0 requests;
- abort preserves complete/partial cache and resumability;
- real network dispatches observed: `0`.

Critical reproducibility state: the validated guard source delta exists in the **local working tree only** and is not yet represented in the GitHub branch. Do not claim remote source parity or run the expensive pilot from a fresh clone until exact source synchronization is complete.

## Next checkpoint

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001`

Goal: capture the exact already-validated local guard implementation for the three files above and synchronize it to GitHub without altering behavior.

Required direction:
1. make NO code changes;
2. do NOT run Git;
3. output exact full UTF-8 contents of the three modified files, or deterministic complete patches against the current branch versions, sufficient for ChatGPT to reproduce them byte-for-byte;
4. include SHA-256 of each local file;
5. rerun no expensive tests; at most re-run the existing synthetic guard test if needed to prove the exported files remain the validated state;
6. no network/target execution.

Classification:
- `BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_PASS`
- `BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_AMBIGUOUS`

After ChatGPT applies the exact source delta and verifies remote parity, authorize the preregistered 3-state Q4-vs-BF16 target causal pilot under hard `8 GiB / 1,024 request` limits.

## Later pilot measurement rule

For each selected state, the eventual causal pilot must preserve both labels:
- frozen Q4 target token for continuity;
- BF16 verifier top1 token at the same state.

Measure DFlash under Q4 vs BF16 taps against the frozen Q4 target and, when representable, against the BF16 verifier top1. This avoids falsely calling recovery/failure if verifier precision itself changes the target top1.

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
