# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — first full Pi agentic Coding Benchmark 01 completed; preliminary scores strongly improve over single-shot; full task/metric ingestion pending
Checkpoint: PI_AGENTIC_BENCHMARK_001_COMPLETED_PRELIMINARY_INGEST_PENDING

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

The user's normal Pi installation remains production tooling with existing OpenAI API/Codex auth, sessions, skills/extensions/packages and customizations.

LOOM added Ollama only as an additional provider in `~/.pi/agent/models.json`.

Do not reset, delete or replace the user's normal Pi configuration.

Controlled benchmark runs use a run-local `PI_CODING_AGENT_DIR` so production Pi state is neither loaded nor modified.

## Harness Comparison 001

Canonical record:
- `research/agents/harness-comparison-001.md`

Qwen Code normal-config read-only smoke at context 4096:
- estimated initial prompt **4474 tokens** vs hard limit **4096**;
- no tool call reached;
- semantic API failure before Ollama model load;
- only Git delta was automatic `"$version": 4` settings migration, now adopted.

Pi minimal read-only smoke at context 4096:
- `read` tool succeeded;
- final response exactly `# LOOM`;
- working tree unchanged;
- Ollama after: **4.2 GB, 100% GPU, context 4096**;
- swap delta **+651.87 MB**;
- elapsed ~34 s.

Conclusion:
> The tested minimal Pi harness is operational at 4096 where normal Qwen Code is not. Harness/context overhead is a practical feasibility constraint on the 8 GB machine.

## Pi Edit+Test Smoke 001

Canonical record:
- `research/agents/pi-edit-test-smoke-001.md`

Run id: `pi-edit-20260818-213432`
Status: **FUNCTIONAL PASS / STRICT OUTPUT FAIL**

Configuration:
- context 4096
- tools `read,edit,bash`
- ephemeral `--no-session`
- disposable ignored workspace

Functional result:
- required tools observed;
- solution changed;
- tests unchanged;
- independent unittest 4/4 pass;
- tracked LOOM tree unchanged;
- no event/JSONL errors.

Strict result:
- required final text exactly `PASS`;
- model added explanation before `PASS`;
- strict protocol therefore failed.

Metrics:
- elapsed ~114 s
- swap **1503.88 -> 2159.19 MB** (+655.31 MB)
- Ollama after **4.8 GB, 100% GPU, context 4096**

Runner defect from this historical run was patched: future runs separate `functional_success` and `strict_success`.

## Pi Agentic Coding Benchmark 001 — COMPLETED / PRELIMINARY

Preregistered protocol:
- `research/agents/pi-agentic-benchmark-001-plan.md`

Adapter:
- `scripts/pi_agentic_benchmark.py`

Preliminary result record:
- `research/agents/pi-agentic-benchmark-001-preliminary.md`

Run id: `20260818-214848`
Run directory:
- `results-local/coding-agentic-pi/20260818-214848`
Summary:
- `results-local/coding-agentic-pi/20260818-214848/run-summary.json`

Frozen run configuration:
- benchmark: Coding Benchmark 01 v1.0.1
- Pi 0.84.2
- Ollama / `qwen3.5:4b-mlx`
- context **4096**
- max output **2048**
- one attempt per task
- no hidden-test feedback
- file tools only: `read,write,edit`
- no bash in this benchmark
- run-local isolated `PI_CODING_AGENT_DIR`
- extensions/skills/prompt templates/themes/context files disabled for benchmark run
- user production Pi configuration not loaded or modified

Agent/test isolation:
- each agent task ran in a temporary workspace outside the repository tree;
- hidden tests were never copied into that workspace;
- only permitted editable artifacts were transferred into a separate scoring tree after Pi exited;
- frozen `runner.py` scored afterward;
- no retries or hidden-test rescue allowed.

### Terminal-observed task protocol/delivery status

```text
T01 delivery=PASS protocol=PASS
T02 delivery=PASS protocol=FAIL
T03 delivery=PASS protocol=FAIL
T04 delivery=PASS protocol=PASS
T05 delivery=PASS protocol=PASS
T06 delivery=PASS protocol=PASS
```

### Preliminary scores

- **artifact_score: 77.15/100**
- **delivery_adjusted_score: 77.15/100**
- **strict_protocol_adjusted_score: 60.00/100**
- **delivery success: 6/6 = 100%**
- **protocol success: 4/6 = 66.7%**

### Immediate comparison with Baseline 001

- artifact: **40.71 -> 77.15** = **+36.44 points**
- strict: **30.00 -> 60.00** = **+30.00 points**, exactly 2x the original strict score
- end-to-end delivery reliability: **3/6 -> 6/6**, 50% -> 100%
- agentic artifact score is **5.71 points below** the recovered single-shot semantic-content diagnostic 82.86; that recovered score remains diagnostic and must not be treated as strict end-to-end delivery.

Preliminary research interpretation:
> Direct filesystem delivery through Pi removes the dominant full-file JSON delivery bottleneck for the same local 4B model. Every benchmark task delivered its required artifacts, and both artifact and strict end-to-end scores improved substantially. Remaining weaknesses include genuine task correctness gaps and strict protocol adherence, with T02 and T03 failing the preregistered protocol condition despite successful delivery.

Do NOT freeze per-task conclusions yet. Exact task points, test counts, final text/protocol reason, tool events, timings, memory/swap trajectory and adapter validity still require ingestion from `run-summary.json`.

## Frozen score definitions for Pi Agentic 001

1. `artifact_score` — raw frozen benchmark runner score of resulting scoring tree.
2. `delivery_adjusted_score` — task points count only when Pi exits cleanly and every permitted editable file is actually created/changed.
3. `strict_protocol_adjusted_score` — delivery points additionally require non-editable inputs unchanged, no unexpected persistent files, and final assistant text exactly `DONE`.

No rule changes after observing results.

## Exact next step

Ingest the complete agentic run summary from:

`<repository-root>/results-local/coding-agentic-pi/20260818-214848/run-summary.json`

Required inspection:
1. T01–T06 `points_earned`, `tests_passed`, `tests_total`;
2. exact protocol failure reason for T02 and T03;
3. per-task final assistant text and observed tool sequence;
4. whether any non-editable input changed or unexpected files persisted;
5. adapter/event/JSONL errors;
6. per-task and total elapsed time;
7. memory-before/after-task/final snapshots, swap and `ollama ps`;
8. any evidence of out-of-workspace access or other preregistration violation.

If valid:
- freeze canonical Pi Agentic Coding Benchmark 001 result;
- write final comparison against Baseline 001;
- identify which remaining points are genuine code/comprehension failures vs protocol-only failures.

Only after canonical freeze return to Qwen Code safe-mode 4096 as a secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — full Pi agentic benchmark completed; preliminary 77.15 artifact/delivery and 60.00 strict; full summary ingestion next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Which tasks account for the 22.85 artifact points still missing from 100?
- Why exactly did T02 and T03 fail strict protocol?
- How much total runtime/swap did the six-task agentic benchmark consume?
- Did Ollama resident size again rise during sustained multi-turn file-tool use?
- How much of the original 30.00 -> 82.86 gap is now closed by filesystem delivery versus still-limited semantic correctness?
- How often does Qwen 4B violate exact protocol when its artifacts are otherwise correct?
- What is the best practical validation/retry strategy for daily use without contaminating benchmark comparability?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
