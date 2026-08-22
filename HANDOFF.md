# LOOM — Active Handoff

Last updated: 2026-08-22
Status: ACTIVE — streaming activation audit
Repository: `Ilcoach/loom`
Local path: `<repository-root>`
Branch: `research/stretch-015-divergence-attribution`
Current checkpoint: `STREAMED_LAYER_GRADIENT_001_COMPLETE`
Next: `STREAMING_ACTIVATION_AUDIT_001`

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

Exact real-M1 parity passed for FULL/H32/H24/H16/H8. Naive synchronous partial residency is memory-effective but far too slow.

Pooled points:
- F0 FULL: 13.433 tok/s; peak MLX 3,621,677,296 B
- F1 H32: 2.527 tok/s; peak 2,756,903,152 B
- F2 H24: 1.168 tok/s
- F3 H16: 0.526 tok/s
- F4 H8: 0.435 tok/s

## STREAMING-ATTRIBUTION 001 — PARTIAL

Exact parity passed, but invasive tracing slowed F1 by ~32.6%, so the internal dominant mechanism remained unresolved. Physical SSD traffic remains unproven.

## SHARED-STAGE-RESIDENCY 001 — COMPLETE

Persisting embedding/final norm/LM head while leaving layers 32..35 streamed produced:
- generation 2.532 -> 3.459 tok/s = +36.66%
- E2E +34.80%
- TTFT -13.34%
- exact parity PASS
- logical stream 882,255,872 -> 337,709,056 B/token
- treatment still saves 337,709,056 B persistent/peak versus FULL.

Conclusion: shared-stage streaming was materially wasteful; shared stages should be treated as hot in the current hierarchy.

## STREAMED-LAYER-GRADIENT 001 — COMPLETE

Report: `research/memory/streamed-layer-gradient-001-result.md`.
Raw local evidence: `results-local/memory/streamed-layer-gradient-001/20260822-165032/`.

All shared stages persistent. Only streamed transformer-layer count varied.

| Arm | Streamed layers | Gen tok/s | Wall/token | Peak MLX B |
|---|---:|---:|---:|---:|
| S0 | 0 | 14.022271 | 71.315 ms | 3,621,677,296 |
| S1 | 1 | 5.819925 | 171.824 ms | 3,537,250,032 |
| S2 | 2 | 4.755397 | 210.287 ms | 3,452,822,768 |
| S4 | 4 | 3.463355 | 288.737 ms | 3,283,968,240 |

All arms 2/2 valid, exact token parity PASS, no resource aborts.

Observed marginal penalties:
- first streamed layer: +100.508 ms/token
- second: +38.464 ms/token
- layers 3–4: +39.225 ms/token/layer

Classification: `STREAM_LAYER_COST_FIXED_OR_NONLINEAR`.

A descriptive two-component fit explains the four pooled points almost exactly:

`wall/token ≈ 71.315 ms + 61.284 ms * I(streaming active) + 39.007 ms * N_streamed_layers`

with `R² ≈ 0.999993`.

This is not yet an internal causal decomposition. It says there is a strong once-per-token activation/fixed term plus a stable marginal per-layer term.

## Exact next step — STREAMING-ACTIVATION-AUDIT 001

Frozen plan: `research/memory/streaming-activation-audit-001-plan.md`.

Perform a low-cost source/control-flow audit comparing S0 and S1. Enumerate operations executed once per generated token only when the streamed-layer set is non-empty, separately from per-streamed-layer operations. Verify invocation counts statically or with low-overhead counters only.

Inspect especially loader/context lifecycle, safetensors/file handle work, parameter rebinding, materialization/sync boundaries, allocator/cache cleanup, explicit release/GC and token-level stream hooks.

Do not optimize yet. The audit must identify an isolatable candidate for the ~61 ms activation term before the next one-factor causal A/B.

## Later

1. STREAMING-ACTIVATION-AUDIT 001
2. one-factor treatment of the strongest isolatable fixed-cost candidate
3. reduce/hide the ~39 ms/layer marginal stream cost
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B full-parameter-count execution
7. capability comparison for promoted behavior-affecting systems

## Local-only warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi focuses on code/tests; ChatGPT owns project-state documentation and GitHub administration.
