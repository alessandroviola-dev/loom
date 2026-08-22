# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `SHARED_STAGE_RESIDENCY_001_COMPLETE`
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

Exact real-M1 parity passed across FULL/H32/H24/H16/H8.

| Config | Resident fraction | Gen tok/s | Peak MLX |
|---|---:|---:|---:|
| F0 | 100.00% | 13.433 | 3,621,677,296 B |
| F1 H32 | 75.38% | 2.527 | 2,756,903,152 B |
| F2 H24 | 56.54% | 1.168 | 2,081,485,040 B |
| F3 H16 | 37.69% | 0.526 | 1,406,066,928 B |
| F4 H8 | 18.85% | 0.435 | 730,648,816 B |

Naive synchronous streaming is memory-effective but far too slow.

## C — STREAMING-ATTRIBUTION 001 — PARTIAL

Exact parity passed, but invasive timing reduced F1 throughput by ~32.6%, so the internal bottleneck remains unresolved. Materialization/sync and shared stages appeared large, but no internal causal claim was promoted. Physical SSD traffic remains unproven.

## D — SHARED-STAGE-RESIDENCY 001 — COMPLETE

Report: `research/memory/shared-stage-residency-001-result.md`.

Direct low-overhead ABBA test:

CONTROL F1/H32:
- layers 32..35 + shared stages streamed
- 2.532 gen tok/s
- 882,255,872 logical B/token
- peak MLX 2,739,421,424 B

TREATMENT:
- same transformer residency
- only layers 32..35 streamed
- embedding/final norm/LM head persistent
- 3.459 gen tok/s
- 337,709,056 logical B/token
- peak MLX 3,283,968,240 B

Treatment effect:
- generation **+36.66%**
- E2E **+34.80%**
- TTFT **-13.34%**
- exact token parity PASS
- no resource aborts

The treatment still saves 337,709,056 B versus FULL, but retains only 25.75% of F0 generation throughput. Shared-stage streaming is therefore material but not the primary explanation for all remaining slowdown.

## E — STREAMED-LAYER-GRADIENT 001 — NEXT

Frozen plan: `research/memory/streamed-layer-gradient-001-plan.md`.

Keep embedding/final norm/LM head persistent in every arm and vary only the number of streamed transformer layers:
- S0: 0 streamed
- S1: 1 streamed
- S2: 2 streamed
- S4: 4 streamed

Use low-overhead symmetric fresh runs, exact token parity and identical streaming lifecycle for every streamed layer.

Primary question: is incremental real-M1 wall cost approximately additive per streamed transformer layer, or is there a large fixed/nonlinear cost?

If approximately additive, the next optimization must reduce/amortize the per-layer stream lifecycle itself. If fixed/nonlinear, scheduling/chunking/orchestration becomes a stronger first target.

## F — First transformer-stream optimization

Select only after STREAMED-LAYER-GRADIENT 001. Candidate one-factor treatments include:
- asynchronous scheduling/prefetch
- buffering
- reconstruction/materialization reuse
- direct range-I/O / mmap / pread
- stream-group/chunk lifecycle changes

Do not assume physical SSD is dominant without evidence.

## G — OUTCORE-BLOCK / representation

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed weights across exact-valid multi-position verification. Representation candidates include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

## H — Scale beyond 8B

1. quantify transformer stream lifecycle cost
2. materially reduce/amortize it on the exact 8B
3. establish a substantially better RAM/speed point
4. transfer architecture to models beyond comfortable physical RAM
5. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
6. optimize toward usable speed and measure capability

## Immediate order

1. STREAMED-LAYER-GRADIENT 001
2. first evidence-selected transformer-stream treatment
3. further overlap/range-I/O/materialization work as justified
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
