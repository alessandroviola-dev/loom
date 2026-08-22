# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `STREAMING_ACTIVATION_AUDIT_001_COMPLETE`
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

Shared-stage residency then established the first hierarchy rule: embedding/final norm/LM head are hot/persistent. Keeping them resident while streaming four transformer layers improved generation by **+36.66%** with exact parity.

## C — Streamed-layer gradient — COMPLETE

All shared stages persistent; streamed transformer count varied 0/1/2/4.

| Streamed layers | Gen tok/s | Wall/token |
|---:|---:|---:|
| 0 | 14.022271 | 71.315 ms |
| 1 | 5.819925 | 171.824 ms |
| 2 | 4.755397 | 210.287 ms |
| 4 | 3.463355 | 288.737 ms |

The first streamed layer adds ~100.5 ms/token; later layers add ~38–39 ms/layer.

Descriptive system model:
`71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms/token, R²≈0.999993.

This creates two engineering targets: fixed stream activation and repeated per-layer lifecycle.

## D — STREAMING-ACTIVATION-AUDIT 001 — COMPLETE

Report: `research/memory/streaming-activation-audit-001-result.md`.

Source-level audit confirmed once-per-token non-scaling streaming-only work:
- three shared-stage explicit `mx.eval` boundaries;
- post-embedding, post-norm and post-head cleanup sequences;
- stream-region bookkeeping.

Per-layer source/load/reconstruction/materialization/forward/release work scales exactly with streamed-layer count.

The strongest isolatable fixed-cost candidate is shared-stage cleanup cadence. This is reinforced only as plausibility context by prior Stretch cleanup work: transformer cleanup batching gave a large gain, shared-stage cleanup consolidation gave +14.11%, and single-final cleanup gave +8.67% on their own frozen geometries.

## E — SHARED-CLEANUP-CONSOLIDATION 001 — NEXT

Frozen plan: `research/memory/shared-cleanup-consolidation-001-plan.md`.

Use S1 with one streamed transformer layer and all shared stages persistent.

CONTROL retains current post-embedding, post-norm and final post-head shared cleanup.

TREATMENT omits/defers only post-embedding and post-norm cleanup, keeping one final post-head shared cleanup. Layer-35 cleanup and every explicit `mx.eval` remain unchanged.

Balanced ABBA, exact parity, first three REALGEN prompts, low-overhead measurement.

Primary routing:
- >=5% reproducible generation gain with gates preserved -> shared cleanup is materially part of fixed activation cost;
- smaller/no gain -> move next to shared-stage eval-boundary isolation.

## F — Remaining fixed activation work

If cleanup alone does not remove most of the fixed activation penalty, isolate stage-local `mx.eval` boundaries one factor at a time without changing model math or layer residency.

Do not use invasive profiling as causal evidence.

## G — Marginal streamed-layer cost

After fixed activation work, reduce/hide the ~39 ms/token/layer marginal lifecycle. Candidate classes, selected by evidence one factor at a time:
- scheduling / async prefetch;
- buffering / grouped stream lifecycle;
- reconstruction/materialization reuse;
- direct range-I/O / mmap / pread only if source access is shown relevant;
- page-cache-aware source handling.

Physical SSD dominance remains unproven.

## H — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights over multiple exact-valid positions. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## I — Scale beyond 8B

1. reduce/remove fixed stream-activation cost
2. reduce/hide ~39 ms/layer marginal lifecycle
3. establish a substantially better exact 8B RAM/speed point
4. transfer architecture to models beyond comfortable physical RAM
5. first scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
6. optimize toward usable speed and measure capability

## Immediate order

1. SHARED-CLEANUP-CONSOLIDATION 001
2. shared-stage eval-boundary isolation if still justified
3. marginal streamed-layer treatments
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting systems

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
