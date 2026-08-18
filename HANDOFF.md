# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Qwen Code selected; prerequisites verified; installation pending
Checkpoint: AGENT_LAYER_PREREQUISITES_VERIFIED

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, with particular focus on making larger models useful on machines that normally cannot hold them entirely in RAM.

## Long-term destination

1. Build a practical self-hosted local coding agent with no per-token cloud usage limits.
2. Establish reproducible quality/performance/memory benchmarks for constrained local inference.
3. Explore quantization, offloading, unified memory, memory mapping, swap, SSD streaming and MoE expert streaming.
4. Compare Ollama, MLX, llama.cpp, Colibrì and other promising runtimes.
5. Determine the largest useful, not merely launchable, models on small consumer machines.
6. If the research reveals a useful gap, prototype LOOM-specific tools/runtime techniques.

## Reference system

- Apple M1
- 8 GB unified memory
- macOS
- Canonical local repo: `<repository-root>`
- GitHub: `Ilcoach/loom` (private)
- Node.js: `v25.9.0`
- npm: `11.12.1`
- Ollama: `0.32.14`

Installed Ollama models verified on 2026-08-18:
- `qwen3.5:4b-mlx` — 4.0 GB — required baseline/agent model;
- `qwen3.5:2b` — 2.7 GB — retained for now, not active baseline.

## Frozen project decisions

- Project name: `LOOM`
- Tagline: `Big models. Small machines.`
- Baseline runtime/model: Ollama + `qwen3.5:4b-mlx`
- Baseline context: 4096
- Coding Benchmark 01 prompts, fixtures, tests, expected semantics and task weights are frozen.
- Current scorer: Benchmark 01 v1.0.1 after a scoring-only defect fix.
- `single_shot` and `agentic` are distinct experimental conditions.
- Quality, delivery reliability, inference speed and memory are separate dimensions.
- Failed/malformed responses are preserved; no silent retries in strict baseline mode.
- `HANDOFF.md` is canonical and must be updated after every meaningful project step.

## CODING BASELINE 001 — FROZEN

Run id: `20260818-203156`

Configuration:
- model: `qwen3.5:4b-mlx`
- runtime/backend: Ollama / MLX
- mode: `single_shot`
- context: 4096

Frozen quality views:
- canonical strict delivery-adjusted score: **30.00 / 100**;
- structured-output delivery success: **3/6 = 50%**;
- artifact diagnostic score: **40.71 / 100**;
- deterministic recovered semantic-content score: **82.86 / 100**.

Raw-response recovery showed:
- T04 malformed JSON contained code that passed **7/7** tests after envelope-only repair;
- T05 malformed JSON contained code that passed **7/7** tests;
- T06 malformed JSON contained code that passed **6/7** tests, failing only boolean `True` validation.

Main research finding:

> The first 4B baseline was limited much more by structured-output delivery reliability than raw generated-code quality.

This is why the next phase must use true file/edit/shell tools instead of full source files serialized inside one JSON response.

Full six-call performance:
- prompt tokens: 2,520 @ **186.46 tok/s** weighted;
- output tokens: 1,068 @ **16.01 tok/s** weighted;
- summed Ollama API wall time: **85.535 s**;
- full benchmark process: ~91.25 s.

Memory:
- run-start swap: 885.69 MB;
- peak observed swap: 2486.94 MB;
- final swap: 2403.44 MB;
- model remained 100% GPU;
- Ollama reported resident size rising ~4.1 → 4.8 GB across the sequence.

Detailed frozen result:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Phase 3 — Agent layer selection

### Selected first candidate: Qwen Code

Decision record:
- `research/agents/agent-layer-selection-001.md`

Why selected:
- open-source agent CLI;
- supports local/self-hosted models through OpenAI-compatible endpoints, including Ollama;
- Ollama endpoint target: `http://localhost:11434/v1`;
- built-in file tools: read, write, edit, list, glob, grep;
- built-in shell execution for tests and commands;
- tool confirmation/approval modes;
- sandbox support;
- macOS can use lightweight Seatbelt / `sandbox-exec` rather than requiring Docker;
- local model context window is configurable;
- directly tests whether tool-based editing can close the 30.00 → 82.86 gap discovered in Baseline 001.

### Comparators queued

1. Qwen Code — selected first.
2. Aider — second comparator; mature Ollama/repo-map/test workflow but still relies on edit-format conformance.
3. OpenCode — later comparator; strong built-in tool model and Ollama integration, but current guidance favors much larger contexts than are comfortable for the 8 GB reference system.

## Completed checkpoint — prerequisites verified

Environment check from the reference Mac:

```text
node --version   -> v25.9.0
npm --version    -> 11.12.1
ollama --version -> 0.32.14
```

`ollama list` confirms `qwen3.5:4b-mlx` is installed and available.

Qwen Code's current official npm installation requires Node.js 22+, so the reference environment satisfies the prerequisite.

## Exact next step

Install the latest Qwen Code package via the official npm package:

```bash
npm install -g @qwen-code/qwen-code@latest
```

Then verify:

```bash
qwen --version
```

Do not start an authenticated/cloud session yet. After version verification, configure Qwen Code explicitly for local Ollama:
- model: `qwen3.5:4b-mlx`;
- base URL: `http://localhost:11434/v1`;
- initial context window: **4096**.

Do not increase context before measuring the first smoke test. If tool calls fail at 4096, context scaling becomes an explicit LOOM experiment with memory/swap measurements.

### Smoke-test goals

1. connect Qwen Code to Ollama;
2. confirm the local model identity;
3. run inside a disposable LOOM test working directory;
4. enable macOS Seatbelt sandbox where compatible;
5. ask the agent to read a file;
6. make one targeted edit;
7. run a test command;
8. verify the edit and tool loop;
9. measure `ollama ps`, memory pressure and swap;
10. update this handoff before full agentic benchmark.

## Roadmap state

- Phase 0 foundation: DONE.
- Phase 1 Ollama/MLX baseline: DONE.
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN.
- Phase 3 local coding agent: ACTIVE — Qwen Code selected, prerequisites verified, install next.
- Phase 4 llama.cpp larger quantized models: queued.
- Phase 5 direct MLX: queued.
- Phase 6 Colibrì / SSD streaming / MoE: queued.
- Phase 7 other runtimes: queued.
- Phase 8 synthesis: queued.

## Open research questions

- Can Qwen Code use Qwen 3.5 4B tool calls reliably at only 4096 context?
- How much can agentic edit/test loops close the strict 30.00 → recovered 82.86 quality gap?
- What latency and memory overhead does the agent layer add?
- Why does Ollama resident size rise ~4.1 → 4.8 GB during sustained inference?
- What is the best quality/memory tradeoff for 7B–9B Q4/Q3/Q2 models on 8 GB?
- Can direct MLX improve memory behavior versus Ollama MLX?
- How much practical capacity can SSD-backed / MoE expert streaming unlock before latency becomes unacceptable?

## Continuation rule

Before starting any new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
