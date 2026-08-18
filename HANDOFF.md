# LOOM — Project Handoff

Last updated: 2026-08-18
Status: ACTIVE — Coding Baseline 001 frozen; next phase is local coding-agent selection
Checkpoint: CODING_BASELINE_001_FROZEN

## Mission

Study, test and improve ways to run capable local language models and self-hosted AI agents on resource-constrained consumer computers, with particular focus on making larger models useful on machines that normally cannot hold them entirely in RAM.

## Long-term destination

1. Build a practical self-hosted local coding agent with no per-token cloud usage limits.
2. Establish reproducible quality/performance/memory benchmarks for constrained local inference.
3. Explore quantization, offloading, unified memory, memory mapping, swap, SSD streaming and MoE expert streaming.
4. Compare Ollama, MLX, llama.cpp, Colibrì and other promising runtimes.
5. Determine the largest useful, not merely launchable, models on small consumer machines.
6. If the research reveals a useful gap, prototype LOOM-specific tools/runtime techniques.

## Reference system

- Apple M1
- 8 GB unified memory
- macOS
- Canonical local repo: `<repository-root>`
- GitHub: `Ilcoach/loom` (private)

## Frozen project decisions

- Project name: `LOOM`
- Tagline: `Big models. Small machines.`
- Baseline runtime/model: Ollama + `qwen3.5:4b-mlx`
- Baseline context: 4096
- Coding Benchmark 01 prompts, fixtures, tests, expected semantics and task weights are frozen.
- Current scorer: Benchmark 01 v1.0.1 after a scoring-only defect fix.
- `single_shot` and `agentic` are distinct experimental conditions.
- Quality, delivery reliability, inference speed and memory are separate dimensions.
- Failed/malformed responses are preserved; no silent retries in strict baseline mode.
- `HANDOFF.md` is canonical and must be updated after every meaningful project step.

## Completed checkpoint — inference baseline

Qwen 3.5 4B MLX:
- MLX runner confirmed.
- 100% GPU execution confirmed.
- Initial simple generation throughput: ~15.02 tok/s.
- Initial model resident report: ~4.3 GB.

Initial model OFF vs ON memory comparison showed substantial compression/swap pressure on the 8 GB machine.

## Completed checkpoint — Coding Benchmark 01

Benchmark structure:
- T01 generation — 15 points.
- T02 debugging — 15.
- T03 comprehension — 15.
- T04 constrained refactoring — 15.
- T05 multi-file reasoning — 25.
- T06 implementation constraints — 15.
- Total: 100.
- 41 top-level deterministic unittest methods.
- Private reference validation: 41/41, 100/100.

### Scorer defect discovered and fixed

The original v1.0.0 scorer counted failing verbose `subTest` lines as additional tests. The first run therefore produced an invalid historical score of 39.82/100.

Benchmark v1.0.1 now counts each top-level unittest method exactly once. Prompts/tests/weights were not changed.

## CODING BASELINE 001 — FROZEN

Run id: `20260818-203156`

Configuration:
- model: `qwen3.5:4b-mlx`
- runtime/backend: Ollama / MLX
- mode: `single_shot`
- context: 4096

### Strict delivery score — canonical end-to-end baseline

Original delivery status:
- T01 valid/written.
- T02 valid/written.
- T03 valid/written.
- T04 malformed JSON, not written.
- T05 malformed JSON, not written.
- T06 malformed JSON, not written.

Strict delivered task points:
- T01: 15.00
- T02: 6.43
- T03: 8.57
- T04: 0
- T05: 0
- T06: 0

**Canonical strict single-shot score: 30.00 / 100**

Structured-output delivery success rate: **3/6 = 50%**.

### Artifact score — diagnostic only

Corrected v1.0.1 score of files physically present in the original working tree:

**40.71 / 100**

Not canonical because failed deliveries left starter files untouched and those starter files could still pass some tests.

### Raw-response recovery analysis

All six original raw Ollama API responses were preserved and inspected.

T04, T05 and T06 all contained complete generated Python code despite invalid outer JSON.

Only deterministic envelope repair was applied:
- escape literal unescaped newline/control characters where required;
- restore the missing final outer JSON closing brace;
- do not alter generated Python code;
- do not retry the model;
- do not provide test feedback.

Recovered raw code results against the original frozen tests:
- T04: **7/7**, 15.00/15.
- T05: **7/7**, 25.00/25.
- T06: **6/7**, 12.86/15; only boolean `True` validation fails.

