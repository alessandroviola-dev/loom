# LOOM — Direct MLX 8B 4-bit Host-State Replication 001 Diagnostic

Date: 2026-08-19
Target run: `20260819-134012`
Status: **CLOSED — KV8 RESCUE JUSTIFIED**

## Purpose

Read-only diagnosis of the host-state-controlled Qwen3-8B-4bit full Coding Benchmark replication. No model rerun, salvage or scoring correction was performed.

## Run state

- classification: `PARTIAL_RESOURCE_FAIL`
- failure: `memory free 4% < 5%`
- host/full preflight: **72% free / 1381.75 MB swap**
- child exit: **-15** after parent safety termination
- child wall: **49.353 s**
- peak sampled RSS: **332.046875 MB**
- peak swap: **2879.38 MB**
- minimum free memory: **4%**
- disk: **35.333 → 35.328 GiB free**

## Persisted task evidence

Three complete model generations were persisted before the abort:

- T01: `finish_reason=stop`, 276 prompt tok, 101 generated tok, 13.1458 gen tok/s, MLX peak 4.981664948 GB, adapter `written`.
- T02: `finish_reason=stop`, 374 prompt tok, 119 generated tok, 13.3513 gen tok/s, MLX peak 5.037748316 GB, adapter `written`.
- T03: `finish_reason=stop`, 359 prompt tok, 60 generated tok, 12.7644 gen tok/s, MLX peak 5.037748316 GB, adapter `written`.

T04 was `running` when the guardrail fired. T04–T06 have no completed generation result.

No aggregate score is valid from this partial run.

## Memory timeline

Key observations:

- startup: 71% free at ~0–1 s, then 59% at ~2 s;
- model/session initialization region: free falls to 13% at ~3.2 s;
- T01 begins around 6 s with free 22%; peak swap 2879.38 MB occurs at 7.044 s while free remains 22%;
- later T02 samples repeatedly reach low-teens and single digits, including 9% and 7%;
- T03 begins around 38.4 s with free 7%; it touches **5%** at 39.491 s but does not breach the `<5%` rule, then recovers temporarily into 7–14%;
- T04 begins with 6% free at 48.105 s;
- at 49.198 s free reaches **4%** with swap **2099.94 MB**, triggering the abort.

The swap peak occurs early in T01 and is not coincident with the final free-memory breach. At the T04 failure sample swap is materially lower than its peak and far below the 5600 MB guardrail.

## Supported interpretation

> The controlled run shows sustained system-memory pressure across a continuous multi-task session rather than a one-off bad host launch. Three tasks complete and persist, but free memory repeatedly approaches the frozen safety floor and finally crosses it during T04. The exact 4-bit / `max_kv_size=4096` / unquantized-KV profile remains closed as continuous-workload RESOURCE FAIL.

The evidence does **not** prove that KV cache is the only cause of the pressure. However, because the model weights and every benchmark/runtime dimension are frozen, KV-cache precision is the narrowest directly supported memory-control factor exposed by the current Direct MLX generation API.

## KV8 rescue rationale

MLX-LM `stream_generate()` forwards generation kwargs to `generate_step()`. `generate_step()` supports:
- `kv_bits`
- `kv_group_size`
- `quantized_kv_start`
- `max_kv_size`

The rescue will therefore change one conceptual factor: **KV-cache policy**, from unquantized to 8-bit quantized KV.

Frozen rescue values:
- `kv_bits=8`
- `kv_group_size=64`
- `quantized_kv_start=0`
- `max_kv_size=4096` unchanged.

`quantized_kv_start=0` is explicit because these benchmark prompts/generations are far below the CLI's 5000-token deferred-quantization default; using 5000 would make the rescue effectively unquantized for this workload.

## Rescue boundary

Authorize exactly one separately preregistered full-session KV8 rescue under the same >=70% controlled host-state launch gate.

Preserve:
- exact Qwen3-8B-4bit weights;
- exact MLX package versions;
- Coding Benchmark 01 v1.0.1;
- prompts, parser and scorer;
- non-thinking mode;
- `max_kv_size=4096`;
- max 2048 generated tokens/task;
- seed 0;
- one loaded session;
- free<5% / swap>5600 MB abort;
- no retry/repair/salvage/test feedback.

If this single KV8 rescue resource-fails, close the 4-bit branch. Do not test progressively more aggressive KV precisions as a rescue ladder.