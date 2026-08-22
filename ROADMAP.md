# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `STREAMED_LAYER_GRADIENT_002_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on four axes:
1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

Final promoted LOOM models require a validated decensored behavioral profile using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## A — Capability baseline — COMPLETE

Canonical CAPABILITY001:
- practical-agent 1/11 = 9.09%
- Coding Benchmark 45/100
- critical failures 0.

## B — Memory frontier — COMPLETE

Exact partial residency works, but naive synchronous streaming is too slow. Shared-stage residency established embedding/final norm/LM head as hot/persistent.

## C — Fixed stream activation — CLOSED

Old Streamed-Layer Gradient001:
- S0 71.315 ms/token
- S1 171.824
- S2 210.287
- S4 288.737
- descriptive `71.315 + 61.284*I(streaming) + 39.007*N` ms/token.

Shared cleanup consolidation: +25.206% generation / -35.678 ms/token, exact parity, no peak-MLX increase. Promoted.

Embed eval removal: NO-GO (-3.346%).
Norm eval removal: SMALL (+0.762%), not promoted.

Fixed-activation cleanup work is closed unless new evidence emerges.

## D — Marginal streamed-layer lifecycle — ACTIVE

### STREAMED-LAYER-CLEANUP-DEFER001 — MATERIAL PASS

Deferring only per-layer post-forward `gc.collect()/mx.clear_cache()` on S1 while retaining select-time cleanup and all model/lifecycle semantics produced:
- 6.997 -> 8.223 tok/s
- +17.522%
- -21.308 ms/token
- exact parity PASS
- peak active/active+cache unchanged in the A/B
- no resource aborts.

Promoted.

### STREAMED-LAYER-GRADIENT002 — COMPLETE

Report: `research/memory/streamed-layer-gradient-002-result.md`.

Under promoted deferred post-forward cleanup:

| Streamed layers | Tok/s | Wall/token | Min free |
|---:|---:|---:|---:|
| 0 | 11.101 | 90.078 ms | 23% |
| 1 | 8.037 | 124.425 ms | 20% |
| 2 | 6.546 | 152.775 ms | 15% |
| 4 | 5.015 | 199.383 ms | 23% |

All arms 2/2 valid, exact parity PASS, no resource aborts. Deferred cleanup remains resource-safe through four streamed layers.

New marginal penalties:
- first layer +34.347 ms
- second +28.350 ms
- layers 3–4 +23.304 ms/layer.

Mean 28.667 ms/layer. Linear descriptive slope 26.954 ms/layer.

Two-component descriptive fit:
`90.078 + 11.043*I(streaming_active) + 24.746*N_streamed_layers` ms/token, R² 0.998866.

Interpretation: `DEFERRED_STREAM_LAYER_COST_FIXED_OR_NONLINEAR`.

The next remaining clearly scalable cleanup operation is select-time `gc.collect()` once per streamed layer.

### SELECT-TIME-GC-DEFER001 — NEXT

Frozen plan: `research/memory/select-time-gc-defer-001-plan.md`.

Exact promoted S1 A/B.

CONTROL retains select-time `gc.collect()` after loading/selecting weights and releasing the full loaded weight container.

TREATMENT keeps identical deletion/release but omits/defer only that select-time `gc.collect()`.

All post-forward cleanup policy, final cleanup, load/select/reconstruction/materialization/forward/evals, residency, source representation and logical I/O remain identical.

Balanced ABBA, exact parity, low-overhead resource/speed measurement.

If material, remeasure the S0/S1/S2/S4 gradient before selecting another mechanism.

## E — Later marginal mechanisms

After cleanup cadence is exhausted, choose one factor at a time from evidence:
- scheduling / asynchronous prefetch;
- buffering / grouped lifecycle;
- reconstruction/materialization reuse;
- direct source-range I/O / mmap / pread only if source-access evidence supports it;
- page-cache-aware source handling.

Physical SSD dominance remains unproven.

## F — OUTCORE-BLOCK / representation

OUTCORE-BLOCK001 remains a later candidate for amortizing streamed weights over multiple exact-valid positions. Representation work may include mixed/selective precision, compressed cold weights and KV changes while retaining full parameter count.

## G — Scale beyond 8B

1. continue reducing the marginal streamed-layer lifecycle
2. establish a better exact 8B RAM/speed point
3. transfer architecture beyond comfortable physical RAM
4. first major scale checkpoint: ~27B/32B full-parameter model produces correct tokens on M1 8 GB without OOM
5. optimize toward usable speed and measure capability.

## H — Behavioral freedom / decensoring — REQUIRED BEFORE FINAL PROMOTION

Reference:
- audited Heretic snapshot `p-e-w/heretic@bedb94ef117a271532ac2058447fbc165d5051bd`
- `research/behavior/decensoring-requirement-v1.md`.

Initial future sequence begins with `STREAMING_RESIDUAL_MEAN_PARITY`, then direction stability, reversible low-rank transform validation and behavior/capability/resource preservation.

## Immediate order

1. SELECT-TIME-GC-DEFER001
2. remeasure marginal gradient if material
3. next evidence-selected marginal mechanism
4. OUTCORE-BLOCK001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates
8. Heretic-derived / LOOM-native decensoring before final model promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
