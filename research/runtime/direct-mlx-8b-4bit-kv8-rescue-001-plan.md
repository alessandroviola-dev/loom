# LOOM — Direct MLX 8B 4-bit KV8 Rescue 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the otherwise resource-failing Direct MLX Qwen3-8B 4-bit continuous Coding Benchmark profile complete the full six-task session if the KV cache alone is changed from unquantized to 8-bit quantization, while all other benchmark/runtime/safety settings remain frozen?

This is the only authorized rescue for the 4-bit branch. It is a new profile, not a correction or rewrite of the failed unquantized-KV experiments.

## Evidence motivating the rescue

The host-state-controlled unquantized-KV replication `20260819-134012`:
- launched from 72–74% free memory;
- completed/persisted T01, T02 and T03;
- entered T04;
- repeatedly operated near the 5% free-memory floor;
- reached 4% free during T04 and was aborted;
- peak swap 2879.38 MB occurred much earlier during T01;
- swap at the final free-memory breach was 2099.94 MB.

The exact unquantized-KV profile is therefore closed as continuous-workload RESOURCE FAIL.

## Frozen provenance

Environment:
- Darwin arm64
- `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

Model:
- `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64.

Benchmark:
- Coding Benchmark 01 v1.0.1, T01–T06
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`
- exact frozen `TASKS`, `build_prompt()`, `extract_files()` and scorer
- one attempt/task
- no retry, repair, salvage, re-prompt or test feedback.

## One-factor rescue

Everything remains frozen except KV-cache policy.

Control profile:
- `max_kv_size=4096`
- `kv_bits=None` (unquantized KV).

Rescue profile:
- `max_kv_size=4096` unchanged
- **`kv_bits=8`**
- **`kv_group_size=64`**
- **`quantized_kv_start=0`**.

The three explicit KV arguments define one conceptual factor: an 8-bit KV-cache policy active from the beginning of each task. Group size 64 is the MLX-LM default. Start 0 is frozen explicitly so quantization actually engages on this workload; a 5000-token deferred start would not engage on these prompts/generations and would not test the intended rescue.

No weight quantization, context, prompt, sampler, seed, model, scorer or generation-budget change is permitted.

## Runtime

- local/offline Direct MLX
- Qwen3 chat template
- `enable_thinking=False`
- `stream_generate`
- one loaded model process across all T01–T06
- max 2048 generated tokens/task
- `mx.random.seed(0)` once at session start
- persist every completed task before moving to the next.

## Controlled host-state gate

To preserve comparability with the controlled unquantized-KV replication, launch is allowed only after:
- 3 consecutive `memory_pressure` samples;
- each sample >= **70%** system free memory;
- one sample/second.

No automated memory purge, process killing or swap manipulation is allowed.

If the gate is not met:
- classification `HOST_STATE_NOT_READY`;
- MLX is not launched;
- this is not a model/resource result.

## Safety

Frozen runtime aborts:
- free memory < **5%**;
- swap > **5600 MB**.

Missing required telemetry: `TELEMETRY_FAIL`.

Record:
- disk free before/after;
- host preflight samples;
- free-memory/swap timeline;
- child RSS diagnostic;
- progress/current task;
- per-task prompt/gen tokens and t/s;
- MLX peak memory;
- finish reason;
- raw output and adapter delivery;
- frozen scorer results only if all six generations complete.

## Quality gate

If and only if the KV8 run reaches `COMPLETE`, apply the prospectively frozen 4-bit Pi-eligibility gate already defined before the 4-bit quality result existed:
1. delivery-adjusted score **>27.86/100**;
2. structured delivery **>2/6**.

Both must hold. This would authorize only a later isolated Pi validation, not establish a daily-use winner.

No aggregate quality ordering is valid from a partial resource/runtime run.

## Decision

If `COMPLETE`:
- freeze resource + quality result;
- apply the frozen quality gate;
- only if both quality dimensions improve may an isolated Pi experiment be preregistered.

If `PARTIAL_RESOURCE_FAIL`:
- close the Qwen3-8B-4bit branch;
- do not test KV6/KV4, lower context, lower guardrails or begin another rescue ladder;
- move to the next research frontier.

If `RUNTIME_FAIL` caused by the exact supported KV8 profile rather than a clear harness defect, record it as a failed rescue profile and close the branch. Harness defects must not be mislabeled as model/resource failure.