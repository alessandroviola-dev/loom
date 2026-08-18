# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen canonical; repeated-call memory-retention probe preregistered and ready
Checkpoint: PI_AGENTIC_001_FROZEN_MEMORY_RETENTION_PROBE_READY

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, especially Apple M1 / 8 GB unified memory.

## Reference system

- Apple M1
- 8 GB unified memory
- macOS
- canonical local repo: `<repository-root>`
- GitHub: `Ilcoach/loom` (private)
- Ollama: `0.32.14`
- Qwen Code: `0.21.13`
- Pi: `0.84.2`
- canonical local agent model: `qwen3.5:4b-mlx`

## Pi production-configuration constraint

The user's normal Pi installation is production tooling with existing OpenAI API/Codex authentication, sessions, skills/extensions/packages and customizations.

LOOM added Ollama only as an additional provider in `~/.pi/agent/models.json`.

Do not reset, delete or replace the user's normal Pi configuration.

Controlled LOOM benchmark/probe runs use a run-local `PI_CODING_AGENT_DIR`, so production Pi state is neither loaded nor modified.

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

Main finding:
> Code/semantic quality was materially stronger than strict delivery. JSON/full-file transport and protocol reliability were major bottlenecks.

Detailed record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Harness Comparison 001

Canonical record:
- `research/agents/harness-comparison-001.md`

Qwen Code normal-config read-only at 4096:
- estimated initial prompt **4474 tokens** vs hard limit **4096**
- no tool call reached
- semantic API failure before model load
- only Git delta was automatic `"$version": 4` settings migration, now adopted

Pi minimal read-only at 4096:
- `read` succeeded
- final response exactly `# LOOM`
- tracked tree unchanged
- Ollama after **4.2 GB, 100% GPU, context 4096**
- swap delta **+651.87 MB**
- elapsed ~34 s

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

Historical validator defect was patched so functional and strict outcomes are separate.

## Pi Agentic Coding Benchmark 001 — FROZEN / CANONICAL

Canonical record:
- `research/agents/pi-agentic-benchmark-001.md`

Preregistered plan:
- `research/agents/pi-agentic-benchmark-001-plan.md`

Historical preliminary record:
- `research/agents/pi-agentic-benchmark-001-preliminary.md` — **SUPERSEDED**

Adapter:
- `scripts/pi_agentic_benchmark.py`

Run id: `20260818-214848`
Run directory:
- `results-local/coding-agentic-pi/20260818-214848`
Summary:
- `results-local/coding-agentic-pi/20260818-214848/run-summary.json`

### Frozen configuration

