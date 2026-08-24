# LOOM — Pi Agent Protocol

Version: 2.7
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. Prompts contain only the active WP delta.

## Role split

Pi owns local technical execution only: inspect relevant local code/runtime, implement the minimum WP code, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, `HANDOFF.md`, `ROADMAP.md`, research result documents and project-state administration.

Pi must NOT run Git, edit HANDOFF/ROADMAP, open/merge/push PRs, or create project documentation unless explicitly authorized by the WP.

## Scientific rules

1. Read this file, then only exact files/evidence relevant to the WP.
2. Use targeted search; do not rescan the repo without need.
3. Do not restate history or full logs.
4. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
5. Distinguish measured fact, inference, hypothesis and unverified limit.
6. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
7. STOP on scientific ambiguity, missing required artifacts, destructive actions or explicit stop gates.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Stable target/runtime

Reference: Apple M1 / 8 GB unified memory.

Local target:
`results-local/moe/models/Qwen3-30B-A3B-MLX-4bit`

Canonical anatomy:
- 48 MoE layers; 128 experts/layer; top-k 8;
- stored payload 16,220,499,968 B;
- resident non-routed backbone 819,015,680 B;
- routed bank 15,401,484,288 B;
- one local 4-bit expert 2,506,752 B;
- zero-cache expert payload 962,592,768 B/token;
- BF16 KV 98,304 B/token.

Stable runtime invariants:
- external serial-expert math and full 48-layer final logits are exact;
- one routed expert needs to be live at a time;
- lifecycle is `GC_END_ONLY`;
- expert-major contiguous disk access is lossless and faster when available;
- 4-GiB raw `GLOBAL_LRU` is rejected (+2.41 GiB swap and slowdown);
- full expert pack is not automatically authorized.

## DFlash validated chain

Drafter: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Publisher target: `Qwen/Qwen3-30B-A3B`
Required target taps: `[1,12,23,34,45]` as 1-based post-block outputs.

Validated:
- `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`: taps-enabled target preserved router/logit/token behavior;
- `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`: exact seven-position target verifier, 1.653x vs sequential, zero swap/leak;
- `LOOM_DFLASH_DRAFTER_PORT_001_PASS`: all 680,813,824 learned BF16 drafter params mapped;
- missing publisher anchor/block attention mask found and repaired;
- `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`: independent corrected publisher reference, 63/63 proposal parity, deterministic/finite.

First E2E:
- `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`;
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Do not remediate memory/performance while acceptance remains zero.

Frozen target continuation:
- `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`;
- 45/45 historical overlap through independent oracle;
- complete 63/63 token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on the then-frozen tap corpus:
- `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`;
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

Important: this compatibility result remains valid for the frozen states themselves, but live-target interpretation is now reopened by the tap replay failure below.

Target identity:
- `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`: `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- architecture/config/tokenizer/vocab/special-token/d2t-t2d checks PASS;
- local material delta: MLX affine 4-bit, group 128, 386 quantized triplets;
- exact historical DFlash-era verifier revision remains unpinned.

## Unquantized-control preflight

`LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001` = `CONDITIONAL_PREFLIGHT_DISK_AND_ADAPTATION_REQUIRED`.

Candidate pinned upstream BF16 control:
- revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`;
- 16 BF16 safetensors shards + index;
- total 61,066,575,648 B;
- full snapshot NOT authorized because disk peak would exceed free space;
- bounded range/shard staging only.

Public provenance: current upstream BF16 shard objects/tokenizer trace to original upload commit `fd4bf3b`; DFlash does not pin an exact verifier revision, so this is a pinned upstream BF16 control, not an exact historical-training replica.

## Current blocker — Q4 tap replay drift

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` classified `CONTROL_ADAPTER_PARITY_FAIL` at Gate A.

Frozen state: `P1_t01`, context 43.

Measured:
- new control adapter vs **current** local Q4 oracle: bitwise parity PASS;
- current router/logits/greedy: PASS;
- deterministic rerun PASS; finite/no leak;
- current Q4 replay vs previously frozen P1_t01 taps: FAIL at all five taps `[1,12,23,34,45]`;
- first tap mismatch: layer 1;
- BF16 access: none; bytes fetched 0 B; peak dedicated disk 0 B.

Interpretation:
- BF16/quantization causality is not tested yet;
- immediate blocker is provenance/replay integrity of the frozen Q4 tap state;
- possibilities include prefix/state identity drift, off-by-one/capture semantics, target/runtime code-path drift, or genuine deterministic hidden-state drift;
- because adapter and current oracle agree, do not debug the BF16 adapter first;
- do not use the stale/frozen tap corpus as definitive evidence for live-target compatibility until this is resolved.

Next checkpoint:
`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

Required goal: reconstruct exact frozen `P1_t01` provenance and localize the first cause of mismatch against current Q4 replay. Compare exact token prefix/hash and context length, position semantics, tap capture semantics, model/config/weight provenance, runtime/code provenance where recoverable, and layer-by-layer current-vs-frozen outputs. Determine whether this is a mechanical replay/capture mismatch or genuine target hidden-state drift.

If a mechanical mismatch is proven, repair only that variable and validate/refreeze the affected tap corpus before resuming compatibility or BF16 controls. If exact replay provenance matches yet taps deterministically differ, classify genuine Q4 hidden-state drift and identify the earliest differing operation/layer.

Restrictions:
- no BF16 weight access;
- no DFlash proposal/E2E rerun;
- no target/drafter/mapping/acceptance changes except a proven mechanical replay/capture repair inside the diagnostic;
- no memory/performance remediation;
- no quantization-causality claim.

## Work-package contract

```text
LOOM WP <id>
Goal: ...
Inputs: exact files/evidence
Change: single allowed variable/scope
Gates: correctness + stop conditions
Evidence: output directory/files
Return: decisive metrics only
STOP
```

Everything not changed by the WP inherits this file. Original model files are immutable. Raw evidence stays under `results-local/<area>/<checkpoint>/<UTC>/` with exact provenance.