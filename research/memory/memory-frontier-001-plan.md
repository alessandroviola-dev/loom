# MEMORY-FRONTIER 001 — real-M1 residency / RAM / speed Pareto plan

Date: 2026-08-21
Status: FROZEN / RUN PENDING

## Goal

Measure the **real autoregressive M1** trade-off between model-weight residency, host-memory headroom, weight I/O and usable generation speed for the canonical Qwen3-8B 3-bit model on Apple M1 / 8 GB.

This is the first system-level frontier after CAPABILITY 001. It is not a capability benchmark and it is not an oracle M5 verifier benchmark.

The question is:

> How much of the 8B model can be moved out of persistent unified memory before real M1 generation becomes too slow, and where are the useful Pareto points between RAM and token throughput?

The result will guide the architecture used later for models whose weights exceed comfortable physical RAM.

## Why now

CAPABILITY 001 established the canonical practical-agent baseline:

- primary: 1/11 = 9.09%
- coding secondary: 45/100
- four long tasks crossed the 5% system-free floor

Therefore future work needs both:

1. more memory headroom / scalable residency architecture;
2. preservation or improvement of capability when model size/representation later changes.

MEMORY-FRONTIER 001 addresses item 1 while preserving exact model semantics.

## Frozen model/runtime

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2
- mlx-lm 0.31.3
- transformers 5.12.1 where inherited by local streaming helpers
- built-in canonical M1 qmv path for the fully resident reference
- normal Qwen3 chat template
- `enable_thinking=false`
- greedy unknown-token generation
- no drafter/speculation/oracle tokens
- no cloud/Ollama

Canonical weights:
`results-local/mlx/models/Qwen3-8B-3bit/model.safetensors`

Raw weight anatomy:

- total: 3,583,928,320 B
- transformer body: 3,039,381,504 B
- each transformer layer: 84,427,264 B
- embeddings: 272,269,312 B
- final norm: 8,192 B
- LM head: 272,269,312 B

## Real-generation reference

REALGEN 001 remains the practical fully resident reference:

- pooled real M1 generation: 13.184615357 tok/s
- pooled E2E output: 12.046861457 tok/s

MEMORY-FRONTIER 001 must run fresh measurements rather than substitute historical values, but historical REALGEN 001 is retained as an external sanity reference.

## Proven streaming provenance

Reuse the already validated local mechanisms from the Stretch residency/streaming series rather than inventing a new mathematical forward path.

Relevant proven provenance includes:

- full 36-layer streamed-body parity
- autoregressive KV parity/stability
- persistent hotset mechanism
- H8/H16/H24/H32 residency helpers
- exact affine 3-bit/group64 parameter loading

The old H8/H16/H24/H32 results were M5 oracle target-verification experiments. Their token/s values are **not** valid substitutes for this experiment. Only their implementation/provenance may be reused.

## Frontier configurations

Measure five system configurations:

### F0 — FULL
Canonical fully resident MLX model. All model weights persistent as in REALGEN 001.

### F1 — H32
Persistent transformer layers 0..31. Transformer layers 32..35 are streamed/materialized through the proven local path. Shared stages use the same partial-residency handling as the validated hotset implementation.

### F2 — H24
Persistent transformer layers 0..23. Remaining transformer layers streamed through the same mechanism.

### F3 — H16
Persistent transformer layers 0..15. Remaining transformer layers streamed.

### F4 — H8
Persistent transformer layers 0..7. Remaining transformer layers streamed. This is the aggressive low-residency reference, not an expected usability winner.

No other model/runtime factor may differ between F1-F4.

F0 is the canonical full-residency endpoint and may differ from partial points in shared-stage persistence by design; treat this experiment as a **system Pareto frontier**, not as a claim that every adjacent pair differs by exactly one low-level factor.

## Mandatory implementation audit before science

Before any timed scientific run, Pi must inspect the local proven helpers and document exactly:

- which tensors remain persistent for each F1-F4 point;
- which tensors are loaded/materialized on demand;
- whether shared stages are persistent or streamed;
- exact logical raw-weight residency budget;
- exact logical streamed bytes per full model pass;
- source/helper paths reused.

Do not infer these from names alone.

If the local helpers cannot be adapted to real M1 unknown-token generation without changing model math, classify `MEMORY_FRONTIER_001_INFRASTRUCTURE_INCOMPLETE` and stop.

## Mandatory real-M1 parity preflight

Before timing each partial configuration, use a separate non-scientific process to prove real greedy M1 token parity against F0 for a frozen short prompt.

Requirements:

- at least 16 generated unknown tokens, or EOS if earlier;
- exact token IDs versus F0;
- no oracle target block;
- ordinary BF16 KV;
- same tokenizer/chat template;
- no speculative/draft mechanism.

A harness defect may be repaired before the scientific run without consuming a frontier measurement.

Any genuine model-output divergence invalidates that frontier point and must not be hidden.

## Frozen prompt workload

Reuse the canonical public deterministic prompt list from REALGEN 001.

Do not reconstruct prompts from memory.

For the frontier run use the **first three prompts in canonical REALGEN 001 order**, unchanged.

