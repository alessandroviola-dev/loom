# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — fixed stream-activation cleanup treatment
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STREAMING_ACTIVATION_AUDIT_001_COMPLETE`
Next: `SHARED_CLEANUP_CONSOLIDATION_001`

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

Stable Pi bridge published at `4d204471aedb9262ccaa3b86f29b0e344d0c2884`.

## Memory/residency findings

MEMORY-FRONTIER 001 proved exact real-M1 partial residency but naive synchronous streaming is too slow:
- FULL 13.433 tok/s
- H32 2.527
- H24 1.168
- H16 0.526
- H8 0.435

SHARED-STAGE-RESIDENCY 001 then showed that embedding/final norm/LM head should remain hot: making only those shared stages persistent recovered +36.66% generation throughput with exact parity.

## STREAMED-LAYER-GRADIENT 001 — COMPLETE

With all shared stages persistent:

| Arm | Streamed layers | Gen tok/s | Wall/token |
|---|---:|---:|---:|
| S0 | 0 | 14.022271 | 71.315 ms |
| S1 | 1 | 5.819925 | 171.824 ms |
| S2 | 2 | 4.755397 | 210.287 ms |
| S4 | 4 | 3.463355 | 288.737 ms |

Exact parity PASS everywhere; no resource aborts.

Marginals:
- first streamed layer +100.508 ms/token
- second +38.464 ms
- layers 3–4 +39.225 ms/layer

Interpretation: `STREAM_LAYER_COST_FIXED_OR_NONLINEAR`.

Descriptive model:
`wall/token ≈ 71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms, R²≈0.999993.

The fixed and marginal terms are system-level descriptions, not internal causal attribution.

## STREAMING-ACTIVATION-AUDIT 001 — COMPLETE

Report: `research/memory/streaming-activation-audit-001-result.md`.
Raw local evidence: `results-local/memory/streaming-activation-audit-001/20260822-170803/`.

Source/control-flow audit found strict once-per-token, non-scaling streaming-only operations:
- embedding stage-local `mx.eval`;
- post-embedding `gc.collect()/mx.clear_cache()` cleanup;
- norm stage-local `mx.eval`;
- post-norm cleanup;
- LM-head stage-local `mx.eval`;
- final post-head cleanup;
- stream-region bookkeeping.

Per-streamed-layer lifecycle scales exactly 1/2/4 across S1/S2/S4:
- `mx.load` + selection;
- select-time deletion/GC;
- transient block construction/quantized parameter rebinding;
- parameter materialization;
- streamed forward/eval;
- transient release + GC/cache clear.

Top fixed-cost candidates:
1. three shared-stage cleanup sequences — HIGH;
2. three shared-stage eval boundaries — HIGH;
3. final cleanup alone — MEDIUM.

Historical LOOM context strengthens cleanup cadence as the first treatment: Stretch 025 batching transformer cleanup gave ~3.86x on its frozen path; Stretch 026 shared-stage cleanup consolidation gave +14.11%; Stretch 027 one final cleanup gave +8.67%. These values are contextual only, not transferred causal effects.

## Exact next step — SHARED-CLEANUP-CONSOLIDATION 001

Frozen plan: `research/memory/shared-cleanup-consolidation-001-plan.md`.

Use S1 only: layers 0..34 persistent, layer 35 streamed, all shared stages persistent.

CONTROL: exact current S1 lifecycle.

TREATMENT changes only shared-stage cleanup cadence:
- keep embedding `mx.eval`, omit/defer post-embedding cleanup;
- leave layer-35 streaming and its cleanup unchanged;
- keep norm `mx.eval`, omit/defer post-norm cleanup;
- keep head `mx.eval` and retain exactly one final post-head shared cleanup.

Run low-overhead contemporaneous ABBA with exact token parity and the first three REALGEN prompts. This directly tests the fixed non-scaling cleanup component without changing residency, source format, eval boundaries or per-layer lifecycle.

## Later

1. SHARED-CLEANUP-CONSOLIDATION 001
2. if needed, isolate shared-stage eval-boundary cost
3. reduce/hide the ~39 ms/layer marginal streamed-layer lifecycle
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
