# LOOM — Active Handoff

Last updated: 2026-08-24
Status: ACTIVE — Q4 frozen-tap replay mismatch localized to MLX runtime-version provenance and repaired; bounded BF16 control ready to resume under freeze-time MLX 0.31.2
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001_MECHANICAL_REPLAY_MISMATCH_REPAIRED`
Next core checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB while preserving correctness, bounded memory and reproducible evidence.

Stable context lives in `/AGENTS.md`. Pi executes compact local WPs; ChatGPT owns Git/HANDOFF/ROADMAP and checkpoint administration.

## DFlash chain already proven

Candidate: `RedHatAI/Qwen3-30B-A3B-speculator.dflash`
Publisher target: `Qwen/Qwen3-30B-A3B`

Proven:
- target tap interface `[1,12,23,34,45]`;
- exact B7 wavefront target verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E remains rejected:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Do not optimize memory/performance while acceptance remains zero.

## Frozen target and compatibility

Frozen continuation reference:
- 45/45 historical overlap;
- complete 63/63 token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on frozen tap states:
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal ranks structurally far from target;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

## Target identity / BF16 preflight

Target identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

No material architecture/tokenizer/vocab/mapping mismatch was found. Local material delta remains MLX affine 4-bit (group 128).

BF16 preflight:
- pinned upstream control candidate available;
- full BF16 snapshot ~61.1 GB;
- full snapshot rejected due disk shortfall;
- bounded range/shard staging designed;
- no causal quantization claim yet.

## Q4 TAP REPLAY DRIFT DIAG — REPAIRED

Checkpoint:
`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001`

Classification:
`MECHANICAL_REPLAY_MISMATCH_REPAIRED`

Report:
`research/architecture/loom-dflash-q4-tap-replay-drift-diag-001-result.md`

Evidence:
`results-local/research/dflash-q4-tap-replay-drift-diag-001/20260824T164505Z/`

Runtime proof:
`results-local/research/dflash-q4-tap-replay-drift-diag-001/20260824T164128Z-mlx032-probe/`

Exact state identity:
- `P1_t01`;
- 43 tokens;
- prefix SHA-256 `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- positions 0..42;
- anchor 42, token 271;
- capture float32 `[5,43,2048]`;
- taps `[1,12,23,34,45]` as 1-based post-block outputs.

Model provenance:
- config/scripts unchanged;
- all four Q4 shards match download-manifest hashes.

Root cause:
- frozen taps were produced under MLX 0.31.2;
- failed range-control replay used MLX 0.32.0;
- first layer-1 tap difference max abs `2.3841858e-07`;
- earliest localized difference: layer 1 / position 0 / expert 116 SwiGLU, max abs `2.9802322e-08`;
- gate/up projections remained bitwise equal.

Despite those tiny hidden-state differences:
- router logits remained exact;
- final logits remained exact;
- greedy token remained 12050.

Repair:
- replay under freeze-time environment `results-local/mlx/venv-mlx-lm-0.31.3` / MLX 0.31.2;
- no code/model/prefix/position/capture changes.

Post-repair:
- frozen taps **5/5 bitwise**;
- independent exact-oracle confirmation PASS;
- router 48/48 bitwise;
- final logits bitwise;
- deterministic/finite/no-leak PASS.

Conclusion:
- runtime provenance mismatch, not persistent Q4 hidden-state drift;
- frozen tap corpus remains reproducible and does not need refreezing;
- BF16/quantization has still not been tested.

## Exact next step

Resume `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` under the freeze-time MLX 0.31.2 runtime.

Hard one-factor gate:
1. run control adapter with local/dequantized Q4 weights in MLX 0.31.2;
2. require 5/5 frozen-tap bitwise parity, 48/48 router parity, final-logit bitwise parity and greedy parity;
3. only after that gate passes may the weight source switch to pinned upstream BF16 tensors;
4. keep runtime, prefix, code/capture path and comparison logic fixed.

Then compare BF16 vs Q4 for `P1_t01` only:
- taps `[1,12,23,34,45]`;
- final normalized hidden;
- router logits/top-k/weights;
- full logits;
- greedy top1, margin, top5 overlap;
- max/mean abs, RMSE, relative-L2, cosine.

Restrictions:
- bounded range/shard staging only;
- no full BF16 snapshot;
- no DFlash E2E;
- no model/mapping/acceptance changes;
- no memory/performance remediation;
- no quantization-causality claim from a single state.

## Later order

1. resume P1_t01 BF16 one-factor control;
2. broader-state confirmation only if needed;
3. decide whether precision drift plausibly explains DFlash incompatibility and whether drafter is salvageable;
4. memory remediation only after useful acceptance;
5. full E2E economics/capability/context if DFlash becomes viable;
6. otherwise return to next high-leverage LOOM architecture/I/O branch.
