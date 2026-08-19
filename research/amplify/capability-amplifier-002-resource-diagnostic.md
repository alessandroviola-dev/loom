# Capability Amplifier 002 — Call-Isolated Resource Diagnostic

Date: 2026-08-19
Run id: `20260819-144256`
Status: **FROZEN / DIAGNOSTIC COMPLETE**

## Frozen subject

- Model: `qwen3.5:4b-mlx`
- Runtime: Ollama
- Context: 4096
- Benchmark: LOOM Coding Benchmark 01 v1.0.1
- Capability mechanism inherited unchanged from Amplifier 001
- Maximum one repair
- Runtime guardrail: free memory <5% OR swap >5600 MB
- Initial launch gate: three consecutive samples >=70% free
- One-factor change vs Amplifier 001: unload and confirm target model absent between every model call

Runner:
`scripts/capability_amplifier_002_call_isolated.py`

Runner blob:
`df332568820e28c90baa5247df27e92cba43c0d6`

Base Amplifier 001 blob:
`9f472c60b523762276291232f6e8c6ffc1c5fcae`

## Outcome

Classification: **PARTIAL_RESOURCE_FAIL**

Exact failure reason:
`memory free 4% < 5%`

Whole wall: 55.4 s

Disk:
- before: 35.346 GiB
- after: 35.345 GiB

Overall telemetry:
- samples: 39
- minimum free memory: 4%
- peak swap: 2611.50 MB

Initial host gate:
- 71%, 72%, 72% free
- swap 1699.0 MB

No aggregate quality score is valid because the run did not reach COMPLETE.

## Completed task evidence

### T01 initial

- adapter: written
- tests: 6/6
- score: 15/15
- prompt tokens: 301
- generation tokens: 98
- generation: 13.933 tok/s
- wall: 14.256 s
- load duration: ~4.153 s
- repair not needed

Telemetry:
- pre-isolation: 71% free / 1699.0 MB swap
- during call: minimum 5% free; peak swap 2369.06 MB
- post-isolation: 38% free / 2241.06 MB swap

### T02 initial

- adapter: written
- tests: 3/7
- score: 6.43/15
- prompt tokens: 406
- generation tokens: 118
- generation: 14.395 tok/s
- wall: 14.106 s
- load duration: ~3.153 s
- repair correctly authorized from frozen-test failure

Telemetry:
- pre-isolation: 67% free / 2241.06 MB swap
- during call: minimum 5% free; peak swap 2578.94 MB
- post-isolation: 39% free / 2354.94 MB swap

## Isolation validation

The intended residency isolation is operationally confirmed by the persisted telemetry.

Before T02 repair:
- post-T02-initial unload sample: 39% free / 2354.94 MB swap
- immediately following repair pre-isolation unload confirmation: **68% free / 2346.94 MB swap**
- `isolation_event = model_unloaded`
- `ollama_stop_exit_code = 0`

Cold-load evidence also differs from Amplifier 001 warm behavior:
- Amplifier 001 T02 initial load was ~0.045 s
- Amplifier 002 T01 initial load ~4.153 s
- Amplifier 002 T02 initial load ~3.153 s

Therefore the target model was not simply being reused as a warm resident model across calls in Amplifier 002.

This does not prove any specific allocator/cache mechanism after unload; it establishes only the operational residency boundary observed by `ollama ps` and the cold-load behavior.

## T02 repair failure

T02 repair begins after successful isolation with **68% free memory**.

Observed repair trajectory:
- 68% free / 2346.94 MB swap
- 63% free / 2346.94 MB swap
- 23% free / 2542.88 MB swap
- 16% free / 2560.25 MB swap
- **4% free / 2611.50 MB swap -> guardrail abort**

No repair API response completed and no repair candidate was scored.

After the abort and unload:
- 66% free
- 1776.06 MB swap
- target model confirmed unloaded.

## Canonical interpretation

> Call isolation works operationally, but call isolation alone is insufficient. The T02 repair call, launched after confirmed unload from a materially recovered 68%-free state, independently crosses the 5% free-memory guardrail at context 4096.

The evidence rules against treating retained warm residency as the primary explanation for the Amplifier 002 failure.

The evidence does **not** establish a specific low-level cause such as a leak, KV-cache bug, Metal allocator defect, or prompt-length-only effect.

A recovery gate alone is not the leading next intervention: the failing repair already starts at 68% free, essentially the same host state as the successful T02 initial call at 67% free.

## Next one-factor hypothesis

The narrowest supported memory-control factor is the repair call context allocation.

Prospective next experiment:
- preserve initial calls at context 4096 exactly;
- preserve model, residency isolation, repair prompt, validation, output budget, sampler, scorer and guardrails;
- change **only repair-call `num_ctx` from 4096 to 3072**.

Rationale:
- successful T02 initial at context 4096 reaches exactly the 5% boundary;
- repair at the same 4096 context breaches by only 1 percentage point;
- Ollama exposes `num_ctx` per API request;
- reducing only repair context is a direct memory-aware orchestration test, not a change in model weights or capability mechanism.

The 3072 choice is fixed prospectively as a 25% context reduction while preserving the frozen max-generation request. Do not lower the runtime safety guardrail.
