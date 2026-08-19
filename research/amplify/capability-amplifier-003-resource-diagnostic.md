# Capability Amplifier 003 — Repair Context 3072 — Resource Diagnostic

Date: 2026-08-19
Run id: `20260819-150342`
Status: **FROZEN DIAGNOSTIC**

## Classification

`PARTIAL_RESOURCE_FAIL`

Exact failure:
`memory free 4% < 5%`

No aggregate quality score is valid because the six-task run did not complete.

## Frozen profile

- model: `qwen3.5:4b-mlx`
- runtime: Ollama
- initial context: 4096
- repair context: 3072
- call isolation before/after every model call
- temperature 0
- non-thinking
- max generation request 2048
- same benchmark/prompts/validator/repair feedback/candidate selection/scorer as preregistered
- guardrails unchanged: free <5% OR swap >5600 MB

Runner blob:
`c2bcc8f126eb5b599645ba12d1fd08a348e2b443`

## Host state

Initial host gate:
- 71% free
- 74% free
- 74% free
- swap 1247.88 MB

Disk:
- before: 36.344 GiB free
- after: 35.342 GiB free

Whole wall time: 48.841 s.

Overall telemetry:
- samples: 36
- minimum free: 4%
- peak swap: 2318.12 MB

## T01 initial

- context: 4096
- delivery: written
- frozen tests: 6/6
- score: 15/15
- prompt tokens: 301
- generated tokens: 98
- generation: 15.042 tok/s
- wall: 11.791 s
- load: ~3.155 s
- pre-isolation: 74% free / 1247.88 MB swap
- minimum during call: 6%
- post-isolation: 46% free / 1865.25 MB swap
- repair: not required.

## T02 initial

- context: 4096
- delivery: written
- frozen tests: 3/7
- score: 6.43/15
- prompt tokens: 406
- generated tokens: 118
- generation: 16.199 tok/s
- wall: 12.918 s
- load: ~3.066 s
- pre-isolation: 66% free / 1865.25 MB swap
- minimum during call: 6%
- post-isolation: 32% free / 2069.12 MB swap
- repair correctly authorized.

## T02 repair — decisive evidence

The call-isolation boundary explicitly records:
- `call_context=3072`
- target model unloaded
- `ollama_stop_exit_code=0`
- pre-repair state: **70% free / 2069.12 MB swap**.

Repair trajectory:
- 70% free / 2069.12 MB
- 65% / 2061.12 MB
- 31% / 2264.56 MB
- 7% / 2216.56 MB
- 6% / 2208.56 MB
- **4% / 2250.69 MB** -> guardrail abort.

No completed repair API response was persisted.

Post-abort isolation:
- `call_context=3072`
- model unloaded
- 70% free / 2318.12 MB swap.

## Comparison with Amplifier 002

Amplifier 002 repair:
- context 4096
- starts at 68% free
- trajectory 68 -> 63 -> 23 -> 16 -> 4%
- peak swap 2611.50 MB.

Amplifier 003 repair:
- context 3072
- starts at 70% free
- trajectory 70 -> 65 -> 31 -> 7 -> 6 -> 4%
- peak swap 2318.12 MB overall.

The lower repair context changes the observed pressure trajectory and reduces peak swap relative to Amplifier 002, but it does **not** prevent the same free-memory safety breach.

## Canonical interpretation

> Reducing only repair context from 4096 to 3072 is insufficient to make the frozen repair call safe on the M1 / 8 GB reference system. The repair was confirmed to use 3072 and began from a recovered 70%-free state, yet still crossed the 5% free-memory guardrail.

This result does not prove a specific KV-cache, allocator, prompt-length, MLX, or Ollama root cause.

A further automatic context reduction to 2048 is not authorized by the preregistered plan.

## Important additional observation

The successful initial calls themselves reach minimum free-memory values of only 6%. Therefore the current Ollama/MLX 4B profile has very little operating headroom even before adding a repair call.

Before choosing the next amplifier architecture, measure the actual initial-vs-repair prompt footprint. If the repair prompt is materially inflated by repeated task/context/traceback content, a compact-repair experiment is justified. If it is already compact, the stronger next move is to reconsider the runtime/model profile, including the previously validated llama.cpp 4B efficiency control, rather than continue a repair-context rescue ladder.
