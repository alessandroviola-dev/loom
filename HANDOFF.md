# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — first Qwen 3.5 4B MLX coding run completed; detailed result ingestion pending
Checkpoint: CODING_BASELINE_001_RUN_COMPLETE_PENDING_INGESTION

## Mission

Study, test and eventually improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, with particular focus on making larger models usable on machines that normally cannot hold them entirely in RAM.

## Long-term destination

1. Build a practical self-hosted local coding agent with no per-token cloud usage limits.
2. Establish reproducible benchmarks for local inference on constrained hardware.
3. Explore quantization, offloading, unified memory, memory mapping, swap, SSD streaming and MoE expert streaming.
4. Compare Ollama, MLX, llama.cpp, Colibrì and other promising runtimes.
5. Determine the largest useful, not merely launchable, model configurations on small consumer machines.
6. If research reveals a useful gap, prototype LOOM-specific tooling/runtime techniques.

## Reference hardware

- Apple M1
- 8 GB unified memory
- macOS
- Canonical local repository path: `<repository-root>`

## Frozen project decisions

- Project: `LOOM`
- Tagline: `Big models. Small machines.`
- Repository: `Ilcoach/loom` (private)
- Default branch: `main`
- Baseline runtime/model: Ollama + `qwen3.5:4b-mlx`
- Coding Benchmark 01 v1.0.0 is frozen.
- `single_shot` and `agentic` results are separate experimental conditions.
- Benchmark quality, speed and memory are separate measurement dimensions.
- Failed or malformed runs are preserved, not silently retried.
- `HANDOFF.md` is canonical and must be updated after each meaningful project step.

## Completed checkpoints

### FOUNDATION
- Repository created and scaffolded.
- Research goals, methodology, hardware profile, experiment directories and result directories created.

### BASELINE 001 — inference
- MLX runner confirmed from Ollama logs.
- Ollama reports 100% GPU execution.
- Context: 4096.
- Model resident size: 4.3 GB.
- Initial generation throughput: 15.02 tok/s.
- Short-prompt measurement: 4.36 prompt tok/s; this still needs repeat validation.
- Total request time: 30.01 s.
- Model load time: 0.07 s.

Memory without model:
- PhysMem used: 6529 MB
- compressed: 811 MB
- unused: 1101 MB
- memory_pressure free: 62%
- swap used: 1857.19 MB

Memory with model:
- PhysMem used: 7500 MB
- compressed: 3131 MB
- unused: 130 MB
- memory_pressure free: 32%
- swap used: 3833.81 MB

Interpretation: the 4B MLX model is usable but already pushes the 8 GB machine close to its practical full-resident memory ceiling.

### CODING BENCHMARK 01 v1.0.0
- Frozen under `benchmarks/coding/v1`.
- Six task classes: generation, debugging, comprehension, constrained refactoring, multi-file reasoning, explicit implementation constraints.
- Total score: 100 points.
- 41 deterministic tests.
- Private reference validation: 41/41 tests, 100/100.
- Machine-readable result schema and runner included.

### OLLAMA SINGLE-SHOT ADAPTER
- Implemented at `scripts/ollama_single_shot.py`.
- Uses isolated working copies under ignored `results-local/`.
- Hides tests from the model.
- Gives each task one attempt.
- Records raw Ollama responses, token/timing metrics, memory snapshots and benchmark score.

### CODING BASELINE 001 — FIRST REAL RUN
Reference command:

```bash
python3 scripts/ollama_single_shot.py --model qwen3.5:4b-mlx --context 4096
```

Run completed on the reference M1/8 GB Mac.

Known result:
- model: `qwen3.5:4b-mlx`
- runtime: Ollama / MLX
- mode: `single_shot`
- context: 4096
- score: **39.82 / 100**
- local run directory: `<repository-root>/results-local/coding-single-shot/20260818-203156`
- local summary: `<repository-root>/results-local/coding-single-shot/20260818-203156/run-summary.json`

Important: 39.82/100 must not yet be interpreted as a model-quality conclusion. Per-task scores, adapter failures, malformed outputs, token metrics and memory snapshots have not yet been ingested from `run-summary.json`.

## Exact next step

Ingest and analyze the local `run-summary.json` from run `20260818-203156`.

Required extraction:
1. score per task T01–T06;
2. passed/failed tests per task;
3. any adapter errors or malformed JSON outputs;
4. prompt token counts and prompt tok/s per task;
5. generation token counts and generation tok/s per task;
6. wall time per task and total run time;
7. memory/swap snapshots before, after each task and after the run;
8. identify whether the 39.82 score reflects reasoning/coding weakness, output-format weakness, benchmark-adapter issues, or a combination.

After ingestion:
- commit a summarized result under `benchmarks/results/`;
- update this handoff to `CODING_BASELINE_001_INGESTED`;
- only then move to the next experiment.

## Open research questions

- Is the earlier 4.36 prompt tok/s result reproducible?
- Which coding task class is the dominant weakness of the 4B baseline?
- How much does an agent layer improve correctness, and at what latency/memory cost?
- What is the best quality/memory tradeoff for 7B–9B quantized models on 8 GB?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
