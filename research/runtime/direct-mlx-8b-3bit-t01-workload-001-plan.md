# LOOM — Direct MLX 8B 3-bit T01 Workload Safety 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the safety-valid Direct MLX Qwen3 8B/3-bit profile complete the real frozen Coding Benchmark T01 request at `max_kv_size=4096` without crossing LOOM's 5% free-memory or 5600 MB swap guardrails?

This is a **workload-safety gate**, not yet a full quality comparison.

## Frozen provenance

Direct MLX setup:
- `mlx-lm==0.31.3`
- `mlx==0.31.2`
- `transformers==5.12.1`
- isolated venv `results-local/mlx/venv-mlx-lm-0.31.3`

Model:
- `mlx-community/Qwen3-8B-3bit`
- pinned visible revision `619ded3`
- local main weight SHA256 `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`
- 3-bit / group size 64

Safety-valid smoke:
- run `20260819-124440`
- `max_kv_size=4096`
- unquantized KV
- minimum free memory 23%
- peak swap 1720.75 MB
- FULL_PASS

## Frozen benchmark input

Use Coding Benchmark 01 v1.0.1 task T01 only.

Frozen adapter:
`scripts/ollama_single_shot.py`
Git blob SHA: `62abab57f6463c5813809b43d8f1e7bdfec5f304`

T01:
- path `benchmarks/coding/v1/tasks/t01_generation`
- editable file `solution.py`
- supplied context `solution.py`
- prompt and source are read from the frozen benchmark tree at runtime
- no test feedback
- no retry
- no repair/salvage/re-prompt

The exact frozen single-shot adapter `build_prompt()` envelope is used, including the requirement to return only:
`{"files":{"filename":"complete UTF-8 file contents"}}`
with exactly the permitted editable filename.

The adapter's `extract_files()` may be applied after generation only to record structured-delivery status. Delivery success/failure does **not** determine this workload-safety classification and no benchmark test runner is executed in this probe.

## Direct MLX runtime

Preserve the safety-valid smoke runtime:
- local model path only during inference
- Hugging Face / Transformers offline mode
- Qwen3 chat template
- `enable_thinking=False`
- direct `stream_generate`
- `max_kv_size=4096`
- KV unquantized
- `mx.random.seed(0)`

Changed workload variables relative to the smoke:
1. prompt changes from `Reply only with OK.` to the exact frozen T01 single-shot prompt;
2. generation budget changes from 16 to **2048 tokens**, matching the frozen coding benchmark budget.

No model, quantization, KV precision, KV cap or safety threshold changes.

## Telemetry

Use locale-safe macOS swap parsing that accepts both comma and point decimals.

Record throughout the child process:
- system free-memory percentage;
- swap used MB;
- child RSS (diagnostic only);
- wall time;
- full memory samples;
- MLX prompt/generation token counts and tok/s;
- MLX-reported peak memory when available;
- finish reason;
- generated text;
- structured-delivery parse status;
- disk free before and after.

## Frozen safety guardrails

Abort the child model process if either:
- system free memory < **5%**;
- swap used > **5600 MB**.

A missing/unparseable swap sample is a telemetry/harness failure, not a safety PASS.

## Classification

`FULL_PASS` requires:
- exact environment/model/adapter preflight passes;
- numeric swap telemetry is available before launch and during execution;
- T01 generation exits 0;
- no safety guardrail breach;
- non-empty generation result and generation statistics are captured.

Structured delivery is recorded separately:
- `written` if the exact adapter output schema is satisfied;
- `failed` otherwise.

A delivery failure does not convert a resource-safe T01 into `RESOURCE_FAIL`; it becomes quality/protocol evidence for later use.

Other classifications:
- `RESOURCE_FAIL`: free-memory or swap guardrail fires;
- `TELEMETRY_FAIL`: required swap/free-memory measurement cannot be obtained;
- `PREFLIGHT_FAIL`: environment/model/adapter/benchmark invariant mismatch;
- `RUNTIME_FAIL`: MLX generation fails without guardrail breach;
- `INVALID_HARNESS`: demonstrated runner defect.

## Decision after T01

If `FULL_PASS`:
1. freeze workload-safety telemetry;
2. preregister full Direct MLX Coding Benchmark 01 under the same runtime;
3. quality/delivery becomes the next gate before Pi.

If `RESOURCE_FAIL`:
- do not lower the guardrail;
- do not reduce `max_kv_size` inside this failed condition;
- consider `kv_bits=8` only as a separately preregistered rescue if scientifically justified.

If delivery fails but workload safety passes, proceed only to a preregistered full quality benchmark; do not post-hoc alter the prompt/parser.
