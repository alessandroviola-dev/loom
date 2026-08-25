# LOOM — Pi Agent Protocol

Version: 3.17
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. WP prompts carry only the active delta.

## Role split

Pi owns targeted local execution: inspect local code/evidence, implement the minimum authorized mechanical change, run bounded tests, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, research result documents, `HANDOFF.md`, `ROADMAP.md`, and checkpoint administration.

Pi must NOT run Git, edit AGENTS/HANDOFF/ROADMAP, push/open/merge PRs, or create project documentation unless explicitly authorized.

## Scientific rules

1. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
2. Distinguish fact, inference, hypothesis and unverified limit.
3. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
4. STOP on scientific ambiguity, destructive actions, missing required artifacts, or explicit stop gates.
5. Do not relax preregistered hash/provenance gates post-hoc.
6. Continuation-state provenance includes token IDs, producer segmentation, KV-cache boundary, selector and DFlash continuation row.
7. Before network/expensive compute define retention, resumability and hard pre-dispatch caps.
8. A treatment comparison is invalid if quantization/precision is not the only material factor changed.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

External root:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

## Mission / stable target

Mission: **Big models. Small machines.** Make ~27B/32B-class local AI practical on Apple M1 / 8 GB with exactness, bounded memory and reproducible evidence.

Operational Q4 target:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Stable target facts:
- 48 MoE layers; 128 experts/layer; top-k 8;
- stored payload `16,220,499,968 B`;
- resident non-routed backbone `819,015,680 B`;
- routed bank `15,401,484,288 B`;
- local Q4 expert `2,506,752 B`;
- BF16 KV `98,304 B/token`;
- external serial-expert full-logit math is exact;
- one routed expert logically live at a time;
- expert-major contiguous disk preferred;
- raw 4-GiB global LRU rejected.

## DFlash stable chain

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Verifier: `Qwen/Qwen3-30B-A3B`
Taps: `[1,12,23,34,45]`.

