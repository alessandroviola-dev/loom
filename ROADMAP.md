# LOOM Roadmap

Last updated: 2026-08-22
Current checkpoint: `MEMORY_FRONTIER_001_COMPLETE`
Detailed history through REALGEN 002 remains preserved at commit `844325f63b1880107040b219524ad5391276769c` and in individual research reports.

## Mission

Run excellent full-parameter-count LLMs on Apple M1 / 8 GB, ultimately toward ~27B/32B-class models. Judge major directions on memory, speed and capability.

Pi is reserved for code/tests. ChatGPT owns research direction and repository/project synchronization.

## A — Capability baseline — COMPLETE

Canonical practical-agent reference:
- CAPABILITY 001 primary: **1/11 = 9.09%**
- Coding Benchmark: **45/100**
- critical failures: 0

This is the behavior reference for future representation/model/runtime changes that can affect capability.

## B — MEMORY-FRONTIER 001 — COMPLETE

Report:
`research/memory/memory-frontier-001-result.md`

Real greedy M1 pooled frontier:

| Config | Resident fraction | Gen tok/s | Peak MLX | Min free |
|---|---:|---:|---:|---:|
| F0 FULL | 100.00% | 13.433 | 3,621,677,296 B | 23% |
| F1 H32 | 75.38% | 2.527 | 2,756,903,152 B | 24% |
| F2 H24 | 56.54% | 1.168 | 2,081,485,040 B | 34% |
| F3 H16 | 37.69% | 0.526 | 1,406,066,928 B | 47% |
| F4 H8 | 18.85% | 0.435 | 730,648,816 B | 57% |

All partial points preserve exact token-ID parity. No resource aborts. All five measured points are Pareto non-dominated.

Key result: current synchronous partial-residency streaming buys substantial memory but destroys most throughput. F1 saves ~865 MB peak MLX yet retains only **18.81%** of F0 generation throughput.

Do not equate logical streaming traffic with physical SSD traffic. At F1, logical streamed traffic is ~896 MB/token while process-read diagnostic is only ~26.5 MB/token.

## C — STREAMING-ATTRIBUTION 001 — NEXT

Frozen plan:
`research/memory/streaming-attribution-001-plan.md`

Before choosing an optimization, decompose F1 H32 real-M1 token wall among:
- source/range access;
- tensor/parameter reconstruction;
- required MLX materialization/synchronization;
- streamed-stage forward compute;
- cleanup/orchestration;
- residual/unclassified wall.

Use exact same F1 residency/model math, one canonical REALGEN prompt, 32 greedy unknown tokens, parity preflight and two fresh runs.

The goal is to identify the actual dominant synchronous cost. Do not add artificial `mx.synchronize()` boundaries just to make timings additive.

### Treatment routing after attribution

Only after STREAMING-ATTRIBUTION 001:
- if source access dominates -> test direct range-I/O/mmap/pread/page-cache behavior;
- if materialization/reconstruction dominates -> test persistent compressed structures, reconstruction amortization or buffering;
- if synchronization dominates -> redesign scheduling/overlap;
- if streamed forward compute dominates -> inspect execution path/kernel transfer overhead;
- if mixed -> isolate the largest addressable component first.

One factor per experiment.

## D — Hide / amortize streamed-weight cost

Candidate tools, only when justified by attribution:
1. asynchronous prefetch
2. double/triple buffering
3. transfer/super-layer chunk sizing
4. direct safetensors range I/O / mmap / pread
5. macOS page-cache behavior
6. resident-hotset refinement

OUTCORE-BLOCK 001 remains a later candidate for amortizing one streamed weight load over multiple exact-valid positions.

## E — Representation and capability

Potential later factors:
- mixed/selective precision
- compressed cold weights
- quantized KV
- out-of-core storage formats

Full parameter count remains a major project condition.

Any promoted behavior-affecting system must be evaluated against CAPABILITY 001 rather than promoted solely for fit/speed.

## F — Scale beyond 8B

1. attribute and reduce current partial-residency cost on well-characterized 8B
2. establish a materially better RAM/speed point than naive synchronous streaming
3. transfer architecture to models exceeding comfortable physical RAM
4. first major scale checkpoint: ~27B/32B-class full-parameter model produces correct tokens on M1 8 GB without OOM
5. optimize toward usable speed and measure capability

## Immediate order

1. STREAMING-ATTRIBUTION 001
2. first evidence-selected streaming treatment
3. further overlap/range-I/O/buffering work as justified
4. OUTCORE-BLOCK 001 where justified
5. representation work where justified
6. scale toward 27B/32B
7. capability comparison for promoted behavior-affecting candidates

## Local-only implementation warning

Experimental runners/raw evidence generally remain local unless explicitly synchronized. Pi should focus on code/tests. ChatGPT owns GitHub research documentation and project-state updates.
