# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `STREAMED_LAYER_CLEANUP_DEFER_001_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on four axes:

1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

A final promoted LOOM-produced model must include a validated decensored behavioral profile using Heretic or a LOOM-native independently implemented equivalent. This is a later promotion requirement and does not change the current memory/runtime order.

Frozen project requirement: `research/behavior/decensoring-requirement-v1.md`.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## A — Capability baseline — COMPLETE

Canonical behavior reference:
- CAPABILITY 001 practical-agent: 1/11 = 9.09%
- Coding Benchmark: 45/100
- critical failures: 0

## B — Memory frontier — COMPLETE

Exact partial residency works, but naive synchronous streaming is too slow:
- FULL 13.433 tok/s
- H32 2.527
- H24 1.168
- H16 0.526
- H8 0.435

Shared-stage residency established that embedding/final norm/LM head should remain hot/persistent.

## C — Streamed-layer gradient 001 — COMPLETE

With shared stages persistent and the older streamed-layer cleanup lifecycle:

| Streamed layers | Gen tok/s | Wall/token |
|---:|---:|---:|
| 0 | 14.022271 | 71.315 ms |
| 1 | 5.819925 | 171.824 ms |
| 2 | 4.755397 | 210.287 ms |
| 4 | 3.463355 | 288.737 ms |

Descriptive model:
`71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms/token, R²≈0.999993.

This separated fixed stream activation from repeated marginal per-layer lifecycle.

## D — Fixed activation — CLOSED

### Shared cleanup consolidation — material PASS

Removing only post-embedding/post-norm shared cleanup on S1:
- 5.643 -> 7.065 tok/s
- +25.206% generation
- -35.678 ms/token
- exact parity PASS
- peak MLX unchanged.

### Embed eval — NO-GO

Removing post-embedding `mx.eval(h)` regressed generation by 3.346%. Retain it.

### Norm eval — SMALL / NOT PROMOTED

Removing final-norm `mx.eval(h2)` improved generation only 0.762%. Retain it. Do not test LM-head eval without new evidence.

The fixed-activation axis is closed.

## E — Marginal streamed-layer lifecycle — ACTIVE

### STREAMED-LAYER-CLEANUP-DEFER 001 — COMPLETE / MATERIAL PASS

Report: `research/memory/streamed-layer-cleanup-defer-001-result.md`.

Exact S1 ABBA. TREATMENT changed only the streamed layer's post-forward cleanup cadence: all load/select/reconstruction/materialization/forward/eval and deletion/release semantics remained identical, select-time cleanup remained identical, and one layer-local post-forward `gc.collect()/mx.clear_cache()` per generated token was omitted/deferred to the existing final cleanup.

Pooled:
- CONTROL 6.997 tok/s, 142.918 ms/token
- TREATMENT 8.223 tok/s, 121.610 ms/token

Causal effect:
- generation **+17.522%**
- E2E **+15.750%**
- wall/token **-21.308 ms**
- peak active delta 0 B
- observed peak active+cache delta 0 B
- exact parity PASS
- no resource aborts.

This removes ~54.64% of the historical ~39 ms/layer reference on S1, contextual only. Deferred post-forward streamed-layer cleanup is promoted for further testing.

### STREAMED-LAYER-GRADIENT 002 — NEXT

Frozen plan: `research/memory/streamed-layer-gradient-002-plan.md`.

Remeasure S0/S1/S2/S4 under the promoted lifecycle:
- all shared stages persistent;
- shared intermediate cleanup consolidated;
- embedding/norm/head evals retained;
- per-streamed-layer select-time cleanup unchanged;
- transient deletion/release unchanged;
- per-streamed-layer post-forward GC/cache cleanup omitted/deferred;
- exactly one final cleanup/token.

Balanced fresh order:
`S0 -> S4 -> S2 -> S1 -> S1 -> S2 -> S4 -> S0`.

Primary questions:
1. what is the new real-M1 marginal ms/layer slope?
2. does deferring 2 or 4 layer-local cleanups remain memory-safe?
3. is the new gradient additive, nonlinear, resource-limited or unresolved?

Do not select a different per-layer mechanism until this updated gradient is measured.

## F — Later marginal treatments

Select from evidence after Gradient 002, one factor at a time:
- select-time cleanup cadence;
- scheduling / asynchronous prefetch;
- buffering / grouped lifecycle;
- reconstruction/materialization reuse;
- direct source-range I/O / mmap / pread only if source-access evidence supports it;
- page-cache-aware source handling.

Physical SSD dominance remains unproven.

## G — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights across multiple exact-valid positions. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## H — Scale beyond 8B

1. establish the improved marginal streamed-layer slope/resource envelope
2. materially reduce/hide remaining per-layer lifecycle
3. establish a substantially better exact 8B RAM/speed point
4. transfer architecture beyond comfortable physical RAM
5. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
6. optimize toward usable speed and measure capability

## I — Behavioral freedom / decensoring — REQUIRED BEFORE FINAL PROMOTION

Reference:
- audited Heretic snapshot `p-e-w/heretic@bedb94ef117a271532ac2058447fbc165d5051bd`
- `research/behavior/decensoring-requirement-v1.md`

LOOM treats Heretic's transferable primitive as contrastive residual-direction model editing with reversible low-rank intervention and multi-objective preservation evaluation.

Initial future sequence:
1. `STREAMING_RESIDUAL_MEAN_PARITY`
2. direction reproducibility/stability
3. architecture mapping and global/per-layer direction tests where justified
4. reversible low-rank transform validation
5. behavior change vs sequence/task/capability preservation
6. resource cost on constrained hardware
7. freeze a decensored profile only after preservation/resource gates pass.

## Immediate order

1. STREAMED-LAYER-GRADIENT 002
2. next evidence-selected marginal stream treatment
3. OUTCORE-BLOCK 001 where justified
4. representation work where justified
5. scale toward 27B/32B
6. capability comparison for promoted behavior-affecting candidates
7. Heretic-derived / LOOM-native decensoring stage before final model promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
