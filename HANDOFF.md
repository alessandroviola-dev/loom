# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 summary fully ingested; scores/task failures/memory trajectory classified; raw tool-path validation is the last prerequisite to canonical freeze
Checkpoint: PI_AGENTIC_001_SUMMARY_INGESTED_RAW_PATH_VALIDATION_PENDING

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, especially Apple M1 / 8 GB unified memory.

## Reference system

- Apple M1
- 8 GB unified memory
- macOS
- Canonical local repo: `<repository-root>`
- GitHub: `Ilcoach/loom` (private)
- Ollama: `0.32.14`
- Qwen Code: `0.21.13`
- Pi: `0.84.2`
- canonical local agent model: `qwen3.5:4b-mlx`

## Pi production-configuration constraint

The user's normal Pi installation is production tooling with existing OpenAI API/Codex authentication, sessions, skills/extensions/packages and customizations.

LOOM added Ollama only as an additional provider in `~/.pi/agent/models.json`.

Do not reset, delete or replace the user's normal Pi configuration.

Controlled benchmark runs use a run-local `PI_CODING_AGENT_DIR`, so production Pi state is neither loaded nor modified.

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Benchmark: Coding Benchmark 01 v1.0.1
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical score views:
- strict single-shot delivery-adjusted: **30.00/100**
- structured-output delivery success: **3/6 = 50%**
- artifact score: **40.71/100**
- recovered semantic-content diagnostic: **82.86/100**
- weighted prompt processing: **186.46 tok/s**
- weighted generation: **16.01 tok/s**
- peak observed swap: **2486.94 MB**

Main baseline finding:
> Code/semantic quality was materially stronger than strict delivery. JSON/full-file transport and protocol reliability were major bottlenecks.

Detailed baseline record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Harness Comparison 001

Canonical record:
- `research/agents/harness-comparison-001.md`

Qwen Code normal-config read-only at context 4096:
- estimated initial prompt **4474 tokens** vs hard limit **4096**;
- no tool call reached;
- semantic API failure before model load;
- only Git delta was automatic `"$version": 4` settings migration, now adopted.

Pi minimal read-only at context 4096:
- `read` succeeded;
- final response exactly `# LOOM`;
- tracked tree unchanged;
- Ollama after **4.2 GB, 100% GPU, context 4096**;
- swap delta **+651.87 MB**;
- elapsed ~34 s.

Conclusion:
> A minimal Pi tool harness is operational at 4096 where normal Qwen Code is not. Harness/context overhead is a practical feasibility constraint on the 8 GB machine.

## Pi Edit+Test Smoke 001

Canonical record:
- `research/agents/pi-edit-test-smoke-001.md`

Run id: `pi-edit-20260818-213432`
Status: **FUNCTIONAL PASS / STRICT OUTPUT FAIL**

- tools: `read,edit,bash`
- independent unittest: 4/4 pass
- solution changed; tests unchanged; tracked LOOM tree unchanged
- final response violated exact `PASS` requirement
- elapsed ~114 s
- swap delta **+655.31 MB**
- Ollama after **4.8 GB, 100% GPU, context 4096**

Historical validator defect was patched so functional and strict outcomes are now separate.

## Pi Agentic Coding Benchmark 001 — COMPLETED / VALIDATION NEAR COMPLETE

Preregistered protocol:
- `research/agents/pi-agentic-benchmark-001-plan.md`

Adapter:
- `scripts/pi_agentic_benchmark.py`

Preliminary record:
- `research/agents/pi-agentic-benchmark-001-preliminary.md`

Run id: `20260818-214848`
Run directory:
- `results-local/coding-agentic-pi/20260818-214848`
Summary:
- `results-local/coding-agentic-pi/20260818-214848/run-summary.json`

### Frozen configuration

- Coding Benchmark 01 v1.0.1
- Pi 0.84.2
- Ollama / `qwen3.5:4b-mlx`
- context **4096**
- max output **2048**
- one attempt per task
- no hidden-test feedback
- tools: `read,write,edit`
- no bash/test feedback
- run-local isolated `PI_CODING_AGENT_DIR`
- extensions/skills/prompt templates/themes/context files disabled
- hidden tests excluded from agent workspaces and applied only afterward in a separate scoring tree
- no retries, prompt rescue, JSON salvage or manual repair

### Score views

- **artifact_score: 77.15/100**
- **delivery_adjusted_score: 77.15/100**
- **strict_protocol_adjusted_score: 60.00/100**
- **delivery success: 6/6 = 100%**
- **protocol success: 4/6 = 66.7%**

Versus frozen single-shot baseline:
- artifact: **40.71 -> 77.15** = **+36.44**
- strict: **30.00 -> 60.00** = **+30.00**, exactly 2x
- delivery: **3/6 -> 6/6**, 50% -> 100%
- agentic artifact remains **5.71** below recovered semantic diagnostic 82.86; recovered semantic remains diagnostic, not end-to-end.

### Per-task canonical summary from run-summary.json

