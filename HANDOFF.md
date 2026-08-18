# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — first coding run quality/performance/memory ingested; raw failed outputs pending
Checkpoint: CODING_BASELINE_001_RUN_SUMMARY_INGESTED_RAW_RESPONSES_PENDING

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, with particular focus on making larger models useful on machines that normally cannot hold them entirely in RAM.

## Long-term destination

1. Build a practical self-hosted local coding agent with no per-token cloud usage limits.
2. Establish reproducible quality/performance/memory benchmarks for local inference.
3. Explore quantization, offloading, unified memory, memory mapping, swap, SSD streaming and MoE expert streaming.
4. Compare Ollama, MLX, llama.cpp, Colibrì and other promising runtimes.
5. Determine the largest *useful*, not merely launchable, model configurations on small consumer machines.
6. If research reveals a useful gap, prototype LOOM-specific tooling/runtime techniques.

## Reference hardware

- Apple M1
- 8 GB unified memory
- macOS
- Canonical local repository: `<repository-root>`

## Frozen project decisions

- Project: `LOOM`
- Tagline: `Big models. Small machines.`
- Repository: `Ilcoach/loom` (private)
- Default branch: `main`
- Baseline runtime/model: Ollama + `qwen3.5:4b-mlx`
- Coding Benchmark 01 prompts, fixtures, tests, expected semantics and task weights are frozen.
- Benchmark 01 scorer version is currently `1.0.1` after a scoring-only defect fix.
- `single_shot` and `agentic` are distinct experimental conditions.
- Quality, speed and memory are separate measurement dimensions.
- Failed/malformed runs are retained; no silent retries.
- Strict single-shot quality requires successful output delivery, not merely starter-file test passes.
- `HANDOFF.md` is canonical and must be updated after every meaningful step.

## Completed checkpoints

### FOUNDATION
- Repository created and scaffolded.
- Research goals, methodology, hardware profile, experiment directories and result directories created.

### BASELINE 001 — inference
- MLX runner confirmed from Ollama logs.
- Ollama reported 100% GPU execution.
- Context: 4096.
- Model resident size in initial test: ~4.3 GB.
- Initial generation throughput: 15.02 tok/s.
- Initial short-prompt throughput result of 4.36 prompt tok/s was later shown to be non-representative by the coding benchmark.

Initial memory comparison:
- model OFF: PhysMem 6529 MB used, 811 MB compressed, 1101 MB unused, swap 1857.19 MB, pressure-free 62%.
- model ON: PhysMem 7500 MB used, 3131 MB compressed, 130 MB unused, swap 3833.81 MB, pressure-free 32%.

### CODING BENCHMARK 01
- Six task classes: generation, debugging, comprehension, constrained refactoring, multi-file reasoning, implementation constraints.
- Total weight: 100 points.
- 41 top-level deterministic unittest methods.
- Private reference validation: 41/41 tests, 100/100.
- Machine-readable result schema and runner included.

### CRITICAL SCORING DEFECT — v1.0.0
The first real run exposed a scorer bug:
- verbose `unittest` subtest-failure lines were counted as additional tests;
- T05 appeared as 11 tests although it contains 7 top-level tests;
- T06 appeared as 12 tests although it contains 7 top-level tests.

The original 39.82/100 is preserved only as a historical raw result.

### CODING BENCHMARK 01 v1.0.1 PATCH
- runner now counts each top-level unittest method exactly once;
- failing subtests fail the parent test but do not alter the denominator;
- prompts, fixtures, tests and weights are unchanged;
- deterministic rescoring utility added at `scripts/rescore_coding_run.py`.

### CODING BASELINE 001 — FIRST REAL RUN
Run id: `20260818-203156`

Configuration:
- model: `qwen3.5:4b-mlx`
- runtime/backend: Ollama / MLX
- mode: `single_shot`
- context: 4096
- local run directory: `<repository-root>/results-local/coding-single-shot/20260818-203156`

The exact first-run files were rescored with v1.0.1 without regenerating model outputs.

#### Artifact score
**40.71 / 100**

Per task:
- T01 generation: 15.00/15 — 6/6.
- T02 debugging: 6.43/15 — 3/7.
- T03 comprehension: 8.57/15 — 4/7.
- T04 refactoring: 8.57/15 — 4/7.
- T05 multi-file: 0.00/25 — 0/7.
- T06 constraints: 2.14/15 — 1/7.

#### Adapter-status ingestion
Original `run-summary.json` confirms:
- T01: `written`.
- T02: `written`.
- T03: `written`.
- T04: `failed` — JSON invalid control character at column 340.
- T05: `failed` — JSON missing delimiter at column 584.
- T06: `failed` — JSON missing delimiter at column 1493.

