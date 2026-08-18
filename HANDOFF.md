# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi 0.84.2 inventory complete; no custom models.json exists; non-destructive Ollama merge and matched read-only smoke scripts ready
Checkpoint: PI_OLLAMA_SAFE_MERGE_READY

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
- Existing Pi is production tooling with OpenAI API access, OpenAI/Codex account auth, persistent sessions and user customizations that must be preserved

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

### Local Pi inventory completed

Observed on reference Mac:
- Pi version: `0.84.2`;
- `~/.pi/agent/models.json`: **NOT PRESENT**;
- `~/.pi/agent/sessions/`: present with multiple persistent project sessions;
- `~/.pi/agent/extensions/`: directory present;
- prior inventory command listed only extension/skill subdirectories, so empty printed lists MUST NOT be interpreted as proof that no extension/skill resources exist;
- no write has been made to the user's Pi configuration yet.

Important consequence:
> Ollama can be added by creating a new `~/.pi/agent/models.json`. Existing OpenAI/Codex authentication and settings live separately and do not need to be replaced.

### Verified Pi behavior relevant to LOOM

Current official Pi docs confirm:
- custom providers/models use `~/.pi/agent/models.json`;
- Ollama example uses `http://localhost:11434/v1`, API `openai-completions`, and placeholder API key `ollama`;
- `contextWindow` and `maxTokens` are per-model settings;
- `/model` reloads `models.json`;
- CLI supports `--provider <name> --model <id>`;
- `--no-session` makes a run ephemeral;
- `--tools read` can expose only the read tool for a read-only benchmark;
- JSON event mode reports `tool_execution_start` / `tool_execution_end` events.

### HARD CONSTRAINT — preserve existing Pi installation/configuration

LOOM must never reset or replace the user's existing Pi setup.

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

## New reproducible tooling

Committed:
- `scripts/pi_add_ollama_provider.py`
- `scripts/pi_readonly_smoke.py`

### `pi_add_ollama_provider.py`

Safety properties:
- touches only `$PI_CODING_AGENT_DIR/models.json` or `~/.pi/agent/models.json`;
- if an existing models.json appears later, backs it up before writing;
- preserves every existing provider and field;
- if an Ollama provider already exists, adds missing LOOM values/model without overwriting existing values;
- never touches `auth.json`, `settings.json`, sessions, skills, extensions or packages;
- writes atomically.

LOOM model entry:
- provider: `ollama`
- base URL: `http://localhost:11434/v1`
- API: `openai-completions`
- placeholder key: `ollama`
- model: `qwen3.5:4b-mlx`
- context: **4096**
- max output: **2048**
- reasoning: false
- cost: zero
- compatibility disables developer-role/reasoning-effort fields for local Ollama shim reliability.

### `pi_readonly_smoke.py`

Runs Pi with:
- `--provider ollama`
- `--model qwen3.5:4b-mlx`
- `--tools read`
- `--no-session`
- `--mode json`

Therefore the smoke does not change the user's saved default model and does not create a normal persistent Pi session. It asks Pi to read LOOM `README.md` and return exactly `# LOOM`, while recording JSON events, read-tool use, Git status, memory pressure, swap and `ollama ps`.

## Exact next step

On reference Mac:

```bash
cd "<repository-root>"
git pull
python3 scripts/pi_add_ollama_provider.py
pi --list-models ollama
```

Verify that `ollama/qwen3.5:4b-mlx` is listed. Existing OpenAI/Codex providers should remain available because no auth/settings files are modified.

Then run:

```bash
python3 scripts/pi_readonly_smoke.py
```

Interpretation:
- if Pi succeeds at 4096 while Qwen Code normal config fails, agent-harness context overhead is a measured LOOM result;
- if Pi also fails at 4096, context scaling becomes the next controlled experiment.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi safe Ollama merge + 4096 matched smoke ready
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