Combining recovered T04–T06 with originally delivered T01–T03:

**Diagnostic semantic-content score: 82.86 / 100**

This is explicitly NOT the strict benchmark score. It is a model-capability diagnostic separating code quality from protocol reliability.

### Failure classification

- T01: success.
- T02: genuine debugging/coding partial failure.
- T03: genuine comprehension/instruction partial failure.
- T04: **transport/serialization failure only**; underlying code passed 7/7.
- T05: **transport/serialization failure only**; underlying code passed 7/7.
- T06: **mixed transport + coding edge-case failure**; underlying code passed 6/7.

Main research finding:

> On this first Qwen 3.5 4B MLX coding run, fragile structured-output delivery was a substantially larger end-to-end bottleneck than underlying generated-code quality.

The gap is large:
- strict delivery score: **30.00/100**;
- recovered semantic-content score: **82.86/100**.

This directly motivates agentic file/patch tools rather than JSON-encoded complete-file payloads.

## Full six-task performance telemetry

Raw API metrics are available for all six tasks.

Per-task generation throughput remained stable around ~15.7–16.5 tok/s.

Weighted across all six calls:
- prompt tokens: **2,520**;
- weighted prompt throughput: **186.46 tok/s**;
- generated tokens: **1,068**;
- weighted generation throughput: **16.01 tok/s**;
- summed API wall time: **85.535 s**.

Full benchmark process elapsed about **91.25 s**.

The earlier isolated 4.36 prompt tok/s measurement is rejected as non-representative.

## Memory/swap finding

Before benchmark:
- swap: 885.69 MB;
- no model listed by `ollama ps`.

During run:
- model remained 100% GPU;
- Ollama resident report grew approximately 4.1 → 4.8 GB across tasks;
- peak observed swap: **2486.94 MB**;
- final swap: **2403.44 MB**.

Sustained inference is usable but creates significant memory pressure and SSD swap on 8 GB. Resident-size growth needs a later controlled experiment.

## Adapter hardening completed

`scripts/ollama_single_shot.py` was patched after Baseline 001 to:
- preserve metrics before parsing;
- preserve raw API responses;
- read benchmark version from manifest;
- show per-task progress;
- separate artifact and delivery-adjusted scores;
- score failed delivery as zero in strict mode.

Result record:
- `benchmarks/results/coding-baseline-001-qwen35-4b-mlx.md`

## Roadmap state

- Phase 0 foundation: DONE.
- Phase 1 Ollama/MLX baseline: DONE.
- Phase 2 Coding Benchmark + Baseline 001: DONE / FROZEN.
- Phase 3 local coding agent: NEXT.
- Phase 4 llama.cpp larger quantized models: queued.
- Phase 5 direct MLX: queued.
- Phase 6 Colibrì / SSD streaming / MoE: queued.
- Phase 7 other runtimes: queued.
- Phase 8 synthesis: queued.

## Exact next step

Research and select a local coding-agent layer for the reference Mac that can work with Ollama/Qwen and avoid fragile full-file JSON transport.

Selection criteria:
1. works locally with Ollama/OpenAI-compatible local endpoints;
2. can read repository context;
3. can edit files via patch/file tools;
4. can run tests/commands;
5. supports iterative validation/retry;
6. remains usable on an 8 GB M1;
7. can be benchmarked reproducibly in a distinct `agentic` mode;
8. preferably open source / self-hostable.

After selection:
- connect it to `qwen3.5:4b-mlx`;
- run a controlled smoke test;
- then run Coding Benchmark 01 in agentic mode;
- compare strict quality, protocol reliability, latency and memory against Baseline 001.

## Open research questions

- How much can an agent layer close the 30.00 → 82.86 gap by removing transport fragility and adding validation loops?
- Why does Ollama resident size grow ~4.1 → 4.8 GB during the six-task sequence?
- What is the best quality/memory tradeoff for 7B–9B Q4/Q3/Q2 models on 8 GB?
- Can direct MLX improve memory behavior versus Ollama MLX?
- How much practical model capacity can SSD-backed / MoE expert streaming unlock before latency becomes unacceptable?

## Continuation rule

Before starting any new experiment, read this file. After every meaningful experiment, decision, benchmark, architecture change or tooling change, update this file before moving to the next checkpoint.
