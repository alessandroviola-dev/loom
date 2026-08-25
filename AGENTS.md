# LOOM — Pi Agent Protocol

Version: 3.12
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

Selected states:
- P1 `P1_t32:6`, rank 3, frozen target 326, 79-token prefix;
- P2 `P2_t16:3`, rank 3, frozen target 994, 74-token prefix;
- P3 `P3_t01:2`, rank 2, frozen target 1620, 64-token prefix.

No compute sharing across trajectories.

Cache audit:
- 435 dense manifests;
- 3,470 expert manifests / 10,410 projections SHA-256 verified;
- failures 0;
- total BF16 cache `35,837,957,463 B`;
- external free disk `1,152.25 GiB`;
- Q4-route estimate: 703 combined unique misses / `6,634,340,352 B` missing.

Actual BF16 routing may diverge.

Pilot ceiling after source parity:
- hard network `8 GiB`;
- hard requests `1,024`;
- `NETWORK_CAP_ABORT` before dispatch;
- persistent/resumable cache.

## BF16 network-cap guard — VALIDATED LOCALLY

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_001` = `BF16_NETWORK_CAP_GUARD_PASS`.

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-001/20260825T121354Z/`

Validated behavior:
- synthetic tests `6/6` PASS; compile PASS;
- exact boundary allow;
- byte/request reject occurs before `HTTPSConnection.request`;
- deterministic `NETWORK_CAP_ABORT`;
- retries counted and bounded;
- cache hits charge `0 B / 0 requests`;
- abort preserves complete/partial cache and resumability;
- real network dispatches observed `0`.

Validated local files:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py`.

## Guard source export — COMPLETE

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_SYNC_001` = `BF16_NETWORK_CAP_GUARD_SOURCE_EXPORT_PASS`.

Report:
`research/architecture/loom-dflash-bf16-network-cap-guard-source-sync-001-result.md`

Evidence:
`results-local/research/dflash-bf16-network-cap-guard-source-sync-001/20260825T122613Z/`

Export method: `FULL_CONTENT` UTF-8 copies under `full-content/scripts/`.

Pinned validated source identities:
- `scripts/loom_dflash_unquantized_target_p1t01_range_control_001.py` — 74,261 B — SHA-256 `dc0bdb6af282805cdfb623404bcfc778922c28a7b21df750cee08340b365a376`;
- `scripts/loom_dflash_bf16_tap_drafter_probe_001.py` — 26,443 B — SHA-256 `7a6119f01c99eb5d0833ff5bc5b6a7e47c540161ac5414aae246adc62bec479f`;
- `scripts/test_loom_dflash_bf16_network_cap_guard_001.py` — 11,741 B — SHA-256 `7b6577076bffd73733f7766ca87638004618a7c4a121ae4f5fc6a5a318e776ae`.

All exported copies byte-match local validated sources and prior hashes.

Critical remaining blocker: the full exported file bytes were saved on the user's local filesystem but were not included in the chat payload. ChatGPT cannot reconstruct source from hashes alone. Remote/fresh-clone source parity is therefore still NOT established.

## Next checkpoint

`LOOM_DFLASH_BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_HANDOFF_001`

Goal: transfer the exact already-exported full source payload into a form ChatGPT can access, without modifying code.

Required direction:
1. make NO source changes;
2. do NOT run Git;
3. create one deterministic payload containing the exact three exported UTF-8 files, preferably a single base64-encoded tar/zip or equivalent text artifact;
4. include payload SHA-256 plus the three pinned per-file SHA-256 values above;
5. output/present the payload in a way the user can attach or paste into ChatGPT; if attachment creation is possible locally, produce a single compact artifact for upload;
6. no target/network execution.

Classification:
- `BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_READY`
- `BF16_NETWORK_CAP_GUARD_SOURCE_PAYLOAD_AMBIGUOUS`

After ChatGPT receives the actual payload, it must write the exact files to GitHub and verify content hashes before authorizing the expensive BF16 pilot.

## Later pilot measurement rule

For each selected state preserve both labels:
- frozen Q4 target token;
- BF16 verifier top1 token at the same state.

Measure DFlash under Q4 vs BF16 taps against the frozen Q4 target and, when representable, against the BF16 verifier top1.

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
