# Pi Agentic Cold Replay 001 — Result

Date: 2026-08-18
Run id: `20260818-230858`
Status: **COMPLETED — VALID FOR T01–T05; T06 INVALID/TIMEOUT**

## Purpose

Test whether the large Ollama `SIZE` trajectory observed during the frozen warm Pi Agentic Coding Benchmark 001 (`4.4 -> 7.2 GB`) is primarily intrinsic to each task workload or substantially caused by retained warm high-water state across successive tasks.

Each benchmark task was replayed with the same agentic task shape and an explicit `ollama stop qwen3.5:4b-mlx` before that task. Hidden tests were not exposed and no benchmark score was changed by this replay.

Historical warm values are from frozen Pi Agentic Coding Benchmark 001.

## Results

| Task | Cold process | Cold tools | Hist tools | Cold usage | Hist usage | Cold SIZE | Warm historical SIZE | Warm-Cold gap |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| T01 | PASS | 1 | 2 | 2146 | 2474 | 4.3 GB | 4.4 GB | 0.1 GB |
| T02 | PASS | 5 | 8 | 3833 | 4240 | 4.7 GB | 5.2 GB | 0.5 GB |
| T03 | PASS | 3 | 2 | 4217 | 2923 | 4.5 GB | 5.6 GB | 1.1 GB |
| T04 | PASS | 6 | 5 | 5494 | 4213 | 4.9 GB | 6.4 GB | 1.5 GB |
| T05 | PASS | 4 | 3 | 4026 | 2581 | 4.5 GB | 6.8 GB | 2.3 GB |
| T06 | **FAIL / timeout** | 0 | 2 | N/A | 3778 | 4.4 GB | 7.2 GB | **not comparable** |

T06 ran for ~300 s, emitted no tool call and no provider usage snapshot, and therefore is not a valid workload replay. Its 4.4 GB post-timeout measurement must not be used as a cold T06 task requirement.

## Resource observations

Cold replay post-task swap / memory-free values:

- T01: swap 2116.69 MB, free 16%
- T02: swap 2398.38 MB, free 13%
- T03: swap 1571.00 MB, free 8%
- T04: swap 2181.44 MB, free 14%
- T05: swap 1895.56 MB, free 15%
- T06 timeout: swap 2443.69 MB, free 13%

All reported Ollama contexts remained 4096.

## Canonical interpretation

The cold replay provides strong evidence that **retained cross-task warm high-water is a major contributor** to the frozen Agentic 001 `4.4 -> 7.2 GB` trajectory.

The most discriminating observations are T03–T05:

- T03 cold used **4217** provider-reported tokens vs historical **2923**, and 3 tools vs historical 2, yet cold SIZE was only **4.5 GB** vs warm historical **5.6 GB**.
- T04 cold used **5494** vs historical **4213** tokens, and 6 tools vs historical 5, yet cold SIZE was **4.9 GB** vs warm historical **6.4 GB**.
- T05 cold used **4026** vs historical **2581** tokens, and 4 tools vs historical 3, yet cold SIZE was **4.5 GB** vs warm historical **6.8 GB**.

Thus the warm historical values cannot be explained simply by those tasks being individually larger or more tool-heavy. In several cases the cold replay was heavier by the available usage/tool measures and still remained materially smaller.

Across the five valid task replays, cold SIZE stayed within **4.3–4.9 GB**, while the historical warm sequence rose monotonically from **4.4 to 6.8 GB** by T05. The warm-minus-cold gap increased with sequence position: **0.1, 0.5, 1.1, 1.5, 2.3 GB** for T01–T05.

This pattern is consistent with cumulative retained runtime allocation/high-water state across successive warm workloads.

## What this does and does not establish

Supported:

1. Individual cold task workload alone does not reproduce the late-run 6–7 GB `SIZE` values for T01–T05.
2. Cross-task warm retention is a substantial component of the sustained benchmark memory trajectory.
3. The magnitude of the warm-cold gap grows later in the task sequence.
4. `ollama stop` materially resets the runtime state relevant to subsequent `SIZE` observations.

Not established:

- the exact internal meaning of Ollama `SIZE`;
- whether the retained state is KV cache, MLX allocator high-water, fragmentation, buffer reuse, model/runtime bookkeeping, or another mechanism;
- a precise percentage of the 7.2 GB value attributable to any one mechanism;
- a valid cold requirement for T06, because its replay timed out before tool use.

Do not describe the behavior as a memory leak without lower-level evidence.

## Research consequence

The main practical conclusion for LOOM on the 8 GB reference Mac is now actionable:

> Sustained agentic use can accumulate a much larger warm memory high-water than isolated task execution. Periodic model unload/reload is therefore a plausible memory-pressure mitigation, although its latency/performance tradeoff still needs product-level evaluation.

The synthetic multi-turn probes no longer need further redesign solely to explain the original 7.2 GB trajectory. The next queued Phase 3 experiment should return to the secondary harness question: Qwen Code minimal/safe-mode behavior at context 4096.
