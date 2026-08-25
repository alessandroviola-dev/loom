# LOOM — Pi Agent Protocol

Version: 3.10
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

Before materially expensive network/compute work, define retention, provenance, resumability, cache behavior and hard cost/stop gates. A network cap must be enforced **before dispatch**, not only checked after transfer.

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

## Mapping / compatibility facts

Correct publisher decode:
`target_id = draft_row + d2t[draft_row]`.

Support:
- 32,000 valid unique target IDs;
- frozen `50/63` representable, `13/63` unsupported;
- corrected exact top1 remains `0/63`.

For 50 representable states:
- rank min / median / mean / max `2 / 93.5 / 438.82 / 3510`;
- top5 `8/50`, top10 `11/50`, top50 `19/50`, top100 `26/50`;
- top1 `0/50`.

Historical E2E `0/96` used the old decode and is not current acceptance evidence.

## Closed leading hypotheses

Temporal alignment:
- full preregistered `-7..+7` = `NO_SYSTEMATIC_TEMPORAL_SHIFT`.

MLX drafter implementation:
- `LOOM_DFLASH_FULL_LOGIT_REFERENCE_PARITY_001` = `FULL_LOGIT_REFERENCE_PARITY_PASS`;
- decision-level parity exact on 6 stratified states, full 32k vectors numerically equivalent under established gates.

Verifier provenance/tap semantics:
- `LOOM_DFLASH_VERIFIER_PROVENANCE_TAP_INTERFACE_AUDIT_001` = `PROVENANCE_UNPINNED_NO_MATERIAL_MISMATCH_FOUND`;
- static contract `16/16` PASS;
- `[1,12,23,34,45]` are ordered 1-based post-block residuals, pre-final-norm;
- no demonstrated material target revision/config/tokenizer/tap mismatch.

Tap transport dtype:
- `LOOM_DFLASH_TAP_TRANSPORT_BF16_SENSITIVITY_001` = `NO_MATERIAL_TAP_DTYPE_EFFECT`;
- float32 -> BF16 -> float32 tap round-trip caused `0/63` proposal changes, no top-k boundary crossings, exact matches `0/50 -> 0/50`.

Do not revisit these mechanisms without new evidence.

## BF16 target context

Available upstream BF16 target revision:
`ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`.

Prior P1_t01 Q4->BF16 control materially changed routing/taps/logits but target top1 stayed `12050`; P1_t01 is outside DFlash support, so it cannot test exact recovery on a representable target.

Persistent BF16 cache is reusable.

## Representable BF16 target pilot preflight — COMPLETE

`LOOM_DFLASH_REPRESENTABLE_BF16_TARGET_CONTROL_PREFLIGHT_001` = `BF16_TARGET_PILOT_READY_WITH_BOUNDED_MISSING_CACHE`.

Report:
`research/architecture/loom-dflash-representable-bf16-target-control-preflight-001-result.md`

Evidence:
`results-local/research/dflash-representable-bf16-target-control-preflight-001/20260825T115402Z/`

Selected deterministic near-target states:
- P1 `P1_t32:6`, rank 3, target 326, 79-token verifier prefix;
- P2 `P2_t16:3`, rank 3, target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, target 1620, 64-token prefix.

No compute sharing: distinct P1/P2/P3 trajectories and fresh KV state.

BF16 cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections SHA-256 verified;
- failures `0`;
- dense `3,082,218,423 B`;
- experts `32,755,649,797 B`;
- total `35,837,957,463 B`;
- free external disk `1,152.25 GiB`.

Q4-routing planning estimate only, because BF16 routing may diverge:
- P1: 1,942 hits / 315 misses / 2,972,712,960 B missing;
- P2: 1,476 / 507 / 4,784,652,288 B;
- P3: 371 / 13 / 122,683,392 B;
- combined unique: 2,325 hits / 703 misses / 6,634,340,352 B.

Existing BF16 fetch/cache path is atomic and resumable but does **not** pre-check byte/request caps before dispatch.

Proposed expensive pilot ceiling after safety repair:
- 8 GiB total network budget;
- 1,024 request budget;
- `NETWORK_CAP_ABORT` before dispatch if next request would exceed either limit;
- retain taps, final logits, routing, DFlash 32k logits, target ranks/top-k, network/cache ledger and partial persistent cache.

## Next checkpoint

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001`

Goal: mechanically add and validate a pre-dispatch network byte/request guard to the existing on-demand BF16 fetch/cache path before any new BF16 target execution.

Required direction:
1. modify only the shared BF16 fetch/cache accounting/dispatch path required for the later pilot;
2. support explicit hard caps for cumulative network bytes and requests;
3. before every network dispatch, compute the maximum accounted cost of that request from the existing range/request plan and refuse dispatch if it would exceed either cap;
4. emit deterministic `NETWORK_CAP_ABORT` with current ledger, proposed request cost and cap values;
5. cache hits must consume zero network bytes/requests;
6. successful requests update the persistent/run ledger exactly once; retries must be explicitly counted and bounded;
7. abort must preserve already-valid persistent cache and resumability;
8. add local synthetic/unit tests for: exact-boundary allow, byte-cap reject-before-dispatch, request-cap reject-before-dispatch, cache-hit zero-cost, retry accounting, and resume/partial-cache preservation;
9. no real network request is authorized in this checkpoint.

Classification:
- `BF16_NETWORK_CAP_GUARD_PASS`
- `BF16_NETWORK_CAP_GUARD_FAIL`
- `BF16_NETWORK_CAP_GUARD_AMBIGUOUS`

If PASS, next checkpoint may authorize the preregistered 3-state Q4-vs-BF16 target causal pilot under hard `8 GiB / 1,024 request` limits.

Restrictions:
- no target/BF16 target forward;
- no real downloads/network;
- no E2E;
- no retraining/remapping;
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
