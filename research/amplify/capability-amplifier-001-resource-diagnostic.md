# LOOM — Capability Amplifier 001 Resource Diagnostic

Date: 2026-08-19
Run: `20260819-142640`
Status: **FROZEN / DIAGNOSTIC COMPLETE**

## Classification

The frozen Capability Amplifier 001 run remains:

`PARTIAL_RESOURCE_FAIL`

Exact failure reason recovered from the run summary:

`memory free 4% < 5%`

This was a free-memory guardrail breach, not a swap-threshold breach.

## Host state

Launch gate passed cleanly:
- free memory: 74%, 74%, 74%
- swap: 1206.12 MB on all three samples.

Therefore poor initial host state is not a material explanation for this run.

## Completed work

T01 initial:
- adapter written
- 6/6 frozen tests
- 15/15 points
- no repair
- prompt 301 tokens
- generation 98 tokens
- generation 15.922 tok/s
- wall 12.391 s
- load duration ~3.668 s.

T02 initial:
- adapter written
- 3/7 frozen tests
- 6.43/15 points
- repair correctly authorized
- prompt 406 tokens
- generation 118 tokens
- generation 16.026 tok/s
- wall 10.020 s
- load duration ~0.045 s.

The T02 repair did not complete and therefore no repair model-call record or repair candidate exists.

No aggregate Amplify quality score is valid from this partial run.

## Telemetry by phase

T01 initial:
- 12 samples
- min free 5%
- peak swap 1889.94 MB
- last free 16%
- last swap 1819.25 MB.

T02 initial:
- 10 samples
- min free 6%
- peak swap 1958.25 MB
- last free 10%
- last swap 1902.25 MB.

T02 repair:
- 4 samples
- free: 7% -> 5% -> 5% -> 4%
- swap rises to 2500.88 MB
- final 4% sample triggers the frozen abort.

Overall:
- 26 telemetry samples
- min free 4%
- peak swap 2500.88 MB
- whole run 42.789 s.

## Interpretation

The evidence supports a **warm-residency / cumulative-headroom problem at the orchestration level**, but it does not establish a memory leak or any specific internal Ollama/MLX mechanism.

Two observations motivate that interpretation:
1. the first call is cold-loaded (`load_duration` ~3.668 s), whereas T02 initial reuses a warm loaded model (`load_duration` ~0.045 s);
2. free-memory headroom remains narrow across successive calls and the repair begins at only 7% free before reaching the 4% guardrail.

The correct claim is therefore narrow:

> Capability Amplifier 001, when executed with continuous warm Ollama model residency between sequential calls, does not provide enough memory headroom for the validator + one-repair workflow on the M1/8 GB reference system.

Do not label this as an Ollama leak, MLX leak, KV leak, fragmentation bug, or causal proof that warm residency alone is responsible.

## Decision

Do not rerun Amplifier 001 unchanged.

Preregister a one-factor operational profile:

**Capability Amplifier 002 — Call-Isolated**

Preserve:
- same `qwen3.5:4b-mlx`
- same frozen Coding Benchmark 01 v1.0.1
- same initial prompt/request/parser
- same deterministic validation
- same maximum one repair and feedback
- same candidate selection
- same scorer
- same initial >=70% host-state gate
- same 5% / 5600 MB runtime guardrails.

Change only residency policy:
- after every model call, explicitly unload the Ollama model;
- verify absence from `ollama ps` before the next model call;
- record pre/post-isolation memory/swap;
- no additional 70% threshold between calls, so call isolation remains the single changed factor.

This profile intentionally trades cold-load latency for memory headroom.
