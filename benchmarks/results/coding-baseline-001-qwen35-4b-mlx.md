# Coding Baseline 001 — Qwen 3.5 4B MLX

Date: 2026-08-18
Status: **FROZEN — COMPLETE**

## Configuration

- Benchmark: LOOM Coding Benchmark 01
- Original run benchmark version: 1.0.0
- Corrected scorer version: 1.0.1
- Model: `qwen3.5:4b-mlx`
- Runtime: Ollama
- Backend: MLX
- Mode: `single_shot`
- Context: 4096
- Reference hardware: Apple M1 / 8 GB unified memory
- Local run id: `20260818-203156`

## Primary conclusion

The first LOOM coding baseline exposed a major distinction between **semantic coding ability** and **structured-output delivery reliability**.

Qwen 3.5 4B MLX produced useful code for all six tasks, but only three responses were valid enough for the strict adapter to write automatically. The three failed deliveries contained recoverable code; two of those recovered implementations passed all tests.

Therefore LOOM records three separate quality views rather than collapsing them into one number.

## Frozen score views

### 1. Strict delivery-adjusted score — primary end-to-end metric

A task scores only if the original model response is successfully parsed and written with no repair or retry.

**30.00 / 100**

This is the canonical strict single-shot end-to-end score for Baseline 001.

### 2. Artifact score — diagnostic only

The corrected v1.0.1 scorer applied to the original isolated working tree produced:

**40.71 / 100**

This is not a valid end-to-end score because failed deliveries left starter files in place and those starter files could still pass some tests.

### 3. Recovered semantic-content score — diagnostic model-capability view

For T04–T06, only deterministic transport repair was applied to the preserved raw `response` strings:

- literal unescaped newline/control characters were escaped where necessary;
- the missing final outer JSON brace was restored;
- no generated Python code was edited;
- no retry, test feedback or new model call occurred.

The recovered code was then executed against the original frozen tests.

Recovered results:
- T04 refactoring: **7/7** — 15.00/15.
- T05 multi-file reasoning: **7/7** — 25.00/25.
- T06 implementation constraints: **6/7** — 12.86/15; only boolean `True` validation failed.

Combining these recovered raw contents with the original valid deliveries T01–T03 gives a diagnostic semantic-content score of:

**82.86 / 100**

This score is **not** the strict benchmark result. It measures how good the underlying generated code was after minimal deterministic envelope repair and is retained specifically to separate coding ability from protocol reliability.

## Per-task frozen interpretation

| Task | Skill | Original delivery | Strict score | Recovered semantic score | Interpretation |
|---|---|---|---:|---:|---|
| T01 | generation | valid / written | 15.00 | 15.00 | Complete success |
| T02 | debugging | valid / written | 6.43 | 6.43 | Genuine coding/debugging miss |
| T03 | comprehension | valid / written | 8.57 | 8.57 | Genuine comprehension/instruction miss |
| T04 | refactoring | malformed JSON | 0.00 | 15.00 | Transport failure; recovered code is fully correct |
| T05 | multi-file reasoning | malformed JSON | 0.00 | 25.00 | Transport failure; recovered code is fully correct |
| T06 | instruction following | malformed JSON | 0.00 | 12.86 | Mixed: transport failure plus one real boolean-validation miss |
| **Total** |  | **3/6 valid deliveries** | **30.00** | **82.86** |  |

Structured-output delivery success rate: **3 / 6 = 50%**.

## Raw-response failure analysis

### T04
Original adapter error:
- `JSONDecodeError: Invalid control character at line 1 column 340`.

Raw response contained a complete `_coerce_score` helper and `summarize_scores` implementation. The JSON string included literal unescaped newline/control characters and also lacked the final outer closing brace.

After envelope-only repair, the unchanged Python implementation passed **7/7** frozen tests.

Classification: **transport/serialization failure only**.

### T05
Original adapter error:
- `JSONDecodeError: Expecting ',' delimiter at line 1 column 584`.

The generated `order.py` used `pricing.line_subtotal` for each line, validated tax rate, accumulated subtotals and applied tax. The response was missing the final outer JSON closing brace.

After envelope-only repair, the unchanged Python implementation passed **7/7** frozen tests.

Classification: **transport/serialization failure only**.

