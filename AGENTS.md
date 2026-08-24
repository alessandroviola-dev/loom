# LOOM — Pi Agent Protocol

Version: 2.8
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
5. Treat runtime/library version as an experimental variable whenever bitwise hidden-state parity matters.
6. Distinguish measured fact, inference, hypothesis and unverified limit.
7. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
8. STOP on scientific ambiguity, missing required artifacts, destructive actions or explicit stop gates.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Stable target/runtime

Reference machine: Apple M1 / 8 GB unified memory.

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

Compatibility audit on frozen tap corpus:
- `LOOM_DFLASH_TARGET_COMPATIBILITY_AUDIT_001_PASS`;
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target rank min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

Target identity:
- `LOOM_DFLASH_TARGET_IDENTITY_AUDIT_001`: `IDENTITY_MATCH_EXCEPT_QUANTIZATION`;
- architecture/config/tokenizer/vocab/special-token/d2t-t2d checks PASS;
- local material delta: MLX affine 4-bit, group 128, 386 quantized triplets;
- exact historical DFlash-era verifier revision remains unpinned.

## Unquantized-control preflight

`LOOM_DFLASH_UNQUANTIZED_CONTROL_PREFLIGHT_001` = `CONDITIONAL_PREFLIGHT_DISK_AND_ADAPTATION_REQUIRED`.

Pinned upstream BF16 control candidate:
- revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`;
- 16 BF16 safetensors shards + index;
- total 61,066,575,648 B;
- full snapshot NOT authorized;
- bounded range/shard staging only.

Public provenance: current upstream BF16 shard objects/tokenizer trace to original upload commit `fd4bf3b`; DFlash does not pin an exact verifier revision. Treat this as a pinned upstream BF16 control, not an exact historical-training replica.

## Q4 tap replay provenance invariant

Initial `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` attempt stopped as `CONTROL_ADAPTER_PARITY_FAIL` before BF16 access because current MLX 0.32.0 replay did not bitwise equal the frozen `P1_t01` taps, although adapter vs current Q4 oracle, router, logits and greedy token all matched.

`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001` classified `MECHANICAL_REPLAY_MISMATCH_REPAIRED`.

Exact state/capture identity:
- `P1_t01`, context 43;
- token-prefix SHA-256 `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- positions 0..42; anchor position 42; token 271;
- float32 `[5,43,2048]`;
- taps `[1,12,23,34,45]` 1-based post-block;
- model/config/scripts unchanged; all four Q4 shards match download-manifest hashes.

Root cause:
- frozen evidence was captured under MLX 0.31.2 (`results-local/mlx/venv-mlx-lm-0.31.3`);
- failed replay used MLX 0.32.0;
- first tap difference: layer 1 post-block, 55,514/88,064 elements, max abs `2.3841858e-07`;
- earliest localized difference: layer 1 / position 0 / expert 116 SwiGLU, 157/768 elements, max abs `2.9802322e-08`; gate/up projections bitwise equal;
- router/final-logit/greedy behavior remained exact.

Mechanical repair:
- replay with freeze-time MLX 0.31.2 only;
- no code/model/prefix/position/capture change;
- frozen tap parity restored to **5/5 bitwise**;
- independent exact-oracle rerun confirms parity;
- router logits 48/48 bitwise, final logits bitwise, greedy token 12050, finite/no leak PASS.

Interpretation:
- no persistent Q4 hidden-state drift is established;
- frozen tap corpus does not require refreezing from this diagnostic;
- runtime/library version is part of frozen-state provenance;
- BF16/quantization has still not been tested.

## Next checkpoint

Resume `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` under the pinned freeze-time runtime MLX 0.31.2.

One-factor gate:
1. run the bounded control adapter with local/dequantized Q4 values under MLX 0.31.2;
2. require 5/5 frozen taps bitwise, router 48/48 bitwise, final logits bitwise and greedy parity;
3. only then switch the weight source to pinned upstream BF16 tensors;
4. keep runtime, prefix, code path, capture semantics and comparison logic fixed.

BF16 comparison remains bounded to `P1_t01` and must report post-block taps `[1,12,23,34,45]`, final normalized hidden, router logits/top-k/weights, full logits, greedy top1/margin/top5 overlap, and max/mean abs, RMSE, relative-L2, cosine.

Restrictions:
- no full 61-GB snapshot;
- bounded range/shard staging only;
- no DFlash E2E;
- no target/drafter/mapping/acceptance changes;
- no memory/performance remediation;
- no quantization-causality claim from a single state.

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
