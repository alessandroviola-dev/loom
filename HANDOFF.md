# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi 4096 read/edit workflow validated; full Coding Benchmark 01 Pi agentic adapter built and preregistered
Checkpoint: PI_AGENTIC_BENCHMARK_001_PREREGISTERED_READY_TO_RUN

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
- canonical local agent model: `qwen3.5:4b-mlx`

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Benchmark: Coding Benchmark 01 v1.0.1
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical score views:
- strict single-shot delivery-adjusted: **30.00/100**
- structured-output delivery success: **3/6 = 50%**
- artifact score: **40.71/100**
- recovered semantic-content diagnostic: **82.86/100**

Performance:
- weighted prompt processing: **186.46 tok/s**
- weighted generation: **16.01 tok/s**
- peak observed swap: **2486.94 MB**

Main baseline finding:
> Code/semantic quality was materially stronger than strict delivery. JSON/full-file transport and protocol reliability were major bottlenecks.

## Pi production-configuration constraint

The user's normal Pi installation is production tooling with existing OpenAI API/Codex auth, sessions, skills/extensions/packages and customizations.

LOOM previously added Ollama only as an additional provider in `~/.pi/agent/models.json`.

Do not reset, delete or replace the user's normal Pi configuration.

For controlled benchmark runs, prefer a run-local `PI_CODING_AGENT_DIR` so production Pi state is neither loaded nor modified.

## Harness Comparison 001

Canonical record:
- `research/agents/harness-comparison-001.md`

### Qwen Code normal-config read-only smoke

Run id: `20260818-211009`

- context: 4096
- estimated initial prompt: **4474 tokens**
- hard limit: **4096**
- no tool call reached
- semantic API failure before Ollama model load
- always-on context warning: ~1429 tokens
- the only Git delta was automatic settings schema marker `"$version": 4`, now adopted in versioned config

Conclusion:
> Normal Qwen Code harness is not feasible at context 4096 on this setup before the first tool call.

### Pi minimal read-only smoke

Run id: `pi-20260818-212407`

- context: 4096
- tool: `read`
- result exactly `# LOOM`
- working tree unchanged
- Ollama after: **4.2 GB, 100% GPU, context 4096**
- swap: **1356.69 -> 2008.56 MB** (+651.87 MB)
- elapsed: ~34 s

Conclusion:
> A minimal Pi file-tool harness works at 4096 where normal Qwen Code does not. Harness overhead is a practical feasibility constraint on the 8 GB machine.

## Pi Edit+Test Smoke 001

Canonical record:
- `research/agents/pi-edit-test-smoke-001.md`

Run id: `pi-edit-20260818-213432`
Status: **FUNCTIONAL PASS / STRICT OUTPUT FAIL**

Configuration:
- context: 4096
- tools: `read,edit,bash`
- ephemeral `--no-session`
- disposable ignored workspace

Observed tool sequence:

```text
['read', 'read', 'bash', 'read', 'read', 'bash', 'edit', 'bash']
```

Functional result:
- solution changed: true
- tests unchanged: true
- independent unittest: 4/4 pass
- tracked LOOM tree unchanged
- event errors: none
- JSONL parse errors: none

Strict output result:
- required final text: `PASS`
- model added explanation before `PASS`
- therefore strict output/protocol: **FAIL**

Historical run-summary caveat:
- original summary contains `"success": true` because the old runner computed but omitted `answer_ok` from aggregate success
- runner has been patched; canonical classification remains functional PASS / strict FAIL

Resource metrics:
- elapsed: ~**114.0 s**
- PhysMem used: **5622M -> 7495M** (+1873M)
- system-wide memory free: **73% -> 61%**
- swap: **1503.88 -> 2159.19 MB** (**+655.31 MB**)
- compressor: **295M -> 1238M** (+943M)
- Ollama after: **4.8 GB, 100% GPU, context 4096**

Comparison to Pi read-only:
- runtime increased ~34 s -> ~114 s (~3.35x)
- swap delta remained nearly unchanged: +651.87 vs +655.31 MB
- Ollama final resident report increased 4.2 -> 4.8 GB
- cause of resident-size difference is unresolved; do not attribute it yet
- host memory baselines differed, so absolute PhysMem/free-percentage values are not a controlled apples-to-apples comparison

