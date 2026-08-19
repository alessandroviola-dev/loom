# LOOM — Direct MLX 8B 4-bit Coding Benchmark 001 Result

Date: 2026-08-19
Run: `20260819-133144`
Status: **PARTIAL_RESOURCE_FAIL — NO VALID QUALITY ORDERING**

## Frozen condition

- model `mlx-community/Qwen3-8B-4bit`
- pinned revision `545dc4251c05440727734bcd94334791f6ab0192`
- local weight SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- Direct MLX environment: `mlx-lm==0.31.3`, `mlx==0.31.2`, `transformers==5.12.1`
- exact Coding Benchmark 01 v1.0.1 T01–T06
- exact frozen adapter/scorer
- one loaded model session
- `enable_thinking=False`
- `max_kv_size=4096`
- unquantized KV
- max 2048 generation tokens/task
- seed 0
- no retry/repair/salvage/test feedback
- frozen safety abort: free memory <5% OR swap >5600 MB

Prospectively frozen quality gate required all of:
1. benchmark classification `COMPLETE`;
2. delivery-adjusted score >27.86/100;
3. structured delivery >2/6.

Because this run is not `COMPLETE`, the quality gate is not evaluable.

## Preflight

Observed:
- disk free before: **36.347 GiB**
- version lock: PASS
- model SHA256: PASS
- frozen adapter/scorer blobs: PASS
- benchmark v1.0.1 / 6 tasks: PASS
- frozen prompts T01–T06: PASS
- safety preflight: **56% free**, **948.75 MB swap**

## Runtime result

The continuous six-task Direct MLX session began T01.

Observed before abort:
- progress reached `[1/6] T01 running...`
- peak sampled process RSS: **459.453125 MB**
- peak observed swap: **3028.25 MB**
- minimum observed free memory: **4%**
- disk free after: **35.338 GiB**
- classification: **PARTIAL_RESOURCE_FAIL**

The free-memory guardrail fired because observed free memory fell below the frozen 5% threshold. Swap remained below the 5600 MB threshold.

## Canonical interpretation

> The exact Direct MLX Qwen3-8B 4-bit profile passed the short smoke and a standalone exact T01 workload, but did not remain inside LOOM's frozen safety boundary when the preregistered continuous full-benchmark session began. The full run reached 4% free memory during T01 and was correctly aborted. Therefore the 4-bit profile is not full-session workload-stable at this exact 4096-KV / unquantized-KV condition on the reference M1/8 GB machine.

This is a valid resource result for the exact profile, not evidence that all 4-bit Direct MLX configurations are impossible.

## Quality boundary

No aggregate 4-bit quality result is valid from this run.

Do not:
- compare a partial score with the completed 3-bit benchmark;
- treat any partial T01 output as satisfying the preregistered Pi gate;
- lower the 5% guardrail;
- change `max_kv_size`, KV precision, prompt/parser/scorer or retry policy inside this failed condition.

Pi integration remains blocked.

## Required next step

Inspect the persisted summary and telemetry read-only to determine:
- exact `guardrail_abort_reason`;
- timeline of free-memory and swap samples during T01;
- whether any complete T01 result was persisted before abort;
- child exit state and stderr/stdout tail;
- whether the 4% sample occurred during model load, prompt processing, generation, or only after a completed response, insofar as persisted evidence allows.

Do not rerun the model until this diagnostic is complete.
