# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — first coding run completed; v1.0.0 scoring defect patched; deterministic rescore pending
Checkpoint: CODING_BENCHMARK_01_SCORER_PATCHED_V1_0_1

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

Interpretation: the 4B MLX model is usable but already pushes the 8 GB machine close to its practical full-resident memory ceiling.

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
Reference command:

```bash
python3 scripts/ollama_single_shot.py --model qwen3.5:4b-mlx --context 4096
```

Run completed on the reference M1/8 GB Mac.

Run identity:
- model: `qwen3.5:4b-mlx`
- runtime: Ollama / MLX
- mode: `single_shot`
- context: 4096
- local run directory: `<repository-root>/results-local/coding-single-shot/20260818-203156`
- original local summary: `<repository-root>/results-local/coding-single-shot/20260818-203156/run-summary.json`

The original v1.0.0 scorer reported **39.82 / 100**.

Uploaded quality-result observations:
- T01 generation: 15.00/15, 6/6 reported tests passed.
- T02 debugging: 6.43/15, 3/7 reported tests passed.
- T03 comprehension: 8.57/15, 4/7 reported tests passed.
- T04 refactoring: 8.57/15, 4/7 reported tests passed.
- T05 multi-file reasoning: 0/25; working tree retained `NotImplementedError`.
- T06 instruction following: 1.25/15 under the defective scorer; working tree retained `NotImplementedError` for most checks.

Quality observations independent of scoring defect:
- T01 was a complete success.
- T02 retained incorrect rolling-window update behavior and failed boolean-size validation.
- T03 recognized some structure correctly but missed input-mutation state, unassigned sentinel and expected complexity representation.
- T04 preserved some behavior but failed the required helper/refactoring contract.
- T05 and T06 cannot yet be classified as pure model failures because the uploaded quality-result file does not include adapter-status/raw-response fields.

### CRITICAL BENCHMARK DEFECT — v1.0.0
During result ingestion a scoring bug was discovered.

Root cause:
- v1.0.0 regex-parsed verbose `unittest` output;
- failing `subTest` cases emit additional result lines;
- those extra lines were incorrectly counted as additional tests;
- therefore the denominator depended on failure shape.

Concrete evidence:
- T05 result field claimed 11 tests while unittest reported `Ran 7 tests`.
- T06 result field claimed 12 tests while unittest reported `Ran 7 tests`.

Conclusion:
- **39.82/100 is not a valid official baseline score**;
- it is preserved only as an auditable raw historical result.

### CODING BENCHMARK 01 v1.0.1 SCORING PATCH
Completed:
- runner changed to execute/count each top-level `unittest.TestCase` method exactly once;
- any failing subtest marks its enclosing top-level test failed without increasing the denominator;
- prompts, fixtures, tests, expected semantics and weights were not changed;
- manifest patch version incremented to `1.0.1`;
- defect documented in `benchmarks/coding/v1/VALIDATION.md`;
- preliminary result record created at `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`;
- deterministic rescoring utility added at `scripts/rescore_coding_run.py`.

## Current checkpoint interpretation

The model outputs from run `20260818-203156` must be preserved. We must **not rerun Qwen yet**. The next operation is to apply the corrected v1.0.1 scorer to the exact same generated files, isolating scoring correction from model variance.

The uploaded file was the benchmark quality result, not the full adapter `run-summary.json`. Therefore speed, token and memory ingestion is still pending.

## Exact next step

On the reference Mac, from the LOOM repository:

```bash
cd "<repository-root>"
git pull
python3 scripts/rescore_coding_run.py \
  --run-dir "<repository-root>/results-local/coding-single-shot/20260818-203156" \
  --model qwen3.5:4b-mlx \
  --runtime ollama \
  --backend mlx \
  --mode single_shot \
  --context 4096
```

This rescoring does not call Ollama and does not regenerate model answers. It reuses the exact existing generated files.

After rescoring:
1. ingest the corrected v1.0.1 quality score;
2. update `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`;
3. ingest the original `run-summary.json` for adapter status, token/s, timing and memory;
4. classify T05/T06 model-vs-adapter failure mode;
5. freeze Coding Baseline 001;
6. update this handoff before proceeding to agentic mode.

## Open research questions

- What is the corrected v1.0.1 score of the exact first Qwen output set?
- Were T05/T06 failures caused by model reasoning, output formatting/JSON parsing, or both?
- Is the earlier 4.36 prompt tok/s result reproducible?
- Which coding task class is the dominant weakness of the 4B baseline after valid scoring?
- How much does an agent layer improve correctness, and at what latency/memory cost?
- What is the best quality/memory tradeoff for 7B–9B quantized models on 8 GB?
- Can direct MLX materially improve memory behavior versus Ollama MLX?
- How much useful capacity can SSD-backed or MoE expert streaming unlock before latency becomes impractical?

## Continuation rule

Before starting a new experiment, read this file. After any meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
