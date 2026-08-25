# LOOM — Pi Agent Protocol

Version: 3.14
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
- corrected exact DFlash top1 remains `0/63`;
- representable ranks min/median/mean/max `2 / 93.5 / 438.82 / 3510`;
- top5/top10/top50/top100 `8/11/19/26`.

Historical E2E `0/96` used the old decode and is not current acceptance evidence.

## Closed leading hypotheses

- temporal/off-by-N: `NO_SYSTEMATIC_TEMPORAL_SHIFT` over full `-7..+7`;
- MLX drafter implementation: `FULL_LOGIT_REFERENCE_PARITY_PASS` on 6 stratified states;
- verifier/tap static interface: `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`, contract `16/16` PASS;
- tap transport float32-vs-BF16: `NO_MATERIAL_TAP_DTYPE_EFFECT`, proposal changes `0/63`, no top-k crossings.

Do not reopen these without new evidence.

## BF16 network-cap path — COMPLETE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Validated behavior:
- synthetic tests `6/6` PASS; compile PASS;
- exact-boundary allow;
- byte/request reject occurs before `HTTPSConnection.request`;
- deterministic `NETWORK_CAP_ABORT`;
- retries counted and bounded;
- cache hits charge `0 B / 0 requests`;
- abort preserves complete/partial cache and resumability;
- real network dispatches observed `0` during validation.

Remote source parity is also complete:
`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001` = `BF16_NETWORK_CAP_GUARD_REMOTE_SOURCE_PARITY_PASS`.

Validated remote source identities at user commit `01a5f9b`:
- range control — SHA-256 `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376`;
- BF16 tap probe — SHA-256 `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f`;
- guard test — SHA-256 `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae`.

## Representable BF16 pilot preflight — COMPLETE

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Selected states:
- P1 `P1_t32:6`, baseline DFlash rank 3, frozen Q4 verifier target 326, 79-token prefix;
- P2 `P2_t16:3`, baseline DFlash rank 3, frozen Q4 verifier target 994, 74-token prefix;
- P3 `P3_t01:2`, baseline DFlash rank 2, frozen Q4 verifier target 1620, 64-token prefix.

BF16 cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections SHA-256 verified;
- failures 0;
- total BF16 cache `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route planning estimate: 703 combined unique misses / `6,634,340,352 B` missing.

Pilot hard aggregate ceilings remain frozen for any later re-attempt:
- network `8 GiB`;
- requests `1,024`, retries included;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache.

## Representable BF16 causal pilot — INVALID BEFORE INTERVENTION

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CAUSAL_PILOT_001` stopped before BF16/network and has administrative outcome:
`INVALID_PILOT_Q4_BASELINE_OR_MECHANICAL_STOP`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-causal-pilot-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-causal-pilot-001/20260825T125526Z/`

Pre-dispatch checks:
- all three guard SHA-256 values matched;
- guard tests `6/6` PASS;
- storage/cache available with `1,152.25 GiB` free;
- aggregate ledger started at `0 B / 0 requests / 0 retries`.

First fixed-order state P3 `P3_t01:2`:
- Q4 verifier top1 matched frozen target `1620`;
- final-logit provenance SHA did **not** match the frozen expected SHA;
- reported observed hash abbreviated `97cde5dd...297cd52e`;
- reported expected hash abbreviated `58d20d90...185432`.

No BF16 state was executed. Network remained `0 B / 0 requests / 0 retries`.

Therefore no BF16 scientific outcome classification is valid. Do not infer recovery or non-recovery.

## Next checkpoint

`LOOM_DFLASH_Q4_BASELINE_PROVENANCE_RECONCILIATION_001`

Goal: determine exactly why the P3 Q4 baseline replay matches verifier top1 but fails the final-logit provenance SHA gate, before any BF16 intervention is retried.

Q4-only / P3-only diagnostic. No BF16 and no network.

Required direction:
1. read the invalid-pilot evidence and recover the **full** observed and expected SHA-256 values plus exact source artifact paths;
2. identify precisely what object the expected hash represents: raw contiguous logit vector bytes vs file/NPZ serialization, dtype, shape, selected position, and any canonicalization;
3. identify the exact producer/code path that created the frozen expected P3 final logits and the exact code path used by the invalid pilot replay;
4. freeze and compare input token IDs/prefix length, model/config/tokenizer identities, runtime versions, target code identities, tensor dtype/shape and anchor position;
5. execute only the minimum local Q4 replay needed to compare original-producer and pilot-producer paths under the same current environment;
6. locate the earliest divergence across, in order: input IDs -> taps `[1,12,23,34,45]` -> router IDs/weights -> final hidden -> full final-logit vector;
7. for every differing numerical array report max abs, mean abs, RMSE, rel-L2, cosine, top1 and ordered top-k parity as applicable;
8. compute explicit canonical raw-array SHA-256 using contiguous bytes with dtype/shape recorded for both expected and observed vectors;
9. if the mismatch is purely hash/serialization/selector semantics, demonstrate that mechanically and identify the correct provenance gate without silently weakening it;
10. if true numerical drift exists, identify the earliest material divergence and likely mechanical source. Do not alter model math, quantization, routing, positions, masks, target state, or frozen evidence to make it pass.

Classifications:
- `Q4_BASELINE_EXACT_REPLAY_RESTORED`
- `Q4_BASELINE_HASH_SEMANTICS_RECONCILED`
- `Q4_BASELINE_MATERIAL_DRIFT_IDENTIFIED`
- `Q4_BASELINE_PROVENANCE_AMBIGUOUS`

Instrumentation-only local code changes are permitted if required to expose evidence; no behavior-changing rescue.

Restrictions:
- no BF16 target forward;
- no real network/downloads;
- no E2E;
- no retraining/remapping;
- no state replacement;
- no post-hoc tolerance relaxation;
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
