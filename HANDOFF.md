# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi 4096 minimal harness validated; Qwen Code settings mutation classified as harmless schema migration; Pi edit+test smoke ready
Checkpoint: PI_EDIT_TEST_4096_READY_QWEN_SETTINGS_MIGRATION_CLOSED

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

Pi model available:
- provider: `ollama`
- model: `qwen3.5:4b-mlx`
- context: 4096
- max output: 2048

## Harness Comparison 001

Canonical record:
- `research/agents/harness-comparison-001.md`

### Qwen Code read-only smoke 001

Run id: `20260818-211009`

Result:
- no tool call reached;
- estimated initial prompt: **4474 tokens**;
- hard limit: **4096**;
- ~**378 tokens over limit**;
- always-on context warning: ~**1429 tokens**;
- Ollama model never loaded;
- semantic API failure despite process exit code 0.

Memory snapshots:
- PhysMem used: **6675M -> 6741M** (+66M)
- memory free: **73% -> 73%**
- swap: **1380.69M -> 1380.69M** (+0M)
- elapsed: ~**2.08 s**

### Pi read-only smoke 001

Run id: `pi-20260818-212407`

Conditions:
- `ollama/qwen3.5:4b-mlx`
- context 4096
- only `read` exposed
- `--no-session`

Result:
- exit 0;
- `read` used;
- final text `# LOOM`;
- success true;
- tracked repository status unchanged relative to start;
- Ollama after run: **4.2 GB, 100% GPU, context 4096**.

Memory snapshots:
- PhysMem used: **7207M -> 7462M** (+255M)
- memory free: **73% -> 31%**
- swap: **1356.69M -> 2008.56M** (**+651.87M**)
- compressor: **289M -> 3483M** (+3194M)
- elapsed: ~**34.00 s**

Research finding:
> The tested minimal Pi harness is operational at context 4096 where the tested normal Qwen Code harness cannot reach the first tool call. This proves harness/context overhead is a practical feasibility constraint on the 8 GB reference machine.

Scope limitation:
- Pi exposed only `read`; Qwen Code used its normal larger harness.
- This does not prove Pi is globally better or inherently lower-overhead under matched tool surfaces.

## Qwen Code settings mutation — CLOSED

The first Qwen Code smoke changed only `.qwen/settings.json`.

Exact local diff:

```diff
   "tools": {
     "sandbox": true,
     "approvalMode": "plan"
-  }
+  },
+  "$version": 4
 }
```

Classification:
- automatic Qwen Code settings-schema migration;
- no model/provider/endpoint/security/tool behavior changed;
- not an agent-generated project edit;
- safe to adopt in the versioned LOOM config.

Action completed:
- committed `"$version": 4` into `.qwen/settings.json`.

Consequence:
> The prior `Working tree unchanged: False` from Qwen Code is not evidence that the model attempted a repository modification. It was Qwen Code normalizing its own settings schema.

## Current reproducible tooling

Committed:
- `.qwen/settings.json`
- `scripts/qwen_code_readonly_smoke.py`
- `scripts/pi_add_ollama_provider.py`
- `scripts/pi_readonly_smoke.py`
- `scripts/pi_edit_test_smoke.py`
- `research/agents/harness-comparison-001.md`

Qwen smoke runner now:
- treats `[API Error: ...]` as failure even when process exit is 0;
- requires expected answer and observed tool call for success;
- captures `.qwen/settings.json` diff before/after;
- preserves memory/swap/Git diagnostics.

## Pi edit+test smoke — READY

Script:
- `scripts/pi_edit_test_smoke.py`

Design:
- context: **4096**;
- provider/model: `ollama/qwen3.5:4b-mlx`;
- ephemeral `--no-session`;
- exposed tools: `read,edit,bash`;
- disposable workspace under ignored `results-local/agent-smoke/pi-edit-<run-id>/workspace`;
- no tracked LOOM source file is intentionally editable;
- task contains a deliberately broken `range_utils.py` plus deterministic `unittest` tests;
- Pi must inspect both files, edit only `range_utils.py`, run `python3 -m unittest -v`, and finish after tests pass;
- runner independently reruns tests after Pi exits;
- runner verifies test file unchanged, solution changed, required tool calls observed, repository tracked status unchanged, and captures memory/swap/Ollama state.

Success means Pi can perform a minimal **read -> edit -> test** loop at context 4096, not merely a read-only call.

## Exact next step

On the reference Mac, the local `.qwen/settings.json` already contains the same `"$version": 4` now committed remotely. To avoid pull conflicts, first discard only that now-redundant local schema delta, then pull:

```bash
cd "<repository-root>"
git restore -- .qwen/settings.json
git pull
python3 scripts/pi_edit_test_smoke.py
```

Do not reset any Pi configuration or session files.

After the run, ingest:
- tool sequence;
- final answer;
- external unittest result;
- solution/test integrity checks;
- memory pressure, swap and Ollama resident state;
- total elapsed time.

If Pi passes, next steps are:
1. Qwen Code safe-mode 4096 diagnostic to isolate always-on context overhead;
2. then decide whether Qwen Code 8192 remains worth testing;
3. start adapting Coding Benchmark 01 to Pi agentic mode at context 4096.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi 4096 read-only passed; Qwen settings migration closed; Pi isolated edit+test smoke ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Can Pi perform reliable read/edit/bash loops at context 4096?
- How much additional swap does an edit+test loop cost versus the read-only Pi smoke?
- How much of Qwen Code's 4096 failure is always-on context vs tool schema/core prompt?
- What is the minimum practical Qwen Code context on M1/8 GB?
- How much can Pi agentic mode close the strict 30.00 -> recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