## Pi Agentic Coding Benchmark 001 — PREREGISTERED

Protocol record:
- `research/agents/pi-agentic-benchmark-001-plan.md`

Adapter:
- `scripts/pi_agentic_benchmark.py`

Frozen benchmark:
- Coding Benchmark 01 v1.0.1
- prompts/fixtures/tests/task weights/scoring semantics unchanged

Reference run configuration:
- Pi `0.84.2`
- Ollama / `qwen3.5:4b-mlx`
- context **4096**
- max output **2048**
- one agent attempt per task
- no hidden-test feedback
- tools exposed: `read,write,edit`
- no bash in this first full agentic benchmark

### Agent/test isolation

For every task:
- agent workspace is a temporary directory outside the repository tree
- workspace contains only frozen prompt text plus supplied context/editable starter files
- hidden tests are never copied into the agent workspace
- only permitted editable outputs are copied afterward into a separate scoring tree
- frozen `runner.py` performs scoring only after Pi exits

Pi has no built-in OS sandbox. This run therefore relies on workspace separation, restricted tools and explicit no-outside-access instruction. Evidence of out-of-workspace access would invalidate the affected task and require a stronger sandboxed rerun.

### Production Pi isolation

The benchmark adapter creates a run-local `PI_CODING_AGENT_DIR` with only a minimal Ollama `models.json`.

Per-run customization loading is disabled:
- `--no-extensions`
- `--no-skills`
- `--no-prompt-templates`
- `--no-themes`
- `--no-context-files`
- `--no-approve`
- `--no-session`

Environment:
- `PI_OFFLINE=1`
- `PI_SKIP_VERSION_CHECK=1`
- `PI_TELEMETRY=0`

The user's normal OpenAI/Codex Pi state must remain untouched.

### Frozen score views

1. **artifact_score** — raw frozen runner score of resulting scoring tree.
2. **delivery_adjusted_score** — task points count only when Pi exits cleanly and every permitted editable file is actually created/changed.
3. **strict_protocol_adjusted_score** — delivery points additionally require non-editable inputs unchanged, no unexpected persistent files, and final assistant text exactly `DONE`.

No rule changes after observing results.

### Failure policy

- no retries from hidden-test feedback
- no prompt rescue after seeing task results
- no manual code repair
- no JSON/envelope salvage
- material adapter defect => preserve failed run, fix adapter, document defect, rerun under new run ID

## Exact next step

Pull the preregistered adapter and run the full Pi agentic Coding Benchmark 01:

```bash
cd "<repository-root>"
git pull
python3 scripts/pi_agentic_benchmark.py
```

Preserve the complete terminal output.

Expected final summary format:

```text
LOOM Coding Benchmark 01 — Pi agentic complete
Artifact score: .../100
Delivery-adjusted score: .../100
Strict protocol-adjusted score: .../100
Delivery success: .../6; protocol success: .../6
Run directory: ...
Summary: .../run-summary.json
```

After the run:
1. ingest per-task output/tool/protocol/result metrics;
2. inspect any adapter defects before interpreting score;
3. freeze the Pi agentic result if valid;
4. compare against single-shot 30.00 strict / 40.71 artifact / 82.86 recovered-semantic baselines;
5. only then return to Qwen Code safe-mode 4096 as a secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi agentic benchmark preregistered and ready to run
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- How much does filesystem delivery close the strict 30.00 -> recovered 82.86 single-shot gap?
- Which benchmark failures remain genuine coding/comprehension errors after transport is removed?
- How often does Qwen 4B violate strict protocol even when artifacts are correct?
- Does context 4096 remain sufficient for all six benchmark tasks under minimal Pi file tools?
- What are the total runtime, swap and Ollama resident-size costs of the full agentic benchmark?
- Why did Ollama report 4.2 GB after the Pi read smoke and 4.8 GB after the longer edit/test loop at the same 4096 context?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
