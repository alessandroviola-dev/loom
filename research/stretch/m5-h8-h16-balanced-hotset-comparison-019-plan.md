# LOOM Stretch 019 — Balanced M5 H8 vs H16 Hotset Comparison

Date: 2026-08-20
Status: READY

## Objective

Measure whether doubling persistent transformer residency from 8 layers to 16 layers improves the already-frozen exact `M=5` oracle target path on the Apple M1 / 8 GB reference system.

Stretch 018 established that, under balanced conditions, M5 has a higher pooled target-verification rate than M4 by approximately 9.8%. The block-size axis is therefore frozen at M5 for this experiment.

Question:

> With M=5 and all model/runtime/KV/parity policy unchanged, does persistent hotset H16 reduce target traversal cost enough to outperform H8 without violating the resource envelope?

## Frozen baseline

Preserve exactly:
- Apple M1 / 8 GB reference system
- Qwen3-8B 3-bit/group64 artifact
- mlx `0.31.2`
- mlx-lm `0.31.3`
- transformers `5.12.1`
- M=5 exact oracle geometry from Stretch 017
- resident sequential control
- ordinary BF16 KV cache
- 15-token frozen oracle prefix
- 3 x 5-token target traversals
- exact numerical parity and top-1 gates
- streamed shared stages
- Darwin process-I/O attribution
- launch/resource guardrails
- file-backed child transport
- no tokenizer / sampling / real drafter
- no KV quantization
- no prefetch/double buffering
- no runtime upgrade
- no deliberate cache purge
- no model download.

Frozen H8 source:
- `scripts/stretch_five_token_oracle_block_confirmation_017.py`
- blob `6171440736badf5150297f9c8945209fe49d0826`.

H16 helper:
- `scripts/stretch_five_token_h16_hotset_variant_019.py`
- blob `6a0bd001ad7a5a5bf5646b54a302f7fc372e4367`.

Balanced comparison runner:
- `scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py`
- blob `8ad0666624069d4852daed1188d634806b570ecc`.

## Scientific factor

Only persistent transformer residency changes:

H8:
- persistent layers `0..7`
- expected raw hotset payload `675,418,112 B`.

H16:
- persistent layers `0..15`
- expected raw hotset payload `1,350,836,224 B`.

All layers outside the hotset remain streamed exactly as in the inherited path.

The expected raw-weight budget if the largest newly materialized shared stage remains `272,269,312 B` is approximately:
- H8: `947,687,424 B`
- H16: `1,623,105,536 B` (~1.51 GiB).

These are derived expectations; the runtime summaries remain authoritative.

## Balanced order

Run four independent inherited experiments:

`H8 -> H16 -> H16 -> H8`

No deliberate macOS cache purge is allowed between runs.

The ABBA order reduces simple first/last host-cache ordering bias. It does not imply perfectly identical page-cache state.

## Constituent validity gates

Every H8/H16 constituent must independently:
- exit successfully
- reach inherited `FIVE_TOKEN_ORACLE_BLOCK_CONFIRMATION_PASS`
- preserve oracle block size 5
- accept all 15 oracle tokens
- pass all inherited numerical/top-1/KV/resource/I-O gates
- expose the exact expected hotset layer IDs for its assigned variant
- expose persistent hotset and hybrid raw-weight residency accounting.

If any constituent fails, Stretch 019 is:

`HOTSET_COMPARISON_INCOMPLETE`

and no H8/H16 performance winner may be inferred from the partial sequence.

Do not weaken the host gate or runtime abort threshold to complete the experiment.

## Primary measurements

Pool the two valid runs for each variant and compare:
- accepted-token target verification token/s
- median target-block wall
- median transformer materialization wall
- median transformer forward wall
- mean/median full-pass process-read bytes per block
- mean materialization process-read bytes per block
- process-read bytes per accepted token
- observed persistent hotset bytes
- hybrid simultaneous raw-weight budget
- minimum observed free memory
- peak observed swap.

Primary performance ratio:

`H16 pooled target-verification tok/s / H8 pooled target-verification tok/s`

## PASS classification

`M5_H8_H16_BALANCED_HOTSET_COMPARISON_PASS`

requires all four constituent runs to pass and the normalized comparison to be emitted.

A PASS does not require H16 to be faster; a valid slower H16 result is scientifically useful.

## Interpretation rules

If H16 is faster:
- freeze the measured residency gain;
- inspect whether gain tracks reduced materialization time/process reads;
- consider one further bounded residency point only if resource headroom remains scientifically adequate.

If H16 is equal/slower:
- do not assume more residency is beneficial;
- inspect forward/materialization/read ratios and resource pressure;
- choose the next independent axis from prefetch/double-buffering or a separately preregistered runtime experiment.

If H16 triggers inherited resource/host-state failure:
- preserve it as a resource-boundary observation;
- do not weaken gates;
- do not classify a partial H8/H16 comparison as a performance result.

## Non-claims

- This is still oracle target-side verification, not deployable speculative decoding.
- No draft-model latency, acceptance loss, rejection or rollback is represented.
- Darwin process-read accounting is diagnostic, not forensic SSD tracing.
- H16 changes residency only; it does not change quantized kernels or solve the M>=6 numerical boundary.
- The ~20 token/s interactive promotion target is unchanged.

## Exact next step

```bash
cd "<repository-root>"
git pull --ff-only
python3 -m py_compile scripts/stretch_five_token_h16_hotset_variant_019.py
python3 -m py_compile scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py
python3 scripts/stretch_m5_h8_h16_balanced_hotset_comparison_019.py
```

No download is expected.
