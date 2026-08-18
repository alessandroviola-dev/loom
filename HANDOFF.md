# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen; invocation-count and direct runtime retention probes complete; multi-turn probes 001/002 exposed control defects at deep depth; turn-gated Probe 003 preregistered and ready
Checkpoint: PI_MULTITURN_002_PARTIAL_PI_MULTITURN_003_READY

## Mission

Study how capable local LLMs and coding agents can run usefully on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.

Reference repo: `Ilcoach/loom`
Local path: `<repository-root>`

Reference stack:
- Apple M1, 8 GB unified memory
- Ollama 0.32.14
- Pi 0.84.2
- Qwen Code 0.21.13
- canonical model `qwen3.5:4b-mlx`
- canonical context 4096 unless an experiment explicitly changes it

## Pi production configuration constraint

The user's normal Pi installation contains real OpenAI API/Codex auth, sessions and customizations. LOOM added Ollama only as an additional provider.

Do not reset, overwrite or repurpose normal Pi state. Controlled experiments use run-local `PI_CODING_AGENT_DIR` and explicit per-run resources.

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Benchmark: Coding Benchmark 01 v1.0.1
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical views:
- strict single-shot delivery-adjusted **30.00/100**
- artifact **40.71/100**
- structured delivery **3/6**
- recovered semantic diagnostic **82.86/100**
- weighted generation **16.01 tok/s**
- peak observed swap **2486.94 MB**

Key finding:
> Full-file JSON transport/delivery was a major bottleneck; recovered code quality was materially better than strict end-to-end delivery.

Canonical record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Harness finding

Qwen Code normal configuration at context 4096:
- estimated initial prompt ~4474 tokens
- hard limit 4096
- fails before first tool call

Pi minimal read-only at 4096:
- succeeds with `read`
- returns `# LOOM`

Conclusion:
> Harness/context overhead can determine feasibility on the 8 GB reference machine.

Record:
- `research/agents/harness-comparison-001.md`

## Pi Agentic Coding Benchmark 001 — FROZEN / CANONICAL

Canonical record:
- `research/agents/pi-agentic-benchmark-001.md`

Run id: `20260818-214848`
Configuration:
- Coding Benchmark 01 v1.0.1
- Pi 0.84.2
- Ollama / `qwen3.5:4b-mlx`
- context 4096
- max output 2048
- one attempt/task
- tools `read,write,edit`
- no bash/test feedback
- hidden tests excluded from workspaces
- isolated run-local Pi directory
- no retries/rescue/manual repair

Canonical scores:
- artifact **77.15/100**
- delivery-adjusted **77.15/100**
- strict protocol-adjusted **60.00/100**
- delivery **6/6**
- strict protocol **4/6**

Versus single-shot:
- artifact **40.71 -> 77.15** (+36.44)
- strict **30.00 -> 60.00** (+30.00)
- delivery **3/6 -> 6/6**

Correctness deficit: **22.85 points**.
Additional strict-only protocol loss: **17.15 points**, entirely T02/T03 final-output noncompliance.

Workspace safety: PASS.
Provider-reported cumulative usage: 19,556 input + 653 output = 20,209 total.

## Agentic 001 memory finding

Whole run ~10m12s.

Before:
- swap 1544.12 MB
- model unloaded

After:
- swap 4823.12 MB (+3279.00 MB)
- Ollama SIZE 7.2 GB
- 100% GPU
- context 4096

Ollama SIZE by task:
- **4.4 -> 5.2 -> 5.6 -> 6.4 -> 6.8 -> 7.2 GB**

Observed but not causally explained. Do not label as a leak, KV-cache effect or MLX bug without controlled evidence.

## Pi Memory Retention Probe 001 — COMPLETED

Record:
- `research/agents/pi-memory-retention-probe-001.md`

Run id: `20260818-223251`

Four identical small warm Pi calls:
- SIZE **4.1 -> 4.3 -> 4.4 -> 4.5 GB**
- swap **2050.06 -> 1922.06 MB**

Cold controls both returned **4.1 GB**.

Conclusion:
> Invocation count alone does not explain Agentic 001's 7.2 GB trajectory.

## Ollama Context Retention Probe 001 — COMPLETED / VALID

Canonical record:
- `research/runtime/ollama-context-retention-probe-001.md`

Run id: `20260818-223909`
Direct Ollama `/api/generate`, Pi absent, context 4096.

| Condition | Prompt tokens | SIZE |
|---|---:|---:|
| warm-low | 418 | 4.1 GB |
| warm-medium | 1618 | 4.3 GB |
| warm-high | 3018 | 4.5 GB |
| warm-low-after-high | 418 | 4.6 GB |
| cold-low | 418 | 4.1 GB |
| cold-high | 3018 | 4.2 GB |