Still valid:
- exact target-tap implementation;
- exact B7 wavefront verifier;
- all `680,813,824` learned BF16 drafter params mapped;
- publisher mask repair;
- deterministic finite 32k drafter forward;
- frozen target continuation 63/63, SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`;
- target identity `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- correct mapping `target_id = draft_row + d2t[draft_row]`;
- support `50/63` representable, `13/63` unsupported;
- corrected DFlash exact top1 `0/63`;
- representable rank min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Closed leading explanations:
- temporal shift: `NO_SYSTEMATIC_TEMPORAL_SHIFT`;
- MLX drafter port: `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- static verifier/tap interface: `16/16` PASS, no demonstrated material mismatch;
- tap transport float32/BF16: `NO_MATERIAL_TAP_DTYPE_EFFECT`.

Do not reopen without new evidence.

## BF16 infrastructure — COMPLETE

Pinned BF16 revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Network guard:
`BF16_NETWORK_CAP_GUARD_PASS` with exact remote source parity.

Per valid causal-pilot attempt hard ceilings:
- network `8 GiB`;
- requests `1,024`, retries included;
- reject before dispatch with `NETWORK_CAP_ABORT`;
- persistent/resumable cache.

Frozen causal states/order:
1. P3 `P3_t01:2` — Q4 target `1620`, exact baseline rank `2`;
2. P1 `P1_t32:6` — target `326`, rank `3`;
3. P2 `P2_t16:3` — target `994`, rank `3`.

No substitution or reordering.

## Q4 baseline repair — COMPLETE

`LOOM_DFLASH_Q4_BASELINE_SEGMENTATION_REPLAY_REPAIR_001` = `Q4_BASELINE_SEGMENTATION_REPAIR_PASS`.

Report:
`research/architecture/loom-dflash-q4-baseline-segmentation-replay-repair-001-result.md`

Evidence:
`results-local/research/dflash-q4-baseline-segmentation-replay-repair-001/20260825T132255Z/`

Exact segmentation:
- P3 `[63,1]`, decode token `3889`, KV boundary `63`;
- P1 `[43] + 31x[1]`, branch `[1674,52245,9935,11,1187]`, boundary `74`;
- P2 `[57] + 15x[1]`, branch `[30130,84]`, boundary `72`.

Exact final-logit raw `float32 [151936]` SHA commitments:
- P1 `c3d4987ef17e295ea2a396c60e8dfb273100455059d9e829f4ef75637081c202`;
- P2 `65339a7fd91a8ef7f4cc36a36e897c3fed788cbb57466839b4b8ec3582a50a05`;
- P3 `58d20d9086cff8d2789bbd0fd686eb2e5d6a9483168781cba04218b820185432`.

Restored DFlash baselines:
- P1 rank `3`, proposal `3100`;
- P2 rank `3`, proposal `4057`;
- P3 rank `2`, proposal `5416`.

Remote repair source commit:
`8a74c3a2f039a771b4f1a682cc1754e48c76e50e`.

## BF16 causal pilot 002 — OPERATIONAL CAP ABORT, SCIENTIFIC INTERPRETATION HELD

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_002` reported:
`BF16_TARGET_PILOT_NETWORK_CAP_ABORT`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-002-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-002/20260825T134150Z/`

Operational facts accepted:
- P3 BF16 completed;
- P1 exact Q4 baseline passed, BF16 then cap-aborted;
- P2 unexecuted;
- aggregate network `8,583,061,312 B` (`7.994 GiB`), `1,007` requests, `7` retries;
- cache `20,832` hits / `898` misses including partial P1;
- next `9,437,184 B` request blocked before dispatch.

Reported P3 values exist but are NOT yet causal evidence:
- BF16 verifier top1 `1620`, representable;
- reported frozen/BF16 label rank Q4-taps `5`, BF16-taps `13`;
- proposal reported `4330 -> 2790`;
- no reported exact top1 recovery.

Why interpretation is withheld:
- exact repaired P3 baseline rank is `2`, not reported pilot Q4-tap rank `5`;
- review of remote predecessor source `scripts/loom_dflash_representable_bf16_target_causal_pilot_001.py` found three hazards:
  1. paired scoring receives shared replay `full_taps`, whereas the frozen DFlash baseline gate is computed from `base_taps`;
  2. DFlash scoring selects fixed row `[0,1]` instead of the selected state's preregistered continuation row;
  3. BF16 helper runs a fresh full-prefix forward instead of reproducing the same segmented/KV-boundary continuation producer.

The exact executed source was reported as local:
`scripts/loom_dflash_representable_bf16_target_causal_pilot_002.py`.
It is not yet remote-reproducible, so its exact behavior must be audited before drawing scientific conclusions.

## Next checkpoint

`LOOM_DFLASH_BF16_PILOT_002_CAUSAL_VALIDITY_AUDIT_001`

Goal: byte-exactly audit the executed local `_002` source and existing pilot-002 artifacts, determine whether the three hazards above are present, and establish what P3 evidence (if any) is scientifically reusable.

Strictly OFFLINE. No BF16 target forward and no real network/downloads.

Required:
1. hash and preserve exact local `scripts/loom_dflash_representable_bf16_target_causal_pilot_002.py` source identity;
2. compare `_002` to remote `_001` and report only causal-relevant changes;
3. trace exact objects passed into DFlash scoring for P3: Q4 `base_taps` vs `full_taps`, BF16 tap tensor provenance, anchor and selected continuation row;
4. prove which DFlash row corresponds to P3 continuation position `2`; recompute P3 Q4 score from existing arrays only and require restored rank `2`/proposal `5416` when using the frozen exact inputs;
5. verify whether P3 BF16 target/taps were produced as fresh full-prefix or exact frozen-equivalent segmentation/KV boundary;
6. compare input IDs, segmentation, cache offsets/positions/selectors and tensor shapes for Q4 vs BF16;
7. do not execute any BF16 model forward; use existing `q4-target.npz`, `bf16-target.npz`, JSON reports and source only;
8. if existing BF16 P3 artifacts are treatment-confounded, mark them non-causal; do not rescue by re-running treatment in this checkpoint;
9. inspect cap/cache evidence only to determine what downloaded cache can safely be reused later;
10. instrumentation-only/offline local code allowed; no scientific treatment change.

Classifications:
- `PILOT_002_CAUSAL_PATH_VALID`
- `PILOT_002_CAUSAL_PATH_INVALID_MECHANICAL`
- `PILOT_002_CAUSAL_VALIDITY_AMBIGUOUS`

If invalid, next step is a separate preregistered mechanical pilot-source repair and offline validation before any new BF16/network attempt.

Restrictions:
- no BF16 target forward;
- no network/downloads;
- no E2E;
- no retraining/remapping;
- no cap reset or new pilot execution;
- no state substitution;
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

Original model files are immutable. Raw evidence stays under `results-local/`; expensive retained artifacts may live under the external root.