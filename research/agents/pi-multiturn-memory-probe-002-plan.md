# Pi Multi-turn Memory Probe 002 — Preregistered Plan

Date: 2026-08-18
Status: **PREREGISTERED / READY**

## Why Probe 002 exists

Probe 001 was invalid for causal depth inference because the built-in `read` tool allowed speculative filename guesses:

- nominal 1-read condition produced 3 reads;
- nominal 8-read condition produced 14 reads;
- only the 4-read condition matched its target exactly.

Canonical invalid-run record:
- `research/agents/pi-multiturn-memory-probe-001.md`

The corrected probe must control tool depth mechanically rather than relying on filename-following compliance.

## Question

At fixed model/context and from a cold model load, does Ollama reported allocation increase materially as the number of **sequential within-session model -> tool -> result -> model round trips** rises from 1 to 4 to 8?

## Controlled tool

Probe 002 loads one explicit run-local Pi extension:
- `scripts/pi_probe_step_extension.ts`

The extension registers only:
- `probe_step`

Built-in tools are disabled.

### Token-gated state machine

For every condition:
1. the runner generates a random opaque initial token and gives it to the model in the prompt;
2. `probe_step` advances exactly one step only if called with the currently expected token;
3. after a valid non-final step, the tool generates and returns a new random 128-bit token;
4. the model cannot know that next valid token until it receives the preceding tool result;
5. wrong/reused/guessed tokens return `INVALID_TOKEN` and do not advance state;
6. the final valid step returns `STOP`.

This design creates an actual sequential dependency between tool calls.

## Frozen stack

- Pi `0.84.2`
- Ollama `0.32.14`
- model `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- custom tool surface: `probe_step` only
- built-in tools disabled with `--no-builtin-tools`
- explicit extension loaded with `--extension`; discovery disabled with `--no-extensions`
- isolated run-local `PI_CODING_AGENT_DIR`
- skills/prompt templates/themes/context files disabled
- no persistent session
- user production Pi config/auth/sessions untouched

## Conditions

### cold-1turn
- explicit `ollama stop` before session
- target: exactly 1 valid `probe_step` call

### cold-4turn
- explicit `ollama stop` before session
- target: exactly 4 valid sequential `probe_step` calls

### cold-8turn
- explicit `ollama stop` before session
- target: exactly 8 valid sequential `probe_step` calls

### warm-1turn-after-8
- run only if cold-8turn is valid and guardrails permit
- do not unload after cold-8turn
- target: exactly 1 valid call in a new Pi process
- measures retained post-8-turn high-water

## Validity criteria per condition

A condition is valid only if all hold:
- Pi exit code 0;
- no timeout;
- JSONL parses cleanly;
- no Pi event errors;
- final text exactly `DONE`;
- only `probe_step` is called;
- total tool starts exactly equal target depth;
- total tool ends exactly equal target depth;
- every tool end reports `advanced=true`;
- zero `advanced=false` invalid-token calls;
- no tool error;
- final tool result reports `stop=true`.

Any speculative or incorrect tool call invalidates the condition rather than being silently ignored.

## Metrics

Per condition:
- target depth
- total tool calls
- advanced count
- invalid-token count
- wall time
- last non-zero provider usage
- PhysMem
- system free-memory percentage
- swap used
- Ollama reported SIZE
- Ollama context
- processor placement

## Interpretation

Evidence for within-session depth pressure is supported if valid cold conditions show a material SIZE increase across 1 -> 4 -> 8 turns.

Evidence for retained multi-turn high-water is supported if valid `warm-1turn-after-8` remains materially above valid `cold-1turn`.

If valid 1/4/8 conditions remain near the ~4.1–4.6 GB range seen in earlier reduced probes, multi-turn depth alone is insufficient to explain Agentic 001's 7.2 GB high-water.

## Guardrails

After a condition:
- free memory <8% => unload and prevent warm-dependent follow-up;
- swap >5600 MB => unload and prevent warm-dependent follow-up.

## Non-claims

The probe still does not identify what Ollama `SIZE` internally represents and cannot by itself prove:
- memory leak;
- KV-cache mechanism;
- allocator fragmentation;
- physical RAM equivalence.

It isolates correlation with controlled sequential agent/tool depth.

## Failure policy

- no prompt rescue after results are observed;
- no manual tool injection;
- invalid conditions are preserved;
- a tool/extension/runner defect requires documentation and a new run ID;
- no result from invalid Probe 001 is retroactively reused as a valid depth measurement.
