# Agent Layer Selection 001 — Qwen Code

Date: 2026-08-18
Decision: **Qwen Code selected as first LOOM agentic layer**

## Context

Coding Baseline 001 showed a large gap between strict delivery and underlying code content:

- strict single-shot delivery score: 30.00/100;
- recovered semantic-content score: 82.86/100;
- only 3/6 structured JSON deliveries were valid;
- T04 and T05 contained fully correct code despite malformed outer JSON;
- T06 contained near-correct code despite malformed outer JSON.

Therefore the first agentic experiment should primarily test whether tool-based file operations and validation loops can recover capability otherwise lost to brittle full-file JSON transport.

## Candidates considered

### Qwen Code
Strengths for LOOM:
- open-source coding agent CLI;
- supports local/self-hosted models through OpenAI-compatible APIs, including Ollama at `http://localhost:11434/v1`;
- local model context window is configurable;
- built-in file-system tools include read, write, edit, list, glob and grep;
- built-in shell tool can execute tests/commands;
- supports approval modes and automated tool calls;
- supports sandboxing;
- on macOS, lightweight Seatbelt / `sandbox-exec` sandboxing is available and recommended for most users;
- model-family alignment with Qwen is useful as an initial compatibility hypothesis.

Main risk:
- a 4B model may still struggle with tool-call schemas and multi-step planning;
- agentic loops increase context, latency and memory pressure.

### Aider
Strengths:
- mature terminal coding workflow;
- direct Ollama support;
- repository map;
- diff/whole edit formats;
- integrated lint/test and repair loop;
- Git integration.

Risk for this specific first experiment:
- Aider still depends on the model conforming to an edit format;
- its own documentation notes that weaker/local/quantized models can have edit-format problems;
- this may reproduce part of the transport-format fragility that Baseline 001 exposed.

Aider remains an important second agentic comparator.

### OpenCode
Strengths:
- open-source terminal coding agent;
- first-party Ollama integration;
- built-in read/edit/apply-patch/bash tools and configurable permissions.

Risk for the 8 GB reference machine:
- current Ollama integration guidance recommends very large context windows for OpenCode/tool reliability, making it a less conservative first choice for this memory-constrained baseline.

OpenCode remains a later comparator if Qwen Code proves unsuitable.

## Decision rationale

Qwen Code best matches the immediate research question:

> Can a true tool-calling local agent convert Qwen 3.5 4B's high recovered code-content quality into reliable end-to-end repository edits on 8 GB hardware?

It avoids asking the model to serialize complete source files inside one outer JSON string. Instead the model can request explicit file edit/write operations and inspect command/test feedback in subsequent turns.

## Planned first configuration

- runtime: Ollama
- model: `qwen3.5:4b-mlx`
- endpoint: `http://localhost:11434/v1`
- initial context target: 4096, matching Coding Baseline 001
- sandbox: macOS Seatbelt / `sandbox-exec`
- first run: interactive smoke test with confirmations
- benchmark run: isolated working copy + sandbox + reproducible automated approval policy

Context will only be increased if tool-call reliability requires it, because every context increase must be measured against memory/swap cost on the 8 GB reference machine.

## Success criteria

Before running full agentic Benchmark 01:

1. Qwen Code can connect to local Ollama.
2. Model identity is confirmed as `qwen3.5:4b-mlx`.
3. Agent can read a test repository file.
4. Agent can make a small targeted edit through a tool.
5. Agent can execute a test command and observe failure/success.
6. Sandbox restricts writes outside the test project.
7. Memory/swap remains usable.

After smoke validation, Coding Benchmark 01 will be run in a distinct `agentic` experimental mode and compared against frozen Baseline 001.

## Comparators queued

1. Qwen Code — selected first.
2. Aider — second agentic comparator.
3. OpenCode — later if context/memory requirements can be made practical on 8 GB.
