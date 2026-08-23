# LOOM Roadmap

Last updated: 2026-08-23
Current checkpoint: `SELECT_TIME_GC_DEFER_001_COMPLETE`
Detailed history through REALGEN002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on four axes:
1. memory / residency;
2. speed / usability;
3. practical capability;
4. behavioral freedom / decensoring.

Final promoted LOOM models require a validated decensored behavioral profile using Heretic or a LOOM-native independent equivalent. Frozen requirement: `research/behavior/decensoring-requirement-v1.md`.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## A — Capability baseline — COMPLETE

CAPABILITY001:
- practical-agent 1/11 = 9.09%
- Coding Benchmark 45/100
- critical failures 0.

## B — Memory frontier — COMPLETE

Exact partial residency works. Shared-stage residency established embedding/final norm/LM head as hot/persistent.

## C — Fixed stream activation — CLOSED

Old Gradient001 descriptive model:
`71.315 + 61.284*I(streaming) + 39.007*N` ms/token.

Shared intermediate cleanup consolidation: +25.206% generation / -35.678 ms/token, promoted.

Embedding eval removal: NO-GO.
Norm eval removal: SMALL / not promoted.

## D — Marginal streamed-layer lifecycle — ACTIVE

### Post-forward layer cleanup defer — MATERIAL PASS

Exact S1 one-factor A/B:
- 6.997 -> 8.223 tok/s
- +17.522%
- -21.308 ms/token
- exact parity PASS
- no resource aborts.

Promoted.

### STREAMED-LAYER-GRADIENT002 — COMPLETE

Under promoted deferred post-forward cleanup:

| Streamed layers | Tok/s | Wall/token | Min free |
|---:|---:|---:|---:|
| 0 | 11.101 | 90.078 ms | 23% |
| 1 | 8.037 | 124.425 ms | 20% |
| 2 | 6.546 | 152.775 ms | 15% |
| 4 | 5.015 | 199.383 ms | 23% |

Exact parity PASS, no aborts, resource-safe through S4.

Marginals decline 34.347 -> 28.350 -> 23.304 ms/layer.

Descriptive two-component fit:
`90.078 + 11.043*I(streaming_active) + 24.746*N` ms/token, R² 0.998866.

### SELECT-TIME-GC-DEFER001 — COMPLETE / NO-GO

Report: `research/memory/select-time-gc-defer-001-result.md`.

Removing only the remaining select-time `gc.collect()` on promoted S1 while preserving deletion/ownership and all other behavior produced:
- CONTROL 8.293 tok/s, 120.577 ms/token
- TREATMENT 7.767 tok/s, 128.754 ms/token
- generation **-6.351%**
- E2E **-5.752%**
- TTFT **+15.374%**
- free floor 19% -> 11%
- exact parity PASS
- peak active/active+cache unchanged
- no aborts.

Decision: retain select-time GC. Cleanup cadence is exhausted as an optimization axis on the current implementation.

## E — STREAMED-BLOCK-REUSE-AUDIT001 — NEXT

Frozen plan: `research/memory/streamed-block-reuse-audit-001-plan.md`.

Source/lifetime audit of the current streamed layer path. Separate:
- source load/selection;
- weight-independent module/block construction;
- quantized-structure setup;
- current-weight binding;
- parameter materialization;
- forward;
- ownership release.

Question: can only the **weight-independent block/quantized structure** be retained across tokens while current streamed weights are still reloaded, rebound, materialized and fully detached every token?

Requirements for any future treatment:
- no streamed layer weight survives across tokens;
- persistent raw-weight accounting unchanged;
- 84,427,264 B/token logical streaming unchanged on S1;
- same source/load and forward math;
- exact parity preserved.

Audit first; do not benchmark the treatment until ownership/lifetime safety is proven.

## F — Next marginal mechanisms

Routing after the audit:
- if structure reuse is cleanly isolatable -> one-factor reuse A/B;
- if not -> move to scheduling/asynchronous prefetch or buffering/grouping;
- reconstruction/materialization reuse only with exact residency proof;
- source-range I/O/mmap/pread only if source-access evidence becomes strong;
- physical SSD dominance remains unproven.

## G — OUTCORE-BLOCK / representation

OUTCORE-BLOCK001 remains a later candidate for amortizing streamed weights over multiple exact-valid positions. Representation work may include mixed/selective precision, compressed cold weights and KV changes while preserving full parameter count.

## H — Scale beyond 8B

1. reduce remaining per-layer streamed lifecycle cost
2. establish a stronger exact 8B RAM/speed point
3. transfer architecture beyond comfortable physical RAM
4. first major scale checkpoint: ~27B/32B full-parameter model produces correct tokens on M1 8 GB without OOM
5. optimize toward usable speed and measure capability.

## I — Behavioral freedom / decensoring — REQUIRED BEFORE FINAL PROMOTION

Reference:
- audited Heretic snapshot `p-e-w/heretic@bedb94ef117a271532ac2058447fbc165d5051bd`
- `research/behavior/decensoring-requirement-v1.md`.

Initial future sequence begins with `STREAMING_RESIDUAL_MEAN_PARITY`, then direction stability, reversible low-rank transform validation and behavior/capability/resource preservation.

## Immediate order

1. STREAMED-BLOCK-REUSE-AUDIT001
2. block/quantized-structure reuse A/B if safe and isolatable
3. otherwise next evidence-selected scheduling/prefetch/buffering mechanism
4. OUTCORE-BLOCK001 where justified
5. representation work
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates
8. Heretic-derived / LOOM-native decensoring before final model promotion

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
