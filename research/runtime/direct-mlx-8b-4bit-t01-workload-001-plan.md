# LOOM — Direct MLX 8B 4-bit T01 Workload Safety 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the smoke-safe Direct MLX Qwen3 8B/4-bit profile complete the exact frozen Coding Benchmark 01 T01 request at `max_kv_size=4096` without crossing LOOM's 5% free-memory or 5600 MB swap guardrails?

This is a workload-safety gate before any full 4-bit quality benchmark.

## Frozen provenance

Environment:
- Darwin arm64
- `results-local/mlx/venv-mlx-lm-0.31.3`
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`

Model:
- `mlx-community/Qwen3-8B-4bit`
- pinned revision `545dc4251c05440727734bcd94334791f6ab0192`
- local main weight SHA256 `f2d29621aab300336ad645567ff38c42aac755513006ef4e8a579cf7ef5256d8`
- quantization 4-bit / group size 64

Smoke prerequisite:
- run `20260819-131009`
- FULL_PASS
- minimum free memory 10%
- peak swap 2403.31 MB
- MLX peak memory 4.683327704 GB

## Frozen benchmark input

Use Coding Benchmark 01 v1.0.1 T01 only.

Adapter:
- `scripts/ollama_single_shot.py`
- required Git blob `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- exact existing `TASKS`, `build_prompt()` and `extract_files()` behavior

T01:
- `tasks/t01_generation`
- editable `solution.py`
- source context `solution.py`
- no test feedback
- one attempt
- no retry, repair, salvage, re-prompt or manual intervention

Structured delivery is recorded after generation but does not determine the resource-safety classification.

## Runtime

Keep the 4-bit smoke profile unchanged:
- local/offline model path
- Qwen3 chat template
- `enable_thinking=False`
- direct `stream_generate`
- `max_kv_size=4096`
- unquantized KV
- `mx.random.seed(0)`

Workload changes relative to the smoke only:
1. prompt becomes the exact frozen T01 single-shot prompt;
2. max generation becomes **2048 tokens**, matching Coding Benchmark 01.

## Telemetry / safety

Use locale-safe macOS swap parsing.

Continuously record:
- system free memory percentage
- swap used MB
- child RSS (diagnostic only)
- wall time
- full memory samples
- prompt/generation tokens and tok/s
- MLX peak memory
- finish reason
- generated text
- adapter delivery status
- disk free before/after

Frozen guardrails:
- abort if free memory < **5%**
- abort if swap > **5600 MB**

Missing required free/swap telemetry is `TELEMETRY_FAIL`, not a PASS.

## Classification

`FULL_PASS` requires:
- exact environment/model/adapter preflights pass
- numeric free-memory and swap telemetry available
- T01 generation exits 0
- no guardrail breach
- non-empty generated text and MLX generation statistics captured

Other classifications:
- `RESOURCE_FAIL`
- `TELEMETRY_FAIL`
- `PREFLIGHT_FAIL`
- `RUNTIME_FAIL`
- `INVALID_HARNESS`

A structured-delivery failure is quality evidence and does not itself convert a resource-safe run to `RESOURCE_FAIL`.

## Decision after T01

If `FULL_PASS`:
1. freeze T01 workload-safety result;
2. preregister full six-task 4-bit Coding Benchmark 01 under the same runtime;
3. only then compare quality with the completed 3-bit profile.

If `RESOURCE_FAIL`:
- do not lower guardrails;
- do not reduce `max_kv_size` or quantize KV inside this failed condition;
- diagnose before any separately preregistered rescue.
