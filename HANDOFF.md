# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — deferred-cleanup streamed-layer gradient
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STREAMED_LAYER_CLEANUP_DEFER_001_COMPLETE`
Next: `STREAMED_LAYER_GRADIENT_002`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, jointly balancing:

1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

A final promoted LOOM-produced model must also have a validated decensored behavioral profile produced through Heretic or a LOOM-native independently implemented equivalent. This later requirement does not alter the current memory/runtime sequence.

Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

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

## Memory/residency sequence

MEMORY-FRONTIER 001 proved exact real-M1 partial residency but naive synchronous streaming is too slow: FULL 13.433 tok/s; H32 2.527; H24 1.168; H16 0.526; H8 0.435.

SHARED-STAGE-RESIDENCY 001 established the first hierarchy rule: embedding/final norm/LM head remain hot. Persisting them while streaming layers 32..35 recovered +36.66% generation throughput with exact parity.

## Streamed-layer gradient 001 — COMPLETE

With all shared stages persistent and the original streamed-layer cleanup lifecycle:

| Arm | Streamed layers | Gen tok/s | Wall/token |
|---|---:|---:|---:|
| S0 | 0 | 14.022271 | 71.315 ms |
| S1 | 1 | 5.819925 | 171.824 ms |
| S2 | 2 | 4.755397 | 210.287 ms |
| S4 | 4 | 3.463355 | 288.737 ms |

Exact parity PASS everywhere; no resource aborts.

Descriptive model:
`wall/token ≈ 71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms, R²≈0.999993.

This separated fixed stream activation from repeated marginal per-layer lifecycle.

## Fixed activation work — CLOSED

### SHARED-CLEANUP-CONSOLIDATION 001 — material PASS

On exact S1, removing only post-embedding/post-norm shared cleanup:
- 5.643 -> 7.065 tok/s
- +25.206% generation
- -35.678 ms/token
- exact parity PASS
- peak MLX unchanged.

This cleanup-consolidated S1 became the promoted fixed-activation baseline.

### EMBED-EVAL-BOUNDARY 001 — NO-GO

Removing post-embedding `mx.eval(h)` regressed generation by 3.346%. Retain it.

### NORM-EVAL-BOUNDARY 001 — SMALL / NOT PROMOTED

Removing final-norm `mx.eval(h2)` gave only +0.762% generation / -1.080 ms/token. Below the 5% material threshold. Retain it. Do not test LM-head eval without new evidence.

## STREAMED-LAYER-CLEANUP-DEFER 001 — COMPLETE / MATERIAL PASS

Report: `research/memory/streamed-layer-cleanup-defer-001-result.md`.
Raw evidence: `results-local/memory/streamed-layer-cleanup-defer-001/20260822-180629/`.

Both arms used promoted cleanup-consolidated S1:
- layers 0..34 persistent;
- layer 35 streamed;
- shared stages persistent;
- persistent raw `3,499,501,056 B`;
- logical streaming `84,427,264 B/token`;
- embedding/norm/head evals retained;
- only final shared cleanup retained.

CONTROL retained layer-35 post-forward cleanup.

TREATMENT kept select-time cleanup, load/select/reconstruction/materialization/forward/eval and transient deletion/release identical, but omitted exactly one layer-local post-forward `gc.collect()` and one `mx.clear_cache()` per generated token, deferring reclamation to the existing final post-head cleanup.

Pooled ABBA:
- CONTROL: 6.997 tok/s; 142.918 ms/token; E2E 6.135; median TTFT 1.274 s
- TREATMENT: 8.223 tok/s; 121.610 ms/token; E2E 7.101; median TTFT 1.203 s

Causal effect:
- generation **+17.522%**
- E2E **+15.750%**
- wall/token **-21.308 ms (-14.910%)**
- TTFT **-5.566%**
- peak active delta `0 B`
- observed peak active+cache delta `0 B`
- free-floor delta `-1 pp`
- peak swap delta `-25.81 MB`
- exact parity PASS
- no resource aborts.

The removed 21.308 ms/token is ~54.64% of the historical ~39 ms/layer reference, contextual only. No internal attribution to Python GC, MLX allocator, Metal, CPU or I/O is claimed; physical SSD traffic remains unproven.

Decision: promote deferred post-forward streamed-layer cleanup for further marginal-lifecycle research.

## Exact next step — STREAMED-LAYER-GRADIENT 002

Frozen plan: `research/memory/streamed-layer-gradient-002-plan.md`.

Remeasure S0/S1/S2/S4 under the promoted lifecycle:
- shared stages persistent;
- embedding/norm/head evals retained;
- post-embedding/post-norm shared cleanup absent;
- streamed-layer select-time cleanup unchanged;
- streamed-layer deletion/release unchanged;
- streamed-layer post-forward GC/cache cleanup omitted for every streamed layer;
- exactly one final post-head cleanup/token.

Use balanced order `S0 -> S4 -> S2 -> S1 -> S1 -> S2 -> S4 -> S0`, exact token parity, first three REALGEN prompts and low-overhead telemetry.

Primary question: does the speed gain scale across 2 and 4 streamed layers without unacceptable transient active+cache/free/swap accumulation? Measure the new marginal slope before changing another mechanism.

## Behavioral-freedom / Heretic requirement — FROZEN, NOT ACTIVE YET

Every final promoted LOOM model must eventually pass a behavioral-edit stage reducing unwanted refusal/alignment behavior while preserving measured capability and resource viability.

Accepted routes:
- Heretic directly where licensing/backend fit is acceptable; or
- a LOOM-native clean implementation of the same general contrastive residual-direction / low-rank editing primitive.

Initial future checkpoint: `STREAMING_RESIDUAL_MEAN_PARITY` before any model editing.

## Later

1. STREAMED-LAYER-GRADIENT 002
2. select the next marginal per-layer mechanism only from the new slope/resource evidence
3. candidates: select-time cleanup, scheduling/prefetch, buffering/grouping, reconstruction/materialization reuse, source I/O only when evidenced
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems
8. Heretic-derived / LOOM-native decensoring validation before final model promotion

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
