# Stretch 011 — Materialization I/O Attribution — Preregistered Plan

Date: 2026-08-19
Status: READY AFTER RUNNER FREEZE

## Purpose

Stretch 010 established 16-token numerical/autoregressive stability but exposed a large timing regime change in the streamed transformer weight-materialization path:
- tokens 1–4: ~0.19–0.21 s total 36-layer materialization
- tokens 8–16: ~1.40–1.44 s
- 36-layer forward remains ~0.19 s/token.

Timing alone cannot distinguish page-cache/physical-I/O effects from MLX/allocator/materialization effects.

Stretch 011 is an **instrumentation-only replication** of the exact Stretch 010 scientific workload. Its purpose is to measure Darwin per-process resource counters around streamed weight-selection/materialization boundaries and determine whether the timing transition coincides with increased disk-read bytes and/or page-ins.

## Frozen upstream

Stretch 009 source:
`scripts/stretch_four_token_kv_autoregressive_parity_009.py`
blob `3e0780850bb65f9dccf07946f89597fa2e4d17e1`.

Stretch 010 transform:
`scripts/stretch_sixteen_token_autoregressive_stability_010.py`
blob `ff3dc83abc6388113fca15594eef6b3ec00ebe50`.

Stretch 010 valid result:
`research/stretch/sixteen-token-autoregressive-stability-010-result.md`.

## Scientific workload — UNCHANGED

The runner must reproduce the exact transformed Stretch 010 workload:
- Qwen3-8B 3-bit/group64
- mlx 0.31.2 / mlx-lm 0.31.3 / transformers 5.12.1
- frozen prompt token IDs `[[1,42,2048,151935]]`
- deterministic argmax
- 16 generated/feedback tokens
- ordinary BF16 36-layer `KVCache`
- official fully resident control
- phase-streamed embedding -> 36 transformer layers -> final RMSNorm -> LM head
- same cache/parity/materialization gates
- same host launch gate and runtime guardrail
- no tokenizer
- no sampling
- no KV quantization
- no prefetch/double buffering
- no new model/download
- no cache purge or artificial OS cache manipulation.

Primary scientific correctness must still satisfy every Stretch 010 inherited gate and produce the same resident/streamed sequence for that run.

## New instrumentation only

On Darwin, use `proc_pid_rusage(pid, RUSAGE_INFO_V2, ...)` through `/usr/lib/libproc.dylib`.

The frozen Darwin `rusage_info_v2` fields used are:
- `ri_pageins`
- `ri_resident_size`
- `ri_phys_footprint`
- `ri_diskio_bytesread`
- `ri_diskio_byteswritten`.

`RUSAGE_INFO_V2` flavor is 2.

These counters are cumulative process resource accounting. Deltas will be computed around phases.

### Transformer layer boundaries

For every streamed transformer layer in prompt and token passes, sample:
1. before `build_block()` / weight selection
2. after `build_block()` and before `mx.eval(block.parameters())`
3. immediately after `mx.eval(block.parameters())`.

Record:
- build/select disk-read delta
- build/select page-in delta
- materialization disk-read delta
- materialization page-in delta
- existing materialization wall
- existing forward wall.

The main attribution question concerns the materialization interval because Stretch 010's timing increase occurs in the existing `mx.eval(block.parameters())` timer.

### Shared stages

Capture equivalent before/select/materialize resource snapshots for embedding and LM head, and lightweight snapshots for final norm where practical.

### Pass-level accounting

For prompt and every one of the 16 feedback passes record:
- cumulative resource snapshot at pass start/end
- total process disk-read delta
- total page-in delta
- full-pass wall
- summed transformer materialization disk-read/page-in deltas
- summed transformer build/select disk-read/page-in deltas.

## Derived diagnostics

For the 16 streamed feedback tokens report arrays for:
- 36-layer materialization wall seconds
- full-pass wall seconds
- transformer materialization disk-read bytes
- transformer materialization page-ins
- transformer build/select disk-read bytes
- full-pass process disk-read bytes
- full-pass page-ins.

Also report early tokens 1–4 vs late tokens 8–16 descriptive means.

A Pearson correlation between layer-materialization wall and materialization disk-read bytes may be reported diagnostically if all values are available. It is not a causal gate.

## Interpretation boundaries

A rise in `ri_diskio_bytesread` concurrent with materialization slowdown would support the inference that the process is performing more actual disk I/O during the slow regime. It would not prove that every counted byte belongs to model weights unless separately traced by file.

Flat disk-read/page-in counters despite higher materialization wall would argue against a simple physical-I/O explanation and motivate MLX/allocator/materialization profiling.

Do not call `ri_diskio_bytesread` a guaranteed exact SSD-byte count for the model file. Do not infer device throughput by dividing model payload by time unless the measured per-process disk-read delta supports that interpretation.

Do not purge macOS caches to manufacture a cold-cache state in this experiment.

## Failure classifications

- `MATERIALIZATION_IO_ATTRIBUTION_PASS`
- `IO_TELEMETRY_PREFLIGHT_FAIL`
- inherited Stretch 010 correctness/resource classifications
- `RUNTIME_FAIL`
- `TELEMETRY_FAIL`
- `PARTIAL_RESOURCE_FAIL`.

An I/O telemetry/harness failure is not a model or streaming-concept failure.

## Primary PASS

`MATERIALIZATION_IO_ATTRIBUTION_PASS`

requires:
- inherited 16-token correctness/parity/cache/weight gates PASS
- Darwin I/O telemetry available
- complete attribution records for all 16 feedback passes and all 36 transformer layers per pass.

No threshold on disk-read bytes is required for PASS; the experiment measures which regime actually occurs.

## Decision rule after result

- If slow tokens coincide with large materialization `ri_diskio_bytesread` / page-in deltas: next experiment should address storage/page-cache behavior explicitly before tokenizer integration.
- If slowdown occurs without corresponding I/O/page-in increase: investigate MLX allocation/materialization lifecycle separately.
- If no slowdown reproduces: classify the Stretch 010 timing transition as host/cache-state dependent and repeat only if needed before optimization.

Tokenizer/text integration remains queued until this new performance boundary is characterized.