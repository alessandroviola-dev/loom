# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `STREAMED_LAYER_GRADIENT_001_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## A — Capability baseline — COMPLETE

Canonical behavior reference:
- CAPABILITY 001 practical-agent: **1/11 = 9.09%**
- Coding Benchmark: **45/100**
- critical failures: 0

## B — MEMORY-FRONTIER 001 — COMPLETE

Exact real-M1 parity passed across FULL/H32/H24/H16/H8. Naive synchronous streaming saves large amounts of memory but destroys throughput.

Key endpoints:
- FULL: 13.433 tok/s, peak MLX 3,621,677,296 B
- H32: 2.527 tok/s, peak 2,756,903,152 B
- H8: 0.435 tok/s, peak 730,648,816 B

## C — STREAMING-ATTRIBUTION 001 — PARTIAL

Invasive tracing preserved correctness but imposed ~32.6% slowdown, so no internal dominant mechanism was promoted. Physical SSD traffic remains unproven.

## D — SHARED-STAGE-RESIDENCY 001 — COMPLETE

Keeping embedding/final norm/LM head resident while leaving four transformer layers streamed recovered **+36.66% generation throughput** and preserved exact token parity.

This establishes the first hierarchy rule: large shared stages are hot/persistent in the current architecture rather than repeatedly streamed.

## E — STREAMED-LAYER-GRADIENT 001 — COMPLETE

Report: `research/memory/streamed-layer-gradient-001-result.md`.

With all shared stages persistent:

| Streamed layers | Gen tok/s | Wall/token |
|---:|---:|---:|
| 0 | 14.022271 | 71.315 ms |
| 1 | 5.819925 | 171.824 ms |
| 2 | 4.755397 | 210.287 ms |
| 4 | 3.463355 | 288.737 ms |

Exact parity passed everywhere; no resource aborts.

Observed marginal penalties:
- first layer: +100.508 ms/token
- second: +38.464 ms/token
- later measured layers: +39.225 ms/token/layer

Interpretation: `STREAM_LAYER_COST_FIXED_OR_NONLINEAR`.

A descriptive two-component model fits the points nearly exactly:

`wall/token ≈ 71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms

with `R² ≈ 0.999993`.

This suggests two separate engineering targets: a once-per-token streaming activation cost and a repeated marginal per-layer cost.

## F — STREAMING-ACTIVATION-AUDIT 001 — NEXT

Frozen plan: `research/memory/streaming-activation-audit-001-plan.md`.

Before changing runtime behavior, inspect the exact S0 vs S1 control-flow difference and enumerate operations that execute once per token whenever any streamed transformer layer exists.

Rank isolatable candidates such as stream-region setup/teardown, source-handle lifecycle, parameter rebinding, materialization/synchronization boundaries, allocator/cache cleanup and explicit release/GC. Verify invocation topology statically or with low-overhead counters only.

The next performance experiment must target one confirmed once-per-token candidate, not guess at SSD/prefetch.

## G — Marginal transformer stream cost

After fixed activation work, address the measured ~39 ms/token/layer marginal cost using one-factor evidence-selected treatments. Candidate classes include:
- scheduling / asynchronous prefetch
- buffering or stream-region grouping
- reconstruction/materialization reuse
- direct range-I/O / mmap / pread where source access is proven relevant
- page-cache-aware source handling

Do not assume physical SSD dominance without evidence.

## H — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights over multiple exact-valid positions. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## I — Scale beyond 8B

1. identify and remove/reduce the fixed stream-activation penalty
2. reduce/hide the ~39 ms/layer marginal stream lifecycle
3. establish a substantially better exact 8B RAM/speed point
4. transfer the architecture to models beyond comfortable physical RAM
5. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
6. optimize toward usable speed and measure capability

## Immediate order

1. STREAMING-ACTIVATION-AUDIT 001
2. one-factor fixed-cost treatment
3. marginal per-layer stream treatment(s)
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
