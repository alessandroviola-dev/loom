# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Ollama single-shot adapter implemented; first benchmark run required on reference Mac
Checkpoint: OLLAMA_SINGLE_SHOT_ADAPTER_READY

## Mission

Study, test and eventually improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, with particular focus on making larger models usable on machines that normally cannot hold them entirely in RAM.

## Long-term destination

1. Build a practical self-hosted local coding agent with no per-token cloud usage limits.
2. Establish reproducible benchmarks for local inference on constrained hardware.
3. Explore quantization, offloading, unified memory, memory mapping, swap, SSD streaming and MoE expert streaming.
4. Compare Ollama, MLX, llama.cpp, Colibrì and other promising runtimes.
5. Determine the largest *useful*, not merely launchable, model configurations on small consumer machines.
6. If research reveals a useful gap, prototype LOOM-specific tooling/runtime techniques.

## Reference hardware

- Platform: Apple Silicon Mac
- SoC: Apple M1
- Unified memory: 8 GB
- OS: macOS

## Completed work

### 0. Project foundation
- Project name: `LOOM`.
- Tagline: `Big models. Small machines.`
- Private GitHub repository: `Ilcoach/loom`.
- Default branch: `main`.
- Initial project scaffold committed.
- `HANDOFF.md` is the canonical project state and is updated after every meaningful step.

### 1. Ollama baseline setup
- Ollama updated from 0.31.2 to a current MLX-capable build.
- Baseline model installed: `qwen3.5:4b-mlx`.
- MLX backend confirmed from Ollama logs.
- `ollama ps` confirmed 100% GPU execution.
- Context: 4096 tokens.

### 2. Baseline 001 performance
- Runtime: Ollama.
- Model: Qwen 3.5 4B MLX.
- Model resident size reported by Ollama: 4.3 GB.
- Output tokens: 256.
- Generation throughput: 15.02 tok/s.
- Prompt tokens: 56.
- Prompt throughput: 4.36 tok/s.
- Total request time: 30.01 s.
- Model load time: 0.07 s.

### 3. Memory baseline comparison

Without model loaded:
- Physical memory used: 6529 MB.
- Wired: 2058 MB.
- Compressed: 811 MB.
- Unused: 1101 MB.
- `memory_pressure` free percentage: 62%.
- Swap used: 1857.19 MB.

With Qwen 3.5 4B MLX loaded:
- Physical memory used: 7500 MB.
- Wired: 2037 MB.
- Compressed: 3131 MB.
- Unused: 130 MB.
- `memory_pressure` free percentage: 32%.
- Swap used: 3833.81 MB.

Observed delta while model is resident:
- Physical RAM used: +~971 MB.
- Compressed memory: +~2320 MB.
- Unused RAM: -~971 MB.
- Swap used: +~1976.62 MB.
- Memory-pressure free percentage: -30 points.

Interpretation: Qwen 3.5 4B MLX is practical at roughly 15 tok/s, but the 8 GB reference system is already close to its normal full-resident memory ceiling. Larger-model research must use more aggressive memory techniques.

### 4. Coding Benchmark 01 v1.0.0

Frozen at `benchmarks/coding/v1`.

Coverage and weights:
- T01 generation — 15.
- T02 debugging — 15.
- T03 comprehension — 15.
- T04 constrained refactoring — 15.
- T05 multi-file reasoning — 25.
- T06 implementation constraints — 15.
- Total — 100.

Infrastructure:
- exact prompts and fixtures;
- deterministic standard-library tests;
- `manifest.json`;
- `result-schema.json`;
- `runner.py`;
- explicit `single_shot` and `agentic` modes.

Validation before freeze:
- 41 / 41 tests passed with private reference implementations;
- runner returned 100 / 100;
- reference solutions were not committed;
- validation recorded in `benchmarks/coding/v1/VALIDATION.md`.

### 5. Ollama single-shot adapter

Implemented at `scripts/ollama_single_shot.py`.

Behavior:
- copies the frozen benchmark to an isolated directory under `results-local/`;
- never edits the frozen v1 tree;
- stops the selected Ollama model before the run by default, producing a cold first task and warm subsequent tasks;
- sends every task exactly once to the local `/api/generate` endpoint;
- does not expose tests to the model;
- supplies only the exact task prompt and allowed source/context files;
- requests JSON-only complete file replacements;
- writes only the task's permitted editable files;
- records raw Ollama API responses;
- records per-task prompt/generation token metrics and durations;
- records macOS memory/swap/`ollama ps` snapshots;
- executes the frozen benchmark runner after all tasks;
- writes `run-summary.json` under the ignored `results-local/` tree.

Reference invocation:

```bash
python3 scripts/ollama_single_shot.py \
  --model qwen3.5:4b-mlx \
  --context 4096
```

The adapter is implemented in the repository. Its first real end-to-end run must happen on the reference M1/8 GB Mac because this environment cannot access that machine's local Ollama daemon.

## Decisions frozen so far

- Project name: LOOM.
- Tagline: `Big models. Small machines.`
- Repository: `Ilcoach/loom`, private initially.
- Reference hardware: Apple M1 / 8 GB unified memory.
- Baseline runtime/model: Ollama + Qwen 3.5 4B MLX.
- Coding Benchmark 01 v1.0.0 is frozen.
- Benchmark quality, speed and memory are separate measurement dimensions.
- `single_shot` and `agentic` results are distinct experimental conditions.
- Failed or malformed model runs must be retained rather than silently retried.
- Tests are hidden from the model in `single_shot` mode.
- `HANDOFF.md` is the canonical project state.

## Roadmap state

1. Baseline 001. [DONE]
2. GitHub repository + scaffold. [DONE]
3. Coding Benchmark 01 design. [DONE]
4. Coding Benchmark 01 validation/freeze. [DONE]
5. Ollama single-shot adapter. [DONE]
6. Run Qwen 3.5 4B MLX on Coding Benchmark 01. [NEXT]
7. Store and analyze baseline coding result.
8. Repeat throughput test to investigate prompt-processing measurement.
9. Select a local coding-agent layer.
10. Connect the agent to Ollama and run Coding Benchmark 01 in `agentic` mode.
11. Test llama.cpp with larger Q4/Q3/Q2 configurations.
12. Test direct MLX.
13. Test Colibrì / SSD streaming / sparse MoE candidates.
14. Evaluate other Apple Silicon runtimes when justified.
15. Synthesize daily-use, maximum-capability and experimental profiles.

## Exact next step

On the reference M1/8 GB Mac:

1. clone or update `Ilcoach/loom` locally;
2. ensure Ollama is running and `qwen3.5:4b-mlx` is installed;
3. from the LOOM repository root run:

```bash
python3 scripts/ollama_single_shot.py --model qwen3.5:4b-mlx --context 4096
```

4. preserve the printed run directory and `run-summary.json`;
5. inspect the score, per-task failures, token throughput and memory snapshots;
6. add a summarized result under `benchmarks/results/`;
7. update this handoff before proceeding to agentic mode.

## Open questions

- What score does Qwen 3.5 4B MLX achieve on Coding Benchmark 01 in strict single-shot mode?
- Does the adapter reveal prompt-processing throughput materially different from the earlier 4.36 tok/s short-prompt result?
- Which task class is the dominant weakness of the 4B baseline?
- How much does an agent layer improve correctness, and at what latency/memory cost?
- What is the best quality/memory tradeoff for 7B–9B quantized models on 8 GB?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
