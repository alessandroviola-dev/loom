# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — marginal streamed-layer lifecycle optimization
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STREAMED_LAYER_GRADIENT_002_COMPLETE`
Next: `SELECT_TIME_GC_DEFER_001`

Historical detailed state through REALGEN 002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

## Mission

**Big models. Small machines.** Run the strongest practical full-parameter-count LLM possible on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models, jointly balancing:
1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

Every final promoted LOOM-produced model must also have a validated decensored behavioral profile using Heretic or a LOOM-native independently implemented equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`. This later requirement does not alter the current runtime sequence.

## Operating split

Pi: local code/runtime inspection/tests/concise evidence.
ChatGPT: experiment design/review, GitHub synchronization, HANDOFF/ROADMAP and research continuity.

## Canonical references

- Qwen3-8B full parameter count
- affine 3-bit/group64
- BF16 KV
- MLX/mlx-metal 0.31.2; mlx-lm 0.31.3
- thinking disabled
- REALGEN001 historical real M1 generation 13.184615357 tok/s; E2E 12.046861457 tok/s
- CAPABILITY001 practical-agent 1/11 = 9.09%; Coding Benchmark 45/100

## Memory / residency

MEMORY-FRONTIER001 proved exact partial residency but naive synchronous streaming was too slow: FULL 13.433 tok/s; H32 2.527; H24 1.168; H16 0.526; H8 0.435.

SHARED-STAGE-RESIDENCY001 established that embedding/final norm/LM head should remain hot/persistent.

## Fixed stream activation — CLOSED

STREAMED-LAYER-GRADIENT001 under the old lifecycle measured S0/S1/S2/S4 wall/token 71.315/171.824/210.287/288.737 ms and a descriptive model `71.315 + 61.284*I(streaming) + 39.007*N` ms/token.

SHARED-CLEANUP-CONSOLIDATION001 materially improved exact S1 by +25.206% generation / -35.678 ms/token with no peak-MLX increase. This cleanup consolidation is promoted.

EMBED-EVAL-BOUNDARY001 was NO-GO (-3.346%). Retain embedding eval.

NORM-EVAL-BOUNDARY001 was SMALL (+0.762%). Not promoted; retain norm eval. Do not test LM-head eval without new evidence.

## STREAMED-LAYER-CLEANUP-DEFER001 — MATERIAL PASS

On promoted S1, removing only one per-token layer-35 post-forward `gc.collect()/mx.clear_cache()` while retaining select-time cleanup and all load/reconstruction/materialization/forward/eval/deletion semantics produced:
- 6.997 -> 8.223 tok/s
- +17.522% generation
- -21.308 ms/token
- exact parity PASS
- peak active delta 0 B
- observed peak active+cache delta 0 B
- no resource aborts.

Deferred post-forward streamed-layer cleanup is promoted.

## STREAMED-LAYER-GRADIENT002 — COMPLETE

Report: `research/memory/streamed-layer-gradient-002-result.md`.
Raw evidence: `results-local/memory/streamed-layer-gradient-002/20260822-181943/`.

Frozen improved lifecycle: shared stages persistent; explicit shared evals retained; intermediate shared cleanup absent; select-time cleanup retained per streamed layer; streamed-layer post-forward GC/cache cleanup omitted; transient modules/values deleted; one final post-head cleanup/token.

Pooled:

| Arm | Streamed layers | Tok/s | Wall/token | Peak active B | Min free |
|---|---:|---:|---:|---:|---:|
| S0 | 0 | 11.101 | 90.078 ms | 3,806,718,372 | 23% |
| S1 | 1 | 8.037 | 124.425 ms | 3,633,031,420 | 20% |
| S2 | 2 | 6.546 | 152.775 ms | 3,548,604,156 | 15% |
| S4 | 4 | 5.015 | 199.383 ms | 3,379,749,628 | 23% |

All arms 2/2 valid; exact parity PASS; no resource aborts. Deferred cleanup remained SAFE through four streamed layers.

New marginal penalties:
- S1-S0 +34.347 ms/layer
- S2-S1 +28.350 ms/layer
- S4-S2 +23.304 ms/layer

Mean 28.667 ms/layer. Linear descriptive slope 26.954 ms/layer, R² 0.991260.

Two-component descriptive fit:
`wall/token ≈ 90.078 + 11.043*I(streaming_active) + 24.746*N_streamed_layers` ms, R² 0.998866.

Interpretation: `DEFERRED_STREAM_LAYER_COST_FIXED_OR_NONLINEAR`. Marginal cost declines as more streamed layers are added. Cross-experiment comparison to Gradient001 is contextual only.

## Exact next step — SELECT-TIME-GC-DEFER001

Frozen plan: `research/memory/select-time-gc-defer-001-plan.md`.

Use promoted S1 with one streamed layer and deferred post-forward cleanup.

CONTROL retains the remaining select-time `gc.collect()` after `mx.load`/tensor selection and deletion/release of the full loaded weight container.

TREATMENT keeps deletion/release at the identical point but omits/defer only that select-time `gc.collect()`. No other lifecycle, residency, I/O, eval, model-math or cleanup factor changes.

Run low-overhead ABBA with exact token parity and first three REALGEN prompts. Measure speed plus active/cache/free/swap. If material, remeasure gradient before moving to prefetch/buffering/I-O work.

## Behavioral-freedom / Heretic requirement — FROZEN, NOT ACTIVE

Every final promoted LOOM model must eventually pass behavioral editing/decensoring validation with capability/resource preservation. Initial future checkpoint: `STREAMING_RESIDUAL_MEAN_PARITY` before model editing.

## Later

1. SELECT-TIME-GC-DEFER001
2. remeasure gradient if material
3. next evidence-selected marginal mechanism: scheduling/prefetch, buffering/grouping, reconstruction/materialization reuse, source I/O only if evidenced
4. OUTCORE-BLOCK001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems
8. Heretic-derived / LOOM-native decensoring validation before final promotion

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns GitHub research documentation and GitHub administration.
