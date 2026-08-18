# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Qwen Code 4096 context limit found; Pi elevated as immediate comparator; Pi configuration must be preserved non-destructively
Checkpoint: PI_NONDESTRUCTIVE_OLLAMA_MERGE_REQUIRED

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
- Existing user coding agent: Pi (`earendil-works/pi`), already used with OpenAI API access and OpenAI/Codex account authentication, persistent sessions, installed skills and extensions

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

### Qwen Code first candidate

Qwen Code was selected as the first controlled agent-layer experiment because it supports local Ollama endpoints, filesystem/shell tools, approval modes and macOS Seatbelt. The choice was experimental and never implied superiority over Pi.

Current Qwen Code config:
- model: `qwen3.5:4b-mlx`
- base URL: `http://localhost:11434/v1`
- context: **4096**
- temperature: **0**
- max output: **2048**
- sandbox: enabled
- approval mode: `plan`

### Qwen Code read-only smoke 001 — failed before tool call

Run id: `20260818-211009`

Observed:
- model resolved correctly: `qwen3.5:4b-mlx`;
- macOS Seatbelt activated with `permissive-open`;
- no tool call was reached;
- estimated initial prompt: **4474 tokens** against **4096** hard limit;
- approximately **378 tokens over limit**;
- always-on Qwen Code context warning: approximately **1429 tokens**;
- process returned exit code 0 despite semantic API error;
- runner reported working-tree status delta that still needs exact local inspection.

Research conclusion:

> Qwen Code in normal configuration does not fit inside context 4096 on the reference setup before even the first minimal tool call.

## Pi comparator — immediate priority

Pi is now the matched comparator at context 4096.

Current official Pi behavior relevant to LOOM:
- default core tools: `read`, `write`, `edit`, `bash`;
- built-in providers such as OpenAI/Codex coexist with custom providers;
- custom providers/models can be added via `~/.pi/agent/models.json`;
- Ollama can be added as a separate provider at `http://localhost:11434/v1` using `openai-completions` and a placeholder API key;
- `/model` lists provider/model options and reloads custom model configuration;
- per-model context window is configurable.

### HARD CONSTRAINT — preserve existing Pi installation/configuration

The user's current Pi setup is already important production tooling and MUST NOT be replaced, reset or simplified for LOOM.

Do not delete, overwrite or invalidate:
- OpenAI API configuration/credentials;
- OpenAI/Codex account authentication;
- existing provider/model settings;
- installed skills;
- installed extensions;
- packages;
- session history/persistent sessions;
- any unrelated Pi customizations.

LOOM may only ADD Ollama/Qwen as an additional selectable provider/model.

Implementation rule:
1. inspect the existing local Pi configuration first without printing secrets;
2. if `~/.pi/agent/models.json` already exists, merge only a new `providers.ollama` entry while preserving every existing key/value;
3. if it does not exist, create only the minimal Ollama provider file;
4. make a timestamped local backup before any write;
5. do not touch auth storage, `settings.json`, skills or extensions unless a later experiment explicitly requires it;
6. verify after the change that existing OpenAI/Codex models remain selectable alongside Ollama in `/model`.

## Exact next step

Perform a read-only inventory of the user's existing Pi setup, intentionally avoiding secret values. Determine:
- Pi version;
- whether `~/.pi/agent/models.json` exists;
- existing provider IDs and model IDs only;
- top-level Pi configuration files/directories;
- installed skill/extension directories.

Only after that inventory, construct a non-destructive merge plan for Ollama `qwen3.5:4b-mlx` at context 4096.

Then run a matched Pi read-only smoke:
- model: `qwen3.5:4b-mlx`;
- Ollama endpoint: local;
- context: 4096;
- task: read LOOM `README.md` and return the first Markdown heading;
- no edits;
- measure tool success, latency, memory pressure and swap.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi non-destructive configuration inventory next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Can Pi + Qwen 3.5 4B perform the same tool task at context 4096 while preserving the user's production Pi configuration?
- How much context overhead does Pi consume versus Qwen Code?
- What caused the Qwen smoke working-tree status delta?
- Does Qwen Code safe-mode fit at 4096?
- What is the minimum practical context for Qwen Code on the reference Mac?
- What memory/swap cost is added by context scaling?
- How much can agentic edit/test loops close the strict 30.00 → recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
