# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `EMBED_EVAL_BOUNDARY_001_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

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

Descriptive model:
`71.315 + 61.284*I(streaming active) + 39.007*N_streamed_layers` ms/token, R²≈0.999993.

This separates two engineering targets: fixed stream activation and repeated marginal per-layer lifecycle.

## D — Fixed activation source audit — COMPLETE

Streaming-only once-per-token non-scaling work includes:
- embedding/norm/head eval boundaries;
- shared-stage cleanup points;
- stream-region bookkeeping.

Per-layer load/select/reconstruction/materialization/forward/release scales with streamed-layer count.

## E — Shared cleanup consolidation — COMPLETE / PROMISING

On exact S1, removing only post-embedding and post-norm shared cleanup produced:
- 5.643 -> 7.065 gen tok/s
- +25.206% generation
- -35.678 ms/token
- exact parity PASS
- peak MLX unchanged
- no resource aborts.

This is the current experimental S1 baseline. Cleanup cadence causally explains a material part of the fixed activation penalty.

## F — EMBED-EVAL-BOUNDARY 001 — COMPLETE / NO-GO

Report: `research/memory/embed-eval-boundary-001-result.md`.

CONTROL retained explicit post-embedding `mx.eval(h)`; TREATMENT removed/deferred only that boundary.

Pooled:
- CONTROL 7.069 tok/s, 141.462 ms/token
- TREATMENT 6.833 tok/s, 146.359 ms/token

Effect:
- generation **-3.346%**
- E2E **-3.178%**
- wall/token **+4.897 ms**
- TTFT **+5.475%**
- peak MLX unchanged
- exact parity PASS
- no resource aborts.

Decision: retain the post-embedding eval. It is not a useful fixed-cost removal target on the current path.

## G — NORM-EVAL-BOUNDARY 001 — NEXT

Frozen plan: `research/memory/norm-eval-boundary-001-plan.md`.

CONTROL: cleanup-consolidated S1 with explicit final-norm `mx.eval(h2)`.

TREATMENT: remove/defer only the final-norm eval. Keep the downstream LM-head `mx.eval(logits)`, post-embedding eval, cleanup cadence, layer-35 lifecycle, residency and I/O unchanged.

Balanced ABBA, exact token parity, first three canonical REALGEN prompts, low-overhead measurement.

Routing:
- >=5% gain with gates preserved -> final-norm eval is materially part of residual fixed activation;
- small/no gain -> close or nearly close the shared eval-boundary axis rather than repeatedly removing barriers.

## H — Marginal streamed-layer cost

After fixed activation is closed, the primary scalable problem is the measured ~39 ms/token/layer lifecycle.

Candidate one-factor treatments should target that repeated cost, not the already-tested fixed boundaries. Candidate classes:
- async scheduling/prefetch;
- buffering/grouped lifecycle;
- reconstruction/materialization reuse;
- source-range I/O only if evidence supports it;
- page-cache-aware source handling.

Physical SSD dominance remains unproven.

## I — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights across multiple exact-valid positions. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## J — Scale beyond 8B

1. close remaining fixed activation work
2. materially reduce/hide ~39 ms/layer marginal lifecycle
3. establish a substantially better exact 8B RAM/speed point
4. transfer architecture beyond comfortable physical RAM
5. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
6. optimize toward usable speed and measure capability

## Immediate order

1. NORM-EVAL-BOUNDARY 001
2. close fixed activation unless new evidence strongly justifies another boundary test
3. marginal streamed-layer treatment
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting systems

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
