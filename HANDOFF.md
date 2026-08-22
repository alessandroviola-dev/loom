# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — streamed transformer cost gradient
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `SHARED_STAGE_RESIDENCY_001_COMPLETE`
Next: `STREAMED_LAYER_GRADIENT_001`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, balancing memory, speed and capability.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.

ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical references

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- thinking disabled
- REALGEN 001 real M1 generation 13.184615357 tok/s; E2E 12.046861457 tok/s
- CAPABILITY 001 practical-agent baseline 1/11 = 9.09%; Coding Benchmark 45/100

Stable Pi bridge published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884` with ownership-checked stale-response `prompt_cache` detach + one `mx.clear_cache()` after completed responses.

## MEMORY-FRONTIER 001 — COMPLETE

Report: `research/memory/memory-frontier-001-result.md`.

Exact real-M1 parity passed for FULL/H32/H24/H16/H8 and no resource aborts.

| Config | Resident fraction | Gen tok/s | Peak MLX |
|---|---:|---:|---:|
| F0 FULL | 100.00% | 13.433 | 3,621,677,296 B |
| F1 H32 | 75.38% | 2.527 | 2,756,903,152 B |
| F2 H24 | 56.54% | 1.168 | 2,081,485,040 B |
| F3 H16 | 37.69% | 0.526 | 1,406,066,928 B |
| F4 H8 | 18.85% | 0.435 | 730,648,816 B |

Naive synchronous streaming is correctness-valid and memory-effective but far too slow.

## STREAMING-ATTRIBUTION 001 — PARTIAL

Report: `research/memory/streaming-attribution-001-result.md`.

Classification `STREAMING_ATTRIBUTION_001_PARTIAL`; bottleneck `ATTRIBUTION_UNRESOLVED`.

Tracing preserved parity but slowed F1 from historical 2.527 tok/s to ~1.703 tok/s, preventing a clean internal bottleneck claim. The trace nevertheless identified embedding and LM head as large system-level hotspots. Physical SSD traffic remains unproven.

## SHARED-STAGE-RESIDENCY 001 — COMPLETE

Report: `research/memory/shared-stage-residency-001-result.md`.
Raw local evidence: `results-local/memory/shared-stage-residency-001/20260822-162744/`.

One-factor ABBA test on F1/H32:

CONTROL:
- layers 0..31 persistent
- layers 32..35 streamed
- embedding/final norm/LM head streamed
- 2.532 real tok/s
- peak MLX 2,739,421,424 B
- logical streamed 882,255,872 B/token

TREATMENT:
- identical transformer residency
- layers 32..35 still streamed identically
- embedding/final norm/LM head persistent
- 3.459 real tok/s
- peak MLX 3,283,968,240 B
- logical streamed 337,709,056 B/token

Causal treatment effect:
- generation **+36.66%**
- E2E **+34.80%**
- TTFT **-13.34%**
- peak MLX +544,546,816 B
- exact token parity PASS
- no resource aborts

The treatment still saves 337,709,056 B persistent raw weights / peak MLX versus F0 but retains only 25.75% of F0 generation throughput.

Conclusion: repeated shared-stage streaming is a material addressable cost, but it is not sufficient to explain the F1 slowdown. After shared stages are made persistent, the remaining intentional residency difference versus FULL is the four streamed transformer layers 32..35.

## Exact next step — STREAMED-LAYER-GRADIENT 001

Frozen plan: `research/memory/streamed-layer-gradient-001-plan.md`.

Low-overhead causal gradient with all shared stages persistent:
- S0: 0 streamed transformer layers / FULL residency
- S1: layer 35 streamed
- S2: layers 34..35 streamed
- S4: layers 32..35 streamed

Two fresh runs/arm in symmetric order `S0 -> S4 -> S2 -> S1 -> S1 -> S2 -> S4 -> S0`, first three REALGEN prompts, exact token parity, no invasive tracing.

Measure marginal ms/token per streamed layer and classify whether residual stream cost is approximately additive or fixed/nonlinear. This decides whether the first optimization should target the per-layer lifecycle itself or a larger fixed orchestration/scheduling component.

Do not begin prefetch, buffering, range-I/O or OUTCORE-BLOCK inside this gradient.

## Later

1. STREAMED-LAYER-GRADIENT 001
2. first evidence-selected transformer streaming treatment
3. further overlap/range-I/O/materialization work as justified
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
