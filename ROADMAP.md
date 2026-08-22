# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `NORM_EVAL_BOUNDARY_001_COMPLETE`
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

## C — Streamed-layer gradient — COMPLETE

With shared stages persistent:

| Streamed layers | Gen tok/s | Wall/token |
|---:|---:|---:|
| 0 | 14.022271 | 71.315 ms |
| 1 | 5.819925 | 171.824 ms |
| 2 | 4.755397 | 210.287 ms |
| 4 | 3.463355 | 288.737 ms |

Descriptive system model:
`71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms/token, R²≈0.999993.

This separates fixed stream activation from repeated marginal per-layer lifecycle.

## D — Fixed activation — CLOSED

### Shared cleanup consolidation — material PASS

On S1, removing only post-embedding/post-norm shared cleanup:
- 5.643 -> 7.065 tok/s
- +25.206% generation
- -35.678 ms/token
- exact parity PASS
- peak MLX unchanged.

This is the promoted S1 fixed-activation baseline.

### Embed eval boundary — NO-GO

Removing post-embedding `mx.eval(h)`:
- -3.346% generation
- +4.897 ms/token.

Retain it.

### NORM-EVAL-BOUNDARY 001 — COMPLETE / SMALL

Report: `research/memory/norm-eval-boundary-001-result.md`.

Removing only final-norm `mx.eval(h2)`:
- CONTROL 7.003 tok/s, 142.799 ms/token
- TREATMENT 7.056 tok/s, 141.719 ms/token
- generation +0.762%
- wall/token -1.080 ms
- exact parity PASS
- peak MLX unchanged
- no resource aborts.

Decision: effect below 5% material threshold; do not promote. Retain norm eval. Do not test LM-head eval without new evidence.

The fixed activation axis is considered closed. The material win was cleanup cadence; obvious shared eval removal is not a productive direction.

## E — Marginal streamed-layer lifecycle — ACTIVE

Measured marginal cost after activation is ~38–39 ms/token per additional streamed transformer layer.

### STREAMED-LAYER-CLEANUP-DEFER 001 — NEXT

Frozen plan: `research/memory/streamed-layer-cleanup-defer-001-plan.md`.

Use promoted cleanup-consolidated S1:
- layers 0..34 persistent;
- layer 35 streamed;
- shared stages persistent;
- all explicit shared evals retained;
- only final shared cleanup retained.

CONTROL keeps layer-35 local cleanup.

TREATMENT changes only layer-35 cleanup cadence: keep load/select/reconstruction/materialization/forward/eval and deletion/release identical, but omit/defer the layer-local `gc.collect()/mx.clear_cache()` sequence until the already-existing final post-head cleanup.

Balanced ABBA, exact token parity, low-overhead measurement.

If material, remeasure the S0/S1/S2/S4 slope under the improved cleanup schedule before moving to a different mechanism.

## F — Later marginal treatments

Only after the cleanup result, select one factor at a time from evidence:
- scheduling / asynchronous prefetch;
- buffering / grouped stream lifecycle;
- reconstruction/materialization reuse;
- direct source-range I/O / mmap / pread only if source-access evidence supports it;
- page-cache-aware source handling.

Physical SSD dominance remains unproven.

## G — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights across multiple exact-valid positions. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## H — Scale beyond 8B

1. materially reduce marginal streamed-layer lifecycle
2. establish a substantially better exact 8B RAM/speed point
3. transfer architecture beyond comfortable physical RAM
4. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
5. optimize toward usable speed and measure capability

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

1. STREAMED-LAYER-CLEANUP-DEFER 001
2. remeasure marginal slope if cleanup treatment is material
3. next evidence-selected marginal stream treatment
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates
8. Heretic-derived / LOOM-native decensoring stage before final model promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
