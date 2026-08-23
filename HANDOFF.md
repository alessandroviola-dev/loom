# LOOM — Active Handoff

Last updated: 2026-08-23
Status: ACTIVE — streamed-block reconstruction/reuse audit
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `SELECT_TIME_GC_DEFER_001_COMPLETE`
Next: `STREAMED_BLOCK_REUSE_AUDIT_001`

Historical detailed state through REALGEN002 is preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual reports.

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

MEMORY-FRONTIER001 proved exact partial residency but naive synchronous streaming was too slow. SHARED-STAGE-RESIDENCY001 established embedding/final norm/LM head as hot/persistent.

## Fixed stream activation — CLOSED

Old Gradient001 measured a descriptive `71.315 + 61.284*I(streaming) + 39.007*N` ms/token.

Promoted cleanup consolidation removed shared intermediate cleanup on S1:
- +25.206% generation
- -35.678 ms/token
- exact parity PASS
- no peak-MLX increase.

Embedding eval removal was NO-GO (-3.346%). Retain it.

Norm eval removal was SMALL (+0.762%). Not promoted; retain it. Do not test LM-head eval without new evidence.

## Marginal streamed-layer lifecycle

### STREAMED-LAYER-CLEANUP-DEFER001 — MATERIAL PASS

Removing only the per-layer post-forward `gc.collect()/mx.clear_cache()` on promoted S1 while keeping select-time cleanup and load/reconstruction/materialization/forward/eval/deletion identical produced:
- 6.997 -> 8.223 tok/s
- +17.522% generation
- -21.308 ms/token
- exact parity PASS
- no resource aborts
- no observed peak active/active+cache increase.

Promoted.

### STREAMED-LAYER-GRADIENT002 — COMPLETE

Report: `research/memory/streamed-layer-gradient-002-result.md`.
Raw evidence: `results-local/memory/streamed-layer-gradient-002/20260822-181943/`.

Under promoted deferred post-forward cleanup:

| Arm | Streamed layers | Tok/s | Wall/token | Min free |
|---|---:|---:|---:|---:|
| S0 | 0 | 11.101 | 90.078 ms | 23% |
| S1 | 1 | 8.037 | 124.425 ms | 20% |
| S2 | 2 | 6.546 | 152.775 ms | 15% |
| S4 | 4 | 5.015 | 199.383 ms | 23% |

All arms 2/2 valid, exact parity PASS, no resource aborts. Deferred cleanup remained SAFE through four streamed layers.

Marginals:
- first layer +34.347 ms
- second +28.350 ms
- layers 3–4 +23.304 ms/layer.

Two-component descriptive fit:
`90.078 + 11.043*I(streaming_active) + 24.746*N_streamed_layers` ms/token, R² 0.998866.

Interpretation: `DEFERRED_STREAM_LAYER_COST_FIXED_OR_NONLINEAR`.

### SELECT-TIME-GC-DEFER001 — COMPLETE / NO-GO

Report: `research/memory/select-time-gc-defer-001-result.md`.
Raw evidence: `results-local/memory/select-time-gc-defer-001/20260823-180124/`.

Exact promoted S1 A/B. CONTROL retained one select-time `gc.collect()` after deleting/releasing the full loaded-weight container. TREATMENT omitted only that GC while keeping ownership, logical I/O, residency, post-forward policy and all model/eval semantics identical.

Pooled:
- CONTROL 8.293 tok/s; 120.577 ms/token; E2E 7.141; median TTFT 1.203 s; min free 19%
- TREATMENT 7.767 tok/s; 128.754 ms/token; E2E 6.731; median TTFT 1.388 s; min free 11%

Effect:
- generation **-6.351%**
- E2E **-5.752%**
- wall/token **+8.177 ms**
- TTFT **+15.374%**
- peak active/active+cache unchanged
- free-floor -8 pp
- exact parity PASS
- no resource aborts.

Decision: `SELECT_TIME_GC_NO_GO`. Retain select-time GC in the promoted lifecycle.

Cleanup-cadence exploration is now considered exhausted unless new evidence appears.

## Exact next step — STREAMED-BLOCK-REUSE-AUDIT001

Frozen plan: `research/memory/streamed-block-reuse-audit-001-plan.md`.

Before adding prefetch/buffering or changing source I/O, inspect the exact layer-35 path and separate:
- weight-independent transient module/block construction;
- quantized structure setup;
- current-weight binding;
- parameter materialization;
- forward;
- ownership release;
- source load/selection.

Primary question: can a weightless transformer/quantized module structure be safely reused across tokens while **no layer-35 weight arrays persist**, logical streaming remains 84,427,264 B/token, and model math/materialization/forward stay identical?

This is source/lifetime audit only. No performance treatment yet.

## Behavioral-freedom / Heretic requirement — FROZEN, NOT ACTIVE

Every final promoted LOOM model must eventually pass behavioral editing/decensoring validation with capability/resource preservation. Initial future checkpoint: `STREAMING_RESIDUAL_MEAN_PARITY` before model editing.

## Later

1. STREAMED-BLOCK-REUSE-AUDIT001
2. if safely isolatable, one-factor block/quantized-structure reuse A/B
3. otherwise/selectively move to scheduling/prefetch or buffering based on evidence
4. source-I/O redesign only when source-access dominance is demonstrated
5. OUTCORE-BLOCK001 where justified
6. representation work
7. scale toward 27B/32B full-parameter-count execution
8. capability comparison for promoted behavior-affecting systems
9. Heretic-derived / LOOM-native decensoring validation before final promotion

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
