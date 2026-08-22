# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `SHARED_CLEANUP_CONSOLIDATION_001_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## A — Capability baseline — COMPLETE

Canonical behavior reference:
- CAPABILITY 001 practical-agent: **1/11 = 9.09%**
- Coding Benchmark: **45/100**
- critical failures: 0

## B — Memory frontier — COMPLETE

Exact real-M1 partial residency works, but naive synchronous streaming is too slow:
- FULL 13.433 tok/s
- H32 2.527
- H24 1.168
- H16 0.526
- H8 0.435

Shared-stage residency established the first hierarchy rule: embedding/final norm/LM head are hot/persistent. Keeping them resident while streaming four transformer layers improved generation by **+36.66%** with exact parity.

## C — Streamed-layer gradient — COMPLETE

All shared stages persistent; streamed transformer count varied 0/1/2/4.

| Streamed layers | Gen tok/s | Wall/token |
|---:|---:|---:|
| 0 | 14.022271 | 71.315 ms |
| 1 | 5.819925 | 171.824 ms |
| 2 | 4.755397 | 210.287 ms |
| 4 | 3.463355 | 288.737 ms |

First streamed layer adds ~100.5 ms/token; later layers add ~38–39 ms/layer.

Descriptive model:
`71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms/token, R²≈0.999993.

This creates two engineering targets: fixed stream activation and repeated per-layer lifecycle.

## D — Streaming activation audit — COMPLETE

Source-level audit confirmed once-per-token non-scaling streaming-only work:
- explicit embedding/norm/head `mx.eval` boundaries;
- post-embedding, post-norm and post-head cleanup sequences;
- stream-region bookkeeping.

Per-layer source/load/reconstruction/materialization/forward/release work scales with streamed-layer count.

## E — SHARED-CLEANUP-CONSOLIDATION 001 — COMPLETE

Report: `research/memory/shared-cleanup-consolidation-001-result.md`.

Exact S1 ABBA. TREATMENT removed only post-embedding and post-norm shared cleanup, keeping layer-35 cleanup, final post-head cleanup and every explicit `mx.eval` unchanged.

Pooled:
- CONTROL 5.643 tok/s, 177.226 ms/token
- TREATMENT 7.065 tok/s, 141.548 ms/token

Causal effect:
- generation **+25.206%**
- E2E **+22.960%**
- wall/token **-35.678 ms**
- peak MLX delta 0 B
- exact parity PASS
- no resource aborts.

Thus cleanup cadence causally explains a material part of fixed stream activation. The removed wall is ~58.22% of the previous descriptive 61.284 ms fixed term, but this ratio is contextual rather than an internal timing attribution.

The cleanup-consolidated S1 becomes the current experimental fixed-activation baseline: 7.065 tok/s with one transformer layer still streamed and 84,427,264 B/token logical streaming.

## F — EMBED-EVAL-BOUNDARY 001 — NEXT

Frozen plan: `research/memory/embed-eval-boundary-001-plan.md`.

CONTROL: exact cleanup-consolidated S1, including explicit `mx.eval(h)` immediately after embedding.

TREATMENT: remove/defer only that single embedding eval boundary. The first transformer block retains its existing output eval. All residency, cleanup, layer-35 stream lifecycle, source representation, I/O and remaining eval topology remain unchanged.

Balanced ABBA with exact parity and low-overhead measurement.

Routing:
- >=5% reproducible gain with gates preserved -> embedding eval is materially part of remaining fixed activation;
- smaller/no gain -> leave it closed and isolate the next shared-stage eval boundary.

## G — Remaining fixed activation work

Only continue one-boundary eval experiments while measured gains justify them. Avoid invasive profiling. Once the fixed activation term is materially reduced or remaining candidates are individually small, close this axis.

## H — Marginal streamed-layer cost

Then attack the measured ~39 ms/token/layer marginal lifecycle. Candidate one-factor classes:
- scheduling / asynchronous prefetch;
- buffering / grouped stream lifecycle;
- reconstruction/materialization reuse;
- direct range-I/O / mmap / pread only if source access is demonstrated relevant;
- page-cache-aware source handling.

Physical SSD dominance remains unproven.

## I — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights over multiple exact-valid positions. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## J — Scale beyond 8B

1. reduce/close fixed stream-activation overhead
2. reduce/hide ~39 ms/layer marginal lifecycle
3. establish a substantially better exact 8B RAM/speed point
4. transfer architecture to models beyond comfortable physical RAM
5. first scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
6. optimize toward usable speed and measure capability

## Immediate order

1. EMBED-EVAL-BOUNDARY 001
2. remaining shared eval-boundary isolation only if justified
3. marginal streamed-layer treatments
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting systems

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
