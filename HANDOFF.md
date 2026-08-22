# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — real-M1 streaming attribution
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `MEMORY_FRONTIER_001_COMPLETE`
Next: `STREAMING_ATTRIBUTION_001`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical 8B system

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- `prefill_step_size=512`
- thinking disabled
- built-in M1 qmv_fast for fully resident real generation
- stable Pi bridge published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884`

REALGEN 001 external reference:
- real M1 generation 13.184615357 tok/s
- E2E 12.046861457 tok/s

## Agent/capability checkpoint

Request-boundary reclamation promoted after CAPABILITY 000I–000M:
1. ownership-check completed `GenerationBatch.Response`;
2. detach only stale completed-response `prompt_cache`;
3. call `mx.clear_cache()` once.

CAPABILITY 000M: real Pi reproducibility 3/3 functional and strict.

CAPABILITY 001 canonical baseline:
- `CAPABILITY_001_BASELINE_COMPLETE`
- practical-agent primary **1/11 = 9.09%**
- Coding Benchmark **45/100**
- critical failures 0
- resource-aborted C03, C06, G02, G03
- genuine non-resource reasoning failures include E01/E02

This baseline is retained unchanged for future capability comparisons.

## MEMORY-FRONTIER 001 — COMPLETE

Report:
`research/memory/memory-frontier-001-result.md`

Raw local evidence:
`results-local/memory/memory-frontier-001/20260822-141554/`

Classification:
`MEMORY_FRONTIER_001_COMPLETE`

All F1-F4 parity preflights PASS. All ten constituent runs preserve exact complete real-M1 token-ID sequences for all three prompts. No resource aborts.

### Measured frontier

| Config | Resident fraction | Real gen tok/s | E2E tok/s | Peak MLX | Min free | Logical streamed B/token |
|---|---:|---:|---:|---:|---:|---:|
| F0 FULL | 100.00% | 13.433 | 11.226 | 3,621,677,296 B | 23% | 0 |
| F1 H32 | 75.38% | 2.527 | 2.378 | 2,756,903,152 B | 24% | 896,041,120 |
| F2 H24 | 56.54% | 1.168 | 1.125 | 2,081,485,040 B | 34% | 1,582,012,640 |
| F3 H16 | 37.69% | 0.526 | 0.513 | 1,406,066,928 B | 47% | 2,267,984,160 |
| F4 H8 | 18.85% | 0.435 | 0.425 | 730,648,816 B | 57% | 2,953,955,680 |

All five are Pareto non-dominated: each lower-residency point buys memory/headroom at a throughput cost.

F1 is the strongest current compromise but still poor for practical generation:
- persistent raw-weight saving 882,255,872 B
- peak MLX saving 864,774,144 B
- real-generation retained only 18.81%
- E2E retained 21.18%

The synchronous streaming implementation is therefore a correctness/reference mechanism, not yet a practical runtime.

Important attribution caveat: logical streamed bytes are not physical SSD bytes. F1 logical streaming is ~896 MB/token while Darwin process-read diagnostic is only ~26.5 MB/token. Do not attribute the slowdown to SSD bandwidth without timing evidence.

## Exact next step — STREAMING-ATTRIBUTION 001

Frozen plan:
`research/memory/streaming-attribution-001-plan.md`

Target F1 H32 only, preserving exact residency/model math.

Measure where real-M1 per-token wall is spent among:
- source/range access;
- host-side tensor/parameter reconstruction;
- required MLX materialization/synchronization;
- streamed-stage forward compute;
- cleanup/orchestration;
- residual/unclassified wall.

Use one canonical REALGEN prompt, 32 unknown greedy tokens, separate exact-parity preflight and two fresh scientific F1 runs. Instrumentation must not add artificial synchronization merely to make categories convenient.

Do not implement prefetch/buffering/range-I/O changes until attribution identifies the actual dominant cost.

## Later

1. STREAMING-ATTRIBUTION 001
2. one-factor treatment selected from attribution (prefetch/buffering/range-I/O/materialization/etc.)
3. OUTCORE-BLOCK 001 where justified
4. representation work where justified
5. scale toward 27B/32B full-parameter-count execution
6. compare behavior-affecting promoted systems against CAPABILITY 001

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests; ChatGPT owns project-state documentation and GitHub administration.
