# Pi Multi-turn Memory Probe 003 — Preregistered Plan

Date: 2026-08-18
Status: PREREGISTERED / READY

## Goal

Measure whether true within-session Pi round-trip depth changes Ollama reported allocation at fixed context 4096.

## Background

- Agentic Coding Benchmark 001 reached 7.2 GB reported SIZE.
- Repeated tiny Pi calls reached only 4.5 GB warm.
- Direct Ollama prompt-pressure testing reached 4.5 GB and retained 4.6 GB warm.
- Probe 001 was invalid because the model performed speculative file reads.
- Probe 002 validated depth 1 and 4 at 4.2 and 4.3 GB, but the copied-token control failed at depth 8.

Probe 003 removes filenames and copied tokens from the control path.

## Frozen setup

- Pi 0.84.2
- Ollama 0.32.14
- model `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- custom `probe_step` extension only
- built-in tools disabled
- isolated run-local Pi directory
- no persistent session
- skills, templates, themes, context files and extension discovery disabled

## Control mechanism

`probe_step` takes no arguments. The target depth is supplied to the extension through an environment variable and the extension keeps the completed-step count internally.

The extension resets a per-turn counter on Pi `turn_start`. It permits one `probe_step` call in a model turn and blocks any second call in that same turn.

The runner also records the Pi turn index for every tool start. A valid condition therefore requires each successful probe call to occur in a different model turn.

## Conditions

1. `cold-1turn`: unload first, target depth 1.
2. `cold-4turn`: unload first, target depth 4.
3. `cold-8turn`: unload first, target depth 8.
4. `warm-1turn-after-8`: only after a valid depth-8 condition, without unloading first.

## Validity requirements

A condition is valid only when:

- Pi exits normally;
- no timeout, JSON parse error or event error occurs;
- final text is exactly `DONE`;
- probe call count equals target depth;
- advanced count equals target depth;
- no other tool appears;
- no same-turn duplicate was blocked;
- every probe call has a distinct Pi turn index;
- the last result reports STOP at the requested depth.

Invalid conditions are preserved and are not repaired or rerun under the same run id.

## Measurements

For every condition record wall time, provider usage, Pi turn indices, tool counts, PhysMem, memory-free percentage, swap, Ollama SIZE, configured context and processor placement.

## Interpretation

- Material SIZE growth from valid cold depth 1 -> 4 -> 8 supports round-trip-depth pressure.
- A warm one-turn call remaining above cold one-turn after valid depth 8 supports retained high-water.
- If valid depth 1/4/8 all remain around the reduced-probe range and far below 7.2 GB, round-trip depth alone is insufficient and the next test should reproduce more of the benchmark workload shape.

## Guardrails

Do not run the warm follow-up if free memory falls below 8% or swap exceeds 5600 MB. Unload the model if a guardrail is reached.

## Non-claims

This probe does not identify what Ollama `SIZE` represents internally and does not establish a leak, KV-cache mechanism, allocator fragmentation, or physical-RAM equivalence.