For each prompt:

- same normal Qwen chat template
- thinking disabled
- greedy generation
- max 64 generated tokens or EOS

This produces a bounded but multi-prompt real-generation workload.

## Balanced run order

Because page cache and host state can affect streamed-weight I/O, use two fresh scientific runs per configuration in symmetric order:

`F0 -> F4 -> F3 -> F2 -> F1 -> F1 -> F2 -> F3 -> F4 -> F0`

No deliberate macOS cache purge.

Every constituent run starts from a fresh model process and must independently satisfy host admission.

Pool the two valid runs for each configuration.

## Host admission

Before each constituent scientific process:

- system free >=60% on two consecutive passive samples
- swap <=5600 MB

Wait passively for natural recovery.

Forbidden:

- `purge`
- unrelated process kills
- swap manipulation
- artificial alloc/free
- deliberate OS cache flush

A failed pre-load admission does not consume a constituent run.

## Resource abort

After model execution starts, abort that constituent run if:

- system free <5%; or
- swap >5600 MB.

Do not rescue/retry the same scientific constituent run. Preserve the failure as a frontier result.

## Required measurements

Per constituent run and per prompt where feasible:

### Residency

- configured persistent transformer layers
- measured persistent raw-weight bytes
- logical streamed weight bytes per model pass
- MLX active after load/before prompt
- MLX allocator cache after load

### Memory

- peak MLX active
- peak MLX active+cache
- minimum system free %
- peak swap MB
- process RSS diagnostic

### Speed

- generated tokens
- generation wall
- real greedy generation tok/s
- prompt-to-first-token / TTFT
- end-to-end output tok/s

### I/O

Primary I/O metric:

- **logical model-weight bytes loaded/materialized from the streaming source per generated token**, instrumented directly in the loader/path

Secondary diagnostics:

- process read bytes delta
- process read bytes/generated token

Do not label Darwin process-read bytes as proven physical SSD reads.

### Correctness

- generated token IDs
- exact parity with the F0 canonical output for each corresponding prompt
- EOS position

## Pooled metrics per configuration

For each F0-F4 report:

- valid constituent runs /2
- resident raw-weight bytes
- resident fraction of total raw weights
- pooled generation tok/s
- pooled E2E output tok/s
- median TTFT
- peak MLX across valid constituents
- minimum free across valid constituents
- peak swap across valid constituents
- logical streamed weight bytes/generated token
- process-read bytes/generated token diagnostic
- exact-token parity PASS/FAIL

## Pareto analysis

Construct the RAM/speed frontier using at minimum:

- x-axis concept: resident model bytes / measured MLX footprint
- y-axis concept: real generation tok/s

A configuration is Pareto-dominated if another measured configuration is both:

- no worse in relevant memory footprint/headroom; and
- no slower in real generation throughput;

with at least one strict improvement.

Do not pick a winner using speed alone.

Also report incremental trade-offs relative to F0:

- resident bytes saved
- peak MLX saved
- minimum-free gain/loss
- generation throughput retained (%)
- E2E throughput retained (%)
- extra logical weight I/O/token

## Practical bands

Do not impose a single promotion threshold before seeing the curve.

For interpretation only, classify measured points into:

- **interactive candidate**: >=10 real generation tok/s
- **usable experimental**: >=5 and <10 tok/s
- **slow reference**: >=1 and <5 tok/s
- **impractical reference**: <1 tok/s

These bands are descriptive, not automatic promotion rules.

## Capability preservation

MEMORY-FRONTIER 001 does not rerun CAPABILITY 001 at every residency point.

Exact token parity is required because all points are intended to represent the same Qwen3-8B model math.

Any configuration later promoted as a canonical runtime or used as the basis for a representation/model-size change must be evaluated against the frozen CAPABILITY 001 baseline as appropriate.

Canonical capability reference:

- primary 1/11 = 9.09%
- Coding Benchmark 45/100

## Classification

Use:

`MEMORY_FRONTIER_001_COMPLETE`

if the frontier produces valid/scorable measurements for F0 and at least three partial-residency points, with correctness status explicitly known for every reported point.

Use:

`MEMORY_FRONTIER_001_PARTIAL`

if F0 plus at least one partial point are scientifically valid but other points fail resource/correctness gates. Failed points remain part of the reported boundary.

Use:

`MEMORY_FRONTIER_001_INFRASTRUCTURE_INCOMPLETE`

only when harness/implementation issues prevent a scientifically interpretable frontier.

## Evidence

Store local raw evidence under:

`results-local/memory/memory-frontier-001/<run-id>/`

At minimum:

- `summary.json`
- `implementation-audit.json`
- `host-admission.jsonl`
- `frontier.json`
- `pareto.json`
- `runs/`
- exact prompt/token outputs
- memory samples
- I/O counters

## Pi role

Pi implements/adapts the local runner and executes measurements only.

Pi must not:

- update Git/HANDOFF/ROADMAP
- change frozen model/runtime math
- propose the next experiment
- run CAPABILITY 001 again
- begin prefetch/double-buffering work inside this experiment

Return concise raw evidence to ChatGPT for review.
