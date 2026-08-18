# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen; identical-call memory probe completed; direct Ollama context-pressure probe preregistered and ready
Checkpoint: PI_MEMORY_RETENTION_001_COMPLETE_OLLAMA_CONTEXT_PROBE_READY

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

## Pi production configuration constraint

The user's normal Pi setup contains real OpenAI API/Codex authentication, sessions and customizations.

LOOM added Ollama only as an additional provider. Do not reset or overwrite normal Pi state.

Controlled experiments use run-local isolation where appropriate.

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
> The single-shot model generated much better code than its strict end-to-end score suggested; full-file JSON transport/delivery was a major bottleneck.

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
- proves harness/context overhead can determine practical feasibility on 8 GB

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
- hidden tests excluded from agent workspaces
- isolated run-local Pi directory
- no retries/rescue/manual repair

Canonical scores:
- **artifact: 77.15/100**
- **delivery-adjusted: 77.15/100**
- **strict protocol-adjusted: 60.00/100**
- delivery **6/6**
- strict protocol **4/6**

Versus single-shot:
- artifact **40.71 -> 77.15** (+36.44)
- strict **30.00 -> 60.00** (+30.00; 2x)
- delivery **3/6 -> 6/6**

Per-task:
- T01: 15.00/15, 6/6
- T02: 4.29/15, 2/7
- T03: 12.86/15, 6/7
- T04: 8.57/15, 4/7
- T05: 21.43/25, 6/7
- T06: 15.00/15, 7/7

Correctness deficit from 100 artifact: **22.85 points**.
Additional artifact-to-strict loss: **17.15 points**, entirely T02/T03 final-output protocol noncompliance.

Raw tool-path safety:
- PASS
- no absolute paths
- no `..`
- no out-of-workspace access observed

Provider-reported cumulative usage across six task sessions:
- input **19,556**
- output **653**
- total **20,209**

Do not interpret cumulative usage totals as simultaneous context occupancy.

## Agentic 001 memory finding

Whole run ~10m12s.

Before:
- swap used **1544.12 MB**
- model unloaded
- memory free 73%

After:
- swap used **4823.12 MB** (+3279.00 MB)
- Ollama reported **7.2 GB**, 100% GPU, context 4096
- memory free 24%

Ollama trajectory by task:
- 4.4 -> 5.2 -> 5.6 -> 6.4 -> 6.8 -> 7.2 GB

Observed but not causally explained. Do not call this a leak, KV-cache effect or MLX bug without controlled evidence.

## Pi Memory Retention Probe 001 — COMPLETED

Canonical record:
- `research/agents/pi-memory-retention-probe-001.md`

Run id: `20260818-223251`

Question:
> Does simple repetition of identical Pi calls reproduce the Agentic 001 4.4 -> 7.2 GB growth?

Warm arm, four identical calls without unloading:

| Iteration | Ollama size | Swap | Free | Usage | Wall |
|---|---:|---:|---:|---:|---:|
| warm-01 | 4.1 GB | 2050.06 MB | 22% | 1008 | 17.638 s |
| warm-02 | 4.3 GB | 1954.06 MB | 14% | 1015 | 9.874 s |
| warm-03 | 4.4 GB | 1930.06 MB | 17% | 1010 | 9.329 s |
| warm-04 | 4.5 GB | 1922.06 MB | 16% | 986 | 7.505 s |

Cold controls with `ollama stop` before every call:
- cold-01: **4.1 GB**, swap 1984.31 MB
- cold-02: **4.1 GB**, swap 2056.12 MB

### Canonical interpretation

1. Some warm retention exists: **4.1 -> 4.5 GB** across four identical calls.
2. It is small relative to Agentic 001's **4.4 -> 7.2 GB**.
3. Warm swap did **not** accumulate; it declined ~128 MB across the arm.
4. `ollama stop` resets observed post-call allocation to **4.1 GB**.
5. Therefore **invocation count alone is insufficient** to explain Agentic 001.
6. Evidence is consistent with retained warm allocation plus workload-dependent high-water behavior, but the causal mechanism remains unknown.

## Ollama Context Retention Probe 001 — PREREGISTERED / READY

Plan:
- `research/runtime/ollama-context-retention-probe-001-plan.md`

Runner:
- `scripts/ollama_context_retention_probe.py`

Purpose:
> Remove Pi entirely and test whether direct Ollama/MLX allocation scales with prompt pressure and retains a high-water mark.

Frozen design:
- direct `/api/generate`
- model `qwen3.5:4b-mlx`
- context 4096
- think false
- temperature 0
- output budget 8 tokens

Warm sequence:
1. low prompt pressure
2. medium
3. high
4. low-after-high

Cold controls:
1. cold-low after unload
2. cold-high after unload

Authoritative pressure measurement is Ollama `prompt_eval_count`, not nominal repetition count.

Guardrails:
- abort warm arm if memory free <8%
- abort warm arm if swap >5600 MB

Interpretation goals:
- determine whether allocation scales with prompt pressure even without Pi;
- determine whether a high-pressure call leaves a retained high-water allocation for a later small call;
- separate runtime behavior from agent-harness/tool-turn effects.

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/ollama_context_retention_probe.py
python3 scripts/ollama_context_retention_probe.py
```

Preserve complete terminal output.

After that:
1. ingest direct warm/cold prompt-pressure results;
2. decide whether retention is runtime-level or requires Pi/multi-turn behavior;
3. if needed isolate multi-turn/tool-round-trip effects;
4. then return to Qwen Code safe-mode 4096 as secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent/runtime investigation: ACTIVE — Pi Agentic 001 frozen; Pi memory retention probe complete; direct Ollama context probe ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- Does direct Ollama/MLX allocation scale with prompt pressure at fixed context 4096?
- Does a high-pressure direct call leave a retained high-water allocation for later small calls?
- If direct Ollama remains flat, are Pi multi-turn/tool round trips responsible for the larger Agentic 001 growth?
- What real-world validation/retry strategy best improves Pi reliability?
- How much of Qwen Code's 4096 failure is always-on context vs core/tool surface?

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
