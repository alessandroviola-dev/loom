# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — repository initialized, ready for Benchmark Coding 01
Checkpoint: REPO_INITIALIZED_BASELINE_FROZEN

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
- Canonical handoff discipline defined.
- Private GitHub repository created and verified: `Ilcoach/loom`.
- Initial project scaffold written to the `main` branch.
- Repository includes README, roadmap, methodology, hardware profile, benchmark/result directories, experiment workspaces, research workspaces and this canonical handoff.
- `ROADMAP.md` Phase 0 is complete.

### 1. Ollama baseline setup
- Ollama updated from 0.31.2 to a current MLX-capable build.
- Previous model present: `qwen3.5:2b` (2.7 GB on disk).
- Baseline model installed: `qwen3.5:4b-mlx`.
- MLX backend confirmed from Ollama logs.
- `ollama ps` confirmed 100% GPU execution.
- Context: 4096 tokens.

### 2. Baseline performance
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

Interpretation: Qwen 3.5 4B MLX is usable and reasonably fast, but the 8 GB system is already close to its practical memory ceiling under normal desktop load. Larger models will require more aggressive techniques rather than simple full-resident loading.

## Repository state

Repository: `Ilcoach/loom`
Visibility: private
Default branch: `main`

Initial tracked structure:

- `README.md`
- `ROADMAP.md`
- `HANDOFF.md`
- `.gitignore`
- `docs/research-goals.md`
- `docs/methodology.md`
- `docs/hardware/m1-8gb.md`
- `benchmarks/coding/README.md`
- `benchmarks/reasoning/README.md`
- `benchmarks/results/baseline-001-qwen35-4b-mlx.md`
- `agents/README.md`
- `experiments/ollama/README.md`
- `experiments/mlx/README.md`
- `experiments/llama.cpp/README.md`
- `experiments/colibri/README.md`
- `scripts/README.md`
- `research/notes/README.md`
- `research/papers/README.md`

## Decisions frozen so far

- Project name: LOOM.
- Tagline: `Big models. Small machines.`
- GitHub repository: `Ilcoach/loom`, private initially.
- Baseline runtime/model: Ollama + Qwen 3.5 4B MLX.
- Every runtime/model comparison must use repeatable tests and record quality, speed and memory behavior.
- `HANDOFF.md` is the canonical project state and must be updated after every meaningful step before moving to the next checkpoint.

## Roadmap

1. Freeze baseline 001. [DONE]
2. Initialize private GitHub repository and scaffold. [DONE]
3. Create reproducible Coding Benchmark 01. [NEXT]
4. Run Qwen 3.5 4B MLX through Coding Benchmark 01.
5. Connect a local coding agent to Ollama and test repository-level tasks.
6. Test llama.cpp with larger, aggressively quantized models (Q4/Q3/Q2 where appropriate).
7. Test direct MLX execution without Ollama.
8. Test Colibrì and MoE / SSD expert streaming within 8 GB constraints.
9. Evaluate additional Apple Silicon runtimes if technically relevant.
10. Compare all configurations using identical benchmark tasks.
11. Choose daily, maximum-capability and experimental profiles.

## Exact next step

Create `Benchmark Coding 01` as a fixed, versioned and reproducible suite of coding tasks that can be run unchanged against every model/runtime combination. It must test at least:

1. code generation from specification;
2. debugging of faulty code;
3. code comprehension/explanation;
4. constrained refactoring;
5. multi-file or repository-level reasoning;
6. instruction following under explicit constraints.

The benchmark must define deterministic inputs, expected outcomes/tests, scoring criteria and a machine-readable result format. After the suite is committed, update this handoff to the next checkpoint before running the baseline model against it.

## Open questions

- Is the low measured prompt-processing throughput repeatable or an artifact of the short prompt/test method?
- What is the best quality/memory tradeoff for 7B–9B-class models on this 8 GB M1?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful model capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?
- What is the best local agent layer for coding on this hardware?
- Which benchmark design best predicts real repository-level usefulness while remaining small enough for repeated local testing?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
