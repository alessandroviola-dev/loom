# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — first coding run deterministically rescored; full adapter/performance ingestion pending
Checkpoint: CODING_BASELINE_001_RESCORED_PENDING_RUN_SUMMARY

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
- Coding Benchmark 01 task prompts, fixtures, tests, task weights and semantics are frozen.
- `single_shot` and `agentic` results are separate experimental conditions.
- Benchmark quality, speed and memory are separate measurement dimensions.
- Failed or malformed runs are preserved, not silently retried.
- `HANDOFF.md` is canonical and must be updated after every meaningful project step.

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
- Short-prompt measurement: 4.36 prompt tok/s; repeat validation still pending.
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

Interpretation: Qwen 3.5 4B MLX is usable on the reference 8 GB machine but already pushes it close to the practical full-resident memory ceiling.

### CODING BENCHMARK 01
- Six task classes: generation, debugging, comprehension, constrained refactoring, multi-file reasoning, explicit implementation constraints.
- Total weight: 100 points.
- 41 top-level deterministic unittest methods.
- Private reference validation: 41/41 tests passed, 100/100.
- Machine-readable result schema and runner included.

### OLLAMA SINGLE-SHOT ADAPTER
- Implemented at `scripts/ollama_single_shot.py`.
- Uses isolated working copies under ignored `results-local/`.
- Hides tests from the model.
- Gives each task one attempt.
- Records raw Ollama responses, token/timing metrics, memory snapshots and benchmark score.

### CODING BASELINE 001 — FIRST REAL RUN
Reference invocation:

```bash
python3 scripts/ollama_single_shot.py --model qwen3.5:4b-mlx --context 4096
```

Run identity:
- model: `qwen3.5:4b-mlx`
- runtime: Ollama / MLX
- mode: `single_shot`
- context: 4096
- local run directory: `<repository-root>/results-local/coding-single-shot/20260818-203156`
- original adapter summary: `<repository-root>/results-local/coding-single-shot/20260818-203156/run-summary.json`

The original Benchmark 01 v1.0.0 runner reported **39.82 / 100**.

### CRITICAL SCORING DEFECT — v1.0.0
During first-result ingestion, the scorer was found to count verbose `unittest` subtest failure lines as extra tests. That made the denominator depend on failure shape.

Observed evidence:
- T05 was reported as 11 tests although the suite contains 7 top-level tests.
- T06 was reported as 12 tests although the suite contains 7 top-level tests.

Conclusion:
- 39.82/100 is preserved only as a raw historical artifact;
- it is not the official corrected quality score.

### CODING BENCHMARK 01 v1.0.1 SCORING PATCH
Completed:
- runner now counts each top-level unittest method exactly once;
- failing subtests mark the parent test failed without increasing the denominator;
- prompts, fixtures, tests, expected behavior and weights were unchanged;
- manifest patch version incremented to `1.0.1`;
- defect documented in `benchmarks/coding/v1/VALIDATION.md`;
- deterministic rescoring utility added at `scripts/rescore_coding_run.py`.

### CODING BASELINE 001 — CORRECTED RESCORE
The exact generated files from run `20260818-203156` were rescored with v1.0.1 without calling Ollama again.

**Corrected quality score: 40.71 / 100**

Per task:
- T01 generation: 15.00/15 — 6/6.
- T02 debugging: 6.43/15 — 3/7.
- T03 comprehension: 8.57/15 — 4/7.
- T04 refactoring: 8.57/15 — 4/7.
- T05 multi-file reasoning: 0.00/25 — 0/7.
- T06 instruction following: 2.14/15 — 1/7.

Quality interpretation currently supported:
- T01 is a complete success.
- T02 is a genuine partial debugging failure: rolling-window update behavior remains wrong in several cases and boolean-size validation is missed.
- T03 is a genuine partial comprehension/instruction-following failure. The prompt explicitly required complexity notation in terms of `len(capacities)` and `len(jobs)`, while the model returned `O(n*m)`; mutation/state and sentinel interpretation were also wrong.
- T04 is a genuine partial constrained-refactor failure: required helper contract was not implemented.
- T05 and T06 working copies retained their original `NotImplementedError`; these cannot yet be classified as pure reasoning failures because adapter-status/raw-response fields are not present in the rescored quality artifact.

Corrected result record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Current checkpoint interpretation

The quality score is now valid and reproducible at **40.71/100** for the exact first output set. Coding Baseline 001 is **not yet fully frozen** because the original adapter `run-summary.json` has not been ingested.

The remaining ingestion is important for two reasons:
1. classify T05/T06 as model output/reasoning failures vs adapter JSON/output-format failures;
2. attach prompt/generation throughput, latency and memory/swap behavior to the same run.

## Exact next step

Upload or inspect this exact local file:

`<repository-root>/results-local/coding-single-shot/20260818-203156/run-summary.json`

Required extraction:
1. `adapter_status` and error for every task;
2. prompt token counts and prompt tok/s;
3. generation token counts and generation tok/s;
4. wall time and Ollama durations;
5. memory snapshots before, after each task and after the run;
6. raw-response availability and parse failures;
7. definitive T05/T06 failure classification.

After that:
- update the result record with full quality/performance/memory data;
- freeze Coding Baseline 001 official result;
- update this handoff to `CODING_BASELINE_001_FROZEN`;
- then proceed to the next experiment, likely the local coding-agent layer before larger-runtime comparisons.

## Open research questions

- Why did T05 and T06 remain unimplemented: reasoning failure, JSON/output-format failure, adapter rejection, or a combination?
- Is the earlier 4.36 prompt tok/s short-prompt measurement reproducible?
- How much does an agent layer improve correctness over the 40.71/100 strict single-shot baseline, and at what latency/memory cost?
- What is the best quality/memory tradeoff for 7B–9B quantized models on 8 GB?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
