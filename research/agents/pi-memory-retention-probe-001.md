# Pi Memory Retention Probe 001 — Result

Date: 2026-08-18
Run id: `20260818-223251`
Status: **COMPLETED / VALID**

## Question

Does Ollama reported allocation grow across repeated identical small Pi calls when the model remains warm, or was the Agentic 001 trajectory from 4.4 GB to 7.2 GB primarily associated with task/high-water complexity?

## Configuration

- Reference machine: Apple M1, 8 GB unified memory
- Pi: 0.84.2
- Ollama: 0.32.14
- Model: `qwen3.5:4b-mlx`
- Context: 4096
- Identical small Pi/read workload on every iteration
- Warm arm: model stopped once before arm, then 4 calls without stopping between calls
- Cold arm: 2 calls with `ollama stop` before each call

## Results

| Iteration | Success | Wall | Ollama size | Context | Swap used | Memory free | Usage total |
|---|---|---:|---:|---:|---:|---:|---:|
| warm-01 | true | 17.638 s | 4.1 GB | 4096 | 2050.06 MB | 22% | 1008 |
| warm-02 | true | 9.874 s | 4.3 GB | 4096 | 1954.06 MB | 14% | 1015 |
| warm-03 | true | 9.329 s | 4.4 GB | 4096 | 1930.06 MB | 17% | 1010 |
| warm-04 | true | 7.505 s | 4.5 GB | 4096 | 1922.06 MB | 16% | 986 |
| cold-01 | true | 14.551 s | 4.1 GB | 4096 | 1984.31 MB | 16% | 969 |
| cold-02 | true | 17.392 s | 4.1 GB | 4096 | 2056.12 MB | 18% | 1015 |

All six calls succeeded.

## Findings

### 1. Small warm retention exists

Across four identical warm calls, Ollama reported size increased:

`4.1 -> 4.3 -> 4.4 -> 4.5 GB`

Net warm-arm size increase: **+0.4 GB**.

Therefore repeated calls with the model kept loaded can retain or raise some runtime allocation even when workload and context configuration are unchanged.

### 2. The warm-arm size increase did not produce monotonic swap growth

Swap used across the warm arm was:

`2050.06 -> 1954.06 -> 1930.06 -> 1922.06 MB`

So swap decreased by about **128 MB** while Ollama reported size increased by 0.4 GB.

This is strong evidence that the `ollama ps` SIZE metric and host swap usage must not be treated as equivalent measures of resident physical pressure.

### 3. Cold unload resets the observed Ollama size baseline

Both cold calls ended at exactly **4.1 GB** after `ollama stop` before each run.

This supports that the extra warm allocation is associated with state retained while the model stays loaded and is cleared by unloading the model.

### 4. Simple call count does not reproduce Agentic 001

Pi Agentic Coding Benchmark 001 showed:

`4.4 -> 5.2 -> 5.6 -> 6.4 -> 6.8 -> 7.2 GB`

The identical-call warm probe showed only:

`4.1 -> 4.3 -> 4.4 -> 4.5 GB`

Therefore the large Agentic 001 growth cannot be explained by invocation count alone.

The present evidence is consistent with a combination of retained warm allocation plus workload-dependent high-water behavior, potentially involving provider request size, multiple agent/tool turns, or runtime allocator/cache behavior. These are hypotheses, not yet causal findings.

### 5. Warm calls are faster after initial load

Observed wall times:

`17.638 -> 9.874 -> 9.329 -> 7.505 s`

Cold calls were `14.551 s` and `17.392 s`.

This is consistent with avoiding repeated model load/setup costs in the warm arm, but this probe was designed for memory retention rather than rigorous latency decomposition.

## What this rules out

The data do **not** support the simple hypothesis:

> Every separate Pi invocation inherently adds roughly the same amount of retained memory until the model reaches 7+ GB.

Four identical calls added only 0.4 GB and did not progressively increase swap.

## What remains unresolved

- Whether direct Ollama/MLX calls without Pi show the same warm retention.
- Whether retained allocation scales with prompt/context pressure.
- Whether multiple tool turns/API round trips within a Pi session materially increase the high-water allocation.
- Whether `ollama ps` SIZE reflects allocator reservation, KV/cache state, runtime buffers, or another combination.

Do not label the observed behavior a memory leak without lower-level evidence.

## Next experiment

Run a direct Ollama/MLX context-pressure retention probe, without Pi, using controlled prompt sizes and warm/cold arms. This will determine whether the main retention behavior is present in the runtime itself before adding agent-harness effects back in.
