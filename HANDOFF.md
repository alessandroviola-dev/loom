# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — matched 4096 read-only comparison complete: Pi succeeds where Qwen Code normal config fails before first tool call
Checkpoint: PI_4096_READONLY_SMOKE_PASSED_QWEN_CODE_OVERHEAD_CONFIRMED

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

## Phase 3 — local coding agent

### Qwen Code read-only smoke 001 — FAILED BEFORE TOOL CALL

Run id: `20260818-211009`

Matched conditions relevant to comparator:
- model: `qwen3.5:4b-mlx`
- Ollama local endpoint
- context: 4096
- read-only task: read LOOM `README.md` and return first Markdown heading

Observed:
- model resolved correctly;
- macOS Seatbelt active (`permissive-open`);
- no tool call reached;
- estimated initial prompt: **4474 tokens**;
- hard context limit: **4096**;
- approximately **378 tokens over limit**;
- always-on Qwen Code context warning: approximately **1429 tokens**;
- process returned exit code 0 despite semantic API error;
- runner reported a working-tree status delta that still requires exact local inspection.

Conclusion:
> Qwen Code in normal configuration does not fit inside context 4096 on the reference setup before the first minimal tool call.

### Pi Ollama provider addition — COMPLETED NON-DESTRUCTIVELY

LOOM added only `providers.ollama` in `~/.pi/agent/models.json`.

Verified listing:

```text
provider  model           context  max-out  thinking  images
ollama    qwen3.5:4b-mlx  4.1K     2.0K     no        no
```

Untouched by LOOM setup:
- OpenAI API credentials/configuration;
- OpenAI/Codex account authentication;
- saved default provider/model settings;
- sessions;
- skills;
- extensions;
- packages.

### Pi read-only smoke 001 — PASSED

Run id: `pi-20260818-212407`

Command harness:
- provider: `ollama`
- model: `qwen3.5:4b-mlx`
- context: 4096
- exposed tool set: `read` only
- ephemeral: `--no-session`
- output mode: JSON

Observed terminal result:

```text
Exit code: 0
Provider/model: ollama/qwen3.5:4b-mlx
Tools: ['read']
Result: '# LOOM'
Working tree unchanged: True
Success: True
```

Result directory:
- `results-local/agent-smoke/pi-20260818-212407`
- summary: `results-local/agent-smoke/pi-20260818-212407/smoke-summary.json`

### Matched 4096 comparison — KEY RESULT

Same reference hardware, model family/build, Ollama runtime, context limit and equivalent read-only repository task:

| Harness | Context | First read tool | Result |
|---|---:|---|---|
| Qwen Code 0.21.13 normal config | 4096 | Not reached | FAIL — initial prompt estimated 4474 tokens |
| Pi 0.84.2 minimal read harness | 4096 | Reached (`read`) | PASS — returned `# LOOM` |

Research finding:
> Agent-harness overhead is now a measured practical constraint on the 8 GB reference machine. At the same 4096-token model context, Pi can complete the minimal tool task while Qwen Code normal configuration cannot reach the first tool call.

Important scope:
- this does **not** yet prove Pi is globally better than Qwen Code;
- Pi was deliberately run with only one exposed tool, while Qwen Code normal configuration carries a larger tool/context surface;
- the result does prove that harness/context overhead can determine feasibility at small context windows.

## Committed tooling

- `.qwen/settings.json`
- `scripts/qwen_code_readonly_smoke.py`
- `scripts/pi_add_ollama_provider.py`
- `scripts/pi_readonly_smoke.py`

## Exact next step

Ingest the two smoke summaries before changing context or running edit tests.

Required local files:
1. Qwen Code:
   `results-local/agent-smoke/20260818-211009/smoke-summary.json`
2. Pi:
   `results-local/agent-smoke/pi-20260818-212407/smoke-summary.json`

Use them to compare:
- memory before/after;
- swap before/after;
- `ollama ps` resident/context state;
- wall/runtime data available in each harness;
- exact Qwen `git_status_before` vs `git_status_after` delta;
- any event/token metadata Pi exposes.

After ingesting those metrics, run a controlled Pi edit+test smoke before attempting full Coding Benchmark 01 agentic mode. Qwen Code safe-mode 4096 and/or context 8192 remain separate experiments.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — matched read-only 4096 comparison complete; Pi passed, Qwen Code normal config failed on context overhead; metric ingestion next
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 other runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- How much lower is Pi's first-turn context/tool-schema overhead than Qwen Code's?
- What are the RAM/swap differences between the two smoke runs?
- What caused the Qwen smoke working-tree status delta?
- Can Pi perform reliable edit + test loops at context 4096?
- Does Qwen Code safe-mode fit at 4096?
- What is the minimum practical context for Qwen Code normal configuration?
- What memory/swap cost is added by Qwen Code context scaling to 8192?
- How much can agentic workflows close the strict 30.00 → recovered 82.86 gap?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
