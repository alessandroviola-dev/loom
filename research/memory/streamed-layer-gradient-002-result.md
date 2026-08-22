# LOOM — STREAMED-LAYER-GRADIENT 002 — RESULT

Date: 2026-08-22
Classification: `STREAMED_LAYER_GRADIENT_002_COMPLETE`
Interpretation: `DEFERRED_STREAM_LAYER_COST_FIXED_OR_NONLINEAR`
Raw evidence: `results-local/memory/streamed-layer-gradient-002/20260822-181943/`

## Frozen lifecycle

All shared stages persistent. Explicit embedding/norm/head eval boundaries retained. Post-embedding/post-norm shared cleanup absent. Per-streamed-layer select-time cleanup retained. Per-streamed-layer post-forward `gc.collect()/mx.clear_cache()` omitted/deferred. Transient module/value deletion remained. Exactly one final post-head cleanup/token.

Arms:
- S0: 0 streamed layers; persistent raw 3,583,928,320 B; 0 streamed B/token
- S1: layer 35 streamed; persistent raw 3,499,501,056 B; 84,427,264 streamed B/token
- S2: layers 34..35 streamed; persistent raw 3,415,073,792 B; 168,854,528 streamed B/token
- S4: layers 32..35 streamed; persistent raw 3,246,219,264 B; 337,709,056 streamed B/token

Exact token parity passed for all streamed arms and all eight scientific constituents. No resource aborts.

## Pooled results

| Arm | Tok/s | Wall/token | E2E tok/s | Peak active B | Peak active+cache B | Min free | Peak swap MB |
|---|---:|---:|---:|---:|---:|---:|---:|
| S0 | 11.101 | 90.078 ms | 9.454 | 3,806,718,372 | 3,621,988,600 | 23% | 1918.81 |
| S1 | 8.037 | 124.425 ms | 6.927 | 3,633,031,420 | 3,537,569,528 | 20% | 1782.31 |
| S2 | 6.546 | 152.775 ms | 5.791 | 3,548,604,156 | 3,453,142,264 | 15% | 1810.12 |
| S4 | 5.015 | 199.383 ms | 4.541 | 3,379,749,628 | 3,284,287,736 | 23% | 1722.69 |

## New marginal penalties

- S1 vs S0: +34.347 ms/token for 1 added streamed layer
- S2 vs S1: +28.350 ms/token for 1 added streamed layer
- S4 vs S2: +46.608 ms/token for 2 added streamed layers = +23.304 ms/layer

Mean marginal: 28.667 ms/layer.
Range: 23.304–34.347 ms/layer.
CV: 19.284%.

Descriptive linear fit:

`wall/token = 94.496 ms + 26.954 ms * N_streamed_layers`

R² = 0.991260.

A two-component descriptive fit is stronger:

`wall/token ≈ 90.078 ms + 11.043 ms * I(streaming_active) + 24.746 ms * N_streamed_layers`

R² = 0.998866.

The fixed/nonlinear classification is retained because the first streamed layer remains more expensive and the measured marginal penalty declines as more layers are streamed.

## Resource scaling

Deferred post-forward cleanup remained scientifically usable through four streamed layers:
- S1 SAFE
- S2 SAFE
- S4 SAFE

There was no resource abort and no evidence of runaway allocator-cache growth under the frozen gates. S2 reached the lowest observed free-memory floor at 15%, still well above the 5% abort threshold. Cross-arm free/swap differences remain host-state/resource telemetry rather than intrinsic memory causality by themselves.

## Context versus Gradient 001

Historical old-lifecycle points:
- S0 71.315 ms/token, 14.022 tok/s
- S1 171.824 ms/token, 5.820 tok/s
- S2 210.287 ms/token, 4.755 tok/s
- S4 288.737 ms/token, 3.463 tok/s

New-lifecycle points:
- S0 90.078 ms/token, 11.101 tok/s
- S1 124.425 ms/token, 8.037 tok/s
- S2 152.775 ms/token, 6.546 tok/s
- S4 199.383 ms/token, 5.015 tok/s

These are contextual cross-experiment comparisons only. The causal evidence for cleanup defer remains the dedicated S1 ABBA from `STREAMED-LAYER-CLEANUP-DEFER 001` (+17.522%).

The historical later-layer marginal was ~39 ms/layer; the new descriptive linear slope is 26.954 ms/layer and the two-component marginal term is 24.746 ms/layer.

## Decision

Promote deferred post-forward streamed-layer cleanup as the current lifecycle for continued marginal-cost research.

Do not claim physical SSD dominance. Physical SSD traffic remains unproven.

The remaining clearly scalable cleanup operation is the select-time `gc.collect()` executed once per streamed layer after weight selection/all-weight container release. It is the next clean one-factor candidate before introducing prefetch, buffering or source-I/O redesign.
