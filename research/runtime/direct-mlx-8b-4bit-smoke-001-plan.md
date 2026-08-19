# LOOM — Direct MLX 8B 4-bit Smoke 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the same Qwen3-8B family in a less aggressive native-MLX 4-bit quantization load and complete the frozen Direct MLX smoke at `max_kv_size=4096` on the reference Apple M1 / 8 GB machine while preserving LOOM's existing safety boundary?

This is a technical/safety probe only. It does not yet claim better coding quality.

## Motivation

Direct MLX Qwen3-8B-3bit completed the full frozen coding benchmark safely, but quality was not competitive enough for Pi promotion:
- delivery-adjusted 27.86/100;
- structured delivery 2/6;
- four protocol failures, with additional semantic defects visible on at least T04 and T06.

A 4-bit weight profile is therefore a prospectively motivated same-family test of the quality/memory frontier, not a post-hoc rescue of the completed 3-bit benchmark.

## Frozen environment

Reuse the validated isolated environment:
- Darwin arm64
- venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

No production Pi configuration is touched.

## Model artifact

Candidate:
- repository: `mlx-community/Qwen3-8B-4bit`
- pinned revision: `545dc4251c05440727734bcd94334791f6ab0192`
- base family: Qwen3-8B
- MLX quantization: 4 bits, group size 64
- main weight: `model.safetensors`
- published remote size: approximately 4.61 GB
- required SHA256: `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`

Local destination:
`results-local/mlx/models/Qwen3-8B-4bit`

This is not bit-identical to any GGUF profile and is not used to make causal claims about quantization algorithms across runtimes.

## Storage policy

1. Record disk free before acquisition.
2. Require at least 10 GiB free before a first acquisition attempt.
3. Acquire/reuse only the pinned snapshot.
4. Verify `model.safetensors` SHA256.
5. Verify config quantization metadata is 4-bit / group-size 64.
6. Record local model directory size and disk free after acquisition and runtime.
7. Never delete or overwrite a mismatching existing artifact automatically.
8. Retain all previously verified 3-bit/GGUF artifacts.

## Frozen smoke runtime

Keep the Direct MLX smoke policy identical to the safety-valid 3-bit smoke except for the model weight quantization:
- local model path / offline inference after acquisition;
- Qwen3 chat template;
- `enable_thinking=False`;
- prompt `Reply only with OK.`;
- direct `stream_generate`;
- `mx.random.seed(0)`;
- maximum generation 16 tokens;
- `max_kv_size=4096`;
- unquantized KV (`kv_bits=None`);
- one generation attempt;
- no retry/rescue in the same run.

The locale-safe macOS swap parser is required from the start.

## Telemetry

Continuously record:
- system free-memory percentage;
- swap used MB;
- child process RSS (diagnostic only);
- MLX-reported peak memory;
- prompt/generation tokens and tok/s;
- finish reason;
- generated text;
- wall time;
- disk free before/acquisition-after/final.

## Frozen safety guardrails

Abort the model process if either:
- system free memory < **5%**;
- swap used > **5600 MB**.

Missing/unparseable required memory/swap telemetry is a harness/telemetry failure, not a safety PASS.

## Classification

`FULL_PASS` requires:
- exact environment preflight;
- exact pinned artifact acquisition/reuse;
- SHA256 PASS;
- 4-bit / group-size 64 metadata PASS;
- numeric free-memory and swap telemetry;
- Direct MLX child exits 0;
- no guardrail breach;
- non-empty generated text;
- generation statistics captured.

Other classifications:
- `PREFLIGHT_FAIL`
- `DOWNLOAD_FAIL`
- `HASH_FAIL`
- `MODEL_METADATA_FAIL`
- `RESOURCE_FAIL`
- `TELEMETRY_FAIL`
- `RUNTIME_FAIL`
- `INVALID_HARNESS`

## Decision after smoke

If `FULL_PASS`:
1. freeze smoke telemetry;
2. preregister exact Coding Benchmark T01 workload-safety using the same 4-bit runtime;
3. only after T01 safety PASS run the full frozen Coding Benchmark 01;
4. compare 4-bit vs 3-bit quality descriptively under their frozen results before any Pi decision.

If `RESOURCE_FAIL`:
- do not lower the 5%/5600 MB guardrails;
- do not reduce `max_kv_size` inside this failed condition;
- do not quantize KV post-hoc inside this smoke;
- diagnose before considering a separately preregistered 4-bit rescue.

Pi remains blocked until technical, workload-safety and quality gates are all satisfied.
