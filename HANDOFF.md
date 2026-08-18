# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Pi Agentic Coding Benchmark 001 frozen; runtime prompt-pressure/high-water retention confirmed; Pi multi-turn memory probe preregistered and ready
Checkpoint: OLLAMA_CONTEXT_RETENTION_001_COMPLETE_PI_MULTITURN_PROBE_READY

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

Controlled experiments use run-local `PI_CODING_AGENT_DIR` isolation where appropriate.

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
- **4.4 -> 5.2 -> 5.6 -> 6.4 -> 6.8 -> 7.2 GB**

Observed but not causally explained. Do not call this a leak, KV-cache effect or MLX bug without controlled evidence.

## Pi Memory Retention Probe 001 — COMPLETED

Canonical record:
- `research/agents/pi-memory-retention-probe-001.md`

Run id: `20260818-223251`

Four identical tiny warm Pi calls:
- **4.1 -> 4.3 -> 4.4 -> 4.5 GB**
- swap **2050.06 -> 1922.06 MB** rather than accumulating

Cold controls with unload:
- cold-01 **4.1 GB**
- cold-02 **4.1 GB**

Conclusion:
> Some warm retention exists, but simple invocation count alone is far too small to explain Agentic 001's 7.2 GB trajectory.

## Ollama Context Retention Probe 001 — COMPLETED / VALID

Canonical result:
- `research/runtime/ollama-context-retention-probe-001.md`

Preregistered plan:
- `research/runtime/ollama-context-retention-probe-001-plan.md`

Run id: `20260818-223909`
Run directory:
- `results-local/ollama-context-retention/20260818-223909`

Direct Ollama `/api/generate`, Pi absent, context 4096:

| Condition | Prompt tokens | Ollama SIZE | Swap | Free |
|---|---:|---:|---:|---:|
| warm-low | 418 | 4.1 GB | 1925.50 MB | 15% |
| warm-medium | 1618 | 4.3 GB | 2374.12 MB | 17% |
| warm-high | 3018 | 4.5 GB | 2407.56 MB | 20% |
| warm-low-after-high | 418 | 4.6 GB | 2205.38 MB | 12% |
| cold-low | 418 | 4.1 GB | 2189.38 MB | 17% |
| cold-high | 3018 | 4.2 GB | 2386.62 MB | 23% |

All calls succeeded.

### Canonical interpretation

1. **Runtime-level prompt/context-pressure allocation is confirmed.** Pi is not required for Ollama SIZE to grow.
2. Warm prompt pressure produced **4.1 -> 4.3 -> 4.5 GB** as prompt tokens rose 418 -> 1618 -> 3018.
3. **Retained high-water behavior is confirmed:** after warm-high, a later 418-token call remained at **4.6 GB** rather than returning to 4.1 GB.
4. `ollama stop` resets the observed low-pressure baseline: cold-low = **4.1 GB**.
5. Prompt pressure alone remains **insufficient** to explain Agentic 001's **7.2 GB**. Even cold-high at 3018 tokens was only **4.2 GB**.
6. `ollama ps` SIZE and macOS swap are not equivalent metrics; warm-low-after-high retained higher SIZE while swap decreased.

Do not infer the internal cause. Leak/KV-cache/allocator-fragmentation claims remain unsupported.

## Pi Multi-turn Memory Probe 001 — PREREGISTERED / READY

Plan:
- `research/agents/pi-multiturn-memory-probe-001-plan.md`

Runner:
- `scripts/pi_multiturn_memory_probe.py`

Question:
> Is within-session model/tool round-trip depth the missing factor that materially raises Ollama high-water allocation beyond the ~4.5–4.6 GB seen from invocation count and direct prompt pressure?

Design uses forced sequential file chains: each read result reveals the exact filename of the next file, so Pi cannot know later paths in advance.

Cold-start conditions:
1. `cold-1turn` — exactly 1 sequential read
2. `cold-4turn` — exactly 4 sequential reads
3. `cold-8turn` — exactly 8 sequential reads

Then, without unloading after the deepest valid condition:
4. `warm-1turn-after-8` — tiny one-read session to test retained high-water

Validation requires:
- exit 0
- exact `DONE`
- exact expected number/order of read paths
- all paths safe/relative
- no parse/event errors

Metrics:
- wall time
- provider usage
- PhysMem/free%
- swap
- Ollama SIZE/context/processor

Guardrails:
- free memory <8% => stop/unload
- swap >5600 MB => stop/unload

## Exact next step

On the reference Mac:

```bash
cd "<repository-root>"
git pull
python3 -m py_compile scripts/pi_multiturn_memory_probe.py
python3 scripts/pi_multiturn_memory_probe.py
```

Preserve complete terminal output.

Expected sections:
- `=== COLD DEPTH ARM ===`
- `cold-1turn`
- `cold-4turn`
- `cold-8turn`
- `=== WARM RETENTION ARM ===`
- `warm-1turn-after-8`
- `=== COMPLETE ===`

After that:
1. classify size vs tool-depth relationship;
2. decide whether multi-turn explains a substantial part of Agentic 001's 7.2 GB;
3. if still insufficient, move to a lower-level/runtime probe closer to benchmark workload shape;
4. then return to Qwen Code safe-mode 4096 as secondary harness diagnostic.

## Roadmap state

- Phase 0 foundation: DONE
- Phase 1 inference baseline: DONE
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN
- Phase 3 local coding agent/runtime investigation: ACTIVE — Agentic 001 frozen; invocation and direct context probes complete; forced multi-turn probe ready
- Phase 4 llama.cpp: queued
- Phase 5 direct MLX: queued
- Phase 6 Colibrì / SSD streaming / MoE: queued
- Phase 7 extended runtimes: queued
- Phase 8 synthesis: queued

## Open research questions

- How strongly does Ollama SIZE scale with forced within-session tool/turn depth at fixed context 4096?
- Does a deep tool loop leave a retained high-water visible to a subsequent tiny session?
- If multi-turn remains insufficient, what workload property differentiates the full benchmark from all reduced probes?
- What real-world validation/retry strategy best improves Pi reliability?
- How much of Qwen Code's 4096 failure is always-on context vs core/tool surface?

## Continuation rule

Before a new experiment, read this file. After every meaningful experiment/decision/result, update this file before moving to the next checkpoint.
