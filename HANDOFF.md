# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Ollama provider added successfully without altering existing OpenAI/Codex setup; matched 4096 read-only smoke ready
Checkpoint: PI_OLLAMA_PROVIDER_ADDED_SMOKE_READY

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
- Pi: `0.84.2`
- Existing Pi remains production tooling with OpenAI API access, OpenAI/Codex account auth, persistent sessions and user customizations

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

## Qwen Code experiment

Qwen Code was selected first as a controlled agent-layer test because it supports local Ollama, real filesystem/shell tools, approval modes and macOS Seatbelt.

Read-only smoke 001 (`20260818-211009`) result:
- model resolved correctly: `qwen3.5:4b-mlx`;
- Seatbelt active (`permissive-open`);
- no tool call reached;
- estimated initial prompt: **4474 tokens** against **4096** limit;
- approximately **378 tokens over**;
- always-on context warning: approximately **1429 tokens**;
- process exit code was 0 despite semantic API error;
- working-tree status delta still needs exact local inspection.

Conclusion:
> Qwen Code in normal configuration does not fit inside context 4096 on the reference setup before the first minimal tool call.

## Pi comparator — immediate priority

Pi is the matched comparator at context 4096.

### HARD CONSTRAINT — preserve existing Pi setup

LOOM must not reset or replace the user's existing Pi installation/configuration.

Do not delete, overwrite or invalidate:
- OpenAI API credentials/configuration;
- OpenAI/Codex account authentication;
- existing provider/model settings;
- installed skills;
- installed extensions;
- packages;
- session history;
- unrelated Pi customizations.

Ollama/Qwen is only an additional selectable provider/model.

## Pi Ollama provider addition — COMPLETED

Observed on reference Mac:

```text
LOOM Pi Ollama provider merge complete
models.json: <user-home>/.pi/agent/models.json
backup: not needed (file did not previously exist)
- added providers.ollama
Untouched: auth.json, settings.json, sessions, skills, extensions, packages
```

`pi --list-models ollama` now reports:

```text
provider  model           context  max-out  thinking  images
ollama    qwen3.5:4b-mlx  4.1K     2.0K     no        no
```

Research consequence:
- Pi resolves the local Ollama provider/model successfully;
- no existing custom `models.json` had to be merged;
- existing OpenAI/Codex auth/settings were not touched by the LOOM setup script;
- the LOOM model is available as an additional selectable model at context 4096 and max output 2048.

Committed tooling:
- `scripts/pi_add_ollama_provider.py`
- `scripts/pi_readonly_smoke.py`

### `pi_readonly_smoke.py`

Runs Pi with:
- `--provider ollama`
- `--model qwen3.5:4b-mlx`
- `--tools read`
- `--no-session`
- `--mode json`

The run is intentionally ephemeral and does not change the user's saved default model or normal persistent sessions. It asks Pi to use the read tool on LOOM `README.md` and return the first Markdown heading, while recording JSON events, Git status, memory pressure, swap and `ollama ps`.

## Exact next step

Run the matched Pi 4096 read-only smoke:

```bash
cd "<repository-root>"
python3 scripts/pi_readonly_smoke.py
```

Interpretation:
- if Pi succeeds at 4096 while Qwen Code normal config fails, agent-harness context overhead becomes a measured LOOM result;
- if Pi also fails at 4096, context scaling becomes the next controlled experiment.

After the smoke, ingest the exact tool-call result, latency, memory/swap and Git-status outcome before changing context.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi Ollama provider added successfully; matched 4096 read-only smoke next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Can Pi + Qwen 3.5 4B complete the same read-tool task at context 4096?
- How much context overhead does Pi consume versus Qwen Code?
- What caused the Qwen smoke working-tree status delta?
- Does Qwen Code safe-mode fit at 4096?
- What is the minimum practical context for Qwen Code on the reference Mac?
- What memory/swap cost is added by context scaling?
- How much can agentic edit/test loops close the strict 30.00 → recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
