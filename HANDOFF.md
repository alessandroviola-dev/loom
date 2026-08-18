# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi 4096 completes real read/edit/test loop; functional correctness passes, exact final-output protocol fails; validator patched
Checkpoint: PI_4096_EDIT_LOOP_FUNCTIONAL_PASS_STRICT_OUTPUT_FAIL

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
- `qwen3.5:4b-mlx` — canonical baseline/agent model
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

Main baseline finding:
> Generated code quality was much better than strict delivery score; protocol/transport reliability was a major bottleneck.

## Pi configuration rule

LOOM added Ollama only as an additional provider in `~/.pi/agent/models.json`.

Must remain untouched:
- OpenAI API credentials/configuration
- OpenAI/Codex account authentication
- saved defaults
- sessions
- skills/extensions/packages
- unrelated Pi customizations

Pi LOOM model:
- provider: `ollama`
- model: `qwen3.5:4b-mlx`
- context: 4096
- max output: 2048

## Harness Comparison 001

Canonical record:
- `research/agents/harness-comparison-001.md`

### Qwen Code normal-config read-only smoke

Run id: `20260818-211009`

Result:
- no tool call reached;
- estimated initial prompt: **4474 tokens** vs hard limit **4096**;
- ~378 tokens over;
- always-on context warning ~1429 tokens;
- Ollama model never loaded;
- semantic API failure despite process exit code 0.

The only repository delta was Qwen Code automatically adding `"$version": 4` to `.qwen/settings.json`. This was classified as a harmless schema migration and adopted in the versioned config.

### Pi minimal read-only smoke

Run id: `pi-20260818-212407`

Result:
- `read` used;
- final text exactly `# LOOM`;
- tracked repository unchanged;
- Ollama after run: **4.2 GB, 100% GPU, context 4096**;
- swap **1356.69M -> 2008.56M** (+651.87M);
- memory free **73% -> 31%**;
- elapsed ~34 s.

Research finding:
> The tested minimal Pi harness is operational at context 4096 where the tested normal Qwen Code harness cannot reach the first tool call. Harness/context overhead is therefore a practical feasibility constraint on the 8 GB reference machine.

Scope limitation:
- Pi exposed only `read` in the first smoke;
- Qwen Code used its normal larger harness;
- this does not prove Pi is globally better under fully matched tool surfaces.

## Pi Edit+Test Smoke 001

Canonical record:
- `research/agents/pi-edit-test-smoke-001.md`

Run id: `pi-edit-20260818-213432`

Configuration:
- provider/model: `ollama/qwen3.5:4b-mlx`
- context: 4096
- exposed tools: `read,edit,bash`
- ephemeral `--no-session`
- disposable ignored workspace under `results-local/agent-smoke/.../workspace`
- tracked LOOM source intentionally excluded from the task

Task:
- inspect deliberately broken `range_utils.py` and deterministic tests;
- edit only the solution;
- run `python3 -m unittest -v`;
- leave tests unchanged;
- reply exactly `PASS` after success.

Observed tool sequence:

```text
['read', 'read', 'bash', 'read', 'read', 'bash', 'edit', 'bash']
```

Functional checks from the run:
- Pi process exit code: 0
- required tools `read`, `edit`, `bash`: observed
- solution changed: **true**
- test file unchanged: **true**
- independent external tests: **PASS**
- tracked LOOM working tree: **unchanged**

The model correctly diagnosed the clamp bug and repaired it.

### Functional result

**PASS**

This proves Pi + Qwen 3.5 4B MLX can perform a real minimal agentic coding loop at context 4096:

```text
read -> diagnose -> edit -> test -> externally verified pass
```

### Strict protocol result

**FAIL**

Required final response:

```text
PASS
```

Observed final text:

```text
Now I understand the bug. The return statement is wrong: `max(high, min(low, value))` should be `max(low, min(high, value))`. Let me fix it:PASS
```

Therefore exact final-output compliance failed even though the code workflow succeeded.

### Runner validation defect found and patched

The original `scripts/pi_edit_test_smoke.py` computed `answer_ok` but accidentally omitted it from aggregate `success`, so the terminal printed `Success: True` despite strict output noncompliance.

The runner is now patched to report separately:
- `functional_success`
- `strict_success`
- `answer_exact_pass`

and aggregate `success` now follows strict success.

Research consequence:
> Full agentic benchmarking must keep functional correctness and protocol/instruction adherence separate. This mirrors Baseline 001, where semantic/code quality was materially stronger than delivery/protocol reliability.

## Current reproducible tooling

Committed:
- `.qwen/settings.json`
- `scripts/qwen_code_readonly_smoke.py`
- `scripts/pi_add_ollama_provider.py`
- `scripts/pi_readonly_smoke.py`
- `scripts/pi_edit_test_smoke.py`
- `research/agents/harness-comparison-001.md`
- `research/agents/pi-edit-test-smoke-001.md`

## Exact next step

Ingest the Pi edit+test run metrics from:

`results-local/agent-smoke/pi-edit-20260818-213432/smoke-summary.json`

Required fields:
- memory before/after;
- swap before/after;
- `ollama ps` before/after;
- elapsed time;
- event/JSONL errors;
- external unittest output.

On the reference Mac:

```bash
python3 -m json.tool "<repository-root>/results-local/agent-smoke/pi-edit-20260818-213432/smoke-summary.json"
```

After metric ingestion:
1. run Qwen Code safe-mode 4096 diagnostic to isolate always-on context overhead;
2. decide whether Qwen Code 8192 is still worth measuring;
3. adapt Coding Benchmark 01 to Pi agentic mode at context 4096 with separate functional and strict protocol scoring;
4. run the full agentic benchmark.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi 4096 real edit/test loop functionally validated; strict final-output compliance issue identified; metric ingestion next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- What memory/swap cost did the Pi edit+test loop add over the read-only smoke?
- How often will Qwen 4B violate exact final/protocol instructions in longer agentic tasks?
- How much of Qwen Code's 4096 failure is always-on context vs tool schema/core prompt?
- What is the minimum practical Qwen Code context on M1/8 GB?
- How much can Pi agentic mode close the strict 30.00 -> recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
