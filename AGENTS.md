# LOOM — Pi Agent Protocol

Version: 3.0
Mode: `TOKEN_EFFICIENT / BOUNDED_EXECUTION`

This file is persistent context for Pi. Prompts contain only the active WP delta.

## Role split

Pi owns local technical execution only: inspect relevant local code/runtime, implement the minimum WP code, run tests/benchmarks, create `results-local/` evidence, and mechanically self-correct inside scope.

ChatGPT owns scientific direction, Git/GitHub synchronization, `HANDOFF.md`, `ROADMAP.md`, research result documents and project-state administration.

Pi must NOT run Git, edit HANDOFF/ROADMAP, open/merge/push PRs, or create project documentation unless explicitly authorized by the WP.

## Scientific rules

1. Read this file, then only exact files/evidence relevant to the WP.
2. Use targeted search; do not rescan the repo without need.
3. Preserve one-factor experiments, deterministic inputs, provenance and explicit gates.
4. Treat runtime/library version as an experimental variable whenever exact hidden-state parity matters.
5. Distinguish measured fact, inference, hypothesis and unverified limit.
6. Mechanical failures may be repaired inside scope; failed scientific treatments may not be silently rescued.
7. STOP on scientific ambiguity, missing required artifacts, destructive actions or explicit stop gates.
8. Do not optimize memory/performance while the active scientific blocker is unresolved unless optimization is explicitly required for feasibility.

Loop: `OBSERVE -> EXECUTE -> VERIFY -> DIAGNOSE -> CORRECT(mechanical only) -> CHECKPOINT`.

## Expensive-run retention rule

Before any run that is expensive in network, compute time, or difficult-to-reproduce remote data, create a retention plan before execution.

The retention plan must identify:
- estimated cost/time/network volume;
- expensive intermediate artifacts that future work may need;
- which artifacts are retained;
- exact storage location;
- hashes/provenance required for reuse;
- resumability/cache behavior where practical.

An expensive run must not be considered complete if required retained artifacts were only transient.

Reusable immutable remote/model-derived payloads should be cached when doing so prevents material repeated cost and does not change scientific semantics.

External LOOM research storage currently available:
`<external-archive>/`

Persistent BF16 cache:
`<external-archive>/bf16-cache/`

Persistent research artifacts:
`<external-archive>/artifacts/`

The operational local Q4 target remains on the Mac internal SSD; do not move serving/runtime-critical model files to the HDD unless a future WP explicitly authorizes it.

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
- `LOOM_DFLASH_TARGET_INTERFACE_001_PASS`;
- `LOOM_DFLASH_B7_WAVEFRONT_VERIFIER_001_PASS`;
- `LOOM_DFLASH_DRAFTER_PORT_001_PASS`: all 680,813,824 learned BF16 drafter params mapped;
- publisher anchor/block attention mask repaired;
- `LOOM_DFLASH_MASKED_REFERENCE_PARITY_001_PASS`: corrected publisher reference proposal parity 63/63, deterministic/finite.

First E2E:
- `LOOM_DFLASH_GREEDY_E2E_001_FAIL_GATE`;
- target committed behavior exact;
- acceptance 0/96;
- DFlash 0.1544 tok/s vs control 0.7735 tok/s;
- swap +737.43 MiB.

Frozen continuation:
- `LOOM_DFLASH_TARGET_CONTINUATION_FREEZE_001_PASS`;
- historical overlap 45/45;
- complete 63/63 token reference;
- SHA-256 `0a8eda21e7074e49f6e6c0c01b5e2c20b429935a9029457319b9b7c631946dea`.

Compatibility audit:
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

## BF16 control provenance

Pinned upstream BF16 control:
- revision `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`;
- 16 BF16 safetensors shards + index;
- total full snapshot 61,066,575,648 B;
- full snapshot NOT authorized;
- bounded range/shard staging only.

Treat this as a pinned current-upstream BF16 control, not an exact historical-training replica.

Freeze-time exact runtime for P1_t01 comparisons:
`results-local/mlx/venv-mlx-lm-0.31.3` / MLX exactly `0.31.2`.

`LOOM_DFLASH_Q4_TAP_REPLAY_DRIFT_DIAG_001` established that MLX 0.32.0 caused tiny replay drift; MLX 0.31.2 restores frozen tap/router/logit/token parity. Runtime/library version is part of frozen-state provenance.

## P1_t01 BF16 vs Q4 control — COMPLETE

`LOOM_DFLASH_UNQUANTIZED_TARGET_P1T01_RANGE_CONTROL_001` = `PASS`.

Frozen state:
- `P1_t01`, context 43;
- prefix SHA-256 `7ec7658fa9f4ce945144d9627c57b65a20d993e39f193093069ab105c79a176f`;
- anchor position 42, token 271.

