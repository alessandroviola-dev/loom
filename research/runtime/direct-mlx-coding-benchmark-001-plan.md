# LOOM — Direct MLX Coding Benchmark 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the workload-safe Direct MLX Qwen3-8B/3-bit profile complete all six frozen Coding Benchmark 01 v1.0.1 tasks under the existing LOOM safety boundary, and what structured coding quality/delivery does it achieve?

This is the first full quality benchmark for the Direct MLX 8B/3-bit profile.

## Frozen provenance

Environment:
- Darwin arm64
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

Model:
- `mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- local weight SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64

Workload-safety prerequisite:
- Direct MLX T01 Workload Safety 001 run `20260819-124952`
- FULL_PASS
- minimum free memory 19%
- peak swap 1643.12 MB
- structured delivery `written`

Frozen benchmark:
- `benchmarks/coding/v1`
- version 1.0.1
- T01–T06 exactly
- frozen adapter `scripts/ollama_single_shot.py`
- required adapter blob SHA `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- frozen scorer `benchmarks/coding/v1/runner.py`
- required scorer blob SHA `754e9a6506968d2b191bff57997710591efe8133`

## Prompt / delivery policy

For every task:
1. use the exact task entry from the frozen adapter `TASKS` table;
2. build the prompt with the exact frozen adapter `build_prompt()`;
3. provide the exact frozen source files from the isolated benchmark working tree;
4. require the exact existing JSON outer envelope;
5. after generation, apply the exact frozen adapter `extract_files()`;
6. write files only when extraction succeeds.

No prompt edits, retries, repair, salvage, re-prompting, test feedback, or manual intervention are allowed.

## Direct MLX runtime

Retain the workload-safe Direct MLX condition:
- model loaded from the verified local path only;
- HF/Transformers offline during inference;
- Qwen3 chat template;
- `enable_thinking=False`;
- direct `stream_generate`;
- `max_kv_size=4096`;
- unquantized KV;
- maximum 2048 generated tokens per task;
- `mx.random.seed(0)` before the benchmark session;
- one loaded model process for the six sequential tasks.

The single process is intentional: the full benchmark measures a realistic continuous session and can expose retained-memory behavior that six cold launches would hide.

## Isolation

Copy the complete frozen benchmark tree into:
`results-local/mlx/coding-benchmark-001/<runid>/benchmarks/coding/v1`

All generated files and scoring occur only in that isolated copy. The canonical benchmark tree is never modified.

## Runtime persistence / crash resilience

The child process writes one result JSON per completed task before moving to the next task. This allows the parent runner to distinguish completed tasks from a later resource abort without reconstructing model output.

## Telemetry and safety

Use the locale-safe swap parser validated on this Mac.

Continuously record:
- system free-memory percentage;
- swap used MB;
- child RSS (diagnostic only);
- wall time;
- full samples;
- current task/progress state;
- per-task prompt tokens/tok/s;
- per-task generation tokens/tok/s;
- MLX-reported peak memory;
- finish reason;
- raw generated text.

Frozen abort thresholds remain:
- free memory < **5%**;
- swap > **5600 MB**.

Any unparseable required free-memory/swap sample is `TELEMETRY_FAIL`, not a safety PASS.

## Scoring

If all six model attempts complete without resource/telemetry/runtime abort:
1. apply frozen `extract_files()` to each raw output;
2. record task delivery `written` or `failed`;
3. run the exact frozen benchmark scorer on the isolated working tree;
4. record artifact score;
5. calculate delivery-adjusted score by counting benchmark points only for tasks whose adapter delivery status is `written`;
6. record written task count / 6.

Primary quality metric: **delivery-adjusted score**.
Secondary metrics: artifact score, per-task points, delivery count, protocol errors, prompt/generation throughput, memory/swap telemetry.

Historical baselines may be compared descriptively after the run, but no new post-hoc scoring rule or threshold may be invented to rescue a disappointing result.

## Classification

`COMPLETE` requires:
- all environment/model/benchmark/blob preflights pass;
- numeric memory and swap telemetry remains available;
- all six Direct MLX generation attempts complete;
- no safety guardrail fires;
- frozen scorer completes.

`PARTIAL_RESOURCE_FAIL`:
- memory/swap guardrail fires before all tasks complete.

`TELEMETRY_FAIL`:
- required memory/swap telemetry becomes unavailable.

`RUNTIME_FAIL`:
- MLX child exits/fails before all six tasks without a guardrail breach.

`PREFLIGHT_FAIL`:
- environment/model/adapter/scorer/benchmark invariant mismatch.

`INVALID_HARNESS`:
- demonstrated runner defect.

A delivery/parser failure for an individual task is **quality evidence**, not a runtime failure; the benchmark continues to subsequent tasks.

## Decision after result

If `COMPLETE`:
1. freeze the full quality result;
2. compare delivery-adjusted/artifact/per-task behavior with existing 4B and llama.cpp evidence without claiming bit-identical equivalence;
3. decide whether Direct MLX 8B has earned an isolated Pi integration/agentic validation.

If resource/telemetry/runtime partial:
- do not infer a clean aggregate quality ordering;
- diagnose the exact mechanism before changing any runtime parameter.

Do not lower guardrails, alter `max_kv_size`, quantize KV, change prompts/parsers, or retry individual tasks inside this frozen condition.
