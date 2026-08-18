# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen; practical cause of sustained memory growth narrowed to cumulative warm runtime high-water; Qwen Code safe-mode 4096 diagnostic preregistered and ready
Checkpoint: PI_COLD_REPLAY_001_COMPLETE_QWEN_SAFE_MODE_4096_READY

## Mission

Study practical local LLM/agent execution on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.

Reference repo: `Ilcoach/loom`
Local path: `<repository-root>`

Reference stack:
- Apple M1, 8 GB unified memory
- Ollama 0.32.14
- Pi 0.84.2
- Qwen Code 0.21.13
- canonical model `qwen3.5:4b-mlx`
- canonical context 4096 unless an experiment explicitly changes it

## Production Pi constraint

The user's normal Pi installation contains real OpenAI API/Codex auth, sessions and customizations. LOOM added Ollama only as an additional provider.

Do not reset/overwrite normal Pi state. Controlled experiments use run-local `PI_CODING_AGENT_DIR` and explicit per-run resources.

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Benchmark: Coding Benchmark 01 v1.0.1
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical views:
- artifact **40.71/100**
- strict delivery-adjusted **30.00/100**
- structured delivery **3/6**
- recovered semantic diagnostic **82.86/100**
- weighted prompt throughput **186.46 tok/s**
- weighted generation **16.01 tok/s**

Record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

Key finding:
> Full-file JSON delivery was a major bottleneck; recovered code quality was much stronger than strict end-to-end delivery.

## Harness comparison

Historical Qwen Code normal-config read-only at context 4096:
- Qwen Code 0.21.13
- estimated initial prompt ~4474 tokens
- hard limit 4096
- always-on context warning ~1429 tokens
- no tool call
- model never loaded

Pi minimal read-only at 4096:
- succeeds with `read`
- returns `# LOOM`

Conclusion:
> Harness/context packaging can determine feasibility on the 8 GB machine.

Record:
- `research/agents/harness-comparison-001.md`

## Pi Agentic Coding Benchmark 001 — FROZEN / CANONICAL

Run id: `20260818-214848`
Record:
- `research/agents/pi-agentic-benchmark-001.md`

