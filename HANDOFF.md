# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — shared-stage residency refinement
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STREAMING_ATTRIBUTION_001_PARTIAL`
Next: `SHARED_STAGE_RESIDENCY_001`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical 8B references

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- thinking disabled
- REALGEN 001 real M1 generation 13.184615357 tok/s; E2E 12.046861457 tok/s
- CAPABILITY 001 practical-agent baseline 1/11 = 9.09%; Coding Benchmark 45/100

Stable Pi bridge is published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884` with ownership-checked stale-response `prompt_cache` detach + one `mx.clear_cache()` after every completed response.

## MEMORY-FRONTIER 001 — COMPLETE

Report: `research/memory/memory-frontier-001-result.md`.

Exact real-M1 token parity passed for all partial-residency points. No resource aborts.

Measured pooled frontier:

| Config | Resident fraction | Gen tok/s | Peak MLX | Min free |
|---|---:|---:|---:|---:|
| F0 FULL | 100.00% | 13.433 | 3,621,677,296 B | 23% |
| F1 H32 | 75.38% | 2.527 | 2,756,903,152 B | 24% |
| F2 H24 | 56.54% | 1.168 | 2,081,485,040 B | 34% |
| F3 H16 | 37.69% | 0.526 | 1,406,066,928 B | 47% |
| F4 H8 | 18.85% | 0.435 | 730,648,816 B | 57% |

Current synchronous streaming is correctness-valid but too slow. F1 saves ~865 MB peak MLX yet retains only 18.81% of F0 generation throughput.

## STREAMING-ATTRIBUTION 001 — PARTIAL

Report: `research/memory/streaming-attribution-001-result.md`.

Classification: `STREAMING_ATTRIBUTION_001_PARTIAL`.
Bottleneck classification: `ATTRIBUTION_UNRESOLVED`.

Exact 16-token parity passed.

Two instrumented F1/H32 runs:
- 1.689 tok/s and 1.718 tok/s
- TTFT 3.286 s / 3.384 s
- peak MLX 2,752,856,248 B
- minimum free 17%

Largest traced category was materialization/synchronization (~240 ms/token mean), but MLX asynchrony makes category shares non-additive.

Largest traced stage hotspots:
1. LM head ~134.5 ms/token
2. embedding ~131.8 ms/token
3. streamed transformer layers ~50–58 ms/token each

F1 streams 882,255,872 logical B/token. Embedding + final norm + LM head account for 544,546,816 B/token (~61.7%).

Critical limitation: instrumented pooled rate ~1.703 tok/s was ~32.6% below historical uninstrumented F1 2.527 tok/s, with no contemporaneous uninstrumented control. Therefore no primary bottleneck claim is promoted. Physical SSD traffic remains unproven.

## Exact next step — SHARED-STAGE-RESIDENCY 001

Frozen plan:
`research/memory/shared-stage-residency-001-plan.md`

One factor only.

CONTROL: exact F1/H32 — layers 0..31 persistent; layers 32..35 + embedding + final norm + LM head streamed.

TREATMENT: keep the same transformer residency, but make embedding + final norm + LM head persistent. Only layers 32..35 remain streamed.

Expected treatment persistent raw weights: 3,246,219,264 B.
Expected streamed token-path bytes: 337,709,056 B.

This adds 544,546,816 B persistent versus F1 but still saves 337,709,056 B versus F0. Run contemporaneous ABBA control/treatment without invasive tracing, exact token parity, first three REALGEN prompts and full memory/speed/I/O metrics.

The question is whether removing repeated shared-stage streaming recovers enough real-M1 speed to create a materially better RAM/speed point.

Do not start prefetch/range-I/O/buffering until this direct A/B is reviewed.

## Later

1. SHARED-STAGE-RESIDENCY 001
2. evidence-selected scheduling/I/O/materialization treatment
3. OUTCORE-BLOCK 001 where justified
4. representation work where justified
5. scale toward 27B/32B full-parameter-count execution
6. capability comparison for promoted behavior-affecting systems

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