Interpretation:
1. Runtime-level prompt/context-pressure allocation is real; Pi is not required.
2. Warm high-water retention is real.
3. `ollama stop` resets low-pressure baseline to 4.1 GB.
4. Prompt pressure alone remains insufficient to explain 7.2 GB.
5. Ollama SIZE and macOS swap are distinct metrics.

## Pi Multi-turn Memory Probe 001 — INVALID FOR CAUSAL DEPTH

Run id: `20260818-224524`
Record:
- `research/agents/pi-multiturn-memory-probe-001.md`

Observed:
- nominal 1-turn: expected 1 read, observed 3, SIZE 4.3 GB — invalid
- nominal 4-turn: exact 4 reads, SIZE 4.3 GB — valid
- nominal 8-turn: expected 8 reads, observed 14, SIZE 4.9 GB — invalid

Cause:
> Built-in `read` allowed speculative filename guesses, so hidden future filenames did not mechanically constrain round-trip depth.

## Pi Multi-turn Memory Probe 002 — PARTIALLY VALID

Plan:
- `research/agents/pi-multiturn-memory-probe-002-plan.md`

Result:
- `research/agents/pi-multiturn-memory-probe-002.md`

Runner:
- `scripts/pi_multiturn_memory_probe_v2.py`

Custom extension:
- `scripts/pi_probe_step_extension.ts`

Run id: `20260818-225330`

Observed:
- `cold-1turn`: VALID — calls=1, advanced=1, SIZE **4.2 GB**, swap 1786.81 MB, usage 1102
- `cold-4turn`: VALID — calls=4, advanced=4, SIZE **4.3 GB**, swap 1949.75 MB, usage 1608
- `cold-8turn`: INVALID — calls=7, advanced=1, invalid=6, SIZE 4.5 GB, swap 1955.50 MB, usage 2406
- warm follow-up skipped

Valid inference:
> Increasing controlled true depth from 1 to 4 changed reported SIZE only **4.2 -> 4.3 GB** (+0.1 GB). The available valid subset does not show a large depth effect.

Invalid inference:
> The 4.5 GB depth-8 value cannot be treated as an eight-valid-turn measurement because only one call advanced state and six later calls failed the opaque-token protocol.

New finding:
> Opaque-token propagation itself became a model-control bottleneck at deep depth. This is an experiment-control failure, not evidence that eight Pi turns cannot execute.

## Pi Multi-turn Memory Probe 003 — PREREGISTERED / READY

Plan:
- `research/agents/pi-multiturn-memory-probe-003-plan.md`

Runner:
- `scripts/pi_multiturn_memory_probe_v3.py`

Custom extension:
- `scripts/pi_probe_step_extension_v3.ts`

### Control design

`probe_step` takes no arguments. Target depth and completed count live entirely inside the extension.

The extension:
- resets a per-turn counter on Pi `turn_start`;
- permits at most one `probe_step` call in each model turn;
- blocks a second/sibling call in the same turn;
- advances exactly one internal step per successful call;
- emits `CONTINUE` until target depth and `STOP` at the final step.

The runner independently records Pi turn indices. A condition is valid only if:
- tool count exactly equals target depth;
- advanced count exactly equals target depth;
- every tool call has a distinct turn index;
- no same-turn duplicate is blocked;
- no other tool appears;
- final result reaches requested depth and final assistant text is exactly `DONE`.

Cold conditions:
- 1 turn
- 4 turns
- 8 turns

Warm follow-up:
- 1 turn immediately after a valid 8-turn condition without unloading

Guardrails:
- free memory <8% => unload/prevent warm follow-up
- swap >5600 MB => unload/prevent warm follow-up

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/pi_multiturn_memory_probe_v3.py
python3 scripts/pi_multiturn_memory_probe_v3.py
```

Preserve complete output from `=== COLD DEPTH ARM ===` through `=== COMPLETE ===`.

Expected key fields:
- `calls`
- `advanced`
- `distinct_turns`
- `blocked_same_turn`
- `ollama_size`
- `swap`
- `usage_total`

After the run:
1. validate true distinct-turn depths 1/4/8;
2. classify SIZE vs controlled round-trip depth;
3. if depth is still insufficient, move to a benchmark-workload-shape probe;
4. only afterward return to Qwen Code safe-mode 4096 as secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 benchmark/baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: ACTIVE — Agentic 001 frozen; invocation/context probes complete; Probe 002 valid through depth 4 but control fails at depth 8; turn-gated Probe 003 ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Does true distinct-turn depth from 1 to 8 materially increase Ollama SIZE at fixed context 4096?
- Does a valid 8-turn loop leave retained high-water for a subsequent tiny session?
- If controlled depth remains insufficient, which workload-shape feature of Agentic 001 drives the 7.2 GB high-water?
- What validation/retry strategy best improves daily-use Pi reliability?
- How much of Qwen Code's 4096 failure is always-on context versus core/tool surface?

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
