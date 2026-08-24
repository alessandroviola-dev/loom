# LOOM Roadmap

Last updated: 2026-08-24
Current checkpoint: `LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001_MECHANICAL_REPLAY_MISMATCH_REPAIRED`
Strategic next: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

## Mission

Run ~27B/32B-class local AI on Apple M1 / 8 GB with practical speed, exactness and reproducible bounded experiments.

Canonical long-lived context is in `/AGENTS.md`.

## Proven DFlash chain

- target tap interface `[1,12,23,34,45]` established;
- exact B7 wavefront verifier;
- complete MLX drafter port;
- publisher anchor/block mask repaired;
- independent masked publisher reference PASS;
- corrected MLX/reference proposal parity 63/63.

First E2E:
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Memory/performance remediation remains deferred while acceptance is zero.

## Frozen-state compatibility history

Frozen target continuation:
- independent-oracle historical overlap 45/45;
- complete 63/63 target token reference;
- deterministic/finite;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on frozen target-tap states:
- target token replay/control 63/63 PASS;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target ranks structurally distant;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

## Target identity / BF16 preflight

Identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

No material non-quantization architecture/tokenizer/vocab/mapping mismatch was found. Local material delta is MLX affine 4-bit, group 128.

Unquantized-control preflight:
- pinned upstream BF16 control candidate identified;
- 16 shards, ~61.1 GB total;
- full snapshot rejected because it exceeds available/staging disk budget;
- bounded range/shard control designed;
- BF16 reader/math adapter required.

## Q4 tap replay mismatch — mechanical runtime provenance

The first `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` attempt stopped before BF16 access because the MLX 0.32.0 replay did not bitwise reproduce the earlier frozen `P1_t01` taps.

`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001` classified:
`MECHANICAL_REPLAY_MISMATCH_REPAIRED`.

Exact state/capture identity was proven:
- 43-token `P1_t01` prefix;
- SHA-256 `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- positions 0..42, anchor 42/token 271;
- float32 `[5,43,2048]`;
- taps `[1,12,23,34,45]` 1-based post-block;
- model/config/scripts unchanged;
- all four Q4 shards match download-manifest hashes.

Cause:
- frozen taps: MLX 0.31.2;
- failed replay: MLX 0.32.0.

Observed numerical delta:
- first tap mismatch layer 1;
- 55,514/88,064 elements differ;
- max abs `2.3841858e-07`;
- earliest localized difference layer 1 / position 0 / expert 116 SwiGLU;
- 157/768 differing elements, max abs `2.9802322e-08`;
- gate/up projections bitwise equal.

Downstream controls remained stable:
- router logits exact;
- final logits exact;
- greedy token 12050.

Repair:
- replay with freeze-time environment `results-local/mlx/venv-mlx-lm-0.31.3` / MLX 0.31.2;
- no code/model/prefix/position/capture change.

Post-repair:
- frozen taps 5/5 bitwise;
- independent exact-oracle confirmation PASS;
- router 48/48 bitwise;
- final logits bitwise;
- deterministic/finite/no-leak PASS.

Therefore:
- no persistent Q4 hidden-state drift is established;
- frozen tap corpus remains valid/reproducible under its pinned runtime provenance;
- no refreeze or compatibility rerun is required solely because of this runtime-version effect;
- BF16/quantization remains untested.

## Next — resume bounded P1_t01 BF16 control

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Pin runtime to freeze-time MLX 0.31.2.

Gate A:
1. use the new bounded adapter with local/dequantized Q4 values;
2. require 5/5 frozen taps bitwise;
3. require 48/48 router logits bitwise;
4. require final logits and greedy token bitwise;
5. deterministic/finite/no-leak PASS.

Only if Gate A passes:
- switch only the weight source to pinned upstream BF16 tensors;
- keep runtime, prefix, adapter, capture semantics and comparison logic fixed.

Compare for `P1_t01`:
- post-block taps `[1,12,23,34,45]`;
- final normalized hidden;
- 48-layer router logits/top-k/weights;
- full logits;
- greedy top1, top1/top2 margin, top5 overlap;
- max/mean abs, RMSE, relative-L2, cosine.

Restrictions:
- bounded range/shard staging only;
- no full ~61-GB BF16 snapshot;
- no DFlash E2E;
- no target/drafter/mapping/acceptance changes;
- no memory/performance remediation;
- no causal quantization claim from one state.

## Decision after control

- adapter gate FAIL under MLX 0.31.2 -> debug adapter only;
- adapter PASS + substantial BF16/Q4 hidden-state/router/logit divergence -> direct evidence for precision/weight drift, requiring broader confirmation before causal promotion;
- adapter PASS + BF16/Q4 states remain close -> reject simple Q4 hidden-state drift as sufficient explanation and reopen the next DFlash training/interface hypothesis;
- memory optimization resumes only after a supported route to useful acceptance exists.

## Later order

1. P1_t01 bounded BF16 control under pinned runtime;
2. broader confirmation if needed;
3. decide DFlash salvageability;
4. memory remediation only after useful acceptance;
5. full E2E economics/capability/context if viable;
6. otherwise return to next high-leverage LOOM architecture/I/O branch.

## Token-efficient Pi workflow

Root `/AGENTS.md` is persistent context. Pi prompts carry only the active delta. Pi executes local work; ChatGPT owns Git/HANDOFF/ROADMAP.
