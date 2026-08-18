# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Qwen Code installed/configured; reproducible read-only smoke test ready to run on reference Mac
Checkpoint: QWEN_CODE_READONLY_SMOKE_READY

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

Raw-response recovery:
- T04 malformed JSON contained code that passed **7/7** tests after envelope-only repair
- T05 malformed JSON contained code that passed **7/7**
- T06 malformed JSON contained code that passed **6/7**, failing only boolean `True` validation

Main finding:

> The first 4B baseline was limited substantially more by fragile structured-output delivery than by underlying generated-code quality.

Full six-call inference performance:
- prompt tokens: 2,520 @ **186.46 tok/s** weighted
- output tokens: 1,068 @ **16.01 tok/s** weighted
- summed Ollama API wall time: **85.535 s**
- full benchmark process: ~91.25 s

Memory during baseline:
- run-start swap: 885.69 MB
- peak observed swap: 2486.94 MB
- final swap: 2403.44 MB
- model remained 100% GPU
- Ollama resident report rose approximately 4.1 → 4.8 GB across the six-task sequence

Detailed baseline record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Phase 3 — local coding agent

### Selected first candidate

Qwen Code.

Decision record:
- `research/agents/agent-layer-selection-001.md`

Why:
- supports OpenAI-compatible local endpoints such as Ollama
- built-in repository read/search/edit/write tools
- built-in shell/test execution
- iterative tool loop
- approval modes
- macOS sandbox support via Seatbelt / `sandbox-exec`
- directly attacks the fragile full-file JSON delivery bottleneck found in Baseline 001

Comparators queued:
1. Qwen Code
2. Aider
3. OpenCode if its context requirements prove practical on 8 GB

## Qwen Code installation

Installed successfully on reference Mac:

```text
qwen --version -> 0.21.13
```

Installation command:

```bash
npm install -g @qwen-code/qwen-code@latest
```

## Project-local Qwen Code configuration

Committed:
- `.qwen/settings.json`

Verified current official Qwen Code configuration behavior:
- project settings live at `.qwen/settings.json`
- `modelProviders.openai` accepts local OpenAI-compatible servers such as Ollama
- Ollama base URL: `http://localhost:11434/v1`
- local OpenAI-compatible provider still needs an API-key environment variable value; for Ollama a placeholder such as `ollama` is valid
- `security.auth.selectedType: openai` skips cloud/provider auth selection
- `tools.approvalMode: plan` provides the initial read-only analysis posture
- `tools.sandbox: true` enables sandboxing; on macOS the built-in path uses Seatbelt/sandbox-exec, with `permissive-open` as the default profile

Current LOOM config:
- model: `qwen3.5:4b-mlx`
- base URL: `http://localhost:11434/v1`
- env key: `OPENAI_API_KEY`
- placeholder value: `ollama`
- context window: **4096**
- temperature: **0**
- max output tokens: **2048**
- max provider retries: **1**
- sandbox: enabled
- approval mode for first smoke test: **plan**

Do not raise context before measuring the first tool smoke. If 4096 fails, context scaling becomes a separate LOOM experiment.

## Reproducible read-only smoke test

Committed script:
- `scripts/qwen_code_readonly_smoke.py`

The script:
1. records Git status before the run
2. records PhysMem, memory pressure, swap and `ollama ps`
3. launches Qwen Code headlessly from the LOOM root
4. forces `--approval-mode plan`
5. asks Qwen Code to use the repository file-reading tool on `README.md`
6. explicitly forbids edits and shell commands
7. limits wall time to 2 minutes, tool calls to 5 and session turns to 8
8. captures Qwen's full JSON output and stderr under ignored `results-local/agent-smoke/<run-id>/`
9. extracts detected model, tool names and final result where possible
10. records memory/swap after the run
11. verifies Git working-tree status is unchanged

This is deliberately a connection + tool-protocol smoke test, not a coding-quality test yet.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 scripts/qwen_code_readonly_smoke.py
```

Expected high-level success conditions:
- Qwen Code exits 0
- local model resolves as `qwen3.5:4b-mlx`
- a repository read tool is observed
- final answer is the first Markdown heading of `README.md`
- working tree remains unchanged
- no cloud authentication flow appears

Preserve the exact output if any step fails. Do not alter context/provider/sandbox settings manually before diagnosing it.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — read-only Qwen Code smoke test ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Can Qwen Code + Qwen 3.5 4B perform reliable tool calls at only 4096 context?
- Does Seatbelt sandbox behave correctly with the local Ollama endpoint and read tools?
- How much memory/swap overhead does Qwen Code add over direct Ollama inference?
- How much can an edit/test loop close the strict 30.00 → semantic 82.86 gap?
- Why did Ollama resident size rise ~4.1 → 4.8 GB during sustained baseline inference?
- What is the best 7B–9B quantization/runtime configuration on 8 GB?
- Can direct MLX improve memory behavior?
- How far can SSD-backed / MoE expert streaming extend useful model size?

## Continuation rule

Before starting any new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
