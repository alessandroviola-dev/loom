# Pi Agentic Coding Benchmark 001 — Canonical Result

Date: 2026-08-18
Run id: `20260818-214848`
Status: **FROZEN / CANONICAL**

## Frozen configuration

- Benchmark: LOOM Coding Benchmark 01 v1.0.1
- Agent harness: Pi `0.84.2`
- Provider/runtime: Ollama
- Model: `qwen3.5:4b-mlx`
- Context: `4096`
- Max output: `2048`
- One attempt per task
- Hidden tests excluded from agent workspaces
- Exposed tools: `read,write,edit`
- No bash/test feedback
- Run-local isolated `PI_CODING_AGENT_DIR`
- Extensions, skills, prompt templates, themes and context files disabled for the benchmark run
- User production Pi configuration not loaded or modified
- No retries, hidden-test rescue, prompt rescue, JSON salvage or manual repair
- Scoring protocol preregistered in `research/agents/pi-agentic-benchmark-001-plan.md`

Run directory:
`results-local/coding-agentic-pi/20260818-214848`

Summary:
`results-local/coding-agentic-pi/20260818-214848/run-summary.json`

## Canonical scores

- **artifact_score: 77.15/100**
- **delivery_adjusted_score: 77.15/100**
- **strict_protocol_adjusted_score: 60.00/100**
- **delivery success: 6/6 = 100%**
- **protocol success: 4/6 = 66.7%**

## Per-task result

| Task | Score | Tests | Delivery | Protocol | Wall time |
|---|---:|---:|---|---|---:|
| T01 | 15.00/15 | 6/6 | PASS | PASS | 52.759 s |
| T02 | 4.29/15 | 2/7 | PASS | FAIL | 143.436 s |
| T03 | 12.86/15 | 6/7 | PASS | FAIL | 81.407 s |
| T04 | 8.57/15 | 4/7 | PASS | PASS | 141.575 s |
| T05 | 21.43/25 | 6/7 | PASS | PASS | 48.690 s |
| T06 | 15.00/15 | 7/7 | PASS | PASS | 138.960 s |

Task wall-time sum: **606.827 s**.
Whole run elapsed from summary timestamps: approximately **612.14 s (~10m12s)**.

## Delivery result

All six tasks delivered their required editable artifact.

No task failed because of JSON/full-file transport, adapter parsing or missing output files.

This closes the dominant delivery failure seen in the frozen single-shot baseline, where only 3/6 tasks were successfully delivered by the adapter.

## Genuine correctness deficit

Artifact score is missing **22.85 points** from 100. These are frozen-test correctness/comprehension deficits:

- T02: **10.71 points missing** — 2/7 tests passed
- T03: **2.14 points missing** — 6/7 tests passed
- T04: **6.43 points missing** — 4/7 tests passed
- T05: **3.57 points missing** — 6/7 tests passed
- T01 and T06: full credit

No hidden-test feedback was available to Pi/Qwen during any task.

## Strict protocol deficit

The additional gap from artifact/delivery **77.15** to strict **60.00** is exactly **17.15 points**.

That equals the earned artifact points of T02 + T03:

- T02: 4.29
- T03: 12.86
- total: **17.15**

For both T02 and T03:

- delivery succeeded;
- non-editable inputs remained unchanged;
- no unexpected files persisted;
- no event errors occurred;
- no JSONL parse errors occurred;
- the only strict-protocol failure was final assistant text not being exactly `DONE`.

T02 appended `DONE` after an explanation of the Python bool/int issue.
T03 appended `DONE` after a long source-code analysis.

Therefore the 17.15-point strict-only loss is classified as **final-output protocol noncompliance**, not delivery failure.

## Raw tool-path isolation validation

A retrospective inspector parsed the saved Pi JSONL events and checked every `tool_execution_start` path.

Result:

- `workspace_path_safety: PASS`
- every explicit file path was relative to the task workspace;
- no absolute path was used;
- no `..` parent traversal was used;
- session `cwd` values were task-specific temporary directories;
- no out-of-workspace file access was observed.

