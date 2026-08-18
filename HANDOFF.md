# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi 4096 minimal harness validated; Qwen Code normal harness blocked by context overhead; smoke metrics ingested
Checkpoint: PI_4096_SMOKE_METRICS_INGESTED_QWEN_SETTINGS_DIFF_PENDING

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, especially Apple M1 / 8 GB unified memory.

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
- Pi remains production tooling with existing OpenAI API/Codex auth, sessions and user customizations preserved

Installed Ollama models:
- `qwen3.5:4b-mlx` — 4.0 GB — canonical baseline/agent model
- `qwen3.5:2b` — retained, not active baseline

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical metrics:
- strict delivery-adjusted score: **30.00/100**
- structured-output delivery success: **3/6 = 50%**
- artifact score: **40.71/100**
- recovered semantic-content score: **82.86/100**
- weighted prompt processing: **186.46 tok/s**
- weighted generation: **16.01 tok/s**
- peak observed swap: **2486.94 MB**

Main finding:
> Generated code quality was much better than strict delivery score; fragile structured-output transport was a major bottleneck.

## Pi configuration rule

LOOM added Ollama only as an additional provider in `~/.pi/agent/models.json`.

Must remain untouched:
- OpenAI API credentials/configuration
- OpenAI/Codex account authentication
- saved defaults
- sessions
- skills/extensions/packages
- unrelated Pi customizations

Pi model now available:
- provider: `ollama`
- model: `qwen3.5:4b-mlx`
- context: 4096
- max output: 2048

## Qwen Code read-only smoke 001

Run id: `20260818-211009`

Conditions:
- model: `qwen3.5:4b-mlx`
- context: 4096
- normal Qwen Code harness
- plan/read-only
- Seatbelt enabled

Result:
- process exit code: 0, but semantic API error
- no tool call reached
- estimated initial prompt: **4474 tokens**
- hard limit: **4096**
- ~**378 tokens over limit**
- always-on context warning: ~**1429 tokens**
- Ollama model never loaded

Memory snapshots:
- PhysMem used: **6675M -> 6741M** (+66M)
- memory free: **73% -> 73%**
- swap: **1380.69M -> 1380.69M** (+0M)
- compressor: **283M -> 283M**
- elapsed from first snapshot to finish: ~**2.08 s**

Git:
- before: clean
- after: ` M .qwen/settings.json`

Important: exact local diff is still pending. Do not assume what Qwen Code changed until `git diff -- .qwen/settings.json` is inspected.

## Pi read-only smoke 001

Run id: `pi-20260818-212407`

Conditions:
- provider/model: `ollama/qwen3.5:4b-mlx`
- context: 4096
- only tool exposed: `read`
- `--no-session`
- JSON event mode

Result:
- exit code: 0
- success: true
- tool used: `read`
- final text: `# LOOM`
- no event errors
- no JSONL parse errors
- repository status unchanged relative to start
- Ollama after run: **4.2 GB, 100% GPU, context 4096**

Memory snapshots:
- PhysMem used: **7207M -> 7462M** (+255M)
- memory free: **73% -> 31%**
- swap: **1356.69M -> 2008.56M** (**+651.87M**)
- compressor: **289M -> 3483M** (+3194M)
- elapsed: ~**34.00 s**

Git:
- before: ` M .qwen/settings.json`
- after: ` M .qwen/settings.json`
- therefore Pi caused no additional repository delta

## Harness Comparison 001 — key result

Canonical record:
- `research/agents/harness-comparison-001.md`

| Harness | Tool surface | Context | Tool reached | Result |
|---|---|---:|---|---|
| Qwen Code 0.21.13 | normal config | 4096 | No | FAIL before first tool call; prompt ~4474 tokens |
| Pi 0.84.2 | `read` only | 4096 | Yes | PASS; returned `# LOOM` |

Research finding:
> Agent-harness/context overhead is a practical feasibility constraint on the 8 GB reference machine. The tested minimal Pi profile works at 4096 where the tested normal Qwen Code profile does not.

Scope limitation:
- Pi exposed only `read`; Qwen Code had its normal larger harness/tool/context surface.
- This does not yet prove Pi is globally better or that its base framework always has lower overhead.
- Qwen's memory run is not comparable to Pi's loaded-model memory because Qwen failed before Ollama loaded.

## Tooling updates

Committed:
- `.qwen/settings.json`
- `scripts/qwen_code_readonly_smoke.py`
- `scripts/pi_add_ollama_provider.py`
- `scripts/pi_readonly_smoke.py`
- `research/agents/harness-comparison-001.md`

Qwen smoke runner has now been hardened to:
- detect `[API Error: ...]` as semantic failure even with exit code 0
- require expected final text + observed tool call for success
- capture `.qwen/settings.json` diff before/after
- preserve Git status and memory/swap diagnostics

## Exact next step

On the reference Mac, after pulling latest repo, inspect the existing Qwen Code settings delta:

```bash
cd "<repository-root>"
git pull
git diff -- .qwen/settings.json
```

Do not reset or commit the local settings modification until its contents are understood.

After that:
1. classify the Qwen Code settings mutation;
2. restore/accept it deliberately;
3. run a controlled Pi edit + test smoke at context 4096;
4. separately run Qwen Code safe-mode 4096 to isolate always-on context overhead;
5. only then decide whether to test Qwen Code at 8192 or move Pi directly to full agentic Coding Benchmark 01.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi minimal 4096 passes; Qwen normal 4096 fails on context; metrics ingested; settings diff next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- What exactly did Qwen Code rewrite in `.qwen/settings.json`?
- How much of Qwen Code's 4096 failure is always-on context vs tool schema/core prompt?
- Can Pi perform reliable edit + test loops at 4096?
- What is the minimum practical Qwen Code context on M1/8 GB?
- What extra swap cost comes from 8192 context?
- How much can Pi agentic mode close the strict 30.00 -> recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
