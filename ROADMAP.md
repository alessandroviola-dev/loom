# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `STREAMING_ATTRIBUTION_001_PARTIAL`
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

| Config | Resident fraction | Gen tok/s | Peak MLX | Min free |
|---|---:|---:|---:|---:|
| F0 | 100.00% | 13.433 | 3,621,677,296 B | 23% |
| F1 H32 | 75.38% | 2.527 | 2,756,903,152 B | 24% |
| F2 H24 | 56.54% | 1.168 | 2,081,485,040 B | 34% |
| F3 H16 | 37.69% | 0.526 | 1,406,066,928 B | 47% |
| F4 H8 | 18.85% | 0.435 | 730,648,816 B | 57% |

Conclusion: naive synchronous streaming is memory-effective but far too slow.

## C — STREAMING-ATTRIBUTION 001 — PARTIAL

Report: `research/memory/streaming-attribution-001-result.md`.

Exact parity passed, but tracing slowed F1 from historical 2.527 tok/s to ~1.703 tok/s pooled, so a primary bottleneck cannot be cleanly assigned.

Observed evidence:
- materialization/sync was the largest traced interval;
- LM head and embedding were the two largest stage hotspots;
- F1 token-path logical streaming = 882,255,872 B/token;
- embedding + final norm + LM head = 544,546,816 B/token (~61.7%);
- physical SSD traffic is not proven.

Classification: `ATTRIBUTION_UNRESOLVED`.

This is enough to motivate a direct low-overhead A/B on shared-stage persistence without claiming that materialization or SSD is definitively dominant.

## D — SHARED-STAGE-RESIDENCY 001 — NEXT

Frozen plan: `research/memory/shared-stage-residency-001-plan.md`.

CONTROL:
- H32 transformer residency
- layers 32..35 streamed
- embedding/final norm/LM head streamed
- persistent raw weights 2,701,672,448 B
- streamed token-path bytes 882,255,872 B

TREATMENT:
- identical H32 transformer residency
- layers 32..35 still streamed identically
- embedding/final norm/LM head persistent
- persistent raw weights 3,246,219,264 B
- streamed token-path bytes 337,709,056 B

Run contemporaneous ABBA control/treatment with exact token parity and first three canonical REALGEN prompts. Measure real M1 generation, E2E, TTFT, peak memory/headroom and logical/process-read diagnostics.

This test directly asks whether repeated streaming of large shared stages is a major addressable cost. No profiler-derived percentage claim is required.

## E — Hide / amortize streamed transformer cost

After the shared-stage A/B, select one factor from measured evidence:
- scheduling / asynchronous prefetch
- double/triple buffering
- direct range-I/O / mmap / pread
- chunk/super-layer sizing
- materialization/reconstruction reuse
- page-cache behavior

One factor at a time.

OUTCORE-BLOCK 001 remains a later candidate for amortizing streamed layer loads across multiple exact-valid positions.

## F — Representation and capability

Later factors may include mixed/selective precision, compressed cold weights, quantized KV and out-of-core formats. Full parameter count remains a major condition.

Any behavior-affecting promoted system must be evaluated against CAPABILITY 001 rather than promoted solely for memory/speed.

## G — Scale beyond 8B

1. obtain a materially better exact 8B RAM/speed point than naive synchronous streaming
2. reduce/hide streamed transformer cost
3. transfer the architecture to models beyond comfortable physical RAM
4. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
5. optimize toward usable speed and measure capability

## Immediate order

1. SHARED-STAGE-RESIDENCY 001
2. evidence-selected streaming treatment
3. further overlap/range-I/O/materialization work as justified
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
