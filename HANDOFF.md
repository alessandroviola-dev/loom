# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — fixed stream-activation eval-boundary isolation
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `SHARED_CLEANUP_CONSOLIDATION_001_COMPLETE`
Next: `EMBED_EVAL_BOUNDARY_001`

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

## Memory/residency sequence

MEMORY-FRONTIER 001 proved exact real-M1 partial residency but naive synchronous streaming is too slow: FULL 13.433 tok/s; H32 2.527; H24 1.168; H16 0.526; H8 0.435.

SHARED-STAGE-RESIDENCY 001 established the first hierarchy rule: embedding/final norm/LM head should remain hot. Making only those shared stages persistent recovered +36.66% generation throughput with exact parity.

## STREAMED-LAYER-GRADIENT 001 — COMPLETE

All shared stages persistent; streamed transformer count 0/1/2/4:

| Arm | Streamed layers | Gen tok/s | Wall/token |
|---|---:|---:|---:|
| S0 | 0 | 14.022271 | 71.315 ms |
| S1 | 1 | 5.819925 | 171.824 ms |
| S2 | 2 | 4.755397 | 210.287 ms |
| S4 | 4 | 3.463355 | 288.737 ms |

Exact parity PASS everywhere; no resource aborts.

Descriptive model:
`wall/token ≈ 71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms, R²≈0.999993.

This is system-level description, not internal causal attribution.

## STREAMING-ACTIVATION-AUDIT 001 — COMPLETE

Source audit found stream-only once-per-token non-scaling work:
- explicit embedding/norm/head `mx.eval` boundaries;
- post-embedding/post-norm/post-head shared cleanup;
- stream-region bookkeeping.

Per-layer load/select/reconstruction/materialization/forward/release scales exactly with streamed-layer count.

Top fixed-cost candidates were shared-stage cleanup and shared-stage eval boundaries.

## SHARED-CLEANUP-CONSOLIDATION 001 — COMPLETE

Report: `research/memory/shared-cleanup-consolidation-001-result.md`.
Raw local evidence: `results-local/memory/shared-cleanup-consolidation-001/20260822-172422/`.

Exact S1 residency in both arms:
- layers 0..34 persistent;
- layer 35 streamed;
- shared stages persistent;
- persistent raw weights 3,499,501,056 B;
- 84,427,264 logical streamed B/token.

CONTROL retained post-embedding, layer-35, post-norm and post-head cleanup.

TREATMENT removed only the two intermediate shared-stage cleanup sequences; layer-35 cleanup, final post-head cleanup and all explicit `mx.eval` calls remained unchanged.

Pooled:
- CONTROL 5.643 tok/s; 177.226 ms/token; E2E 5.047; TTFT 1.336 s
- TREATMENT 7.065 tok/s; 141.548 ms/token; E2E 6.206; TTFT 1.228 s

Causal effect:
- generation **+25.206%**
- E2E **+22.960%**
- wall/token **-35.678 ms (-20.131%)**
- TTFT -8.080%
- peak MLX delta 0 B
- exact parity PASS everywhere
- no resource aborts.

The removed 35.678 ms/token is ~58.22% of the prior descriptive ~61.284 ms fixed term, contextual only.

Conclusion: shared-stage cleanup cadence is causally a material part of fixed stream activation. No internal subsystem timing claim is made; physical SSD traffic remains unproven.

## Exact next step — EMBED-EVAL-BOUNDARY 001

Frozen plan: `research/memory/embed-eval-boundary-001-plan.md`.

Use the successful cleanup-consolidated S1 as both-arm baseline.

CONTROL retains the explicit `mx.eval(h)` immediately after persistent embedding.

TREATMENT removes/defers only this one eval boundary. The first transformer block keeps its existing output eval, all other evals/cleanup/layer-35 streaming/residency/I-O/model math remain identical.

Run low-overhead ABBA, exact parity, first three REALGEN prompts. This tests whether the embedding eval boundary is part of the remaining fixed activation cost without changing per-layer streaming.

## Later

1. EMBED-EVAL-BOUNDARY 001
2. isolate remaining shared eval boundaries only if justified
3. reduce/hide the ~39 ms/layer marginal streamed-layer lifecycle
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
