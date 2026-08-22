# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — marginal streamed-layer lifecycle optimization
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `NORM_EVAL_BOUNDARY_001_COMPLETE`
Next: `STREAMED_LAYER_CLEANUP_DEFER_001`

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

## Streamed-layer gradient — COMPLETE

With all shared stages persistent:

| Arm | Streamed layers | Gen tok/s | Wall/token |
|---|---:|---:|---:|
| S0 | 0 | 14.022271 | 71.315 ms |
| S1 | 1 | 5.819925 | 171.824 ms |
| S2 | 2 | 4.755397 | 210.287 ms |
| S4 | 4 | 3.463355 | 288.737 ms |

Exact parity PASS everywhere; no resource aborts.

Descriptive system model:
`wall/token ≈ 71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms, R²≈0.999993.

This separates a fixed stream-activation term from a repeated marginal per-layer cost.

## Fixed activation work — CLOSED

Source audit found shared-stage eval boundaries and cleanup as once-per-token stream-only work.

### SHARED-CLEANUP-CONSOLIDATION 001 — material PASS

On exact S1, removing only post-embedding and post-norm shared cleanup while retaining layer-35 cleanup, final cleanup and all evals produced:
- 5.643 -> 7.065 gen tok/s
- +25.206% generation
- -35.678 ms/token
- exact parity PASS
- peak MLX unchanged
- no resource aborts.

This cleanup-consolidated S1 is the promoted experimental baseline.

### EMBED-EVAL-BOUNDARY 001 — NO-GO

Removing only post-embedding `mx.eval(h)`:
- 7.069 -> 6.833 tok/s
- -3.346% generation
- +4.897 ms/token
- exact parity PASS
- peak MLX unchanged.

Decision: retain post-embedding eval.

### NORM-EVAL-BOUNDARY 001 — COMPLETE / SMALL

Report: `research/memory/norm-eval-boundary-001-result.md`.
Raw evidence: `results-local/memory/norm-eval-boundary-001/20260822-175311/`.

Removing only final-norm `mx.eval(h2)` while keeping downstream `mx.eval(logits)` produced:
- CONTROL 7.003 tok/s; 142.799 ms/token
- TREATMENT 7.056 tok/s; 141.719 ms/token
- generation +0.762%
- E2E +0.667%
- wall/token -1.080 ms
- peak MLX delta 0 B
- exact parity PASS
- no resource aborts.

Interpretation: `NORM_EVAL_COST_SMALL`. Below the 5% material threshold, so this treatment is **not promoted**. Retain the explicit norm eval in the baseline.

The obvious shared-stage eval-boundary axis is now closed. Do not test LM-head eval removal without new evidence.

## Exact next step — STREAMED-LAYER-CLEANUP-DEFER 001

Frozen plan: `research/memory/streamed-layer-cleanup-defer-001-plan.md`.

Use the promoted cleanup-consolidated S1 baseline:
- layers 0..34 persistent;
- layer 35 streamed;
- shared stages persistent;
- all explicit embedding/norm/head evals retained;
- post-embedding/post-norm shared cleanups absent;
- final post-head cleanup retained.

CONTROL keeps the current layer-35 cleanup.

TREATMENT keeps layer-35 load/select/reconstruction/materialization/forward/eval and deletion/release semantics identical, but defers only its `gc.collect()/mx.clear_cache()` cleanup to the final cleanup already present later in the token pass.

Run low-overhead ABBA with exact token parity and first three REALGEN prompts. This is the first direct treatment of the marginal streamed-layer lifecycle, not the fixed activation term.

## Behavioral-freedom / Heretic requirement — FROZEN, NOT ACTIVE YET

Every final promoted LOOM model must eventually pass a behavioral-edit stage reducing unwanted refusal/alignment behavior while preserving measured capability and resource viability.

Accepted routes:
- Heretic directly where licensing/backend fit is acceptable; or
- a LOOM-native clean implementation of the same general contrastive residual-direction / low-rank editing primitive.

Initial future checkpoint: `STREAMING_RESIDUAL_MEAN_PARITY` before any model editing.

## Later

1. STREAMED-LAYER-CLEANUP-DEFER 001
2. remeasure marginal streamed-layer slope if treatment is material
3. further evidence-selected per-layer treatments: scheduling/prefetch, buffering/grouping, reconstruction/materialization reuse, source I/O only when evidenced
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems
8. Heretic-derived / LOOM-native decensoring validation before final model promotion

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