- Coding Benchmark 01 v1.0.1
- Pi 0.84.2
- Ollama / `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- one attempt per task
- no hidden-test feedback
- tools: `read,write,edit`
- no bash/test feedback
- isolated run-local `PI_CODING_AGENT_DIR`
- extensions/skills/prompt templates/themes/context files disabled
- no retries, prompt rescue, JSON salvage or manual repair

### Canonical scores

- **artifact_score: 77.15/100**
- **delivery_adjusted_score: 77.15/100**
- **strict_protocol_adjusted_score: 60.00/100**
- **delivery success: 6/6 = 100%**
- **protocol success: 4/6 = 66.7%**

Versus Frozen Coding Baseline 001:
- artifact: **40.71 -> 77.15** = **+36.44**
- strict: **30.00 -> 60.00** = **+30.00**, exactly 2x
- delivery: **3/6 -> 6/6**, 50% -> 100%
- agentic artifact remains **5.71** below recovered semantic diagnostic 82.86; recovered semantic remains diagnostic, not end-to-end

### Per-task result

| Task | Score | Tests | Delivery | Protocol | Wall time |
|---|---:|---:|---|---|---:|
| T01 | 15.00/15 | 6/6 | PASS | PASS | 52.759 s |
| T02 | 4.29/15 | 2/7 | PASS | FAIL | 143.436 s |
| T03 | 12.86/15 | 6/7 | PASS | FAIL | 81.407 s |
| T04 | 8.57/15 | 4/7 | PASS | PASS | 141.575 s |
| T05 | 21.43/25 | 6/7 | PASS | PASS | 48.690 s |
| T06 | 15.00/15 | 7/7 | PASS | PASS | 138.960 s |

Task wall-time sum: **606.827 s**.
Whole run elapsed: approximately **612.14 s (~10m12s)**.

### Correctness vs protocol loss

Artifact score is missing **22.85 points** from 100. These are genuine frozen-test deficits:
- T02: -10.71
- T03: -2.14
- T04: -6.43
- T05: -3.57

The additional artifact-to-strict gap is **17.15 points**, exactly T02 + T03 earned artifact points.

For T02 and T03:
- delivery succeeded
- non-editable inputs unchanged
- no unexpected files
- no event/JSONL errors
- strict failure came only from final text not being exactly `DONE`

Therefore the 17.15 strict-only loss is **final-output protocol noncompliance**, not delivery failure.

### Raw workspace isolation — VALIDATED

Retrospective inspector:
- `scripts/inspect_pi_agentic_run.py`

Result:
- `workspace_path_safety: PASS`
- all explicit tool paths were relative task-workspace paths
- no absolute paths
- no `..` parent traversal
- session cwd values were task-specific temporary directories
- no out-of-workspace file access observed

T02 emitted one `write` tool-start with empty args (`path=None`), followed by a valid write to `buggy.py`. It created no unexpected file and does not invalidate workspace safety.

### Provider-reported usage

Last non-zero cumulative usage snapshot per task:

| Task | Input | Output | Total |
|---|---:|---:|---:|
| T01 | 2349 | 125 | 2474 |
| T02 | 4177 | 63 | 4240 |
| T03 | 2891 | 32 | 2923 |
| T04 | 4093 | 120 | 4213 |
| T05 | 2439 | 142 | 2581 |
| T06 | 3607 | 171 | 3778 |
| **Total** | **19556** | **653** | **20209** |

These are cumulative provider-reported session usage totals. Do not interpret values above 4096 as simultaneous prompt context occupancy.

### Resource trajectory — key new problem

Before run:
- PhysMem used **5318M**
- memory free **73%**
- swap used **1544.12M / 3072M**
- Ollama model unloaded

After tasks:
- T01: Ollama **4.4 GB**, swap **1999.06M**
- T02: Ollama **5.2 GB**, swap **2517.12M**
- T03: Ollama **5.6 GB**, swap **3274.75M**; swap capacity 4096M
- T04: Ollama **6.4 GB**, swap **3790.12M**; capacity 5120M
- T05: Ollama **6.8 GB**, swap **4215.06M**
- T06: Ollama **7.2 GB**, swap **4839.12M**; capacity 6144M

Final:
- PhysMem used **7352M**
- memory free **24%**
- swap used **4823.12M** = **+3279.00M** vs start
- Ollama **7.2 GB, 100% GPU, context 4096**

Finding:
> Pi + Qwen 3.5 4B MLX can perform full file-agentic coding work at 4096 on M1/8 GB, but sustained use creates severe memory/swap pressure.

The monotonic Ollama reported-size growth **4.4 -> 7.2 GB** at fixed context 4096 is observed but not causally explained. Do not call it a leak, KV-cache growth, tool-history retention or runtime bug without controlled evidence.

## Pi Memory Retention Probe 001 — PREREGISTERED / READY

Plan:
- `research/agents/pi-memory-retention-probe-001-plan.md`

Runner:
- `scripts/pi_memory_retention_probe.py`

Question:
> Does Ollama reported allocation grow across repeated identical small Pi calls when the model remains warm, or was Agentic 001's 4.4 -> 7.2 GB trajectory mainly task/high-water dependent?

Frozen design:

### Warm arm
- stop model once before arm
- 4 separate identical Pi/read calls
- no `ollama stop` between calls
- same tiny file, same prompt, same tool surface, context 4096

### Cold control
- 2 identical calls
- `ollama stop` before each call

Metrics per iteration:
- Pi success/final text/read tool
- provider usage
- wall time
- PhysMem
- memory free percentage
- swap used
- Ollama reported size/context/processor

Guardrails:
- abort warm arm and stop model if memory free falls below 8%
- abort warm arm and stop model if swap used exceeds 5600 MB

This probe does not modify any frozen benchmark score.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/pi_memory_retention_probe.py
python3 scripts/pi_memory_retention_probe.py
```

Preserve the complete terminal output.

After the probe:
1. ingest warm vs cold size/swap trajectory;
2. classify whether simple repeated-call accumulation is supported;
3. if needed add a lower-level Ollama/MLX probe;
4. only then return to Qwen Code safe-mode 4096 as a secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent: ACTIVE — Pi Agentic 001 frozen canonical; memory-retention probe ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Is the 4.4 -> 7.2 GB Ollama size trajectory reproducible with identical repeated calls?
- Does `ollama stop` reset the post-call allocation to a stable cold baseline?
- Is further lower-level Ollama/MLX instrumentation needed?
- What validation/retry strategy best improves daily-use reliability without changing benchmark results?
- How much of Qwen Code's 4096 failure is always-on context versus normal tool/core prompt surface?

## Continuation rule

Before starting a new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
