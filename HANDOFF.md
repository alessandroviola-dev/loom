# LOOM — Active Handoff

Last updated: 2026-08-25
Status: ACTIVE — bounded P1_t01 BF16 vs Q4 control COMPLETE; material internal precision drift measured, greedy top1 unchanged; next isolate whether BF16 target taps improve DFlash proposal compatibility
Repository: `Ilcoach/loom`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`
Next core checkpoint: `LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

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

## Frozen target compatibility

Frozen continuation reference:
- 45/45 historical overlap;
- complete 63/63 token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit on frozen target-tap states:
- target replay/control 63/63;
- drafter/target top1 0/63;
- top5/top10/top50 all 0/63;
- proposal target ranks min/P50/mean/max 987 / 14,195 / 28,621.08 / 146,487;
- accepted prefixes all zero;
- verdict `INCOMPATIBLE_ON_FROZEN_TARGET_PREFIXES`.

## Target identity / BF16 provenance

Target identity audit:
`IDENTITY_MATCH_EXCEPT_QUANTIZATION`.

No material architecture/tokenizer/vocab/mapping mismatch was found. Local material delta remains MLX affine 4-bit, group 128.

Pinned upstream BF16 control:
- revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`;
- 16 BF16 safetensors shards + index;
- total full snapshot `61,066,575,648 B`;
- full snapshot NOT authorized;
- bounded range/shard staging only.

Public provenance does not establish an exact historical DFlash-training verifier revision. Treat BF16 as a pinned current-upstream control, not a historical training replica.

## Runtime provenance repair — complete

`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001` classified `MECHANICAL_REPLAY_MISMATCH_REPAIRED`.

Frozen `P1_t01` state:
- 43 tokens;
- prefix SHA-256 `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- positions 0..42;
- anchor position 42, token 271;
- float32 `[5,43,2048]` taps `[1,12,23,34,45]`.

Root cause of earlier replay mismatch:
- frozen evidence: MLX 0.31.2;
- failed replay: MLX 0.32.0.

Under freeze-time environment `results-local/mlx/venv-mlx-lm-0.31.3` / MLX 0.31.2:
- frozen taps 5/5 bitwise;
- router 48/48 bitwise;
- final logits bitwise;
- greedy token 12050;
- deterministic/finite/no-leak PASS.

Runtime/library version is part of frozen-state provenance.

## P1_t01 BF16 vs Q4 control — COMPLETE

Checkpoint:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001`

Classification:
`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001_PASS`

Report:
`research/architecture/loom-dflash-unquantized-target-p1t01-range-control-001-result.md`

Completed evidence:
`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T212818Z/`

Primary evidence:
- `summary.json`;
- `bf16-control.json`;
- `progress.json`.

Transport selection evidence:
`results-local/research/dflash-unquantized-target-p1t01-range-control-001/20260824T212313Z/transport-microbenchmark-aggregate.json`

### Gate A — adapter/Q4 parity

Under MLX 0.31.2:
- frozen taps 5/5 bitwise;
- router 48/48 bitwise;
- final logits bitwise;
- greedy token 12050;
- deterministic/finite/no-leak PASS.

Therefore the adapter/capture path was not an uncontrolled variable in Gate B.

### Gate B execution

Only the target weight source changed from local Q4 values to pinned upstream BF16 values.

Execution:
- BF16 layer-expert pairs completed: `3,470`;
- expert payload fetched: `32,747,028,480 B`;
- dense cache reused: 435 tensors / `3,082,186,752 B`;
- no dense redownload;
- network retries: `13`;
- exhausted network failures: `0`;
- peak dedicated disk: `3,091,655,835 B` (<12 GiB);
- wall time: `5,888.0 s`;
- deterministic rerun: PASS;
- finite: PASS;
- no routed-expert leak: PASS.

Mechanical feasibility changes only:
- expert-major execution;
- persistent pooled HTTPS;
- 64 MiB maximum coalesced ranges selected by transport microbenchmark;
- ephemeral expert staging;
- no scientific model/math/capture/gate change.

### Scientific measurements

Router:
- first divergence: layer 0, position 1;
- full-prefix Q4/BF16 router top-k identical layers: `0/48`.

Required DFlash target-tap relative-L2 at post-block `[1,12,23,34,45]`:
- layer 1: `0.114863`;
- layer 12: `0.345792`;
- layer 23: `0.310635`;
- layer 34: `0.198639`;
- layer 45: `0.274675`.

Final normalized hidden:
- relative-L2 `0.270665`;
- cosine `0.964671`.

Final logits:
- relative-L2 `0.336189`;
- cosine `0.957269`.

Final token behavior:
- Q4 top1 = `12050`;
- BF16 top1 = `12050`;
- top1 parity PASS;
- Q4 top1/top2 margin `12.90015`;
- BF16 top1/top2 margin `11.875`;
- top-5 overlap `4/5`.

## Scientific interpretation

Measured fact:
- changing only the target weight source Q4 -> pinned BF16 materially changes the internal target hidden states, MoE routing and final logit distribution on frozen `P1_t01`;
- the drift appears essentially immediately and is substantial at all five DFlash-consumed taps;
- despite this, the greedy next token remains `12050` under both Q4 and BF16.

Implication:
- simple next-token instability is not established on this state;
- target precision/hidden-state distribution shift remains a serious mechanistic hypothesis because DFlash consumes the internal tap tensors, not only the final greedy token.

Limit:
`NOT_CAUSAL`.

This checkpoint does NOT establish that quantization caused the earlier 0/63 DFlash compatibility failure because:
- only one frozen state was tested;
- BF16 is a pinned current-upstream control, not a proven exact historical training verifier;
- no intervention has yet shown that substituting BF16 taps into the unchanged drafter improves proposal compatibility.

## Exact next step

Checkpoint:
`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001`

Goal:
isolate whether the measured Q4/BF16 target-tap distribution shift actually changes DFlash proposal compatibility on the same frozen `P1_t01` state.

One-factor intervention:
1. use the unchanged, already validated DFlash drafter;
2. preserve drafter weights, mapping, publisher mask, anchor semantics and proposal path;
3. establish/replay the validated Q4-tap proposal baseline;
4. replace only the five target tap tensors `[1,12,23,34,45]` with the completed BF16 control taps;
5. compare Q4-tap-driven vs BF16-tap-driven drafter proposal token/logits and target rank/top-k compatibility against the pinned BF16 target distribution for the same state.

Required interpretation:
- material compatibility recovery under BF16 taps -> precision-induced tap distribution shift becomes a strong mechanistic contributor; preregister broader frozen-state confirmation before causal promotion;
- no material recovery -> simple target-tap precision drift becomes less likely to explain the catastrophic DFlash failure; reopen training/interface/distribution hypotheses.

Restrictions:
- no DFlash E2E;
- no retraining/remapping;
- no target weight-source change inside this WP beyond use of already captured BF16 target evidence;
- no acceptance/memory/performance remediation;
- no broader state sweep;
- no causal claim from one state.

## Later order

1. BF16-tap drafter probe on `P1_t01`;
2. broader preregistered frozen-state confirmation only if the one-state intervention materially recovers compatibility;
3. decide whether precision drift can explain enough of DFlash incompatibility to justify salvage;
4. memory remediation only after useful acceptance is supported;
5. full E2E economics/capability/context if DFlash becomes viable;
6. otherwise return to the next high-leverage LOOM architecture/I/O branch.