| Task | Score | Tests | Delivery | Protocol | Wall time |
|---|---:|---:|---|---|---:|
| T01 | 15.00/15 | 6/6 | PASS | PASS | 52.759 s |
| T02 | 4.29/15 | 2/7 | PASS | FAIL | 143.436 s |
| T03 | 12.86/15 | 6/7 | PASS | FAIL | 81.407 s |
| T04 | 8.57/15 | 4/7 | PASS | PASS | 141.575 s |
| T05 | 21.43/25 | 6/7 | PASS | PASS | 48.690 s |
| T06 | 15.00/15 | 7/7 | PASS | PASS | 138.960 s |

Task wall time sum: **606.827 s**.
Whole run elapsed from summary timestamps: approximately **612.14 s (~10m12s)**.

### Remaining correctness deficit

Artifact score is missing **22.85 points** from 100. These are genuine frozen-test correctness/comprehension deficits:
- T02: **10.71 points missing** (2/7 tests pass)
- T03: **2.14 points missing** (6/7)
- T04: **6.43 points missing** (4/7)
- T05: **3.57 points missing** (6/7)
- T01/T06: full credit

No hidden-test feedback was available to the agent.

### Strict-protocol deficit

The additional gap from artifact 77.15 to strict 60.00 is **17.15 points**.

That equals the earned artifact points of T02 + T03:
- T02: 4.29
- T03: 12.86
- total: **17.15**

For both T02 and T03:
- delivery succeeded;
- non-editable inputs remained unchanged;
- no unexpected files persisted;
- no event errors;
- no JSONL parse errors;
- protocol failure was caused by final assistant text not being exactly `DONE`.

T02 final text included an explanation of the bool/int issue followed by `DONE`.
T03 final text included a long source-code analysis followed by `DONE`.

Therefore T02/T03 strict failures are **final-output protocol failures**, not delivery failures.

### Resource trajectory

Memory before run:
- PhysMem used: **5318M**
- system-wide memory free: **73%**
- swap used: **1544.12M** / 3072M total
- Ollama model unloaded

After tasks:
- T01: Ollama **4.4 GB**, swap **1999.06M**, free 16%
- T02: Ollama **5.2 GB**, swap **2517.12M**, free 14%
- T03: Ollama **5.6 GB**, swap **3274.75M**, swap capacity auto-expanded to 4096M
- T04: Ollama **6.4 GB**, swap **3790.12M**, capacity 5120M
- T05: Ollama **6.8 GB**, swap **4215.06M**, capacity 5120M
- T06: Ollama **7.2 GB**, swap **4839.12M**, capacity 6144M

Final snapshot:
- PhysMem used: **7352M** (+2034M vs start)
- system-wide memory free: **24%**
- swap used: **4823.12M** (+3279.00M vs start)
- Ollama: **7.2 GB, 100% GPU, context 4096**

Important interpretation:
> Sustained multi-task agentic use creates severe memory/swap pressure on the 8 GB reference Mac. Ollama's reported model allocation rose monotonically from 4.4 to 7.2 GB while configured context remained 4096.

Do **not** yet attribute that growth to a leak, KV cache, tool history or MLX/Ollama retention. The cause is unmeasured.

## Final validation still pending — raw tool paths

The summary records tool names but not tool arguments. The preregistered isolation rule forbids parent/absolute/out-of-workspace access. Non-editable files and persistent outputs are clean, but read/write/edit paths from raw JSONL must still be checked before canonical freeze.

Official Pi JSON mode documents `tool_execution_start` as containing `toolName` and `args`, and `message_update` as containing provider `usage`.

New retrospective inspector:
- `scripts/inspect_pi_agentic_run.py`

It reads the already-saved raw JSONL, prints every tool path, rejects absolute or `..` paths, and also prints the last non-zero provider usage per task when available. It does **not** rerun the model.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 scripts/inspect_pi_agentic_run.py \
  --run-dir "<repository-root>/results-local/coding-agentic-pi/20260818-214848"
```

Preserve the complete output.

If `workspace_path_safety: PASS` and no other raw anomaly appears:
1. freeze `Pi Agentic Coding Benchmark 001` as canonical;
2. create final result record `research/agents/pi-agentic-benchmark-001.md`;
3. mark preliminary record superseded;
4. then run a lightweight repeated-call memory-retention probe before returning to Qwen Code safe-mode.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi Agentic 001 summary ingested; raw tool-path isolation validation pending before canonical freeze
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Did any Pi file tool attempt an absolute or parent-directory path during Agentic 001?
- What provider token/usage telemetry exists in the raw Pi JSONL?
- Why did Ollama reported allocation grow 4.4 -> 7.2 GB across separate Pi invocations at context 4096?
- Is that growth reproducible with identical repeated calls, or is it a task/context high-water effect?
- What validation/retry strategy best improves daily-use reliability without changing benchmark results?
- How much of Qwen Code's 4096 failure is always-on context versus its normal tool/core prompt surface?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