Therefore T04–T06 never wrote the model-generated file to the working tree. Their residual starter-file test passes cannot be credited to Qwen.

#### Delivery-adjusted strict single-shot score
Only tasks successfully parsed/written contribute:

- T01: 15.00
- T02: 6.43
- T03: 8.57
- T04: 0
- T05: 0
- T06: 0

**Strict end-to-end score: 30.00 / 100**

This is the primary quality score for strict single-shot delivery on the first run. The 40.71 artifact score is retained as a diagnostic secondary metric.

### Successful-task performance telemetry
Complete Ollama metrics exist in the old run summary for T01–T03:

- T01: 301 prompt tokens @ 151.511 tok/s; 98 output tokens @ 16.549 tok/s; wall 12.613 s.
- T02: 406 prompt tokens @ 165.932 tok/s; 118 output tokens @ 15.917 tok/s; wall 9.976 s.
- T03: 390 prompt tokens @ 222.342 tok/s; 50 output tokens @ 15.724 tok/s; wall 5.056 s.

Weighted across T01–T03:
- prompt: 1,097 tokens @ **177.29 tok/s**;
- generation: 266 tokens @ **16.11 tok/s**.

Conclusion: the earlier 4.36 prompt tok/s short-prompt measurement was not representative of normal benchmark prompt processing.

Full run elapsed time: approximately **91.25 s**.

For T04–T06 the old adapter failed to retain token metrics because it stored metrics only after successful JSON extraction. Their raw API files still exist locally and must be inspected.

### Memory/swap during Coding Baseline 001
Before run:
- PhysMem: 7551 MB used, 1027 MB compressed, 79 MB unused.
- swap used: 885.69 MB.
- `ollama ps`: no loaded model.

After T01:
- model: 4.1 GB, 100% GPU.
- swap: 1983.31 MB.
- memory-pressure free: 17%.

Resident size reported across tasks:
- T01 4.1 GB
- T02 4.2 GB
- T03 4.4 GB
- T04 4.5 GB
- T05 4.7 GB
- T06/final 4.8 GB

Peak observed swap: **2486.94 MB** after T05.
Final swap: **2403.44 MB**, roughly +1517.75 MB versus run start.

Interpretation: generation remains responsive, but sustained multi-task use creates substantial memory pressure/swap on the M1/8 GB. The reported resident-size growth needs a later controlled memory experiment.

### ADAPTER HARDENING AFTER FIRST RUN
`scripts/ollama_single_shot.py` has been updated to:
- record Ollama metrics before attempting model-output parsing;
- preserve metrics even when JSON/file extraction fails;
- preserve raw API responses;
- read benchmark version from `manifest.json` rather than hard-code 1.0.0;
- print T01–T06 progress live;
- report `artifact_score` separately from `delivery_adjusted_score`;
- count adapter/output-format failures as zero for strict end-to-end delivery.

Result record updated at:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Current checkpoint interpretation

We now know the first run's quality, successful-task throughput, memory behavior and exact adapter failure mode.

Important conclusion:
- Qwen 3.5 4B MLX can generate correct small code in strict single-shot mode (T01 100%).
- It is partially capable at debugging/comprehension.
- Its main first-run end-to-end failure is not only coding reasoning: on the longer/later tasks it failed the required JSON transport format three times in a row.
- Strict delivered baseline is **30.00/100**.

Coding Baseline 001 is not yet fully closed because the preserved raw T04–T06 API responses have not been inspected. Those files can reveal whether useful code exists inside malformed JSON and provide the missing token metrics for failed-delivery tasks.

## Exact next step

Inspect these local files from run `20260818-203156`:

- `<repository-root>/results-local/coding-single-shot/20260818-203156/raw/T04-api.json`
- `<repository-root>/results-local/coding-single-shot/20260818-203156/raw/T05-api.json`
- `<repository-root>/results-local/coding-single-shot/20260818-203156/raw/T06-api.json`

Required analysis:
1. recover prompt/output token metrics for T04–T06;
2. inspect the raw `response` strings;
3. determine whether malformed JSON contains otherwise valid/near-valid code;
4. classify each failure as transport-only, coding-only, or mixed;
5. finalize and freeze `CODING_BASELINE_001`;
6. only then move to local agent selection/agentic mode.

## Open research questions

- Are T04–T06 primarily JSON serialization failures or also code-quality failures?
- Why does Ollama's reported resident size grow from ~4.1 to ~4.8 GB across this six-task run?
- How much does an agent layer improve strict delivery/correctness over 30.00/100, and at what latency/memory cost?
- What is the best quality/memory tradeoff for 7B–9B quantized models on 8 GB?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
