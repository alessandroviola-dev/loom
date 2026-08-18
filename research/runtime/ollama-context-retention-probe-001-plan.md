# Ollama Context Retention Probe 001 — Preregistered Plan

Date: 2026-08-18
Status: **PREREGISTERED / READY**

## Question

Does the Qwen 3.5 4B MLX allocation growth observed during Pi Agentic Coding Benchmark 001 appear in direct Ollama/MLX inference without Pi, and does it scale with prompt/context pressure?

## Motivation

Pi Memory Retention Probe 001 established:

- four identical warm Pi/read calls increased Ollama reported size only **4.1 -> 4.5 GB**;
- warm-arm swap did not accumulate;
- cold calls after `ollama stop` returned to **4.1 GB**;
- therefore simple invocation count alone does not explain Agentic 001's **4.4 -> 7.2 GB** trajectory.

The next experiment must remove Pi from the path.

## Frozen configuration

- Runtime: Ollama `0.32.14`
- Backend/model: `qwen3.5:4b-mlx`
- Context: `4096`
- API: direct Ollama `/api/generate`
- streaming: false
- thinking: false
- temperature: 0
- output budget: 8 tokens
- no agent harness
- no tools
- no repository files are modified

## Prompt-pressure levels

The runner constructs deterministic text prompts from repeated neutral tokens.

Nominal repetition levels:

- `low`: 400 repetitions
- `medium`: 1600 repetitions
- `high`: 3000 repetitions

The actual `prompt_eval_count` returned by Ollama is the authoritative prompt-token measurement. Nominal repetition counts must not be treated as exact token counts.

If a high-pressure call fails because the context is too large, preserve the failure and do not rescue or change the prompt during the same run.

## Warm arm

1. Stop the model once.
2. Run `low`.
3. Run `medium`.
4. Run `high`.
5. Run `low-after-high` without unloading the model.

Purpose:
- observe whether reported allocation scales with prompt pressure;
- determine whether high-water allocation remains after returning to a small prompt.

## Cold controls

Before each cold call, execute `ollama stop qwen3.5:4b-mlx`.

Run:

1. `cold-low`
2. `cold-high`

Purpose:
- establish post-unload baseline for low pressure;
- measure high-pressure allocation from a fresh load;
- determine whether warm-arm growth is retained state rather than purely per-call requirement.

## Metrics per call

- success / API error
- wall time
- `prompt_eval_count`
- `eval_count`
- prompt throughput
- generation throughput
- done reason
- PhysMem
- system memory free percentage
- swap used
- `ollama ps` reported size
- `ollama ps` context
- processor placement

## Safety guardrails

After each warm-arm call:

- abort warm arm and unload model if system-wide free memory falls below **8%**;
- abort warm arm and unload model if swap used exceeds **5600 MB**.

Cold controls may proceed after an abort because each begins with an explicit model unload.

## Interpretation rules

### Evidence for runtime-level context-pressure allocation

Supported if direct Ollama reported size materially increases from low to medium/high with Pi absent.

### Evidence for retained high-water allocation

Supported if `low-after-high` remains materially larger than the initial warm `low`, while `cold-low` returns near the baseline.

### Evidence against simple runtime prompt-pressure explanation

Supported if direct Ollama stays nearly flat across low/medium/high while Pi agentic workloads showed large growth.

## Non-claims

This probe does not identify the internal meaning of Ollama `SIZE`. It does not prove a leak, KV-cache mechanism, MLX allocator behavior, or physical resident-memory equivalence.

## Failure policy

- no prompt rescue after observing results;
- no rerun under the same run id;
- preserve API failures;
- script/measurement defects require a new run id after documentation.