Gate A Q4 under MLX 0.31.2:
- taps 5/5 bitwise;
- routers 48/48 bitwise;
- final logits bitwise;
- greedy token 12050;
- deterministic/finite/no-leak PASS.

Gate B Q4 -> pinned BF16:
- 3,470 BF16 layer-expert pairs;
- expert payload `32,747,028,480 B`;
- dense cache 435 tensors / `3,082,186,752 B`;
- peak dedicated disk `3,091,655,835 B`;
- deterministic/finite/no-leak PASS.

Measured Q4 vs BF16:
- first router divergence layer 0, position 1;
- identical full-prefix router top-k layers `0/48`;
- tap relative-L2 `[1,12,23,34,45]`: `0.114863, 0.345792, 0.310635, 0.198639, 0.274675`;
- final hidden relative-L2 `0.270665`, cosine `0.964671`;
- final logits relative-L2 `0.336189`, cosine `0.957269`;
- Q4 top1 = BF16 top1 = `12050`;
- top-5 overlap `4/5`.

Interpretation remains `NOT_CAUSAL`: precision materially changes internal target distributions, but this one state did not establish that quantization caused DFlash incompatibility.

## BF16 persistent cache / retained artifacts

During the follow-up probe, exact BF16 artifacts were re-extracted and retained permanently.

External cache final state:
- `3,470` routed expert entries retained;
- routed experts ~31 GiB;
- dense ~2.9 GiB;
- ~33 GiB total;
- initial cache build network payload `32,747,028,480 B`;
- subsequent full re-extraction: `3,470` HDD hits, `0 B` network, `0` retries.

Retained exact BF16 artifacts include:
- five float32 target taps, aggregate shape `[5,43,2048]`;
- tap hashes/provenance;
- exact final-anchor BF16 logits;
- validation tying them to the completed control.

Future P1_t01 BF16 work must reuse these retained artifacts/cache rather than repeat remote acquisition without cause.

## BF16 tap drafter probe — COMPLETE

`LOOM_DFLASH_BF16_TAP_DRAFTER_PROBE_001` = `NO_MATERIAL_RECOVERY`.

Report:
`research/architecture/loom-dflash-bf16-tap-drafter-probe-001-result.md`

Evidence:
- local: `results-local/research/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`;
- external: `<external-archive>/artifacts/dflash-bf16-tap-drafter-probe-001/20260825T084409Z/`.

One-factor intervention:
- baseline = exact frozen Q4 target taps;
- treatment = exact retained BF16 target taps;
- unchanged drafter weights/mapping/mask/anchor/proposal path/scoring.

Results:
- Q4-tap proposal `1778`, BF16-target rank `41641`, top5/top10/top50 false;
- BF16-tap proposal `1778`, BF16-target rank `41641`, top5/top10/top50 false;
- Q4->BF16 drafter-logit movement: max abs `2.72215`, mean abs `0.343385`, RMSE `0.432349`, relative-L2 `0.215100`, cosine `0.977013`;
- both conditions deterministic and finite;
- mask bitwise equal; only tap hashes differ.

Interpretation:
- BF16 taps materially alter drafter logits, so tap precision does affect drafter internals;
- however it produces no proposal-token, rank, or top-k recovery;
- simple target-tap precision drift is therefore not sufficient to explain/repair P1_t01 DFlash incompatibility.

Critical observation:
- target token `12050` is absent from the current drafter mapped ~32k output support;
- exact target-token proposal is therefore structurally unavailable on P1_t01 through the current mapping, independent of Q4 vs BF16 taps;
- prevalence across the 63 frozen states is not yet known.

## Next checkpoint

`LOOM_DFLASH_OUTPUT_SUPPORT_COVERAGE_AUDIT_001`

Goal: perform a static, cheap audit of the validated drafter output mapping against all 63 frozen target next tokens.

Required:
1. prove mapping provenance/uniqueness and exact target-vocab interpretation;
2. for each frozen state, determine whether its exact target next token is representable by drafter output support;
3. report representable/63 and unsupported/63;
4. list unsupported state IDs/tokens;
5. partition the existing 0/63 proposal compatibility evidence by representable vs unsupported states;
6. do not run BF16 forwards, DFlash E2E, or model downloads.

Interpretation:
- large unsupported fraction -> output-support coverage becomes a major structural explanation requiring resolution before DFlash salvage;
- most/all representable -> P1_t01 support absence is local/minority and other training/interface/distribution hypotheses remain primary.

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

Everything not changed by the WP inherits this file. Original model files are immutable. Raw evidence stays under `results-local/<area>/<checkpoint>/<UTC>/` with exact provenance; expensive retained artifacts may additionally live under the declared external LOOM storage root.