Observed paths were limited to benchmark files such as:
- `solution.py`
- `buggy.py`
- `source.py`
- `answer.json`
- `order.py`
- `pricing.py`

T02 also emitted one `write` tool-start event with empty args (`path=None`). It did not identify an external path, did not create an unexpected persistent file, and was followed by a valid write to `buggy.py`. It is recorded as a minor tool-call anomaly but does not violate the preregistered workspace boundary.

This closes the final isolation-validation requirement.

## Provider-reported usage

Pi JSON mode exposed non-zero provider usage for every task. The last non-zero usage snapshot per task is treated as the cumulative provider-reported usage for that task session, not as simultaneous context occupancy.

| Task | Input | Output | Total |
|---|---:|---:|---:|
| T01 | 2349 | 125 | 2474 |
| T02 | 4177 | 63 | 4240 |
| T03 | 2891 | 32 | 2923 |
| T04 | 4093 | 120 | 4213 |
| T05 | 2439 | 142 | 2581 |
| T06 | 3607 | 171 | 3778 |
| **Total** | **19556** | **653** | **20209** |

Because Pi reports cumulative provider usage across a session, values above 4096 here must not be interpreted as a single simultaneous prompt exceeding the configured context window.

## Resource trajectory

Memory before run:

- PhysMem used: **5318M**
- system-wide memory free: **73%**
- swap used: **1544.12M / 3072M**
- Ollama model unloaded

After each task:

- T01: Ollama **4.4 GB**, swap **1999.06M**, memory free 16%
- T02: Ollama **5.2 GB**, swap **2517.12M**, memory free 14%
- T03: Ollama **5.6 GB**, swap **3274.75M**, swap capacity expanded to 4096M
- T04: Ollama **6.4 GB**, swap **3790.12M**, capacity 5120M
- T05: Ollama **6.8 GB**, swap **4215.06M**, capacity 5120M
- T06: Ollama **7.2 GB**, swap **4839.12M**, capacity 6144M

Final snapshot:

- PhysMem used: **7352M**
- system-wide memory free: **24%**
- swap used: **4823.12M**
- swap delta vs start: **+3279.00M**
- Ollama: **7.2 GB, 100% GPU, context 4096**

Research finding:

> Pi + Qwen 3.5 4B MLX is practically capable of full file-agentic coding work at context 4096 on the Apple M1 / 8 GB reference machine, but sustained multi-task use creates severe memory and swap pressure.

The monotonic Ollama reported-size growth from **4.4 GB to 7.2 GB** at fixed context 4096 is observed but **not causally explained**. Do not label it as a leak, KV-cache growth, tool-history retention or MLX/Ollama bug without a controlled follow-up experiment.

## Comparison with Frozen Coding Baseline 001

Single-shot baseline:

- artifact: **40.71/100**
- strict delivery-adjusted: **30.00/100**
- delivery success: **3/6 = 50%**
- recovered semantic-content diagnostic: **82.86/100**

Pi agentic:

- artifact: **77.15/100**
- delivery-adjusted: **77.15/100**
- strict protocol-adjusted: **60.00/100**
- delivery success: **6/6 = 100%**

Deltas:

- artifact: **+36.44 points**
- strict: **+30.00 points** — exactly 2x the original strict score
- delivery reliability: **50% -> 100%**
- agentic artifact remains **5.71 points below** the recovered semantic-content diagnostic 82.86

Canonical interpretation:

> Replacing fragile full-file JSON transport with direct filesystem tools through Pi removes the dominant delivery bottleneck for the same local 4B model and materially improves end-to-end coding performance. The remaining limits are now primarily genuine task correctness and strict instruction/protocol adherence, not file delivery.

## Follow-up research

Highest-priority next experiment:

1. investigate repeated-call memory retention / Ollama reported-size growth at fixed context 4096;
2. distinguish accumulation across separate Pi invocations from per-task/context high-water behavior;
3. only after that return to Qwen Code safe-mode 4096 as a secondary harness-overhead diagnostic.

This result is frozen. Future fixes, retries or alternate harness settings must use new run IDs and must not modify this record's score classification.
