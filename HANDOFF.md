# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Qwen Code installed and project-local Ollama configuration committed; first local-agent smoke test pending
Checkpoint: QWEN_CODE_INSTALLED_LOCAL_CONFIG_COMMITTED

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, with particular focus on making larger models useful on machines that normally cannot hold them entirely in RAM.

## Reference system

- Apple M1
- 8 GB unified memory
- macOS
- Canonical local repo: `<repository-root>`
- GitHub: `Ilcoach/loom` (private)
- Node.js: `v25.9.0`
- npm: `11.12.1`
- Ollama: `0.32.14`
- Qwen Code: `0.21.13`

Installed Ollama models:
- `qwen3.5:4b-mlx` — 4.0 GB — canonical baseline/agent model
- `qwen3.5:2b` — 2.7 GB — retained, not active baseline

## Frozen baseline

Coding Baseline 001 is frozen for `qwen3.5:4b-mlx`, Ollama/MLX, context 4096.

Canonical metrics:
- strict single-shot delivery score: **30.00/100**;
- structured-output delivery success: **3/6 = 50%**;
- artifact score: **40.71/100**;
- recovered semantic-content score: **82.86/100**;
- weighted prompt processing: **186.46 tok/s** across all six calls;
- weighted generation: **16.01 tok/s**;
- peak observed swap: **2486.94 MB**.

Main finding: the first 4B baseline was limited substantially more by fragile structured-output delivery than by underlying generated-code quality. T04 and T05 raw code passed 7/7 after envelope-only recovery; T06 passed 6/7.

Detailed result:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Phase 3 — local coding agent

### Selected first agent layer

Qwen Code.

Decision record:
- `research/agents/agent-layer-selection-001.md`

Reasons:
- OpenAI-compatible local provider support, including Ollama;
- built-in file read/write/edit/search tools;
- shell/test execution;
- iterative tool loop;
- approval modes;
- lightweight macOS Seatbelt sandbox;
- directly attacks the JSON full-file transport bottleneck discovered in Baseline 001.

### Installation checkpoint

The reference Mac successfully installed:

```text
qwen --version -> 0.21.13
```

Installation command used:

```bash
npm install -g @qwen-code/qwen-code@latest
```

### Reproducible LOOM Qwen Code configuration

Committed file:
- `.qwen/settings.json`

Configuration:
- provider protocol: OpenAI-compatible;
- base URL: `http://localhost:11434/v1`;
- model: `qwen3.5:4b-mlx`;
- context window: **4096**;
- temperature: **0**;
- max output tokens: **2048**;
- sandbox: enabled;
- approval mode: `default`.

This project-level configuration is intentionally versioned so the agent experiment is reproducible and does not require cloud authentication. Ollama's OpenAI-compatible `/v1/chat/completions` endpoint supports tool calls, and Qwen Code uses tool schemas for filesystem/shell actions.

Do not increase context yet. Context scaling is a separate LOOM experiment if 4096 proves insufficient for tool calling.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
cat .qwen/settings.json
```

Confirm that the pulled config contains `qwen3.5:4b-mlx` and `http://localhost:11434/v1`.

Then perform a **read-only connection/tool smoke test** before allowing edits. Start Qwen Code from the LOOM root:

```bash
qwen
```

Expected checks inside Qwen Code:
1. it starts without cloud authentication;
2. active model is `qwen3.5:4b-mlx`;
3. `/model` shows the local Ollama model;
4. `/doctor` shows the OpenAI-compatible local endpoint/config;
5. first prompt asks only to inspect/read a known LOOM file — no edits yet;
6. macOS sandbox should resolve to Seatbelt/sandbox-exec when enabled.

If connection/tool calling fails at context 4096, preserve the exact error. Do not silently raise context or change provider settings.

## Roadmap state

- Phase 0 foundation: DONE.
- Phase 1 inference baseline: DONE.
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN.
- Phase 3 local coding agent: ACTIVE — Qwen Code installed/config committed; read-only smoke test next.
- Phase 4 llama.cpp: queued.
- Phase 5 direct MLX: queued.
- Phase 6 Colibrì / SSD streaming / MoE: queued.
- Phase 7 other runtimes: queued.
- Phase 8 synthesis: queued.

## Open research questions

- Can Qwen Code + Qwen 3.5 4B execute reliable tool calls at only 4096 context?
- How much can tool-based agent editing close the strict 30.00 → semantic 82.86 gap?
- What latency and memory overhead does the agent layer add?
- Why did Ollama's resident report grow ~4.1 → 4.8 GB during sustained baseline inference?
- What is the best 7B–9B quantization/runtime configuration on 8 GB?
- Can direct MLX improve memory behavior?
- How far can SSD-backed / MoE expert streaming extend useful model size?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