### T06
Original adapter error:
- `JSONDecodeError: Expecting ',' delimiter at line 1 column 1493`.

The generated implementation was recoverable after restoring the missing outer JSON closing brace. It passed **6/7** frozen tests. The only failed top-level test was invalid-`k` handling because Python `bool` is a subclass of `int`; the model checked `isinstance(k, int)` but did not explicitly reject booleans.

Classification: **mixed transport + coding edge-case failure**.

## Inference performance — full six-task raw telemetry

All six preserved raw API files include Ollama timing metrics, including the three deliveries whose parsing failed.

Per-task values:

| Task | Prompt tokens | Prompt tok/s | Output tokens | Generation tok/s | API wall time |
|---|---:|---:|---:|---:|---:|
| T01 | 301 | 151.511 | 98 | 16.549 | 12.613 s |
| T02 | 406 | 165.932 | 118 | 15.917 | 9.976 s |
| T03 | 390 | 222.342 | 50 | 15.724 | 5.056 s |
| T04 | 526 | 171.478 | 262 | 15.962 | 19.602 s |
| T05 | 537 | 197.201 | 168 | 15.714 | 13.535 s |
| T06 | 360 | 234.249 | 372 | 16.101 | 24.753 s |

Weighted across all six API calls:

- prompt tokens: **2,520**;
- weighted prompt throughput: **186.46 tok/s**;
- generated tokens: **1,068**;
- weighted generation throughput: **16.01 tok/s**;
- summed API wall time: **85.535 s**.

The full benchmark process lasted about **91.25 s**, so adapter/test overhead outside API inference was relatively small.

The earlier isolated 4.36 prompt tok/s measurement is rejected as non-representative for ordinary benchmark prompts.

## Memory / swap behavior

Before the benchmark run:
- PhysMem: 7551 MB used;
- compressed: 1027 MB;
- unused: 79 MB;
- swap used: 885.69 MB;
- `ollama ps`: no loaded model.

After T01:
- model reported by Ollama: 4.1 GB, 100% GPU;
- swap: 1983.31 MB;
- memory-pressure free: 17%.

Reported Ollama resident size increased across the sequence:
- T01 4.1 GB;
- T02 4.2 GB;
- T03 4.4 GB;
- T04 4.5 GB;
- T05 4.7 GB;
- T06/final 4.8 GB.

Peak observed swap: **2486.94 MB** after T05.
Final swap: **2403.44 MB**, about **+1517.75 MB** versus run start.

Interpretation: the model is fast enough for interactive coding, but sustained use on 8 GB creates substantial memory pressure and SSD swap activity. The resident-size growth requires a later controlled memory experiment.

## Benchmark / adapter defects discovered and patched

Baseline 001 exposed two LOOM infrastructure issues.

### Scorer defect in Benchmark 01 v1.0.0
Verbose failing `unittest` subtest lines were incorrectly counted as additional tests. Patched in v1.0.1 so each top-level test method counts exactly once.

The original raw score **39.82/100** is retained only for audit history.

### Adapter delivery/telemetry defect
The original adapter:
- recorded metrics only after successful response parsing;
- allowed untouched starter files to receive artifact points after delivery failures;
- hard-coded benchmark version 1.0.0;
- provided no per-task progress output.

The hardened adapter now:
- records metrics before parsing;
- preserves raw responses;
- distinguishes artifact score and delivery-adjusted strict score;
- assigns zero strict points to failed deliveries;
- loads benchmark version from the manifest;
- prints per-task progress.

## Research finding from Baseline 001

For this model/runtime/hardware combination, structured-output reliability is a much larger end-to-end bottleneck than the raw code-content score suggests:

- strict delivery: **30.00/100**;
- deterministic raw-content recovery: **82.86/100**.

The 52.86-point gap is primarily caused by malformed JSON transport on T04–T06, not by absent code generation.

This finding directly motivates agentic-mode work: a practical local coding agent should not rely on a fragile JSON-encoded full-file payload when it can instead use robust file tools, patches, validation and retry loops.

## Frozen status

`CODING_BASELINE_001` is now frozen as the first complete LOOM quality/performance/memory reference.

Any future run must retain the distinction among:
- strict end-to-end delivery score;
- artifact score;
- optional explicitly labeled semantic/recovery analysis;
- protocol success rate;
- throughput;
- memory/swap behavior.
