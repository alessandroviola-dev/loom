# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — first Qwen Code smoke completed; 4096 context insufficient in normal configuration; Pi elevated as immediate comparator
Checkpoint: QWEN_CODE_4096_CONTEXT_LIMIT_FOUND_PI_COMPARATOR_ELEVATED

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
- Existing user coding agent: Pi (`earendil-works/pi`), previously used with persistent sessions resumed via `pi -c`

Installed Ollama models:
- `qwen3.5:4b-mlx` — 4.0 GB — canonical baseline/agent model
- `qwen3.5:2b` — 2.7 GB — retained, not active baseline

## Frozen Coding Baseline 001

Run id: `20260818-203156`

Configuration:
- model: `qwen3.5:4b-mlx`
- runtime/backend: Ollama / MLX
- mode: `single_shot`
- context: 4096

Canonical baseline views:
- strict single-shot delivery-adjusted score: **30.00/100**
- structured-output delivery success: **3/6 = 50%**
- artifact score: **40.71/100**
- recovered semantic-content score: **82.86/100**
- weighted prompt processing: **186.46 tok/s**
- weighted generation: **16.01 tok/s**
- peak observed swap: **2486.94 MB**

Main baseline finding:

> The 4B model's generated code was substantially better than its strict delivery score; fragile structured-output transport was a major bottleneck.

Detailed baseline record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Phase 3 — local coding agent

### Why Qwen Code was selected first

Qwen Code was selected as the first controlled agent-layer experiment because it:
- supports OpenAI-compatible local endpoints such as Ollama;
- provides real repository read/search/edit/write tools and shell/test execution;
- directly removes the full-file-inside-JSON transport problem seen in Baseline 001;
- supports explicit approval modes and macOS Seatbelt sandboxing;
- offers a reproducible project-local configuration.

The choice was experimental, not a claim that Qwen Code is inherently better than Pi.

## Qwen Code configuration

Committed:
- `.qwen/settings.json`
- `scripts/qwen_code_readonly_smoke.py`

Current configuration:
- model: `qwen3.5:4b-mlx`
- base URL: `http://localhost:11434/v1`
- context: **4096**
- temperature: **0**
- max output: **2048**
- sandbox: enabled
- approval mode: `plan`

## Qwen Code read-only smoke 001 — COMPLETED / FAILED BEFORE TOOL CALL

Run id: `20260818-211009`

Observed:
- Qwen Code process exit code: `0`, but semantic result contained an API error;
- model resolved correctly: `qwen3.5:4b-mlx`;
- macOS Seatbelt activated successfully with profile `permissive-open`;
- no tool call was reached;
- Qwen Code reported estimated prompt size **4474 tokens** against hard context limit **4096**;
- over-limit amount: approximately **378 tokens**;
- Qwen Code warned that always-on context (QWEN.md context files + auto-memory) consumed approximately **1429 tokens** (>15% of the context window);
- repository code search found no tracked `QWEN.md`, so the always-on overhead is not coming from a tracked LOOM QWEN.md file;
- runner printed `Working tree unchanged: False`; exact changed path/source still needs inspection before interpreting this as an agent write;
- runner also needs hardening so `[API Error: ...]` is treated as failure even when the Qwen Code process exits `0`.

Research conclusion:

> Normal Qwen Code configuration does not fit inside a 4096-token context window for even the first minimal tool smoke on this setup. The failure is agent-context overhead, not a failure of Ollama connectivity or model resolution.

Do not silently raise context yet.

## Pi comparator — ELEVATED

The user already uses Pi (`earendil-works/pi`) as a coding agent in other projects. Pi is now an immediate LOOM comparator rather than a later optional tool.

Verified current Pi capabilities from official project documentation:
- default tools: `read`, `write`, `edit`, `bash`;
- custom local providers/models supported through `~/.pi/agent/models.json`;
- Ollama can be configured at `http://localhost:11434/v1` with an OpenAI-compatible API and placeholder key;
- per-model context window is configurable;
- persistent sessions and extensibility through skills/extensions/packages.

Why Pi is especially relevant now:
- its default tool surface is deliberately small (four core tools), which may imply lower context/tool-schema overhead than Qwen Code — this is a hypothesis to measure, not an assumption;
- the user already knows its workflow;
- testing Pi with the same model and the same 4096 context before increasing Qwen Code context gives a cleaner scientific comparison.

## Exact next step

Before increasing Qwen Code context, run a matched Pi read-only smoke with:
- same model: `qwen3.5:4b-mlx`;
- same Ollama endpoint;
- same context: 4096;
- equivalent task: read `README.md` and return its first Markdown heading;
- no edits;
- capture prompt/context feasibility, tool-call success, latency, memory pressure and swap.

Also inspect the Qwen Code smoke `git_status_before` vs `git_status_after` to identify why `Working tree unchanged` was false.

If Pi succeeds at 4096 while Qwen Code does not, agent harness overhead becomes a measured LOOM result. If both fail, context scaling becomes the next controlled experiment.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Qwen Code 4096 normal-config smoke failed before tool call; Pi 4096 matched comparator is next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Can Pi + Qwen 3.5 4B perform the same tool task at context 4096?
- How much context overhead does each agent harness consume before the first user task?
- What caused the Qwen smoke working-tree status delta?
- Does Qwen Code safe-mode fit at 4096 once always-on context is removed?
- What is the minimum practical context for Qwen Code on the 8 GB reference Mac?
- What memory/swap cost is added by moving from 4096 to 8192 context?
- How much can agentic edit/test loops close the strict 30.00 → recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
