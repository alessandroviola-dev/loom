# CAPABILITY 000D Fix1 — preflight failure

Date: 2026-08-21
Status: INFRASTRUCTURE ONLY / NO SCIENCE

## Classification

`CAPABILITY_000D_FIX1_PREFLIGHT_FAIL`

The frozen scientific Pi-loop run was not started, so this result does not consume a capability/scientific attempt and provides no evidence against `prefill_step_size=512`.

## Original 000D instrumentation root cause

The first 000D attempt failed because instrumentation assumed a prompt object exposing `.shape`.

Exact failure recovered during Fix1:

- exception: `AttributeError: 'list' object has no attribute 'shape'`
- file: `scripts/capability_000d_pi_loop.py`
- function: `watched_prompt`
- line: 114

Fix1 created `scripts/capability_000d_fix1_pi_loop.py` with list-safe `PromptProcessingBatch.prompt` observation using `len(sequence)`, exception-contained observation callbacks, and disabled Pi retry settings.

## Fix1 preflight outcome

The local canonical provider/model path was preserved:

`loom-mlx-local -> localhost -> canonical Qwen3-8B-3bit`

No fallback was observed.

The model did execute during preflight and returned `OK.` to the tiny request asking for `OK`, proving the original server-thread crash was repaired far enough for inference to run.

However the instrumentation did not produce a completed turn-metrics record. Therefore the observational harness was still not reliable enough to admit the scientific Pi-loop run.

The punctuation difference `OK.` vs `OK` is not itself treated as a model-science failure: the preflight exists to validate harness health, not capability instruction-following. The material blocker is incomplete turn-metrics/instrumentation lifecycle recording.

## Scientific status

- scientific Pi run: NOT STARTED
- functional score: N/A / not measured
- strict score: N/A / not measured
- tool sequence: none
- `answer.txt`: absent
- scientific KV/peak/free/swap trajectory: not measured

Preflight diagnostics only:

- initial free memory: 57%
- initial swap: 977.44 MB
- preflight peak MLX: 3502.438 MB

Evidence directory:

`results-local/capability/capability-000d-fix1/20260821-154137/`

Local implementation/evidence files created by Pi and not yet synchronized to GitHub:

- `scripts/capability_000d_fix1_pi_loop.py`
- Fix1 evidence under the local `results-local/...` directory

## Decision

Do not change model, quantization, context, KV format, tools or `prefill_step_size=512`.

Next work is a minimal **000D Fix2 harness repair**:

1. keep the now-fixed list-safe prompt instrumentation;
2. make telemetry strictly non-fatal and ensure request/turn lifecycle records close correctly;
3. do not require exact `OK` text for harness preflight — require only a valid local-model response plus complete non-crashing instrumentation;
4. once preflight passes, rerun the original frozen numbers.txt Pi-loop unchanged with `prefill_step_size=512`.

No CAPABILITY 001 run until that admission succeeds.
