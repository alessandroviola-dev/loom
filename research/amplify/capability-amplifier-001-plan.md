# LOOM — Capability Amplifier 001 Plan

Date: 2026-08-19
Status: **PREREGISTERED — READY**

## Research question

Can the already validated local `qwen3.5:4b-mlx` produce materially better end-to-end Coding Benchmark 01 results when surrounded by a minimal deterministic validation/repair system, without changing model weights, context size, sampler, benchmark, or human involvement?

This experiment changes the research question from **largest model that fits** to **maximum useful capability obtainable from a constrained local system**.

## Subject model / runtime

Primary Amplify subject:
- model: `qwen3.5:4b-mlx`
- runtime/provider: Ollama
- context: 4096
- non-thinking
- temperature: 0
- max generation: 2048 tokens/call
- local/offline inference

Historical frozen reference, Coding Baseline 001 (`20260818-203156`):
- artifact score: **40.71/100**
- strict/delivery-adjusted score: **30.00/100**
- successful structured delivery: **3/6**
- recovered semantic diagnostic: **82.86/100**

Historical Pi agentic reference (`20260818-214848`):
- artifact/delivery-adjusted: **77.15/100**
- strict protocol-adjusted: **60.00/100**
- delivery: **6/6**
- no hidden-test feedback.

The Pi result is descriptive only because Amplify 001 intentionally permits one deterministic hidden-test feedback round after the frozen initial attempt.

## Frozen benchmark / provenance

- LOOM Coding Benchmark 01 v1.0.1
- manifest blob `547050ecd0183b8d447dc3e21e724a8232f10297`
- initial single-shot adapter: `scripts/ollama_single_shot.py`
- required adapter blob: `62abab57f6463c5813809b43d8f1e7bdfec5f304`
- scorer: `benchmarks/coding/v1/runner.py`
- required scorer blob: `754e9a6506968d2b191bff57997710591efe8133`
- T01–T06 exactly, total 100 points
- isolated working benchmark copy; canonical benchmark tree is never modified.

## Amplification policy

Each task receives at most **two model calls**.

### Call 1 — frozen baseline attempt

The initial attempt must use the exact frozen adapter behavior:
- exact `TASKS`
- exact `build_prompt()`
- exact `ollama_generate()` request envelope
- exact `extract_files()` parser
- no test feedback before the first response.

This makes the first attempt directly comparable to the historical single-shot condition.

### Deterministic validation

After Call 1:

1. If structured extraction fails, record the exact parser error and raw model response. No candidate file is written from an invalid envelope.
2. If extraction succeeds, write only the permitted editable file(s) and run the exact frozen task tests using the frozen scorer logic.
3. If all frozen tests pass, the task is complete and **no repair call is allowed**.
4. If parser validation or frozen tests fail, exactly one repair call is authorized.

A scorer/test-probe malfunction is a harness failure, not model feedback and not a model-quality result.

### Call 2 — single repair

The repair prompt contains only information available to the deterministic amplifier:
- original task prompt;
- original non-editable source context;
- current editable candidate when one exists;
- either the exact parser error + initial raw output, or the exact frozen test-failure summary;
- the same required structured JSON output contract.

Repair call runtime remains:
- same model
- same Ollama endpoint
- context 4096
- non-thinking
- temperature 0
- max 2048 tokens
- JSON mode.

No third call, chain of retries, prompt rescue, manual edit, external model, web lookup, Pi agent, retrieval system, or fine-tuning is permitted in Amplify 001.

## Deterministic candidate selection

If the initial candidate is structurally valid and the repair candidate is invalid, retain the initial candidate.

If only the repair candidate is structurally valid, select the repair candidate.

If both are structurally valid:
- run the exact task tests on both;
- select the candidate with more passed tests;
- ties retain the initial candidate.

If neither candidate is structurally valid, leave the isolated benchmark fixture unchanged and count final delivery as failed.

This selection rule is frozen before the experiment and uses no model judgment.

## Safety / host-state control

Before loading the model:
- issue `ollama stop qwen3.5:4b-mlx` to start from a cold model state, matching the existing single-shot harness policy;
- require **3 consecutive samples >=70% system free memory**, one sample/second;
- if the gate is not met, classification is `HOST_STATE_NOT_READY` and no benchmark model call is made.

During every Ollama model call continuously sample:
- system free-memory percentage;
- swap used MB.

Frozen abort boundary:
- free memory < **5%**; or
- swap > **5600 MB**.

On a guardrail breach, stop the Ollama model and classify the benchmark `PARTIAL_RESOURCE_FAIL`. Missing required telemetry is `TELEMETRY_FAIL`.

Disk free is recorded before and after. No verified models/results are deleted.

## Metrics

Primary quality metric:
- **final delivery-adjusted score** from the exact frozen scorer, counting task points only for a selected valid delivered candidate.

Secondary quality metrics:
- artifact score;
- final structured delivery count / 6;
- per-task tests before/after repair;
- repair trigger reason;
- repairs attempted;
- repairs selected;
- tasks solved without repair.

Efficiency metrics:
- total model calls;
- total prompt tokens;
- total generated tokens;
- total model-call wall time;
- whole benchmark wall time;
- prompt/generation throughput per call;
- minimum free memory;
- peak swap;
- disk before/after.

## Prospectively frozen amplification gates

Reference single-shot:
- artifact 40.71
- delivery-adjusted 30.00
- delivery 3/6.

`QUALITY_IMPROVED` requires:
- benchmark `COMPLETE`; and
- final delivery-adjusted score **>30.00/100**.

`STRONG_AMPLIFICATION` requires all of:
- `QUALITY_IMPROVED`;
- artifact score **>40.71/100**;
- final structured delivery **>3/6**.

`PI_REFERENCE_REACHED` is a descriptive flag only if delivery-adjusted score is **>=77.15/100**. Because Pi Agentic 001 had no hidden-test feedback, this flag must not be interpreted as an intrinsic model or harness superiority claim.

## Interpretation boundary

Amplify 001 tests a **system**, not a newly trained model. Any improvement is attributable to the combined model + deterministic validator + one repair opportunity under this frozen experiment; it must not be described as the 4B model becoming intrinsically more capable.

If successful, later experiments may add one factor at a time, e.g. planner/verifier, retrieval, or specialization/distillation. The faster llama.cpp 4B remains a future secondary control after the Amplify mechanism is established on the primary Ollama/MLX 4B.
