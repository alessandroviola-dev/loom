# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen; synthetic memory probes have isolated invocation/context effects but deep synthetic control is unreliable; exact-workload cold replay preregistered and ready
Checkpoint: PI_MULTITURN_003_PARTIAL_AGENTIC_COLD_REPLAY_001_READY

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

Canonical:
- artifact **40.71/100**
- strict delivery-adjusted **30.00/100**
- structured delivery **3/6**
- recovered semantic diagnostic **82.86/100**
- weighted prompt throughput **186.46 tok/s**
- weighted generation **16.01 tok/s**

Key finding:
> Full-file JSON delivery was a major bottleneck; recovered code quality was much stronger than strict end-to-end delivery.

Record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Harness comparison

Qwen Code normal config at 4096:
- initial prompt estimated ~4474 tokens
- hard limit 4096
- fails before first tool call

Pi minimal read-only at 4096:
- succeeds with `read`
- returns `# LOOM`

Conclusion:
> Harness/context overhead can determine feasibility on the 8 GB machine.

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

### Agentic 001 memory trajectory

Historical post-task Ollama SIZE:
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

Observed but not causally explained. Do not label as leak/KV-cache/MLX bug without evidence.

## Memory investigation summary

### Pi Memory Retention Probe 001

Run `20260818-223251`.
Four identical small warm Pi calls:
- SIZE **4.1 -> 4.3 -> 4.4 -> 4.5 GB**
- swap did not accumulate; it declined 2050.06 -> 1922.06 MB

Cold controls both returned 4.1 GB.

Conclusion:
> Invocation count alone is insufficient.

Record:
- `research/agents/pi-memory-retention-probe-001.md`

### Ollama Context Retention Probe 001

Run `20260818-223909`, Pi absent, direct `/api/generate`, context 4096.

- 418 prompt tokens -> 4.1 GB
- 1618 -> 4.3 GB
- 3018 -> 4.5 GB
- 418 after warm-high -> 4.6 GB
- cold-low -> 4.1 GB
- cold-high 3018 -> 4.2 GB

Conclusion:
> Runtime-level prompt-pressure allocation and warm high-water retention are real, but prompt pressure alone remains insufficient to explain 7.2 GB.

Record:
- `research/runtime/ollama-context-retention-probe-001.md`

### Pi Multi-turn Memory Probe 001

Run `20260818-224524`.
Invalid for causal depth inference because speculative filename reads broke requested 1/8 depths. Only nominal 4-turn was exact at 4.3 GB.

Record:
- `research/agents/pi-multiturn-memory-probe-001.md`

### Pi Multi-turn Memory Probe 002

Run `20260818-225330`.
Token-gated custom tool.

Valid subset:
- depth 1: 4.2 GB
- depth 4: 4.3 GB

Depth 8 invalid: 7 tool calls, only 1 valid advance, 6 token failures.

Record:
- `research/agents/pi-multiturn-memory-probe-002.md`

### Pi Multi-turn Memory Probe 003

Run `20260818-230129`.
Turn-gated no-argument custom tool; target depth stored inside extension; one tool call max per Pi turn.

Observed:
- `cold-1turn`: VALID, calls=1, advanced=1, distinct turns, SIZE **4.1 GB**, swap 2036.69 MB, usage 927
- `cold-4turn`: VALID, calls=4, advanced=4, distinct turns, SIZE **4.3 GB**, swap 2061.81 MB, usage 1245
- `cold-8turn`: INVALID, target=8 but model stopped after first valid tool turn; SIZE 4.3 GB
- warm follow-up skipped

Depth-8 final text was `Done! Step 1/3 completed successfully.`

Code verification confirms runner passes `LOOM_PROBE_DEPTH=str(depth)` and extension reads that variable. For depth 8 the tool would have returned `STEP 1/8` + `CONTINUE`; therefore `1/3` is model-generated protocol error, not configuration mismatch.

Valid inference across synthetic probes:
> Controlled true depth from 1 to 4 changes reported SIZE only about **+0.1 to +0.2 GB**. This is far too small to explain Agentic 001's later 7.2 GB state.

Do not infer depth-8 memory cost from this run.

Record:
- `research/agents/pi-multiturn-memory-probe-003.md`

Decision:
> Stop iterating synthetic deep-turn probes for now. Qwen's rigid-protocol reliability at depth 8 is itself interfering with experimental control. Move to the real frozen benchmark workload shape.

## Pi Agentic Cold Replay 001 — PREREGISTERED / READY

Plan:
- `research/agents/pi-agentic-cold-replay-001-plan.md`

Runner:
- `scripts/pi_agentic_cold_replay.py`

Purpose:
> Replay the exact frozen T01-T06 agent-facing workload, but execute `ollama stop` before every task, so each task starts cold. Compare each cold post-task SIZE/tool count/usage to the historical warm Agentic 001 sequence.

Frozen replay properties:
- same Coding Benchmark 01 v1.0.1 task prompts
- same task wrapper from `pi_agentic_benchmark.py`
- same supplied files
- same `read,write,edit` tool surface
- no bash/tests/hidden-test feedback
- one attempt per task
- context 4096
- max output 2048
- isolated run-local Pi directory
- `ollama stop` before every T01-T06

This is a memory/workload replay, **not a benchmark rescore**. Canonical benchmark scores must not change.

Historical warm reference embedded in the runner:
- T01 size 4.4 GB, tools 2, usage 2474
- T02 size 5.2 GB, tools 8, usage 4240
- T03 size 5.6 GB, tools 2, usage 2923
- T04 size 6.4 GB, tools 5, usage 4213
- T05 size 6.8 GB, tools 3, usage 2581
- T06 size 7.2 GB, tools 2, usage 3778

Interpretation:
- cold tasks near 4.1-4.6 GB => cumulative warm retention is a major driver;
- individual cold tasks near 6+ GB => workload-specific high-water is a major driver;
- intermediate values => mixed workload + retention effect.

If replay tool count/usage differs materially from the historical task, record the mismatch and avoid treating that task as perfectly matched.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/pi_agentic_cold_replay.py
python3 scripts/pi_agentic_cold_replay.py
```

Preserve output from `=== COLD TASK REPLAY ===` through `=== COMPLETE ===`.

Expected lines report for each T01-T06:
- replay tool count vs historical tool count
- replay provider usage vs historical usage
- cold post-task SIZE vs historical warm SIZE
- context/swap/free memory

After this run:
1. classify cumulative retention vs per-workload high-water;
2. decide whether lower-level MLX/Ollama instrumentation is still needed;
3. then return to Qwen Code safe-mode 4096 as secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 baseline: DONE
- Phase 2 Coding Benchmark/Baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: ACTIVE — exact-workload cold replay ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD/MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
