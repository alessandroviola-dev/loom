# Pi Multi-turn Memory Probe 001 — Preregistered Plan

Date: 2026-08-18
Status: **PREREGISTERED / READY**

## Question

Does Ollama reported allocation increase materially with **within-session Pi tool/turn depth** at fixed context 4096, beyond the modest warm retention already observed from repeated calls and direct prompt pressure?

## Motivation

Three prior observations now exist:

1. Pi Agentic Coding Benchmark 001: sustained agentic work produced Ollama SIZE **4.4 -> 7.2 GB**.
2. Pi Memory Retention Probe 001: four identical small warm Pi calls produced only **4.1 -> 4.5 GB**, so invocation count alone is insufficient.
3. Ollama Context Retention Probe 001: direct Ollama prompt pressure produced **4.1 -> 4.5 GB**, with `low-after-high` retained at **4.6 GB`; runtime-level prompt-pressure/high-water behavior exists, but still does not explain 7.2 GB.

The next unresolved factor is repeated **model -> tool -> tool-result -> model** cycling inside a single Pi session.

## Frozen configuration

- Pi `0.84.2`
- Ollama `0.32.14`
- model `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- tool surface: `read` only
- isolated run-local `PI_CODING_AGENT_DIR`
- extensions/skills/prompt templates/themes/context files disabled
- no persistent session
- no user production Pi state loaded or modified
- no bash, write or edit tools

## Forced sequential tool-chain design

The workspace contains deterministic chain files. Each file tells Pi which file must be read next.

Pi is given only the first filename in the prompt. Therefore it cannot know the next filename until the preceding read result is returned.

This forces sequential tool-result round trips rather than allowing all file paths to be known in advance.

Each chain ends with `STOP`.

## Conditions

### cold-1turn

- execute `ollama stop` before session
- chain length: 1 read
- expected read tool calls: exactly 1

### cold-4turn

- execute `ollama stop` before session
- chain length: 4 reads
- expected read tool calls: exactly 4

### cold-8turn

- execute `ollama stop` before session
- chain length: 8 reads
- expected read tool calls: exactly 8

### warm-1turn-after-8

- do **not** unload after `cold-8turn`
- immediately run the 1-read chain
- purpose: test whether the high-water from the deepest tool loop remains visible during a subsequent tiny session

## Success criteria per session

A condition is valid if:

- Pi exits code 0;
- no timeout;
- JSONL parses cleanly;
- no Pi event errors;
- final text exactly `DONE`;
- observed `read` count exactly equals expected chain length;
- observed read paths exactly match expected chain files in order;
- every explicit path is relative and contains no `..` traversal.

Invalid conditions are preserved and not rescued under the same run id.

## Metrics

Per condition:

- success/validation status
- exact tool sequence and read paths
- wall time
- last non-zero provider usage snapshot
- PhysMem
- system memory free percentage
- swap used
- Ollama reported SIZE
- Ollama context
- processor placement

Also capture memory state after every explicit `ollama stop`.

## Interpretation rules

### Evidence for within-session multi-turn/tool-depth pressure

Supported if cold-started reported SIZE rises materially across:

`cold-1turn -> cold-4turn -> cold-8turn`

while model/context are unchanged.

### Evidence for retained multi-turn high-water

Supported if `warm-1turn-after-8` remains materially above `cold-1turn`.

### Evidence against tool-depth as major missing driver

Supported if cold-started 1/4/8-turn sessions remain close in reported SIZE, materially below Agentic 001's 7.2 GB.

In that case the investigation should move lower into runtime/session allocation behavior or more closely reproduce the benchmark's task/token shape.

## Guardrails

After every session:

- if system-wide free memory < 8%, stop model and abort remaining warm-dependent step;
- if swap used > 5600 MB, stop model and abort remaining warm-dependent step.

Cold-start conditions can continue only if the machine recovers after unload.

## Non-claims

This probe does not identify what Ollama `SIZE` internally represents and does not prove:

- a memory leak;
- KV-cache allocation;
- MLX allocator behavior;
- physical RAM equivalence;
- that tool calls themselves rather than accumulated text/context are causal.

It isolates only whether controlled sequential agent/tool depth correlates with the observed allocation high-water.

## Failure policy

- no prompt rescue;
- no manual tool injection;
- no rerun under the same run id;
- preserve invalid conditions;
- measurement defects require a documented new run id.