Configuration:
- Coding Benchmark 01 v1.0.1
- Pi 0.84.2
- Ollama / `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- one attempt/task
- tools `read,write,edit`
- no bash/test feedback
- hidden tests excluded
- isolated run-local Pi directory
- no retries/rescue/manual repair

Canonical scores:
- artifact **77.15/100**
- delivery-adjusted **77.15/100**
- strict protocol-adjusted **60.00/100**
- delivery **6/6**
- protocol **4/6**

Versus single-shot:
- artifact **40.71 -> 77.15** (+36.44)
- strict **30.00 -> 60.00** (+30.00)
- delivery **3/6 -> 6/6**

Correctness deficit from 100 artifact: **22.85 points**.
Additional strict-only protocol loss: **17.15 points**, entirely T02/T03 final-output noncompliance.

Workspace/tool-path safety: PASS.
Provider usage across task sessions: **19,556 input + 653 output = 20,209 total**.

### Historical sustained memory trajectory

Post-task Ollama SIZE:
- T01 4.4 GB
- T02 5.2 GB
- T03 5.6 GB
- T04 6.4 GB
- T05 6.8 GB
- T06 7.2 GB

Swap:
- start 1544.12 MB
- final 4823.12 MB
- delta +3279.00 MB

Context remained 4096 and processor 100% GPU.

## Memory investigation — current canonical conclusion

### 1. Invocation-count probe

`Pi Memory Retention Probe 001`, run `20260818-223251`:
- four identical small warm Pi calls: **4.1 -> 4.3 -> 4.4 -> 4.5 GB**
- warm swap did not accumulate
- cold controls reset to **4.1 GB**

Conclusion: invocation count alone is insufficient.

Record:
- `research/agents/pi-memory-retention-probe-001.md`

### 2. Direct Ollama context-pressure probe

`Ollama Context Retention Probe 001`, run `20260818-223909`, Pi absent:
- 418 prompt tokens -> 4.1 GB
- 1618 -> 4.3 GB
- 3018 -> 4.5 GB
- 418 after warm-high -> 4.6 GB
- cold-low -> 4.1 GB
- cold-high 3018 -> 4.2 GB

Conclusion:
> Runtime-level prompt-pressure allocation and warm high-water retention are real, but prompt pressure alone is insufficient to explain 7.2 GB.

Record:
- `research/runtime/ollama-context-retention-probe-001.md`

### 3. Synthetic multi-turn probes

Probe 001:
- invalid at nominal depth 1/8 because built-in read allowed speculative filename guesses
- only exact 4-read condition valid at 4.3 GB

Probe 002:
- valid depth 1: 4.2 GB
- valid depth 4: 4.3 GB
- depth 8 invalid due opaque-token protocol failures

Probe 003:
- valid depth 1: 4.1 GB
- valid depth 4: 4.3 GB
- depth 8 invalid because model terminated after first valid turn
- runner/extension plumbing verified correct; model-generated final text incorrectly said `Step 1/3`

Valid inference:
> Controlled true round-trip depth from 1 to 4 changes SIZE by only ~0.1–0.2 GB. Synthetic depth alone does not explain the late 6–7 GB state.

Decision:
> Stop iterating synthetic deep-turn protocols for this question.

Records:
- `research/agents/pi-multiturn-memory-probe-001.md`
- `research/agents/pi-multiturn-memory-probe-002.md`
- `research/agents/pi-multiturn-memory-probe-003.md`

### 4. Pi Agentic Cold Replay 001 — COMPLETED

Run id: `20260818-230858`
Record:
- `research/agents/pi-agentic-cold-replay-001.md`

Design:
- exact frozen T01–T06 agent-facing workload shape
- same wrapper/files/tool surface as Agentic 001
- `ollama stop` before every task
- memory/workload replay only; canonical benchmark scores unchanged

Results:

| Task | Cold tools | Hist tools | Cold usage | Hist usage | Cold SIZE | Warm hist SIZE |
|---|---:|---:|---:|---:|---:|---:|
| T01 | 1 | 2 | 2146 | 2474 | 4.3 GB | 4.4 GB |
| T02 | 5 | 8 | 3833 | 4240 | 4.7 GB | 5.2 GB |
| T03 | 3 | 2 | 4217 | 2923 | 4.5 GB | 5.6 GB |
| T04 | 6 | 5 | 5494 | 4213 | 4.9 GB | 6.4 GB |
| T05 | 4 | 3 | 4026 | 2581 | 4.5 GB | 6.8 GB |
| T06 | 0 | 2 | N/A | 3778 | 4.4 GB | 7.2 GB |

T06 replay is **invalid for workload comparison**: it timed out at ~300 s with no tool call and no provider-usage snapshot. Do not use its 4.4 GB value as a cold T06 requirement.

Strongest evidence:
- T03 cold had more usage/tools than historical yet was **4.5 vs 5.6 GB**.
- T04 cold had more usage/tools than historical yet was **4.9 vs 6.4 GB**.
- T05 cold had more usage/tools than historical yet was **4.5 vs 6.8 GB**.

Warm-minus-cold gap for valid T01–T05 grows with sequence position:
- **0.1, 0.5, 1.1, 1.5, 2.3 GB**.

### Practical memory conclusion

> Cross-task retained warm runtime high-water is a **major contributor** to the sustained Agentic 001 memory trajectory. Individual cold tasks T01–T05 remain within 4.3–4.9 GB even when some cold replays are heavier by tool/usage measures than the historical warm run.

This does not identify the internal mechanism. Do not call it a memory leak, KV-cache effect, MLX allocator bug or fragmentation without lower-level evidence.

Practical implication:
> Periodic model unload/reload is a plausible memory-pressure mitigation for long local-agent sessions on 8 GB, with a latency tradeoff that can be evaluated later in the daily-use profile.

The memory investigation is sufficiently resolved for Phase 3 progression; lower-level MLX internals are not blocking the next agent comparison.

## Qwen Code Safe-Mode 4096 Diagnostic — PREREGISTERED / READY

Plan:
- `research/agents/qwen-code-safe-mode-4096-plan.md`

Runner:
- `scripts/qwen_code_safe_mode_smoke.py`

Purpose:
> Test whether Qwen Code's minimal official safe-mode harness can form/execute the first local request at context 4096 once optional context/customizations are removed.

Frozen characteristics:
- Qwen Code 0.21.13
- `--safe-mode`
- explicit `--auth-type openai`
- explicit model `qwen3.5:4b-mlx`
- explicit Ollama OpenAI endpoint/key
- output cap 2048
- project model provider remains the canonical 4096 configuration
- read-only task: read `README.md` and return exactly `# LOOM`
- approval mode `plan`
- JSON output
- model unloaded before run
- repository status/settings diff captured before/after
- memory/swap/Ollama state captured before/after

Interpretation:
- success => optional Qwen custom/context surface was the binding cause of historical preflight failure;
- pre-inference failure => core safe-mode harness still does not fit 4096;
- request reaches Ollama but fails later => classify separately as model/tool transport behavior.

No 8192 rescue is permitted inside this experiment.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/qwen_code_safe_mode_smoke.py
python3 scripts/qwen_code_safe_mode_smoke.py
```

Preserve complete output, including any stderr warning.

After the run:
1. classify whether safe mode reaches Ollama at 4096;
2. compare with historical normal-config 4474-token preflight failure;
3. decide whether Qwen Code remains useful as a primary local comparator;
4. only consider 8192 as a separate context-scaling experiment if it still adds value.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 baseline: DONE
- Phase 2 Coding Benchmark/Baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: ACTIVE — memory question practically resolved; Qwen safe-mode diagnostic ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD/MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
