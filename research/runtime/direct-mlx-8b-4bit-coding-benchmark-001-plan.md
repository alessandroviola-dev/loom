# LOOM — Direct MLX 8B 4-bit Coding Benchmark 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the T01-safe Direct MLX Qwen3-8B 4-bit profile complete all six frozen Coding Benchmark 01 v1.0.1 tasks in one loaded-model session without crossing LOOM safety guardrails, and does it improve useful structured coding quality over the completed same-runtime 3-bit profile?

## Frozen provenance

Environment:
- Darwin arm64
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

Model:
- `mlx-community/Qwen3-8B-4bit`
- revision `545dc4251c05440727734bcd94334791f6ab0192`
- local weight SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- 4-bit / group size 64

Prerequisite:
- T01 Workload Safety 001 run `20260819-132612`
- FULL_PASS
- minimum free memory 6%
- peak swap 2470.31 MB
- structured delivery `written`

Frozen benchmark:
- `benchmarks/coding/v1`
- version 1.0.1
- T01–T06 exactly
- frozen adapter `scripts/ollama_single_shot.py`
- adapter blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- frozen scorer `benchmarks/coding/v1/runner.py`
- scorer blob `754e9a6506968d2b191bff57997710591efe8133`

## Prompt / delivery policy

For each task use the exact frozen adapter `TASKS`, `build_prompt()` and `extract_files()` behavior. The benchmark working tree is isolated. No prompt edits, retries, repair, salvage, re-prompting, test feedback or manual intervention are permitted.

A delivery/parser failure is quality evidence and does not stop later tasks if the runtime remains healthy.

## Direct MLX runtime

Retain the T01-safe condition exactly:
- local/offline model path
- Qwen3 chat template
- `enable_thinking=False`
- direct `stream_generate`
- one loaded model process for all six sequential tasks
- `max_kv_size=4096`
- unquantized KV
- max 2048 generated tokens per task
- `mx.random.seed(0)` at session start
- locale-safe swap telemetry

No cold restart is allowed between tasks. The continuous session intentionally tests retained-memory behavior.

## Safety

Continuously record free-memory percentage, swap MB, child RSS, task progress and per-task MLX metrics.

Abort if:
- free memory < **5%**
- swap > **5600 MB**

Missing required telemetry is `TELEMETRY_FAIL`.

## Scoring

If all six generations complete without resource/telemetry/runtime abort:
1. apply the exact frozen `extract_files()` to every response;
2. write only successfully extracted files into the isolated benchmark copy;
3. run the exact frozen scorer;
4. record artifact score;
5. calculate delivery-adjusted score using scorer points only for tasks with `written` delivery;
6. record structured delivery count / 6 and per-task diagnostics.

Primary quality metric: **delivery-adjusted score**.
Secondary metrics: artifact score, structured delivery count, per-task points/tests, protocol errors, throughput and safety telemetry.

## Prospectively frozen 4-bit vs 3-bit quality gate

Reference same-runtime 3-bit result (`20260819-125647`):
- delivery-adjusted score **27.86/100**
- structured delivery **2/6**

The 4-bit profile becomes eligible for a later isolated Pi agentic validation only if all of the following hold:
1. full benchmark classification is `COMPLETE`;
2. delivery-adjusted score is **strictly greater than 27.86**;
3. structured delivery count is **strictly greater than 2/6**.

This gate only authorizes a later isolated Pi experiment. It does not establish that 4-bit is a daily-use upgrade.

If either quality dimension fails to improve, Pi remains blocked for this profile and no post-hoc threshold or prompt/parser rescue is allowed.

## Classification

`COMPLETE` requires all six generations, valid required telemetry, no guardrail breach and successful frozen scoring.

Other classifications:
- `PARTIAL_RESOURCE_FAIL`
- `TELEMETRY_FAIL`
- `RUNTIME_FAIL`
- `PREFLIGHT_FAIL`
- `INVALID_HARNESS`

Do not interpret an aggregate quality ordering from a partial resource/runtime run.

## Decision after result

If `COMPLETE`, freeze the full result and compare 4-bit vs 3-bit descriptively under the prospectively frozen gate above.

If resource/telemetry/runtime partial, diagnose the exact mechanism before changing any runtime parameter. Do not lower guardrails, reduce `max_kv_size`, quantize KV, alter prompts/parsers/scorer or retry individual tasks inside this condition.
