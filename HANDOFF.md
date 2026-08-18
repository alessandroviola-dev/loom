# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Coding Benchmark 01 frozen; Ollama execution adapter is next
Checkpoint: CODING_BENCHMARK_01_FROZEN

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
- Project name frozen as `LOOM`.
- Tagline frozen as `Big models. Small machines.`
- Private GitHub repository created: `Ilcoach/loom`.
- Repository visibility: private.
- Default branch: `main`.
- Initial project scaffold committed.
- Canonical handoff discipline defined: this file must be updated after every meaningful project step.

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

Interpretation: the 4B MLX configuration is practical at roughly 15 tok/s, but the 8 GB machine is already near its normal full-resident memory ceiling. Larger-model research must therefore focus on quantization, offload, memory mapping, SSD streaming and/or sparse/MoE techniques.

### 4. Coding Benchmark 01 v1.0.0

Created and frozen at `benchmarks/coding/v1`.

Coverage:
- T01 code generation — 15 points.
- T02 debugging — 15 points.
- T03 code comprehension — 15 points.
- T04 constrained refactoring — 15 points.
- T05 multi-file reasoning — 25 points.
- T06 instruction-following under implementation constraints — 15 points.
- Total: 100 points.

Benchmark infrastructure:
- exact versioned prompts;
- deterministic Python standard-library fixtures;
- automated unittest suites;
- `manifest.json`;
- machine-readable `result-schema.json`;
- `runner.py` for scoring and JSON output;
- separate `single_shot` and `agentic` benchmark modes.

Validation:
- private reference implementations were used only for QA and were not committed;
- 41 / 41 tests passed;
- reference score: 100 / 100;
- runner aggregation validated at 100 / 100;
- T03 was corrected before freeze to accept equivalent Big-O multiplication order;
- validation record committed as `benchmarks/coding/v1/VALIDATION.md`.

Freeze rule: v1 prompts, fixtures, tests and scoring are now immutable except for a documented critical defect. Semantic changes require a new benchmark version.

## Decisions frozen so far

- Project name: LOOM.
- Tagline: `Big models. Small machines.`
- Repository: `Ilcoach/loom`, private initially.
- Reference hardware: Apple M1 / 8 GB unified memory.
- Baseline runtime/model: Ollama + Qwen 3.5 4B MLX.
- Benchmark quality must be measured separately from speed and memory behavior.
- `single_shot` and `agentic` scores are separate experimental conditions.
- Failed runs must be retained.
- `HANDOFF.md` is the canonical project state.

## Roadmap state

1. Baseline 001. [DONE]
2. GitHub repository + scaffold. [DONE]
3. Coding Benchmark 01 v1.0.0 design. [DONE]
4. Coding Benchmark 01 validation/freeze. [DONE]
5. Build Ollama single-shot execution adapter. [NEXT]
6. Run Qwen 3.5 4B MLX through Coding Benchmark 01.
7. Repeat throughput test to investigate low prompt-processing measurement.
8. Select and connect a local coding agent to Ollama.
9. Run the same benchmark in `agentic` mode.
10. Test llama.cpp with larger Q4/Q3/Q2 configurations.
11. Test direct MLX.
12. Test Colibrì / MoE / SSD expert streaming.
13. Evaluate other Apple Silicon runtimes only when technically justified.
14. Synthesize daily-use, maximum-capability and experimental profiles.

## Exact next step

Build an Ollama `single_shot` benchmark adapter that:

1. reads each frozen task prompt and allowed source files;
2. constructs a deterministic request for `qwen3.5:4b-mlx`;
3. sends it to the local Ollama API;
4. requires machine-parseable file outputs;
5. writes only the task's permitted target files into an isolated working copy;
6. records Ollama timing/token metrics for every task;
7. runs `runner.py` after all six tasks;
8. stores raw model outputs separately from benchmark scores;
9. never edits the frozen benchmark source tree.

After the adapter is validated, run it on the reference M1/8 GB machine and commit only the resulting summarized benchmark record, not transient working files.

## Open questions

- Is the low measured 4.36 tok/s prompt-processing result repeatable or a short-prompt measurement artifact?
- How strong is Qwen 3.5 4B MLX on the frozen coding benchmark in single-shot mode?
- How much does an agent layer improve correctness, and at what latency/memory cost?
- What is the best quality/memory tradeoff for 7B–9B-class quantized models on this 8 GB M1?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful model capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
