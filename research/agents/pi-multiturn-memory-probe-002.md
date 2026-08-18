# Pi Multi-turn Memory Probe 002 — Result

Date: 2026-08-18
Run id: `20260818-225330`
Status: **PARTIALLY VALID — DEPTH 8 INVALID; NOT SUFFICIENT FOR FULL CAUSAL DEPTH INFERENCE**

## Purpose

Replace the speculative filename-chain design from Probe 001 with a custom run-local `probe_step` Pi extension. Each successful call required an opaque token returned by the immediately preceding tool result, intended to force sequential model -> tool -> result -> model round trips.

## Frozen configuration

- Pi 0.84.2
- Ollama 0.32.14
- `qwen3.5:4b-mlx`
- context 4096
- custom `probe_step` tool only
- built-in tools disabled
- explicit run-local extension
- isolated run-local `PI_CODING_AGENT_DIR`
- no persistent session
- cold-start depth conditions 1, 4, 8
- warm one-step follow-up planned only after a valid depth-8 condition

## Observed result

```text
cold-1turn: success=True depth=1 calls=1 advanced=1 invalid=0 wall=25.352s ollama_size=4.2GB context=4096 swap=1786.81MB free=22% usage_total=1102

cold-4turn: success=True depth=4 calls=4 advanced=4 invalid=0 wall=47.624s ollama_size=4.3GB context=4096 swap=1949.75MB free=15% usage_total=1608

cold-8turn: success=False depth=8 calls=7 advanced=1 invalid=6 wall=93.023s ollama_size=4.5GB context=4096 swap=1955.5MB free=12% usage_total=2406

warm-1turn-after-8: SKIPPED
```

Depth-8 final text:

```text
I will use the provided token to continue with your instructions
```

No event errors or JSONL parse errors were reported.

## Valid inference

The depth-1 and depth-4 conditions are valid under the preregistered token-gated protocol:

- 1 true round-trip: **4.2 GB**
- 4 true round-trips: **4.3 GB**

This is only a **+0.1 GB** difference. Therefore the available valid subset does not show a large memory increase from 1 to 4 controlled tool round trips.

## Invalid inference

The depth-8 condition is invalid because only the first call advanced state; six later calls used invalid tokens. Its **4.5 GB** allocation cannot be interpreted as the memory requirement of eight valid sequential round trips.

The warm post-depth-8 condition was correctly skipped.

Do not use this run to claim:

- 8 valid turns require 4.5 GB;
- tool depth up to 8 has been measured;
- multi-turn depth is or is not sufficient to explain Agentic 001's 7.2 GB high-water.

## New finding

The token-gated protocol itself became a model-control bottleneck at depth 8. Qwen 4B could complete the 1- and 4-step protocol but failed to propagate the opaque token reliably through the deeper sequence.

This is a benchmark-control failure, not evidence that the runtime cannot execute eight turns.

## Corrective action

Probe 003 removes token copying entirely.

A new custom tool:

- accepts no arguments;
- maintains target depth internally;
- advances exactly one step per successful call;
- uses Pi `turn_start` and blockable `tool_call` events to permit at most one `probe_step` call per LLM turn;
- lets the runner verify every tool call occurred in a distinct Pi turn.

This design isolates actual model -> tool -> result -> model depth without requiring the 4B model to copy opaque state.
