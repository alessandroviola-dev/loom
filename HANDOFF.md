# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen; invocation-count and direct runtime retention probes complete; first multi-turn probe invalidated by uncontrolled speculative reads; corrected token-gated multi-turn probe preregistered and ready
Checkpoint: PI_MULTITURN_001_INVALID_PI_MULTITURN_002_READY

## Mission

Study how capable local LLMs and coding agents can run usefully on constrained consumer hardware, initially Apple M1 / 8 GB unified memory.

Reference repo: `Ilcoach/loom`
Local path: `<repository-root>`

Reference stack:
- Apple M1, 8 GB unified memory
- Ollama 0.32.14
- Pi 0.84.2
- Qwen Code 0.21.13
- canonical model: `qwen3.5:4b-mlx`
- canonical context: 4096 unless an experiment explicitly changes it

## Pi production-configuration constraint

The user's normal Pi installation contains real OpenAI API/Codex authentication, sessions and customizations. LOOM added Ollama only as an additional provider.

Do not reset, overwrite or repurpose normal Pi state.

Controlled experiments use run-local `PI_CODING_AGENT_DIR` isolation and explicit per-run resources.

## Frozen Coding Baseline 001

Run id: `20260818-203156`
Benchmark: Coding Benchmark 01 v1.0.1
Model/runtime: `qwen3.5:4b-mlx`, Ollama/MLX, context 4096

Canonical views:
- strict single-shot delivery-adjusted: **30.00/100**
- artifact: **40.71/100**
- structured delivery: **3/6**
- recovered semantic diagnostic: **82.86/100**
- weighted generation: **16.01 tok/s**
- peak observed swap: **2486.94 MB**

Key finding:
> Full-file JSON transport/delivery was a major bottleneck; recovered code quality was materially better than strict end-to-end delivery.

Canonical record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Harness finding

Qwen Code normal configuration at context 4096:
- initial prompt estimate ~4474 tokens
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

Per-task:
- T01: 15.00/15, 6/6
- T02: 4.29/15, 2/7
- T03: 12.86/15, 6/7
- T04: 8.57/15, 4/7
- T05: 21.43/25, 6/7
- T06: 15.00/15, 7/7

Correctness deficit: **22.85 points**.
Additional strict-only protocol loss: **17.15 points**, entirely T02/T03 final-output noncompliance.

Workspace safety:
- PASS
- no absolute paths
- no `..`
- no out-of-workspace access observed

Provider-reported cumulative usage across task sessions:
- input 19,556
- output 653
- total 20,209

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

Cold controls:
- 4.1 GB
- 4.1 GB

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

Canonical interpretation:
1. Runtime-level prompt/context-pressure allocation is real; Pi is not required.
2. Warm high-water retention is real: low-after-high remains 4.6 GB.
3. `ollama stop` resets low-pressure baseline to 4.1 GB.
4. Prompt pressure alone remains insufficient to explain 7.2 GB.
5. Ollama SIZE and macOS swap are distinct metrics.

## Pi Multi-turn Memory Probe 001 — COMPLETED / INVALID FOR CAUSAL DEPTH

Preregistered plan:
- `research/agents/pi-multiturn-memory-probe-001-plan.md`

Result record:
- `research/agents/pi-multiturn-memory-probe-001.md`

Run id: `20260818-224524`

Observed:
- `cold-1turn`: INVALID, expected 1 read but observed 3; SIZE 4.3 GB
- `cold-4turn`: VALID, exactly 4 reads; SIZE 4.3 GB
- `cold-8turn`: INVALID, expected 8 reads but observed 14; SIZE 4.9 GB
- warm follow-up skipped because deepest condition was invalid

Why invalid:
> Built-in `read` allowed the model to emit speculative filename guesses. Hiding later filenames did not mechanically constrain tool count/order.

The 4.9 GB value from the 14-read run is exploratory only. It must not be used as a causal estimate of eight-turn memory cost because failed reads, usage and interaction history differ.

## Pi Multi-turn Memory Probe 002 — PREREGISTERED / READY

Plan:
- `research/agents/pi-multiturn-memory-probe-002-plan.md`

Runner:
- `scripts/pi_multiturn_memory_probe_v2.py`

Controlled extension:
- `scripts/pi_probe_step_extension.ts`

Official Pi behavior used by this design:
- explicit `--extension <path>` loads a selected extension;
- `--no-extensions` disables discovery but explicit extension paths still work;
- `--no-builtin-tools` removes built-in tools;
- `--tools probe_step` allowlists only the custom tool.

### Mechanical round-trip control

The extension registers one custom tool: `probe_step`.

For each condition:
1. runner creates a random opaque initial token;
2. model receives only that token;
3. a valid `probe_step(token)` advances one step;
4. each non-final result generates a fresh random 128-bit next token;
5. the next valid token is unknowable until the prior tool result is received;
6. wrong/reused tokens do not advance state;
7. final valid step returns `STOP`.

A condition is valid only if total tool calls exactly equal target depth and every call advanced successfully. Any speculative call invalidates the condition.

Cold-start conditions:
- 1 turn
- 4 turns
- 8 turns

Warm follow-up:
- 1 turn immediately after a valid 8-turn condition without unloading

Metrics:
- exact call/advance/invalid counts
- wall time
- provider usage
- PhysMem/free%
- swap
- Ollama SIZE/context/processor

Guardrails:
- free memory <8% => unload/prevent warm follow-up
- swap >5600 MB => unload/prevent warm follow-up

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/pi_multiturn_memory_probe_v2.py
python3 scripts/pi_multiturn_memory_probe_v2.py
```

Preserve complete output from:
- `=== COLD DEPTH ARM ===`
- `cold-1turn`
- `cold-4turn`
- `cold-8turn`
- `=== WARM RETENTION ARM ===`
- `warm-1turn-after-8`
- `=== COMPLETE ===`

If the explicit extension fails to load, preserve the exact stderr/output; do not alter production Pi config or manually install packages before review.

After the run:
1. validate exact controlled depths;
2. classify SIZE vs true round-trip depth;
3. decide whether multi-turn explains a material part of Agentic 001 high-water;
4. if still insufficient, move to workload-shape reproduction;
5. only afterward return to Qwen Code safe-mode 4096 as a secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 benchmark/baseline: DONE / FROZEN
- Phase 3 agent/runtime investigation: ACTIVE — Agentic 001 frozen; invocation and direct context probes complete; first multi-turn design invalidated; controlled Probe 002 ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Does true sequential within-session tool depth materially increase Ollama SIZE at fixed 4096 context?
- Does a valid 8-turn tool loop leave a retained high-water for a subsequent tiny session?
- If controlled depth remains insufficient, which workload-shape feature of Agentic 001 drives the 7.2 GB high-water?
- What validation/retry strategy best improves daily-use Pi reliability?
- How much of Qwen Code's 4096 failure is always-on context versus core/tool surface?

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
